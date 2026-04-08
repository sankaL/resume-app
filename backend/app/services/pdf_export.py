from __future__ import annotations

import asyncio
import logging
from typing import Optional

import markdown

logger = logging.getLogger(__name__)

PDF_EXPORT_TIMEOUT_SECONDS = 20


def _build_html(markdown_content: str, personal_info: Optional[dict] = None) -> str:
    """Build full HTML document from Markdown content with ATS-safe CSS."""
    header_block = ""
    if personal_info:
        name = personal_info.get("name") or ""
        parts = []
        if personal_info.get("email"):
            parts.append(personal_info["email"])
        if personal_info.get("phone"):
            parts.append(personal_info["phone"])
        if personal_info.get("address"):
            parts.append(personal_info["address"])
        contact_line = " | ".join(parts)
        header_block = f"<div class='personal-header'><h1>{name}</h1>"
        if contact_line:
            header_block += f"<p class='contact'>{contact_line}</p>"
        header_block += "</div>"

    html_body = markdown.markdown(
        markdown_content,
        extensions=["extra", "sane_lists"],
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.4;
    color: #333;
    margin: 0.75in;
}}
.personal-header {{
    text-align: center;
    margin-bottom: 12pt;
}}
.personal-header h1 {{
    font-size: 20pt;
    margin: 0 0 4pt 0;
    color: #111;
}}
.personal-header .contact {{
    font-size: 10pt;
    color: #555;
    margin: 0;
}}
h1 {{ font-size: 18pt; margin-bottom: 4pt; color: #111; }}
h2 {{ font-size: 13pt; margin-top: 16pt; margin-bottom: 6pt; border-bottom: 1pt solid #999; padding-bottom: 2pt; color: #111; }}
h3 {{ font-size: 11pt; margin-top: 10pt; margin-bottom: 4pt; color: #222; }}
p {{ margin: 4pt 0; }}
ul {{ margin: 4pt 0; padding-left: 20pt; }}
li {{ margin: 2pt 0; }}
/* ATS-safe: no tables, images, or decorative elements */
</style></head>
<body>{header_block}{html_body}</body></html>"""


def _generate_pdf_sync(html: str) -> bytes:
    """Synchronous WeasyPrint conversion. Import is deferred to avoid
    failing at module-load time when native libs are absent (e.g. local dev on macOS)."""
    import weasyprint  # noqa: WPS433 — deferred import
    return weasyprint.HTML(string=html).write_pdf()


async def generate_pdf(
    markdown_content: str,
    personal_info: Optional[dict] = None,
) -> bytes:
    """Convert Markdown to ATS-safe PDF via HTML intermediate.

    Runs WeasyPrint in a thread pool to avoid blocking the event loop.
    Enforced timeout of PDF_EXPORT_TIMEOUT_SECONDS.

    Returns PDF bytes.
    Raises asyncio.TimeoutError if conversion exceeds timeout.
    """
    html = _build_html(markdown_content, personal_info)
    loop = asyncio.get_running_loop()
    pdf_bytes = await asyncio.wait_for(
        loop.run_in_executor(None, _generate_pdf_sync, html),
        timeout=PDF_EXPORT_TIMEOUT_SECONDS,
    )
    return pdf_bytes
