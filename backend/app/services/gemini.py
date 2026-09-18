"""
Gemini Vision service.

Sends dental images to Google Gemini for preliminary visual screening analysis.
When MOCK_AI=true, returns deterministic sample findings instead.
Strictly adheres to non-diagnostic, explainable, and medical safety principles.
"""

import os
import re
import json
import logging
from typing import Dict, Any

from app.schemas.analysis import DentalFindings, FindingDetail, Severity, Evidence, BoundingBox

logger = logging.getLogger(__name__)

# ── Upgraded Strict Screening Prompt ─────────────────────────────────────────
ANALYSIS_PROMPT = """
You are analyzing photographs for a preliminary visual oral-health screening.
You are reviewing 5 dental photographs (front, left, right, upper, lower).

CRITICAL MEDICAL, LEGAL & SAFETY RULES:
- You are an AI preliminary visual screening tool, NOT a dentist.
- You must ONLY describe visible optical characteristics.
- You must NOT diagnose disease (no diagnosis of caries, periodontal disease, gingivitis, malocclusion, bruxism, etc.).
- You must NOT infer hidden pathology (e.g. subgingival calculus, internal root resorption, nerve vitality).
- You must NOT invent visual evidence.
- You must use "uncertain" when the image does not contain sufficient evidence or is obscured.
- Use cautious screening language: "possible", "visible", "appears", "may indicate".
- NEVER use definitive clinical terms: "definitely", "confirmed", "diagnosed", "patient has".
- If no notable visual concerns are seen, use "No obvious visible concern observed".

Analyze the following four categories based ONLY on direct visual observations:

1. ALIGNMENT:
   - Look for visible crowding, spacing, crookedness, or obvious rotation.
   - Do NOT diagnose orthodontic classification.

2. DISCOLORATION:
   - Look for visible surface staining, uneven coloration, or yellow/brown areas.
   - Do NOT diagnose cavities or decay. Use phrases like: "Possible visible staining on some tooth surfaces."

3. TOOTH WEAR:
   - Look for visible surface flattening, edge chipping, or visible wear patterns.
   - Do NOT diagnose cause of wear or bruxism.

4. GUM APPEARANCE:
   - Look for visible redness, swelling, or visible appearance changes along the gum margin.
   - Do NOT diagnose gingivitis or infection.

Return ONLY a valid JSON object matching this exact schema:

{
  "alignment": {
    "finding": "<cautious observation or 'No obvious visible concern observed'>",
    "severity": "<none|mild|moderate|marked|uncertain>",
    "confidence": <float between 0.0 and 1.0>,
    "evidence": {
      "image": "<front|left|right|upper|lower>",
      "region": {"x": <0.0-1.0>, "y": <0.0-1.0>, "width": <0.0-1.0>, "height": <0.0-1.0>}
    }
  },
  "discoloration": {
    "finding": "<cautious observation or 'No obvious visible concern observed'>",
    "severity": "<none|mild|moderate|marked|uncertain>",
    "confidence": <float between 0.0 and 1.0>,
    "evidence": null
  },
  "tooth_wear": {
    "finding": "<cautious observation or 'No obvious visible concern observed'>",
    "severity": "<none|mild|moderate|marked|uncertain>",
    "confidence": <float between 0.0 and 1.0>,
    "evidence": null
  },
  "gum_appearance": {
    "finding": "<cautious observation or 'No obvious visible concern observed'>",
    "severity": "<none|mild|moderate|marked|uncertain>",
    "confidence": <float between 0.0 and 1.0>,
    "evidence": null
  }
}

Evidence rules:
- Set evidence to null if no specific localized region can be reliably identified.
- Never fabricate coordinates. If reliable localization exists, region must be normalized [0.0 - 1.0].
"""

# ── Canonical Mock Data ──────────────────────────────────────────────────────
MOCK_FINDINGS_DATA: dict[str, Any] = {
    "alignment": {
        "finding": "Possible mild crowding visible in the lower anterior teeth",
        "severity": "mild",
        "confidence": 0.82,
        "evidence": {
            "image": "front",
            "region": {"x": 0.38, "y": 0.52, "width": 0.24, "height": 0.22}
        }
    },
    "discoloration": {
        "finding": "Possible visible surface staining observed along outer tooth surfaces",
        "severity": "mild",
        "confidence": 0.85,
        "evidence": {
            "image": "front",
            "region": {"x": 0.44, "y": 0.36, "width": 0.16, "height": 0.18}
        }
    },
    "tooth_wear": {
        "finding": "No obvious visible surface flattening or significant wear patterns detected",
        "severity": "none",
        "confidence": 0.78,
        "evidence": None
    },
    "gum_appearance": {
        "finding": "Possible mild redness visible along the gum margins",
        "severity": "mild",
        "confidence": 0.71,
        "evidence": None
    }
}


def analyze_images(images: Dict[str, bytes]) -> DentalFindings:
    """
    Analyze five dental images.

    If MOCK_AI=true, returns deterministic mock findings.
    Otherwise calls Google Gemini Vision API.
    """
    mock_mode = os.getenv("MOCK_AI", "true").lower() in ("true", "1", "yes")

    if mock_mode:
        logger.info("MOCK_AI enabled — returning deterministic sample findings")
        return DentalFindings.model_validate(MOCK_FINDINGS_DATA)

    return _call_gemini(images)


def _detect_mime(data: bytes) -> str:
    """Infer mime type from image magic bytes."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"RIFF") and len(data) > 12 and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _extract_json_text(text: str) -> str:
    """Extract raw JSON from possible markdown code blocks or surrounding text."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def _call_gemini(images: Dict[str, bytes]) -> DentalFindings:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Set it in .env or set MOCK_AI=true.")

    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        raise RuntimeError("google-genai package is not installed. Run: pip install google-genai")

    client = genai.Client(api_key=api_key)

    # Build content parts: prompt text + 5 images
    parts = [genai_types.Part.from_text(text=ANALYSIS_PROMPT)]

    image_order = ["front", "left", "right", "upper", "lower"]
    for view in image_order:
        img_bytes = images.get(view)
        if img_bytes:
            mime = _detect_mime(img_bytes)
            parts.append(
                genai_types.Part.from_bytes(data=img_bytes, mime_type=mime)
            )

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    logger.info("Calling Gemini model: %s", model_name)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=parts,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )
        )
        response_text = response.text or ""
    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        raise RuntimeError(f"Gemini API request failed: {exc}") from exc

    clean_json = _extract_json_text(response_text)
    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON from Gemini response: %s\nRaw output: %s", exc, response_text)
        raise ValueError("Model output was not valid JSON.") from exc

    try:
        return DentalFindings.model_validate(data)
    except Exception as exc:
        logger.error("Findings failed Pydantic schema validation: %s\nData: %s", exc, data)
        raise ValueError("AI output did not match expected findings schema.") from exc
