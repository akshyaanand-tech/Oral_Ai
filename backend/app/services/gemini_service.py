"""
Optional Gemini Explanation Service.

Provides a user-friendly, plain-language explanation and educational summary
of the preliminary visual screening report.

CRITICAL ARCHITECTURAL CONSTRAINTS:
Gemini acts solely as an EXPLANATION LAYER.
Gemini may:
  - Explain visual ML findings in simple, accessible language.
  - Summarize the preliminary screening result.
  - Generate encouraging, user-friendly educational guidance.
Gemini must NOT:
  - Diagnose the user with medical or dental disease.
  - Invent or hallucinate visual findings not present in the ML output.
  - Independently decide or alter treatments or care pathways.
  - Override the deterministic recommendation engine.
  - Generate fake provider information or prices.

If the Gemini API key is not configured, or if the API call fails or times out,
this service seamlessly uses a rich, deterministic template-based explanation generator.
"""

import os
import logging
from typing import Optional

from app.schemas.ml_output import MLAnalysisOutput, FindingSeverity
from app.schemas.recommendation import CarePathway

logger = logging.getLogger(__name__)

EXPLANATION_PROMPT = """
You are an empathetic, clear educational oral-health assistant summarizing a preliminary visual screening report.

CRITICAL MEDICAL, LEGAL & SAFETY RULES:
- You are strictly an EXPLANATION LAYER, NOT a clinician or diagnosing dentist.
- You must NOT diagnose dental diseases (do NOT diagnose caries, periodontitis, gingivitis, malocclusion).
- You must NOT invent or extrapolate findings beyond what is listed in the provided observations.
- You must NOT suggest treatments, prices, or clinics other than explaining the provided care pathway steps.
- Use encouraging, non-alarmist, educational language. Emphasize that visual screenings are preliminary checks and encourage seeing a qualified dental professional.

SCREENING DATA:
- Screening Score: {score} / 100
- Visual Observations:
{findings_text}
- Recommended Care Pathway:
{pathway_text}

Provide an educational explanation (3 short, friendly paragraphs):
1. An overall friendly summary of what the screening score ({score}/100) means in plain language.
2. A breakdown of the key visible observations (explaining why they matter for preventive health).
3. Encouraging next steps and practical daily hygiene encouragement.
"""


def _generate_template_explanation(
    ml_output: MLAnalysisOutput,
    score: int,
    care_pathway: CarePathway,
) -> str:
    """
    Deterministic offline explanation generator when Gemini API is unconfigured or unavailable.
    Provides clear, empathetic educational guidance tailored to the exact findings.
    """
    findings_map = ml_output.findings_by_category or {f.category: f for f in ml_output.findings}

    # Score interpretation
    if score >= 85:
        score_desc = (
            f"Your preliminary visual screening score is {score}/100, which indicates a low level "
            "of visible optical concerns across your submitted photos. Your teeth and gingival margins appear "
            "generally well-maintained."
        )
    elif score >= 70:
        score_desc = (
            f"Your preliminary visual screening score is {score}/100. The visual analysis noted a few mild "
            "optical indicators (such as minor surface staining or slight alignment variations) that are common "
            "and manageable through routine preventive attention."
        )
    elif score >= 50:
        score_desc = (
            f"Your preliminary visual screening score is {score}/100. Several moderate visible indicators "
            "were observed across your dental photos. Scheduling a clinical evaluation with a dental professional "
            "will help ensure these areas receive proper assessment and preventive care."
        )
    else:
        score_desc = (
            f"Your preliminary visual screening score is {score}/100. Multiple noticeable visual indicators "
            "were detected across your photos. We strongly encourage scheduling an in-person dental consultation "
            "soon so a dentist can perform a thorough examination."
        )

    # Key findings explanation
    notable_points = []
    for cat, finding in findings_map.items():
        if finding.severity in (FindingSeverity.mild, FindingSeverity.moderate, FindingSeverity.marked):
            label = cat.replace("_", " ").title()
            notable_points.append(f"• **{label}**: {finding.finding} ({finding.severity.value} visible indicator)")

    if notable_points:
        findings_summary = (
            "Here is what was observed in your images:\n" +
            "\n".join(notable_points) +
            "\n\nRemember that camera photographs only capture surface appearances under ambient lighting. "
            "A dentist uses specialized operatory illumination, tactile probing, and diagnostic radiographs to evaluate oral health accurately."
        )
    else:
        findings_summary = (
            "No significant visible concerns were flagged in your five oral images. Your enamel surfaces and gum "
            "margins appear within typical healthy ranges on visual inspection."
        )

    # Pathway and encouragement
    pathway_steps = [f"Step {idx+1}: {step.title} ({step.recommended_specialist})" for idx, step in enumerate(care_pathway.steps[:3])]
    pathway_text = ", ".join(pathway_steps) if pathway_steps else "Regular routine dental check-up"

    next_steps = (
        f"**Next Steps:** {care_pathway.summary}\n"
        f"Suggested Pathway: {pathway_text}.\n"
        "In the meantime, maintain twice-daily brushing with fluoride toothpaste for two full minutes and daily flossing to protect your smile."
    )

    return f"{score_desc}\n\n{findings_summary}\n\n{next_steps}"


def generate_explanation(
    ml_output: MLAnalysisOutput,
    score: int,
    care_pathway: CarePathway,
    enabled: bool = True,
) -> str:
    """
    Generate user-friendly educational summary and explanation.

    Attempts Gemini AI explanation when API key is set and enabled.
    Cleanly falls back to deterministic template explanation if key is missing or call fails.
    """
    if not enabled:
        return _generate_template_explanation(ml_output, score, care_pathway)

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    mock_mode = os.getenv("MOCK_AI", "false").lower() in ("true", "1", "yes")

    if not gemini_key or mock_mode:
        logger.info("Using deterministic template explanation (MOCK_AI=%s, has_key=%s)", mock_mode, bool(gemini_key))
        return _generate_template_explanation(ml_output, score, care_pathway)

    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)

        findings_lines = []
        for f in ml_output.findings:
            findings_lines.append(f"- {f.category.replace('_', ' ').title()}: {f.finding} (Severity: {f.severity.value}, Confidence: {f.confidence})")
        findings_text = "\n".join(findings_lines)

        steps_lines = []
        for s in care_pathway.steps:
            steps_lines.append(f"- {s.title} -> {s.action} (Specialist: {s.recommended_specialist}, Urgency: {s.urgency})")
        pathway_text = "\n".join(steps_lines)

        prompt = EXPLANATION_PROMPT.format(
            score=score,
            findings_text=findings_text,
            pathway_text=pathway_text,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip() if response and response.text else ""
        if text:
            logger.info("Generated explanation successfully via Gemini API")
            return text
    except Exception as exc:
        logger.warning("Gemini explanation generation failed (%s); using deterministic template", exc)

    return _generate_template_explanation(ml_output, score, care_pathway)
