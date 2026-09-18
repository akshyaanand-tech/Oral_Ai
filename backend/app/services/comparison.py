"""
Longitudinal Screening Comparison Service.

Compares two historical screenings and identifies visible category-level changes.
CRITICAL SAFETY RULE:
Never uses disease progression language (e.g. "disease progressed" or "condition deteriorated").
Always uses objective visible observational phrases:
"More visible discoloration was observed compared with the previous screening."
"""

from typing import Dict, Any

SEVERITY_ORDER = {
    "none": 0,
    "uncertain": 0,
    "mild": 1,
    "moderate": 2,
    "marked": 3,
}

CATEGORY_NAMES = {
    "alignment": "Alignment & Spacing",
    "discoloration": "Surface Discoloration",
    "tooth_wear": "Tooth Surface Wear",
    "gum_appearance": "Gum Appearance",
}


def _describe_change(category: str, prev_sev: str, curr_sev: str) -> str:
    """Generate cautious, non-diagnostic comparative description."""
    prev_val = SEVERITY_ORDER.get(prev_sev.lower(), 0)
    curr_val = SEVERITY_ORDER.get(curr_sev.lower(), 0)
    cat_lower = category.lower()

    if prev_sev == curr_sev:
        return "No major visible change observed"

    if curr_val > prev_val:
        if "discolor" in cat_lower:
            return "More visible discoloration was observed compared with the previous screening"
        elif "gum" in cat_lower:
            return "More visible gum redness or swelling was noted compared with the previous screening"
        elif "wear" in cat_lower:
            return "More noticeable surface flattening was observed compared with the previous screening"
        elif "align" in cat_lower:
            return "Visible shifting or spacing appears slightly more evident compared with the previous screening"
        else:
            return f"Visible indicators appear more noticeable compared with the previous screening"
    else:
        if "discolor" in cat_lower:
            return "Visible surface discoloration appears less prominent than in the previous screening"
        elif "gum" in cat_lower:
            return "Visible gum margins appear clearer with less redness than in the previous screening"
        elif "wear" in cat_lower:
            return "Surface wear observations appear stabilized or less noticeable than previously recorded"
        elif "align" in cat_lower:
            return "Alignment observations appear consistent or slightly less pronounced than previously noted"
        else:
            return "Visible indicators appear less prominent compared with the previous screening"


def _normalize_findings(findings: Any) -> Dict[str, Any]:
    if isinstance(findings, dict):
        return findings
    if isinstance(findings, list):
        norm = {}
        for item in findings:
            if isinstance(item, dict) and "category" in item:
                norm[item["category"]] = item
        return norm
    return {}


def compare_screenings(prev: Dict[str, Any], curr: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two screenings across overall score and categories.
    """
    prev_score = int(prev.get("score") if prev.get("score") is not None else prev.get("screening_score", 0))
    curr_score = int(curr.get("score") if curr.get("score") is not None else curr.get("screening_score", 0))
    score_change = curr_score - prev_score

    prev_findings = _normalize_findings(prev.get("findings"))
    curr_findings = _normalize_findings(curr.get("findings"))

    categories_result: Dict[str, Any] = {}
    for cat in ["alignment", "discoloration", "tooth_wear", "gum_appearance"]:
        p_item = prev_findings.get(cat, {})
        c_item = curr_findings.get(cat, {})

        p_sev = str(p_item.get("severity", "none"))
        c_sev = str(c_item.get("severity", "none"))

        change_desc = _describe_change(cat, p_sev, c_sev)

        categories_result[cat] = {
            "previous": p_sev,
            "current": c_sev,
            "change": change_desc,
        }

    return {
        "overall": {
            "previous_screening_id": prev.get("screening_id", ""),
            "current_screening_id": curr.get("screening_id", ""),
            "previous_date": prev.get("created_at", "")[:10] if prev.get("created_at") else "",
            "current_date": curr.get("created_at", "")[:10] if curr.get("created_at") else "",
            "previous_score": prev_score,
            "current_score": curr_score,
            "change": score_change,
        },
        "categories": categories_result,
        "disclaimer": (
            "Comparisons reflect photographic visual differences across submitted angles and lighting. "
            "They do not constitute a clinical progression assessment. Please consult a dentist for professional evaluation."
        )
    }
