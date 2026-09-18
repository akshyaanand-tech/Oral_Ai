"""
Recommendation Engine Service.

Implements pure Python rule-based logic to map visual ML findings and
optional patient questionnaire answers into actionable care recommendations.

Crucial Architectural Rule:
Keeps recommendation logic strictly separate from the ML vision model.
Loads rules from backend/data/treatment_rules.json with a resilient in-code fallback.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from app.schemas.ml_output import MLAnalysisOutput, FindingSeverity
from app.schemas.recommendation import CareStep

logger = logging.getLogger(__name__)

# Primary location of treatment rules JSON
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
RULES_FILE = os.path.join(DATA_DIR, "treatment_rules.json")

# In-memory default rules if file is missing or corrupted
DEFAULT_FALLBACK_RULES = {
    "alignment": {
        "mild": {
            "title": "Orthodontic Alignment Assessment",
            "action": "Elective orthodontic evaluation for minor crowding or spacing",
            "urgency": "Elective / Non-urgent",
            "specialty": "Orthodontist",
            "home_care": ["Use interdental brushes or floss threaders", "Ensure focused brushing on crowded areas"]
        },
        "moderate": {
            "title": "Orthodontic Evaluation for Crowding / Spacing",
            "action": "Specialist orthodontic evaluation for arch alignment and bite check",
            "urgency": "Recommended within 1-3 months",
            "specialty": "Orthodontist",
            "home_care": ["Daily flossing with waxed tape or water flosser", "Monitor for plaque build-up at overlapping contacts"]
        },
        "marked": {
            "title": "Comprehensive Orthodontic Consultation",
            "action": "Comprehensive evaluation by an orthodontist for bite alignment and arch crowding",
            "urgency": "Recommended consultation",
            "specialty": "Orthodontist",
            "home_care": ["Extra hygiene focus on irregular tooth surfaces", "Avoid biting hard non-food objects"]
        }
    },
    "discoloration": {
        "mild": {
            "title": "Dental Examination & Prophylaxis",
            "action": "Professional hygiene cleaning and stain assessment",
            "urgency": "Routine",
            "specialty": "General Dentist",
            "home_care": ["Rinse with water after coffee/tea", "Twice-daily brushing with fluoride toothpaste"]
        },
        "moderate": {
            "title": "Professional Dental Cleaning & Enamel Evaluation",
            "action": "Dental examination and professional prophylaxis/scaling to evaluate extrinsic staining",
            "urgency": "Recommended within 1 month",
            "specialty": "General Dentist",
            "home_care": ["Avoid abrasive whitening powders", "Use enamel-safe fluoride toothpaste"]
        },
        "marked": {
            "title": "Clinical Discoloration & Surface Check",
            "action": "Comprehensive dental examination to assess prominent discoloration",
            "urgency": "Recommended within 2-4 weeks",
            "specialty": "General Dentist",
            "home_care": ["Gentle circular brushing with soft bristles", "Schedule professional cleaning promptly"]
        }
    },
    "tooth_wear": {
        "mild": {
            "title": "Occlusal Wear Monitoring",
            "action": "Clinical check to monitor incisal edge smoothing and discuss clenching/dietary acids",
            "urgency": "Routine",
            "specialty": "General Dentist",
            "home_care": ["Wait 30 minutes before brushing after acidic foods", "Avoid chewing ice or hard pens"]
        },
        "moderate": {
            "title": "Occlusal & Wear Assessment (Night Guard Evaluation)",
            "action": "Occlusal evaluation to assess enamel wear and discuss protective night guard",
            "urgency": "Recommended within 1 month",
            "specialty": "General Dentist",
            "home_care": ["Practice daytime jaw relaxation (lips together, teeth apart)", "Use desensitizing toothpaste if sensitive"]
        },
        "marked": {
            "title": "Comprehensive Occlusal & Bite Evaluation",
            "action": "Consultation with dentist or prosthodontist for noticeable wear and edge chipping",
            "urgency": "Recommended within 2-3 weeks",
            "specialty": "General Dentist",
            "home_care": ["Protect compromised tooth edges from hard foods", "Seek custom occlusal appliance evaluation"]
        }
    },
    "gum_appearance": {
        "mild": {
            "title": "Gingival Hygiene Assessment",
            "action": "Dental hygiene evaluation and sulcular plaque removal",
            "urgency": "Routine",
            "specialty": "General Dentist",
            "home_care": ["Floss gently once daily along the gumline", "Use an alcohol-free antiseptic mouth rinse"]
        },
        "moderate": {
            "title": "Periodontal Gum Evaluation",
            "action": "Periodontal assessment and gingival probing for marginal redness or swelling",
            "urgency": "Recommended within 2-4 weeks",
            "specialty": "Periodontist",
            "home_care": ["Brush gently with an ultra-soft toothbrush", "Do not stop flossing if gums bleed; clean gently"]
        },
        "marked": {
            "title": "Specialist Periodontal Consultation",
            "action": "Urgent periodontal evaluation and pocket depth charting for pronounced redness",
            "urgency": "Recommended within 1-2 weeks",
            "specialty": "Periodontist",
            "home_care": ["Gentle antimicrobial rinse as directed", "Avoid smoking/tobacco products", "Seek professional periodontal care"]
        }
    }
}


def _load_rules() -> dict:
    """Safely load rules from JSON, falling back to in-memory defaults on failure."""
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("rules", DEFAULT_FALLBACK_RULES)
        except Exception as exc:
            logger.warning("Failed to load %s: %s; using in-memory defaults", RULES_FILE, exc)
    return DEFAULT_FALLBACK_RULES


def generate_recommendations(
    ml_output: MLAnalysisOutput,
    questionnaire: Optional[Dict[str, Any]] = None,
) -> List[CareStep]:
    """
    Generate deterministic care recommendations based on ML findings and questionnaire context.

    Rule Examples:
      - Possible crowding -> Orthodontic evaluation -> Suggest orthodontist
      - Possible staining -> Dental examination/cleaning -> Suggest general dentist
      - Possible tooth wear -> Occlusal evaluation -> Suggest general dentist
      - Possible gum redness -> Periodontal evaluation -> Suggest periodontist or general dentist
    """
    rules = _load_rules()
    care_steps: List[CareStep] = []
    step_counter = 1

    findings_map = ml_output.findings_by_category or {f.category: f for f in ml_output.findings}

    # Evaluate each indicator category against rules
    for category in ["gum_appearance", "discoloration", "tooth_wear", "alignment"]:
        finding = findings_map.get(category)
        if not finding:
            continue

        sev = finding.severity
        if sev in (FindingSeverity.mild, FindingSeverity.moderate, FindingSeverity.marked):
            cat_rules = rules.get(category, {})
            rule_entry = cat_rules.get(sev.value)

            if rule_entry:
                step_id = f"step_{step_counter}"
                step_counter += 1
                care_steps.append(
                    CareStep(
                        step_id=step_id,
                        title=rule_entry.get("title", f"{category.replace('_', ' ').title()} Care"),
                        category=category,
                        action=rule_entry.get("action", "Clinical evaluation recommended"),
                        urgency=rule_entry.get("urgency", "Routine"),
                        recommended_specialist=rule_entry.get("specialty", "General Dentist"),
                        home_care=rule_entry.get("home_care", []),
                    )
                )

    # Consider questionnaire responses for additional clinical context
    if questionnaire:
        # Check sensitivity or pain
        pain = str(questionnaire.get("pain_discomfort", "none")).lower()
        sensitivity = str(questionnaire.get("tooth_sensitivity", "none")).lower()
        if pain in ("moderate", "severe") or sensitivity in ("moderate", "severe"):
            step_id = f"step_{step_counter}"
            step_counter += 1
            care_steps.insert(
                0,
                CareStep(
                    step_id=step_id,
                    title="Symptomatic Evaluation for Discomfort / Sensitivity",
                    category="symptoms",
                    action="Schedule priority diagnostic evaluation to address active sensitivity or discomfort",
                    urgency="Recommended within 1-2 weeks",
                    recommended_specialist="General Dentist",
                    home_care=[
                        "Avoid extreme hot, cold, or sugary stimuli",
                        "Use potassium-nitrate or stannous-fluoride desensitizing toothpaste",
                    ],
                )
            )

        # Check last dental visit
        last_visit = str(questionnaire.get("last_dental_visit", "")).lower()
        if "more_than_2_years" in last_visit or "never" in last_visit or "1_to_2_years" in last_visit:
            # If no general routine exam step is already included, add one
            if not any(s.category == "preventive" for s in care_steps):
                step_id = f"step_{step_counter}"
                step_counter += 1
                care_steps.append(
                    CareStep(
                        step_id=step_id,
                        title="Baseline Comprehensive Dental Examination",
                        category="preventive",
                        action="Comprehensive baseline oral examination and diagnostic dental X-rays",
                        urgency="Recommended within 1 month",
                        recommended_specialist="General Dentist",
                        home_care=[
                            "Brush twice daily for two minutes",
                            "Floss once daily between all contact areas",
                        ],
                    )
                )

    # If no specific concerns were flagged across all 4 categories, add routine preventive care
    if not care_steps:
        care_steps.append(
            CareStep(
                step_id="step_1",
                title="Routine Preventive Dental Maintenance",
                category="preventive",
                action="Biannual dental check-up and preventive prophylaxis cleaning",
                urgency="Routine (within 6 months)",
                recommended_specialist="General Dentist",
                home_care=[
                    "Brush twice daily with fluoride toothpaste",
                    "Floss daily along the gingival margin",
                    "Maintain healthy diet and stay hydrated",
                ],
            )
        )

    return care_steps
