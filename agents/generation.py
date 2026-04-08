"""Section-based resume generation service.

Generates each enabled resume section individually via LLM, grounded in
the user's base resume and the target job posting.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Callable, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Aggressiveness descriptions
# ---------------------------------------------------------------------------

AGGRESSIVENESS_DESCRIPTIONS: dict[str, str] = {
    "low": (
        "Minimal change; preserve original voice and structure "
        "with light keyword alignment."
    ),
    "medium": (
        "Moderate tailoring; reword and reorder to align with job requirements."
    ),
    "high": (
        "Stronger tailoring; significant rewrite while grounded in source content."
    ),
}

TARGET_LENGTH_GUIDANCE: dict[str, str] = {
    "1_page": "Keep content concise – the entire resume should fit on one page.",
    "2_page": "Content may be more detailed – the resume can span up to two pages.",
}

SUPPORTED_SECTIONS = {"summary", "professional_experience", "education", "skills"}

SECTION_DISPLAY_NAMES: dict[str, str] = {
    "summary": "Summary",
    "professional_experience": "Professional Experience",
    "education": "Education",
    "skills": "Skills",
}


# ---------------------------------------------------------------------------
# Pydantic model for structured LLM output
# ---------------------------------------------------------------------------


class GeneratedSection(BaseModel):
    """Structured output returned by the section-generation LLM call."""

    content: str = Field(
        description="The generated Markdown content for this resume section, "
        "including the ## heading."
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_section_prompt(
    *,
    section_name: str,
    base_resume_content: str,
    job_title: str,
    company_name: str,
    job_description: str,
    aggressiveness: str,
    target_length: str,
    additional_instructions: Optional[str],
) -> list[tuple[str, str]]:
    """Build the chat prompt for generating a single section."""

    aggressiveness_desc = AGGRESSIVENESS_DESCRIPTIONS.get(
        aggressiveness, AGGRESSIVENESS_DESCRIPTIONS["medium"]
    )
    length_guidance = TARGET_LENGTH_GUIDANCE.get(
        target_length, TARGET_LENGTH_GUIDANCE["1_page"]
    )
    display_name = SECTION_DISPLAY_NAMES.get(section_name, section_name.replace("_", " ").title())

    system_msg = (
        "You are a professional resume writer specializing in ATS-optimized resumes. "
        f"Generate only the {display_name} section.\n\n"
        "RULES:\n"
        "- Output clean Markdown starting with a `## {heading}` line.\n"
        "- ALL content MUST be grounded in the base resume provided. "
        "Do NOT invent employers, titles, dates, credentials, or educational institutions. "
        "Only use information present in the base resume.\n"
        "- Do NOT include personal information (name, email, phone, address).\n"
        f"- Tailoring level: {aggressiveness_desc}\n"
        f"- Target page length guidance: {length_guidance}\n"
        "- Use standard Markdown only: headings, bullets, bold, italic. "
        "No tables, images, or HTML.\n"
    )

    if additional_instructions:
        system_msg += f"\nAdditional user instructions: {additional_instructions}\n"

    human_msg = (
        f"Target Position: {job_title} at {company_name}\n\n"
        f"## Job Description\n{job_description}\n\n"
        f"## Base Resume (source of truth)\n{base_resume_content}\n\n"
        f"Based on the above base resume, generate the **{display_name}** section "
        "tailored to the job description."
    )

    return [("system", system_msg), ("human", human_msg)]


async def _call_llm_with_fallback(
    *,
    prompt: list[tuple[str, str]],
    model: str,
    fallback_model: str,
    api_key: str,
    base_url: str,
    timeout: float = 30.0,
) -> tuple[str, str]:
    """Call LLM with primary model, fall back on failure.

    Returns (content, model_used).
    """
    last_error: Optional[Exception] = None
    for model_name in (model, fallback_model):
        try:
            llm = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=base_url,
                temperature=0.4,
                request_timeout=timeout,
            ).with_structured_output(GeneratedSection)

            result: GeneratedSection = await asyncio.wait_for(
                llm.ainvoke(prompt),
                timeout=timeout,
            )
            return result.content, model_name
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "LLM generation failed on both primary and fallback models."
    ) from last_error


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_sections(
    *,
    base_resume_content: str,
    job_title: str,
    company_name: str,
    job_description: str,
    section_preferences: list[dict[str, Any]],
    generation_settings: dict[str, Any],
    model: str,
    fallback_model: str,
    api_key: str,
    base_url: str,
    on_progress: Callable,
) -> dict[str, Any]:
    """Generate each enabled section individually via LLM.

    Returns ``{"sections": [{"name": str, "content": str}], "model_used": str}``.
    """

    enabled = sorted(
        [s for s in section_preferences if s.get("enabled")],
        key=lambda s: s.get("order", 0),
    )

    if not enabled:
        raise ValueError("No enabled sections to generate.")

    aggressiveness = generation_settings.get("aggressiveness", "medium")
    target_length = generation_settings.get("page_length", generation_settings.get("target_length", "1_page"))
    additional_instructions = generation_settings.get("additional_instructions")

    sections: list[dict[str, str]] = []
    model_used = model
    total = len(enabled)

    for idx, pref in enumerate(enabled):
        section_name = pref["name"]
        if section_name not in SUPPORTED_SECTIONS:
            continue

        prompt = _build_section_prompt(
            section_name=section_name,
            base_resume_content=base_resume_content,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            aggressiveness=aggressiveness,
            target_length=target_length,
            additional_instructions=additional_instructions,
        )

        content, used = await _call_llm_with_fallback(
            prompt=prompt,
            model=model,
            fallback_model=fallback_model,
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
        )
        model_used = used
        sections.append({"name": section_name, "content": content.strip()})

        percent = 10 + int((idx + 1) / total * 70)
        await on_progress(percent, f"Generated {section_name} section")

    return {"sections": sections, "model_used": model_used}


def _parse_markdown_sections(content: str) -> list[tuple[str, str]]:
    """Parse a Markdown document into sections split on ``## `` headings.

    Returns a list of ``(heading_text, section_body)`` tuples.  The personal
    info header (starting with ``# ``) and any content before the first ``## ``
    is returned as ``("__header__", body)``.
    """

    parts: list[tuple[str, str]] = []
    current_heading = "__header__"
    current_lines: list[str] = []

    for line in content.splitlines(keepends=True):
        if line.startswith("## "):
            # Flush previous section
            parts.append((current_heading, "".join(current_lines)))
            current_heading = line.strip().lstrip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    # Flush last section
    parts.append((current_heading, "".join(current_lines)))
    return parts


def _replace_section_in_draft(
    draft: str,
    section_name: str,
    new_content: str,
    display_name: str,
) -> str:
    """Replace a section in the Markdown draft identified by its ``## `` heading.

    Falls back to appending if the section heading isn't found.
    """

    # Build a regex that matches the section heading through the next ## or EOF
    pattern = re.compile(
        rf"(^##\s*{re.escape(display_name)}\s*\n)(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(draft)
    if match:
        # Ensure new_content ends with a trailing newline for clean separation
        replacement = new_content.rstrip("\n") + "\n\n"
        return draft[: match.start()] + replacement + draft[match.end() :]

    # Section heading not found – append at end
    return draft.rstrip("\n") + "\n\n" + new_content.strip() + "\n"


async def regenerate_single_section(
    *,
    current_draft_content: str,
    section_name: str,
    instructions: str,
    base_resume_content: str,
    job_title: str,
    company_name: str,
    job_description: str,
    generation_settings: dict[str, Any],
    model: str,
    fallback_model: str,
    api_key: str,
    base_url: str,
) -> str:
    """Regenerate a single section with user instructions.

    Parses the current draft to locate the target section, generates a new
    version via LLM, replaces it in the draft, and returns the complete
    updated draft Markdown.
    """

    aggressiveness = generation_settings.get("aggressiveness", "medium")
    target_length = generation_settings.get("page_length", generation_settings.get("target_length", "1_page"))
    aggressiveness_desc = AGGRESSIVENESS_DESCRIPTIONS.get(
        aggressiveness, AGGRESSIVENESS_DESCRIPTIONS["medium"]
    )
    length_guidance = TARGET_LENGTH_GUIDANCE.get(
        target_length, TARGET_LENGTH_GUIDANCE["1_page"]
    )
    display_name = SECTION_DISPLAY_NAMES.get(
        section_name, section_name.replace("_", " ").title()
    )

    system_msg = (
        "You are a professional resume writer specializing in ATS-optimized resumes. "
        f"Regenerate only the {display_name} section based on the user's instructions.\n\n"
        "RULES:\n"
        "- Output clean Markdown starting with a `## {heading}` line.\n"
        "- ALL content MUST be grounded in the base resume provided. "
        "Do NOT invent employers, titles, dates, credentials, or educational institutions. "
        "Only use information present in the base resume.\n"
        "- Do NOT include personal information (name, email, phone, address).\n"
        f"- Tailoring level: {aggressiveness_desc}\n"
        f"- Target page length guidance: {length_guidance}\n"
        "- Use standard Markdown only: headings, bullets, bold, italic. "
        "No tables, images, or HTML.\n"
        f"\nUser instructions for regeneration: {instructions}\n"
    )

    human_msg = (
        f"Target Position: {job_title} at {company_name}\n\n"
        f"## Job Description\n{job_description}\n\n"
        f"## Base Resume (source of truth)\n{base_resume_content}\n\n"
        f"## Current Draft (full resume)\n{current_draft_content}\n\n"
        f"Based on the above, regenerate the **{display_name}** section "
        "following the user instructions."
    )

    prompt: list[tuple[str, str]] = [("system", system_msg), ("human", human_msg)]

    content, _ = await _call_llm_with_fallback(
        prompt=prompt,
        model=model,
        fallback_model=fallback_model,
        api_key=api_key,
        base_url=base_url,
        timeout=30.0,
    )

    return content.strip()
