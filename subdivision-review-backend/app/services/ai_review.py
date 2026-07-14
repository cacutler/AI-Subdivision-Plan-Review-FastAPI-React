"""
AI review service — converts an uploaded PDF into structured review notes.
"""

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import fitz  # pymupdf

from app.config import settings
from app.schemas import AIReviewNotes

SYSTEM_PROMPT = """
You are an expert civil engineering plan reviewer specializing in city subdivision code compliance.

You will be given one or more images of a civil/structural engineering drawing (site plans,
grading plans, utility plans, etc.). Review them carefully and return a JSON object — with no
preamble, markdown, or commentary — that conforms exactly to this schema:

{
  "review_version": "1.0",
  "reviewed_at": "<ISO 8601 UTC timestamp>",
  "model": "<model name>",
  "overall_status": "pass" | "pass_with_notes" | "fail",
  "confidence": "high" | "medium" | "low",
  "summary": "<1-3 sentence plain-English description of what the drawing shows>",
  "jurisdiction": "<jurisdiction name or null>",
  "findings": [
    {
      "id": "F-001",
      "category": "setback" | "lot_coverage" | "easement" | "grading" | "utilities" | "notation" | "other",
      "description": "<plain-English description of the issue>",
      "code_reference": "<specific clause e.g. §18.40.050(B), or null if you cannot cite one with confidence>",
      "location_description": "<human-readable location on the drawing, or null>",
      "page": <page number integer, or null for single-page drawings>
    }
  ],
  "drawing_metadata": {
    "drawing_type": "<e.g. 'site plan', 'grading plan', or null>",
    "scale_detected": "<e.g. \\"1\\\\" = 20'\\" or null>",
    "north_arrow_present": true | false | null,
    "legend_present": true | false | null
  }
}

Rules:
- Return ONLY the JSON object. No markdown fences, no preamble.
- Set code_reference to null if you cannot cite a specific clause with confidence.
  Never fabricate a citation.
- Set overall_status to "fail" only if there are clear code violations.
  Use "pass_with_notes" for concerns that need engineer attention but are not clear violations.
- Set confidence to "low" if the drawing is illegible, incomplete, or ambiguous.
- findings may be an empty array if the drawing passes with no issues.
""".strip()

_MAX_PAGES = 15  # guardrail — large drawing sets can blow past token/image limits


def _build_user_message(jurisdiction: str | None) -> str:
    base = "Please review the attached engineering drawing for subdivision code compliance."
    if jurisdiction:
        base += f" The applicable jurisdiction is: {jurisdiction}."
    return base


def _render_pdf_to_images(pdf_path: Path) -> list[bytes]:
    """Render each page to a PNG at 150 DPI — enough detail for text/dimensions
    without producing images so large they blow past API size limits."""
    doc = fitz.open(str(pdf_path))
    try:
        if doc.page_count > _MAX_PAGES:
            raise ValueError(
                f"PDF has {doc.page_count} pages; max supported is {_MAX_PAGES}"
            )
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            images.append(pix.tobytes("png"))
        return images
    finally:
        doc.close()


def _strip_json_fences(raw: str) -> str:
    """Defensive: models sometimes wrap JSON in ```json fences despite instructions."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


async def run_ai_review(file_path: str, jurisdiction: str | None = None) -> AIReviewNotes:
    """
    Main entry point called by the plans router.
    """
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {file_path}")

    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    # Step 1: Render PDF pages to images
    images = _render_pdf_to_images(pdf_path)

    # Step 2: Build message content — one image block per page
    content = []
    for img_bytes in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.standard_b64encode(img_bytes).decode()
            }
        })
    content.append({"type": "text", "text": _build_user_message(jurisdiction)})

    # Step 3: Call the Claude vision API
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        response = client.messages.create(
            model=settings.review_model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}]
        )
    except anthropic.APIError as exc:
        raise RuntimeError(f"Anthropic API call failed: {exc}") from exc

    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    # Step 4: Validate the response against our schema
    try:
        parsed = json.loads(_strip_json_fences(raw_text))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON: {exc}\n\nRaw output:\n{raw_text}"
        ) from exc

    parsed["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    parsed["model"] = settings.review_model

    return AIReviewNotes.model_validate(parsed)