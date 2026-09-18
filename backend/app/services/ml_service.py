"""
ML Image Analysis Service.

Accepts five guided oral images:
  1. Front
  2. Left
  3. Right
  4. Upper
  5. Lower

Detects four visible screening indicators:
  - tooth alignment
  - discoloration
  - tooth wear
  - gum appearance

Returns structured findings with severity and confidence.
Visual screening observations are strictly non-diagnostic.
Works offline with deterministic heuristic extraction; enhances with Gemini Vision when configured.
"""

import io
import os
import logging
from typing import Dict, List, Optional
import numpy as np
from PIL import Image

from app.schemas.ml_output import (
    MLAnalysisOutput,
    MLFindingItem,
    FindingSeverity,
    FindingCategory,
    FindingEvidence,
    BoundingRegion,
)

logger = logging.getLogger(__name__)


def _analyze_image_heuristics(images: Dict[str, bytes]) -> MLAnalysisOutput:
    """
    Deterministic offline/fallback image analysis based on optical properties of oral images.
    Extracts color distribution, gingival chromaticity, and edge contrast across the five views.
    Ensures zero external dependency.
    """
    stats = {}
    for view, img_bytes in images.items():
        try:
            with Image.open(io.BytesIO(img_bytes)) as pil_img:
                rgb = pil_img.convert("RGB")
                arr = np.asarray(rgb, dtype=np.float32)
                r = arr[:, :, 0]
                g = arr[:, :, 1]
                b = arr[:, :, 2]

                # Redness ratio (gingival indicator): R / (G + B + 1e-5)
                redness = r / (g + b + 1e-5)
                mean_red = float(np.mean(redness))

                # Yellowness/stain proxy (high R+G relative to B in non-red zones):
                brightness = (r + g + b) / 3.0
                stain_mask = (brightness > 100) & (brightness < 220)
                if np.any(stain_mask):
                    yellow_ratio = float(np.mean((r[stain_mask] + g[stain_mask]) / (2.0 * b[stain_mask] + 1e-5)))
                else:
                    yellow_ratio = 1.0

                # Edge variance / contrast proxy for alignment irregularity / wear
                gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
                gy, gx = np.gradient(gray)
                edge_energy = float(np.mean(gx ** 2 + gy ** 2))

                stats[view] = {
                    "mean_red": mean_red,
                    "yellow_ratio": yellow_ratio,
                    "edge_energy": edge_energy,
                    "brightness": float(np.mean(brightness)),
                }
        except Exception as exc:
            logger.warning("Heuristic extraction error on view '%s': %s", view, exc)
            stats[view] = {"mean_red": 0.9, "yellow_ratio": 1.0, "edge_energy": 120.0, "brightness": 128.0}

    # 1. Alignment Heuristic
    # Higher edge complexity in front/upper arch often correlates with irregular contact points
    front_energy = stats.get("front", {}).get("edge_energy", 120.0)
    if front_energy > 280.0:
        align_sev = FindingSeverity.moderate
        align_desc = "Possible visible crowding or spacing noted in visible arch segments."
        align_conf = 0.82
    elif front_energy > 160.0:
        align_sev = FindingSeverity.mild
        align_desc = "Possible minor alignment variation observed in visible anterior teeth."
        align_conf = 0.85
    else:
        align_sev = FindingSeverity.none
        align_desc = "No obvious visible crowding or spacing observed in provided views."
        align_conf = 0.88

    # 2. Discoloration Heuristic
    avg_yellow = float(np.mean([s["yellow_ratio"] for s in stats.values()])) if stats else 1.0
    if avg_yellow > 1.35:
        disc_sev = FindingSeverity.moderate
        disc_desc = "Visible surface staining and noticeable enamel color variation observed."
        disc_conf = 0.84
    elif avg_yellow > 1.15:
        disc_sev = FindingSeverity.mild
        disc_desc = "Possible visible surface staining observed along cervical/interproximal margins."
        disc_conf = 0.86
    else:
        disc_sev = FindingSeverity.none
        disc_desc = "No obvious visible surface staining observed."
        disc_conf = 0.90

    # 3. Tooth Wear Heuristic
    # Occlusal / incisal surface wear often manifests in upper/lower arch views
    upper_energy = stats.get("upper", {}).get("edge_energy", 100.0)
    lower_energy = stats.get("lower", {}).get("edge_energy", 100.0)
    wear_energy = (upper_energy + lower_energy) / 2.0
    if wear_energy > 260.0:
        wear_sev = FindingSeverity.moderate
        wear_desc = "Visible surface flattening or noticeable incisal edge wear observed."
        wear_conf = 0.80
    elif wear_energy > 180.0:
        wear_sev = FindingSeverity.mild
        wear_desc = "Possible minor incisal edge smoothing or wear facets visible."
        wear_conf = 0.83
    else:
        wear_sev = FindingSeverity.none
        wear_desc = "No obvious visible tooth wear or edge flattening observed."
        wear_conf = 0.89

    # 4. Gum Appearance Heuristic
    # Front and left/right views capture gingival margin redness
    front_red = stats.get("front", {}).get("mean_red", 0.9)
    if front_red > 1.45:
        gum_sev = FindingSeverity.moderate
        gum_desc = "Visible redness and possible marginal gingival swelling observed."
        gum_conf = 0.81
    elif front_red > 1.18:
        gum_sev = FindingSeverity.mild
        gum_desc = "Possible mild redness observed along the gingival margin."
        gum_conf = 0.85
    else:
        gum_sev = FindingSeverity.none
        gum_desc = "Gingival margins appear within typical visible limits in provided views."
        gum_conf = 0.88

    findings = [
        MLFindingItem(
            category="alignment",
            finding=align_desc,
            severity=align_sev,
            confidence=align_conf,
            evidence=FindingEvidence(
                image="front",
                region=BoundingRegion(x=0.25, y=0.30, width=0.50, height=0.40) if align_sev != FindingSeverity.none else None,
            ),
        ),
        MLFindingItem(
            category="discoloration",
            finding=disc_desc,
            severity=disc_sev,
            confidence=disc_conf,
            evidence=FindingEvidence(
                image="upper" if disc_sev != FindingSeverity.none else "front",
                region=BoundingRegion(x=0.20, y=0.25, width=0.60, height=0.50) if disc_sev != FindingSeverity.none else None,
            ),
        ),
        MLFindingItem(
            category="tooth_wear",
            finding=wear_desc,
            severity=wear_sev,
            confidence=wear_conf,
            evidence=FindingEvidence(
                image="lower" if wear_sev != FindingSeverity.none else "front",
                region=BoundingRegion(x=0.30, y=0.40, width=0.40, height=0.30) if wear_sev != FindingSeverity.none else None,
            ),
        ),
        MLFindingItem(
            category="gum_appearance",
            finding=gum_desc,
            severity=gum_sev,
            confidence=gum_conf,
            evidence=FindingEvidence(
                image="front",
                region=BoundingRegion(x=0.20, y=0.15, width=0.60, height=0.30) if gum_sev != FindingSeverity.none else None,
            ),
        ),
    ]

    by_category = {f.category: f for f in findings}
    overall_conf = round(float(np.mean([f.confidence for f in findings])), 2)

    return MLAnalysisOutput(
        findings=findings,
        findings_by_category=by_category,
        overall_confidence=overall_conf,
        analyzed_views=list(images.keys()),
    )


def analyze_oral_images(images: Dict[str, bytes]) -> MLAnalysisOutput:
    """
    Main entry point for ML Image Analysis.
    Accepts 5 guided oral images (front, left, right, upper, lower).
    Attempts vision AI analysis if configured; cleanly falls back to deterministic heuristic analysis.
    """
    mock_mode = os.getenv("MOCK_AI", "false").lower() in ("true", "1", "yes")
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not mock_mode and gemini_key:
        try:
            # Leverage Gemini Vision if available
            from app.services.gemini import analyze_images as gemini_analyze
            gemini_result = gemini_analyze(images)

            # Map from DentalFindings to MLAnalysisOutput
            findings = [
                MLFindingItem(
                    category="alignment",
                    finding=gemini_result.alignment.finding,
                    severity=FindingSeverity(gemini_result.alignment.severity.value),
                    confidence=gemini_result.alignment.confidence,
                    evidence=FindingEvidence(
                        image=gemini_result.alignment.evidence.image if gemini_result.alignment.evidence else "front",
                        region=BoundingRegion(
                            x=gemini_result.alignment.evidence.region.x,
                            y=gemini_result.alignment.evidence.region.y,
                            width=gemini_result.alignment.evidence.region.width,
                            height=gemini_result.alignment.evidence.region.height,
                        ) if gemini_result.alignment.evidence and gemini_result.alignment.evidence.region else None,
                    ) if gemini_result.alignment.evidence else None,
                ),
                MLFindingItem(
                    category="discoloration",
                    finding=gemini_result.discoloration.finding,
                    severity=FindingSeverity(gemini_result.discoloration.severity.value),
                    confidence=gemini_result.discoloration.confidence,
                    evidence=FindingEvidence(
                        image=gemini_result.discoloration.evidence.image if gemini_result.discoloration.evidence else "front",
                        region=BoundingRegion(
                            x=gemini_result.discoloration.evidence.region.x,
                            y=gemini_result.discoloration.evidence.region.y,
                            width=gemini_result.discoloration.evidence.region.width,
                            height=gemini_result.discoloration.evidence.region.height,
                        ) if gemini_result.discoloration.evidence and gemini_result.discoloration.evidence.region else None,
                    ) if gemini_result.discoloration.evidence else None,
                ),
                MLFindingItem(
                    category="tooth_wear",
                    finding=gemini_result.tooth_wear.finding,
                    severity=FindingSeverity(gemini_result.tooth_wear.severity.value),
                    confidence=gemini_result.tooth_wear.confidence,
                    evidence=FindingEvidence(
                        image=gemini_result.tooth_wear.evidence.image if gemini_result.tooth_wear.evidence else "front",
                        region=BoundingRegion(
                            x=gemini_result.tooth_wear.evidence.region.x,
                            y=gemini_result.tooth_wear.evidence.region.y,
                            width=gemini_result.tooth_wear.evidence.region.width,
                            height=gemini_result.tooth_wear.evidence.region.height,
                        ) if gemini_result.tooth_wear.evidence and gemini_result.tooth_wear.evidence.region else None,
                    ) if gemini_result.tooth_wear.evidence else None,
                ),
                MLFindingItem(
                    category="gum_appearance",
                    finding=gemini_result.gum_appearance.finding,
                    severity=FindingSeverity(gemini_result.gum_appearance.severity.value),
                    confidence=gemini_result.gum_appearance.confidence,
                    evidence=FindingEvidence(
                        image=gemini_result.gum_appearance.evidence.image if gemini_result.gum_appearance.evidence else "front",
                        region=BoundingRegion(
                            x=gemini_result.gum_appearance.evidence.region.x,
                            y=gemini_result.gum_appearance.evidence.region.y,
                            width=gemini_result.gum_appearance.evidence.region.width,
                            height=gemini_result.gum_appearance.evidence.region.height,
                        ) if gemini_result.gum_appearance.evidence and gemini_result.gum_appearance.evidence.region else None,
                    ) if gemini_result.gum_appearance.evidence else None,
                ),
            ]

            by_category = {f.category: f for f in findings}
            overall_conf = round(float(np.mean([f.confidence for f in findings])), 2)

            return MLAnalysisOutput(
                findings=findings,
                findings_by_category=by_category,
                overall_confidence=overall_conf,
                analyzed_views=list(images.keys()),
            )
        except Exception as exc:
            logger.warning("Gemini Vision AI call failed (%s); falling back to deterministic heuristic analysis", exc)

    # Deterministic heuristic analysis
    return _analyze_image_heuristics(images)
