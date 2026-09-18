"""
Personalized Preventive Guidance Service.

Generates cautious, evidence-informed oral wellness guidance based on
visual findings and user-reported questionnaire context.
Strictly non-diagnostic: does not diagnose, prescribe treatment, or recommend medication.
"""

from typing import Dict, Any, List, Optional
from app.schemas.analysis import DentalFindings, Severity


def generate_personalized_guidance(
    findings: DentalFindings,
    questionnaire: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate customized preventive guidance based on visual observations and self-reported context.
    """
    category_guidance: Dict[str, str] = {}
    lifestyle_tips: List[str] = []
    user_reported_notes: List[str] = []

    # ── 1. Alignment Guidance ────────────────────────────────────────────────
    align_sev = findings.alignment.severity
    if align_sev in (Severity.mild, Severity.moderate, Severity.marked):
        category_guidance["alignment"] = (
            "Visible crowding or spacing was noted. A dental professional can assess "
            "whether further evaluation or orthodontic alignment is appropriate for comfort and bite balance."
        )
        lifestyle_tips.append(
            "Pay extra attention when brushing and flossing crowded teeth, as overlapping areas can collect plaque more readily."
        )
    else:
        category_guidance["alignment"] = (
            "No significant visible misalignment or crowding observed. Continue routine oral hygiene."
        )

    # ── 2. Discoloration Guidance ────────────────────────────────────────────
    disc_sev = findings.discoloration.severity
    if disc_sev in (Severity.mild, Severity.moderate, Severity.marked):
        category_guidance["discoloration"] = (
            "Some areas appear visibly different in colour. Persistent discoloration can have "
            "different causes (such as dietary staining, superficial enamel changes, or wear), "
            "so consider discussing this with a dental professional."
        )
        lifestyle_tips.append(
            "Rinsing with water after consuming tea, coffee, or acidic beverages can help minimize extrinsic surface staining."
        )
    else:
        category_guidance["discoloration"] = (
            "Tooth surfaces appear evenly colored without noticeable localized staining."
        )

    # ── 3. Tooth Wear Guidance ───────────────────────────────────────────────
    wear_sev = findings.tooth_wear.severity
    if wear_sev in (Severity.mild, Severity.moderate, Severity.marked):
        category_guidance["tooth_wear"] = (
            "Some visible surface changes may be consistent with tooth wear. If these changes persist "
            "or are associated with sensitivity or clenching, consider professional evaluation."
        )
        lifestyle_tips.append(
            "Use a soft-bristled toothbrush with gentle circular pressure to protect enamel surfaces from abrasive wear."
        )
    else:
        category_guidance["tooth_wear"] = (
            "No obvious visible flattening or significant wear patterns detected on chewing edges."
        )

    # ── 4. Gum Appearance Guidance ───────────────────────────────────────────
    gum_sev = findings.gum_appearance.severity
    if gum_sev in (Severity.mild, Severity.moderate, Severity.marked):
        category_guidance["gum_appearance"] = (
            "Some visible gum changes were noted. If redness, swelling, bleeding, or discomfort persists, "
            "consider discussing this with a dental professional for a comprehensive periodontal evaluation."
        )
        lifestyle_tips.append(
            "Maintain daily interdental cleaning with dental floss or interdental brushes to keep gumlines clear of plaque."
        )
    else:
        category_guidance["gum_appearance"] = (
            "Gingival margins appear generally pink and consistent without obvious visible inflammation."
        )

    # ── 5. User-Reported Context (Explicitly labeled) ────────────────────────
    if questionnaire:
        q = questionnaire
        sensitivity = q.get("tooth_sensitivity")
        if sensitivity and sensitivity != "none":
            user_reported_notes.append(
                f"User-reported: You noted tooth sensitivity ({sensitivity}). Sensitive tooth surfaces can benefit from desensitizing fluoride toothpaste."
            )

        pain = q.get("pain_discomfort")
        if pain and pain != "none":
            user_reported_notes.append(
                f"User-reported: You noted discomfort ({pain}). Dental pain should always be promptly examined in-person by a dental professional."
            )

        bleeding = q.get("gum_bleeding")
        if bleeding and bleeding != "none":
            user_reported_notes.append(
                f"User-reported: You noted gum bleeding ({bleeding}). Bleeding is often an early sign of gingival irritation that professional cleaning can resolve."
            )

        changes = q.get("teeth_or_gum_changes")
        if changes and changes != "none":
            user_reported_notes.append(
                f"User-reported: You observed changes in your teeth or gums ({changes}). Note these changes when speaking with your dental provider."
            )

        last_visit = q.get("last_dental_visit")
        if last_visit in ("1_to_2_years", "over_2_years"):
            user_reported_notes.append(
                "User-reported: It has been over a year since your last dental visit. Routine 6-month check-ups are key to early prevention."
            )

        specific_concern = q.get("specific_concern")
        if specific_concern and specific_concern.strip():
            user_reported_notes.append(
                f"User-reported specific concern: \"{specific_concern.strip()}\" — mention this focus area to your dentist."
            )

    # Default foundational tip if none added
    if not lifestyle_tips:
        lifestyle_tips.append("Brush twice daily for two minutes using fluoride toothpaste and clean between teeth daily.")

    return {
        "category_guidance": category_guidance,
        "lifestyle_tips": lifestyle_tips,
        "user_reported_notes": user_reported_notes,
    }
