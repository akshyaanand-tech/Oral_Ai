import io
import os
import re
import json
import time
import logging
from typing import Dict, Any

from app.schemas.analysis import DentalFindings, FindingDetail, Severity, Evidence, BoundingBox

logger = logging.getLogger(__name__)

# ── Fallback model chain ──────────────────────────────────────────────────────
# Tried in order; skips to the next on 503 / UNAVAILABLE / high-demand errors.
# Only use real, verified Google Gemini model identifiers here.
FALLBACK_MODELS = [
    "gemini-3.5-flash",       # Try 3.5 first — often less loaded than 3.6
    "gemini-3.6-flash",       # Recommended for new users
    "gemini-3.7-flash",
    "gemini-3.1-flash-lite",  # Lightest model — fastest fallback
    "gemini-2.5-flash",       # Legacy — may fail for new API keys
]

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
    Otherwise calls Google Gemini Vision API with automatic model fallback.
    """
    # Default to LIVE AI. Mock mode only activates when MOCK_AI is explicitly set to true/1/yes.
    mock_mode = os.getenv("MOCK_AI", "false").lower() in ("true", "1", "yes")

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


# ── Image compression ─────────────────────────────────────────────────────────
_MAX_DIM = 800       # max width or height in pixels
_JPEG_QUALITY = 85   # JPEG quality (85 keeps dental detail, cuts size ~75-80%)


def _compress_image(data: bytes) -> bytes:
    """Resize to _MAX_DIM x _MAX_DIM and re-encode as JPEG to shrink payload."""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as img:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img.thumbnail((_MAX_DIM, _MAX_DIM), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
            compressed = buf.getvalue()
            logger.debug(
                "Compressed image: %d KB → %d KB",
                len(data) // 1024,
                len(compressed) // 1024,
            )
            return compressed
    except Exception as exc:
        logger.warning("Image compression failed (%s) — using original bytes", exc)
        return data


def _compress_images(images: Dict[str, bytes]) -> Dict[str, bytes]:
    """Compress all five dental images before sending to the API."""
    return {view: _compress_image(data) for view, data in images.items()}


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


def _is_transient(error_msg: str) -> bool:
    """Return True if the error should be skipped to try the next fallback model.

    Covers:
    - 503 / UNAVAILABLE / high-demand: temporary server overload
    - 404 'no longer available': model has been deprecated by Google
    """
    transient_markers = (
        "503", "UNAVAILABLE", "high demand", "overloaded", "try again later",
        # Deprecated / non-existent model — treat as skippable so the chain continues
        "no longer available", "404", "not found", "invalid model",
    )
    lower = error_msg.lower()
    return any(m.lower() in lower for m in transient_markers)


# ── Per-model retry settings ──────────────────────────────────────────────────
_MAX_RETRIES_PER_MODEL = 2   # 2 attempts per model before moving to next (fail fast)
_RETRY_BASE_SLEEP = 1        # seconds (1s, 2s) — short sleep so we reach a working model quickly


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

    # ── Compress all images before building parts (reduces payload ~75-80%) ──
    compressed = _compress_images(images)
    logger.info(
        "Image compression complete. Sizes (KB): %s",
        {v: len(b) // 1024 for v, b in compressed.items()},
    )

    # Build content parts: prompt text + 5 compressed JPEG images
    parts = [genai_types.Part.from_text(text=ANALYSIS_PROMPT)]
    image_order = ["front", "left", "right", "upper", "lower"]
    for view in image_order:
        img_bytes = compressed.get(view)
        if img_bytes:
            parts.append(genai_types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))

    # Build model list: env override goes first, then the fallback chain
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    models_to_try = ([env_model] if env_model and env_model not in FALLBACK_MODELS else []) + FALLBACK_MODELS

    last_exception: Exception | None = None

    for model_name in models_to_try:
        # ── Per-model retry loop with exponential backoff for 503s ────────────
        for attempt in range(1, _MAX_RETRIES_PER_MODEL + 1):
            logger.info("Model %s — attempt %d/%d", model_name, attempt, _MAX_RETRIES_PER_MODEL)
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=parts,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                response_text = response.text or ""

                clean_json = _extract_json_text(response_text)
                try:
                    data = json.loads(clean_json)
                except json.JSONDecodeError as exc:
                    logger.error(
                        "Failed to parse JSON from Gemini response: %s\nRaw output: %s",
                        exc, response_text,
                    )
                    raise ValueError("Model output was not valid JSON.") from exc

                try:
                    return DentalFindings.model_validate(data)
                except Exception as exc:
                    logger.error("Findings failed Pydantic schema validation: %s\nData: %s", exc, data)
                    raise ValueError("AI output did not match expected findings schema.") from exc

            except Exception as exc:
                error_msg = str(exc)
                last_exception = exc

                if _is_transient(error_msg):
                    if attempt < _MAX_RETRIES_PER_MODEL:
                        sleep_time = _RETRY_BASE_SLEEP * attempt  # 3s, 6s
                        logger.warning(
                            "Model %s overloaded (attempt %d/%d). Retrying in %ds... [%s]",
                            model_name, attempt, _MAX_RETRIES_PER_MODEL,
                            sleep_time, error_msg[:100],
                        )
                        time.sleep(sleep_time)
                        continue  # retry same model
                    else:
                        logger.warning(
                            "Model %s failed all %d attempts — falling to next model. [%s]",
                            model_name, _MAX_RETRIES_PER_MODEL, error_msg[:100],
                        )
                        break  # exhaust retries → next model

                # Non-transient (bad API key, schema error, etc.) — fail fast
                logger.error("Non-transient error on model %s: %s", model_name, error_msg)
                raise

    raise RuntimeError(
        "All Gemini models are temporarily unavailable (503 / high demand). "
        "Please wait 30 seconds and try again."
    ) from last_exception


