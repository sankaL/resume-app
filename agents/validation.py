"""Resume validation service.

Validates generated resume sections against the base resume for
hallucinations, completeness, ordering, and ATS safety.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pydantic models for structured LLM output
# ---------------------------------------------------------------------------


class HallucinationFinding(BaseModel):
    section: str = Field(description="Section name where the hallucination was found.")
    claim: str = Field(description="The specific claim that is NOT supported by the base resume.")
    reason: str = Field(description="Why this is considered hallucinated.")


class HallucinationCheckResult(BaseModel):
    has_hallucinations: bool = Field(
        description="True if any claims were found that are not supported by the base resume."
    )
    findings: list[HallucinationFinding] = Field(
        default_factory=list,
        description=(
            "List of claims in the generated resume that are NOT supported by "
            "the base resume. Each item identifies the section, the specific "
            "unsupported claim, and the reason it is considered hallucinated. "
            "Return an empty list if everything is grounded."
        ),
    )


# ---------------------------------------------------------------------------
# Individual validation checks
# ---------------------------------------------------------------------------


async def _check_hallucinations(
    *,
    generated_sections: list[dict[str, Any]],
    base_resume_content: str,
    model: str,
    fallback_model: str,
    api_key: str,
    base_url: str,
) -> list[dict[str, Any]]:
    """LLM-based hallucination detection."""

    generated_text = "\n\n".join(
        f"### Section: {s['name']}\n{s['content']}" for s in generated_sections
    )

    system_msg = (
        "You are a resume validation assistant. Compare the generated resume "
        "sections against the base resume and identify ANY claims in the generated "
        "content that are NOT supported by the base resume.\n\n"
        "Look specifically for:\n"
        "- Invented employers or companies not mentioned in the base resume\n"
        "- Job titles that don't appear in the base resume\n"
        "- Dates (start/end) that differ from the base resume\n"
        "- Credentials, certifications, or degrees not in the base resume\n"
        "- Educational institutions not in the base resume\n"
        "- Skills or technologies not reasonably inferable from the base resume\n\n"
        "Set has_hallucinations to true if you find ANY unsupported claims. "
        "If everything is properly grounded, set has_hallucinations to false "
        "and return an empty findings list."
    )

    human_msg = (
        f"## Base Resume (source of truth)\n{base_resume_content}\n\n"
        f"## Generated Resume Sections\n{generated_text}"
    )

    prompt: list[tuple[str, str]] = [("system", system_msg), ("human", human_msg)]

    last_error: Optional[Exception] = None
    for model_name in (model, fallback_model):
        try:
            llm = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=base_url,
                temperature=0,
                request_timeout=30.0,
            ).with_structured_output(HallucinationCheckResult)

            result: HallucinationCheckResult = await asyncio.wait_for(
                llm.ainvoke(prompt),
                timeout=30.0,
            )

            return [
                {
                    "type": "hallucination",
                    "section": f.section,
                    "detail": f"{f.claim} — {f.reason}",
                }
                for f in result.findings
            ]
        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "Hallucination check failed on both primary and fallback models."
    ) from last_error


def _check_required_sections(
    *,
    generated_sections: list[dict[str, Any]],
    section_preferences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Verify all enabled sections are present in generated output."""

    enabled_names = {
        s["name"] for s in section_preferences if s.get("enabled")
    }
    generated_names = {s["name"] for s in generated_sections}
    errors: list[dict[str, Any]] = []

    for name in enabled_names:
        if name not in generated_names:
            errors.append(
                {
                    "type": "missing_section",
                    "section": name,
                    "detail": f"Section is enabled but not generated: {name}",
                }
            )

    return errors


def _check_section_order(
    *,
    generated_sections: list[dict[str, Any]],
    section_preferences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Verify sections are in the correct order per preferences."""

    enabled_ordered = sorted(
        [s for s in section_preferences if s.get("enabled")],
        key=lambda s: s.get("order", 0),
    )
    expected_order = [s["name"] for s in enabled_ordered]
    actual_order = [s["name"] for s in generated_sections]

    # Filter to only sections that exist in both lists
    expected_filtered = [n for n in expected_order if n in set(actual_order)]
    actual_filtered = [n for n in actual_order if n in set(expected_order)]

    errors: list[dict[str, Any]] = []
    if expected_filtered != actual_filtered:
        errors.append(
            {
                "type": "wrong_order",
                "section": None,
                "detail": (
                    f"Section order mismatch. Expected: {expected_filtered}, "
                    f"got: {actual_filtered}"
                ),
            }
        )

    return errors


def _check_ats_safety(
    *,
    generated_sections: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Rule-based ATS safety check. Returns (errors, auto_corrections)."""

    errors: list[dict[str, Any]] = []
    auto_corrections: list[dict[str, Any]] = []

    table_pattern = re.compile(r"^\s*\|.*\|.*\|", re.MULTILINE)
    image_pattern = re.compile(r"!\[")

    for section in generated_sections:
        content = section["content"]
        name = section["name"]

        if table_pattern.search(content):
            errors.append(
                {
                    "type": "ats_violation",
                    "section": name,
                    "detail": f"Table detected in {name} section",
                }
            )

        if image_pattern.search(content):
            errors.append(
                {
                    "type": "ats_violation",
                    "section": name,
                    "detail": f"Image reference detected in {name} section",
                }
            )

        # Auto-correct: strip extra blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", content)
        if cleaned != content:
            auto_corrections.append(
                {
                    "type": "formatting",
                    "detail": f"Fixed extra blank lines in {name}",
                }
            )
            section["content"] = cleaned

    return errors, auto_corrections


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def validate_resume(
    *,
    generated_sections: list[dict[str, Any]],
    base_resume_content: str,
    section_preferences: list[dict[str, Any]],
    model: str,
    fallback_model: str,
    api_key: str,
    base_url: str,
) -> dict[str, Any]:
    """Validate generated resume.

    Returns::

        {
            "valid": bool,
            "errors": [{"type": str, "section": str|None, "detail": str}],
            "auto_corrections": [{"type": str, "detail": str}],
        }
    """

    all_errors: list[dict[str, Any]] = []
    all_corrections: list[dict[str, Any]] = []

    # 1. LLM-based hallucination detection
    hallucination_errors = await _check_hallucinations(
        generated_sections=generated_sections,
        base_resume_content=base_resume_content,
        model=model,
        fallback_model=fallback_model,
        api_key=api_key,
        base_url=base_url,
    )
    all_errors.extend(hallucination_errors)

    # 2. Required sections check
    missing_errors = _check_required_sections(
        generated_sections=generated_sections,
        section_preferences=section_preferences,
    )
    all_errors.extend(missing_errors)

    # 3. Section ordering check
    order_errors = _check_section_order(
        generated_sections=generated_sections,
        section_preferences=section_preferences,
    )
    all_errors.extend(order_errors)

    # 4. ATS-safety check (also applies auto-corrections in-place)
    ats_errors, ats_corrections = _check_ats_safety(
        generated_sections=generated_sections,
    )
    all_errors.extend(ats_errors)
    all_corrections.extend(ats_corrections)

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "auto_corrections": all_corrections,
    }
