"""
Dentist-Ready Report Generation Service.

Assembles structured JSON screening reports and generates print-friendly HTML reports
designed to facilitate productive patient-dentist conversations.
Enforces non-diagnostic phrasing, transparent scoring, and medical disclaimers.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.schemas.analysis import DentalFindings
from app.schemas.score import ScreeningScore

STANDARD_DISCLAIMER = (
    "This is a preliminary visual screening and not a dental diagnosis. "
    "It cannot replace an examination by a qualified dental professional."
)


def _build_recommendation(score: int) -> str:
    """Generate cautious, non-diagnostic guidance based on screening score band."""
    if score >= 85:
        return (
            "No significant visual indicators were noted during this preliminary screening. "
            "Maintain your routine oral hygiene habits and continue scheduling regular check-ups "
            "with a dental professional."
        )
    elif score >= 70:
        return (
            "A few mild visual indicators were observed. "
            "Consider discussing these visible observations with a dental professional at your next visit."
        )
    elif score >= 50:
        return (
            "Several visible indicators were noted across the submitted images. "
            "It is advisable to schedule a routine dental appointment to have these areas professionally examined."
        )
    else:
        return (
            "Multiple visible indicators were observed across the submitted views. "
            "We recommend consulting a dental professional for a comprehensive evaluation and guidance."
        )


def generate_report(
    findings: DentalFindings,
    score_result: ScreeningScore,
    quality_issues: Optional[List[str]] = None,
    questionnaire: Optional[Dict[str, Any]] = None,
    guidance: Optional[Dict[str, Any]] = None,
    views_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate the complete structured response dictionary matching the PRD and clinical specifications.
    """
    screening_id = f"scr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    report: Dict[str, Any] = {
        "screening_id": screening_id,
        "created_at": created_at,
        "status": "completed",
        "score": score_result.score,
        "score_label": score_result.score_label,
        "findings": {
            "alignment": findings.alignment.model_dump(),
            "discoloration": findings.discoloration.model_dump(),
            "tooth_wear": findings.tooth_wear.model_dump(),
            "gum_appearance": findings.gum_appearance.model_dump(),
        },
        "score_breakdown": {
            "starting_score": score_result.breakdown.starting_score,
            "alignment": score_result.breakdown.alignment,
            "discoloration": score_result.breakdown.discoloration,
            "tooth_wear": score_result.breakdown.tooth_wear,
            "gum_appearance": score_result.breakdown.gum_appearance,
            "final_score": score_result.breakdown.final_score,
            "details": {
                k: v.model_dump() for k, v in score_result.breakdown.details.items()
            }
        },
        "recommendation": _build_recommendation(score_result.score),
        "disclaimer": STANDARD_DISCLAIMER,
    }

    if questionnaire:
        report["questionnaire"] = questionnaire

    if guidance:
        report["guidance"] = guidance

    if views_metadata:
        report["views_metadata"] = views_metadata

    if quality_issues:
        report["quality_warnings"] = quality_issues

    return report


def generate_html_report(report: Dict[str, Any]) -> str:
    """
    Generate a clean, high-resolution, print-friendly HTML report
    suitable for sharing with or presenting to a dental professional.
    """
    screening_id = report.get("screening_id", "N/A")
    created_at = report.get("created_at", "")[:10]
    score = report.get("score", 0)
    score_label = report.get("score_label", "Preliminary Visual Screening Score")
    findings = report.get("findings", {})
    breakdown = report.get("score_breakdown", {})
    recommendation = report.get("recommendation", "")
    questionnaire = report.get("questionnaire", {})
    guidance = report.get("guidance", {})

    q_items_html = ""
    if questionnaire:
        for k, v in questionnaire.items():
            k_clean = k.replace("_", " ").capitalize()
            v_clean = str(v).replace("_", " ") if v else "None"
            q_items_html += f"""
            <div style="margin-bottom: 6px;">
                <span style="font-weight: 600; color: #334155;">{k_clean}:</span>
                <span style="color: #475569;">{v_clean}</span>
            </div>
            """

    findings_rows = ""
    cat_titles = {
        "alignment": "Alignment & Spacing",
        "discoloration": "Surface Discoloration",
        "tooth_wear": "Tooth Surface Wear",
        "gum_appearance": "Gum Appearance"
    }

    for cat_key, cat_title in cat_titles.items():
        f_data = findings.get(cat_key, {})
        sev = f_data.get("severity", "none").capitalize()
        finding_text = f_data.get("finding", "No visible observation noted.")
        conf = int(f_data.get("confidence", 0.8) * 100)
        deduction = breakdown.get(cat_key, 0)

        findings_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 10px; font-weight: 600; color: #1e293b;">{cat_title}</td>
            <td style="padding: 10px; color: #334155;">{finding_text}</td>
            <td style="padding: 10px; text-align: center;">
                <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; background: #f1f5f9; color: #0f172a;">
                    {sev}
                </span>
            </td>
            <td style="padding: 10px; text-align: center; color: #64748b;">{conf}%</td>
            <td style="padding: 10px; text-align: right; font-weight: 600; color: {'#e11d48' if deduction > 0 else '#059669'};">
                {f"-{deduction}" if deduction > 0 else "0"}
            </td>
        </tr>
        """

    tips_html = ""
    for tip in guidance.get("lifestyle_tips", []):
        tips_html += f"<li style='margin-bottom: 4px;'>{tip}</li>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dentist Summary — {screening_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            background: #ffffff;
            margin: 0;
            padding: 24px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .report-card {{
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 32px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0284c7;
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 22px;
            font-weight: 800;
            color: #0369a1;
            margin: 0;
        }}
        .subtitle {{
            font-size: 13px;
            color: #64748b;
            margin-top: 4px;
        }}
        .score-box {{
            background: #f0f9ff;
            border: 2px solid #0284c7;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: center;
        }}
        .score-val {{
            font-size: 32px;
            font-weight: 800;
            color: #0284c7;
            line-height: 1;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 24px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}
        th {{
            background: #f8fafc;
            padding: 8px 10px;
            text-align: left;
            font-size: 12px;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            border-bottom: 2px solid #cbd5e1;
        }}
        .disclaimer-box {{
            background: #fffbeb;
            border: 1px solid #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 12px 16px;
            font-size: 12px;
            color: #92400e;
            margin-top: 28px;
            border-radius: 4px;
        }}
        @media print {{
            body {{ padding: 0; }}
            .report-card {{ border: none; padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="no-print" style="margin-bottom: 16px; text-align: right;">
            <button onclick="window.print()" style="background: #0284c7; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                Print / Save PDF
            </button>
        </div>

        <div class="header">
            <div>
                <h1 class="title">OralAI — Preventive Screening Summary</h1>
                <div class="subtitle">Screening ID: <strong>{screening_id}</strong> • Date: {created_at}</div>
                <div class="subtitle">5-View Guided Visual Screening Assessment</div>
            </div>
            <div class="score-box">
                <div class="score-val">{score}</div>
                <div style="font-size: 11px; font-weight: 600; color: #0369a1; text-transform: uppercase; margin-top: 4px;">{score_label}</div>
            </div>
        </div>

        <div class="section-title">1. Patient Self-Reported Context (Questionnaire)</div>
        <div style="background: #f8fafc; padding: 12px 16px; border-radius: 6px; font-size: 13px;">
            {q_items_html or "<p style='color: #64748b; margin: 0;'>No questionnaire data provided.</p>"}
        </div>

        <div class="section-title">2. AI Visual Findings by Category</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Category</th>
                    <th style="width: 45%;">Visible Observation</th>
                    <th style="width: 12%; text-align: center;">Severity</th>
                    <th style="width: 10%; text-align: center;">Confidence</th>
                    <th style="width: 8%; text-align: right;">Points</th>
                </tr>
            </thead>
            <tbody>
                {findings_rows}
            </tbody>
        </table>

        <div class="section-title">3. Guidance & Recommendations</div>
        <p style="color: #334155; margin-top: 6px;">{recommendation}</p>
        {f"<ul style='color: #475569; padding-left: 20px;'>{tips_html}</ul>" if tips_html else ""}

        <div class="disclaimer-box">
            <strong>Mandatory Medical Notice:</strong> {STANDARD_DISCLAIMER} This preliminary visual screening identifies visible characteristics from photograph submissions and is intended to inform patient-dentist consultations. It does not replace professional dental diagnostic examination, periodontal probing, radiographs, or clinical treatment.
        </div>
    </div>
</body>
</html>"""
