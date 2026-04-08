"""Resume assembly service.

Combines a personal-info header with ordered generated sections into a
single clean Markdown document.
"""

from __future__ import annotations

from typing import Any, Optional


def assemble_resume(
    *,
    personal_info: dict[str, Any],
    generated_sections: list[dict[str, str]],
) -> str:
    """Assemble final Markdown from personal info header + ordered sections.

    Args:
        personal_info: ``{"name": str, "email": str, "phone": str|None, "address": str|None}``
        generated_sections: ``[{"name": str, "content": str}]`` already in order.

    Returns:
        Complete Markdown resume string.  Personal info MUST come from the
        profile, NOT from LLM generation.
    """

    lines: list[str] = []

    # -- Header: name --
    name: str = personal_info.get("name", "").strip()
    if name:
        lines.append(f"# {name}")
    else:
        lines.append("# (Name)")

    # -- Contact line --
    contact_parts: list[str] = []
    email: Optional[str] = personal_info.get("email")
    if email and email.strip():
        contact_parts.append(email.strip())
    phone: Optional[str] = personal_info.get("phone")
    if phone and phone.strip():
        contact_parts.append(phone.strip())
    address: Optional[str] = personal_info.get("address")
    if address and address.strip():
        contact_parts.append(address.strip())

    if contact_parts:
        lines.append(" | ".join(contact_parts))

    # -- Blank separator --
    lines.append("")

    # -- Sections --
    for section in generated_sections:
        content = section.get("content", "").strip()
        if content:
            lines.append(content)
            lines.append("")  # blank line between sections

    return "\n".join(lines).rstrip("\n") + "\n"
