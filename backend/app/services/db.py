"""
SQLite Database service for longitudinal screening persistence.
Stores screening metadata, structured findings, scores, and questionnaire answers.
Avoids permanent storage of raw images to respect patient privacy.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./oralai.db").replace("sqlite:///", "")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables and seed an initial baseline screening for demo comparison."""
    conn = _get_connection()
    try:
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                screening_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                score INTEGER NOT NULL,
                score_label TEXT NOT NULL,
                recommendation TEXT,
                disclaimer TEXT,
                report_json TEXT NOT NULL
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS questionnaire_responses (
                screening_id TEXT PRIMARY KEY,
                tooth_sensitivity TEXT,
                pain_discomfort TEXT,
                gum_bleeding TEXT,
                teeth_or_gum_changes TEXT,
                last_dental_visit TEXT,
                specific_concern TEXT,
                FOREIGN KEY (screening_id) REFERENCES screenings(screening_id)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)

        # Seed baseline screenings (uses INSERT OR IGNORE)
        _seed_baseline_screening(conn)
    finally:
        conn.close()


def _seed_baseline_screening(conn: sqlite3.Connection):
    """Seed a realistic prior screening (from 6 months prior) for instant comparison."""
    baseline_id = "scr_baseline_prior"
    past_date = "2026-03-15T10:30:00Z"
    sample_report = {
        "screening_id": baseline_id,
        "created_at": past_date,
        "status": "completed",
        "score": 76,
        "score_label": "Preliminary Visual Screening Score",
        "findings": {
            "alignment": {
                "finding": "Possible mild crowding visible in the lower anterior teeth",
                "severity": "mild",
                "confidence": 0.80,
                "evidence": {"image": "front", "region": {"x": 0.38, "y": 0.52, "width": 0.24, "height": 0.22}}
            },
            "discoloration": {
                "finding": "Possible mild surface staining observed along outer tooth surfaces",
                "severity": "mild",
                "confidence": 0.81,
                "evidence": None
            },
            "tooth_wear": {
                "finding": "No obvious visible surface flattening detected",
                "severity": "none",
                "confidence": 0.75,
                "evidence": None
            },
            "gum_appearance": {
                "finding": "Noticeable redness and mild swelling visible along the lower gingival margin",
                "severity": "moderate",
                "confidence": 0.84,
                "evidence": {"image": "front", "region": {"x": 0.35, "y": 0.65, "width": 0.30, "height": 0.15}}
            }
        },
        "score_breakdown": {
            "starting_score": 100,
            "alignment": 5,
            "discoloration": 4,
            "tooth_wear": 0,
            "gum_appearance": 15,
            "final_score": 76,
            "details": {
                "alignment": {"severity": "mild", "deduction": 5},
                "discoloration": {"severity": "mild", "deduction": 4},
                "tooth_wear": {"severity": "none", "deduction": 0},
                "gum_appearance": {"severity": "moderate", "deduction": 15}
            }
        },
        "recommendation": "Several visible indicators were noted. A routine dental examination is recommended.",
        "disclaimer": "This is a preliminary visual screening and not a dental diagnosis. It cannot replace an examination by a qualified dental professional."
    }

    with conn:
        for s_id in [baseline_id, "scr_demo"]:
            conn.execute("""
            INSERT OR IGNORE INTO screenings (screening_id, created_at, score, score_label, recommendation, disclaimer, report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                s_id,
                past_date,
                76,
                "Preliminary Visual Screening Score",
                sample_report["recommendation"],
                sample_report["disclaimer"],
                json.dumps({**sample_report, "screening_id": s_id})
            ))

            conn.execute("""
            INSERT OR IGNORE INTO questionnaire_responses (screening_id, tooth_sensitivity, pain_discomfort, gum_bleeding, teeth_or_gum_changes, last_dental_visit, specific_concern)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                s_id,
                "mild",
                "none",
                "flossing",
                "none",
                "6_to_12_months",
                "Baseline preventive check"
            ))
    logger.info("Seeded baseline screenings into database")


def save_screening(screening_id: str, report: Dict[str, Any], questionnaire: Optional[Dict[str, Any]] = None) -> bool:
    """Persist screening report and questionnaire responses to SQLite."""
    conn = _get_connection()
    try:
        created_at = report.get("created_at") or datetime.now(timezone.utc).isoformat()
        report["created_at"] = created_at
        report["screening_id"] = screening_id

        with conn:
            conn.execute("""
            INSERT OR REPLACE INTO screenings (screening_id, created_at, score, score_label, recommendation, disclaimer, report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                screening_id,
                created_at,
                int(report.get("score", 0)),
                str(report.get("score_label", "Preliminary Visual Screening Score")),
                str(report.get("recommendation", "")),
                str(report.get("disclaimer", "")),
                json.dumps(report)
            ))

            if questionnaire:
                conn.execute("""
                INSERT OR REPLACE INTO questionnaire_responses (screening_id, tooth_sensitivity, pain_discomfort, gum_bleeding, teeth_or_gum_changes, last_dental_visit, specific_concern)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    screening_id,
                    questionnaire.get("tooth_sensitivity", "none"),
                    questionnaire.get("pain_discomfort", "none"),
                    questionnaire.get("gum_bleeding", "none"),
                    questionnaire.get("teeth_or_gum_changes", "none"),
                    questionnaire.get("last_dental_visit", "6_to_12_months"),
                    questionnaire.get("specific_concern", "")
                ))
        return True
    except Exception as exc:
        logger.error("Failed to save screening %s to SQLite: %s", screening_id, exc)
        return False
    finally:
        conn.close()


def get_all_screenings() -> List[Dict[str, Any]]:
    """Return summary list of all stored screenings ordered chronologically."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT screening_id, created_at, score, score_label FROM screenings ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        summaries = []
        for r in rows:
            summaries.append({
                "screening_id": r["screening_id"],
                "date": r["created_at"][:10] if r["created_at"] else "Unknown",
                "created_at": r["created_at"],
                "score": r["score"],
                "score_label": r["score_label"],
            })
        return summaries
    finally:
        conn.close()


def get_screening_by_id(screening_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full screening report and linked questionnaire responses."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT report_json FROM screenings WHERE screening_id = ?;", (screening_id,))
        row = cursor.fetchone()
        if not row:
            return None

        report = json.loads(row["report_json"])
        report["screening_id"] = screening_id

        # Fetch questionnaire if present
        cursor.execute("SELECT * FROM questionnaire_responses WHERE screening_id = ?;", (screening_id,))
        q_row = cursor.fetchone()
        if q_row:
            report["questionnaire"] = {
                "tooth_sensitivity": q_row["tooth_sensitivity"],
                "pain_discomfort": q_row["pain_discomfort"],
                "gum_bleeding": q_row["gum_bleeding"],
                "teeth_or_gum_changes": q_row["teeth_or_gum_changes"],
                "last_dental_visit": q_row["last_dental_visit"],
                "specific_concern": q_row["specific_concern"],
            }
        return report
    finally:
        conn.close()


def create_user(user_id: str, name: str, email: str, password_hash: str) -> Dict[str, Any]:
    """Insert a new user record into SQLite."""
    conn = _get_connection()
    try:
        created_at = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute("""
            INSERT INTO users (user_id, name, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?);
            """, (user_id, name.strip(), email.strip().lower(), password_hash, created_at))
        return {
            "user_id": user_id,
            "name": name.strip(),
            "email": email.strip().lower(),
            "created_at": created_at,
        }
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by email."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?;", (email.strip().lower(),))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by user_id."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, email, created_at FROM users WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()

