"""
AI review service — converts an uploaded PDF into structured review notes.

Pipeline:
  1. Render each PDF page to an image (pymupdf)
  2. Send page images + system prompt to Claude vision API
  3. Parse and validate the JSON response via AIReviewNotes
  4. Return the validated result to the caller (plans router stores it)

This is a stub with the interface and prompt scaffolding in place.
Fill in the Anthropic client call once you have an API key.
"""

from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.schemas import AIReviewNotes

# Installed via: pip install anthropic pymupdf
# import anthropic
# import fitz  # pymupdf

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
    "scale_detected": "<e.g. \"1\\\" = 20'\" or null>",
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


def _build_user_message(jurisdiction: str | None) -> str:
    base = "Please review the attached engineering drawing for subdivision code compliance."
    if jurisdiction:
        base += f" The applicable jurisdiction is: {jurisdiction}."
    return base


async def run_ai_review(file_path: str, jurisdiction: str | None = None) -> AIReviewNotes:
    """
    Main entry point called by the plans router.

    Args:
        file_path:    Absolute path to the uploaded PDF.
        jurisdiction: Optional jurisdiction name to embed in the prompt.

    Returns:
        A validated AIReviewNotes object ready to be stored in the DB.
    """
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {file_path}")

    # ------------------------------------------------------------------
    # Step 1: Render PDF pages to base64 PNG images
    # ------------------------------------------------------------------
    # import fitz
    # doc = fitz.open(str(pdf_path))
    # images = []
    # for page in doc:
    #     pix = page.get_pixmap(dpi=150)
    #     images.append(pix.tobytes("png"))  # raw bytes; encode to base64 below
    # doc.close()

    # ------------------------------------------------------------------
    # Step 2: Build the message content (one image block per page)
    # ------------------------------------------------------------------
    # import base64
    # content = []
    # for img_bytes in images:
    #     content.append({
    #         "type": "image",
    #         "source": {
    #             "type": "base64",
    #             "media_type": "image/png",
    #             "data": base64.standard_b64encode(img_bytes).decode(),
    #         },
    #     })
    # content.append({"type": "text", "text": _build_user_message(jurisdiction)})

    # ------------------------------------------------------------------
    # Step 3: Call the Claude vision API
    # ------------------------------------------------------------------
    # client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    # response = client.messages.create(
    #     model=settings.review_model,
    #     max_tokens=2048,
    #     system=SYSTEM_PROMPT,
    #     messages=[{"role": "user", "content": content}],
    # )
    # raw_json = response.content[0].text

    # ------------------------------------------------------------------
    # Step 4: Validate the response against our schema
    # ------------------------------------------------------------------
    # import json
    # try:
    #     parsed = json.loads(raw_json)
    # except json.JSONDecodeError as e:
    #     raise ValueError(f"Model returned invalid JSON: {e}\n\nRaw output:\n{raw_json}")
    #
    # parsed["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    # parsed["model"] = settings.review_model
    # return AIReviewNotes.model_validate(parsed)

    # ------------------------------------------------------------------
    # Stub return — replace with the live call above
    # ------------------------------------------------------------------
    raise NotImplementedError(
        "AI review not yet wired up. "
        "Uncomment the steps above and install: pip install anthropic pymupdf"
    )