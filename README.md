# OralAI — AI-Powered Preventive Oral Health Screening & Monitoring

> ⚠️ **Medical Disclaimer:** This application is a **preliminary visual screening and monitoring tool only** and does **NOT** provide a dental diagnosis, clinical prognosis, or medical advice. It cannot replace an examination by a qualified dental professional.

---

## 🦷 Product Vision

**OralAI** is a patient-facing preliminary visual oral-health screening and longitudinal monitoring platform following the complete preventive care pathway:

```text
SCAN → ENHANCE → QUALITY CHECK → ANALYSE → SCORE → UNDERSTAND → TRACK → REPORT → CONNECT
```

The system allows users to complete a guided screening in about **2 minutes** using an ordinary smartphone or webcam.

---

## ✨ Core Features & Architectural Upgrades

1. **Automatic Image Enhancement (`backend/app/services/enhancement.py`)**:
   - Deterministic image processing using Pillow & NumPy.
   - Dual-stage unsharp masking, edge deblurring, gamma correction for shadowed arches, adaptive contrast expansion, and mucosal/enamel color normalization.
   - Strictly preserves original dimensions, aspect ratio, tooth shape, and anatomical contours. Never hallucinate dental features or generative artificial structures.
   - Exposes `enhance_image(image_bytes: bytes) -> bytes`.

2. **Two-Stage Quality Assessment (`backend/app/services/quality.py`)**:
   - **Stage 1 (Basic Validation)**: Checks file decodability, valid image formats, and minimum dimensions (200×200px).
   - **Stage 2 (Multi-Signal Usability Check)**: Evaluates sharpness (Laplacian variance), illumination, contrast distribution, and overall usability before and after automatic enhancement.
   - Avoids single-threshold blur rejection; auto-enhances moderately poor smartphone photos to make them usable.
   - Returns granular metrics: `quality_score`, `original_quality_score`, `enhanced_quality_score`, `enhanced`, and view-specific retake reasons if unrecoverable.

3. **Standard 6-Question Survey (`Questionnaire.jsx` & `questionnaire.py`)**:
   - Captures self-reported patient context: tooth sensitivity, pain/discomfort, gum bleeding, noticeable changes, last dental visit, and specific concerns.
   - Kept strictly independent from deterministic visual AI scoring and clearly labeled as user-reported context.

4. **Guided 5-View Capture (`CameraCapture.jsx`)**:
   - Guided steps: **Front**, **Left**, **Right**, **Upper Arch**, **Lower Arch**.
   - Ergonomic dental positioning overlays.
   - Live camera capture, file upload fallback, and instant sample test images.
   - Immediate feedback: *"✓ Image quality improved automatically"* or *"⚠️ Image still needs improvement: Please retake with better lighting"*.
   - Original vs. Enhanced visual toggle.

5. **AI Visual Analysis (`gemini.py`)**:
   - Google Gemini Vision (with deterministic `MOCK_AI=true` fallback).
   - Inspects 4 distinct categories: **Alignment**, **Discoloration**, **Tooth Wear**, and **Gum Appearance**.
   - Strict medical safety prompt: cautious screening language (*"possible"*, *"visible"*, *"appears"*), never diagnostic (*"definitely"*, *"diagnosed"*, *"patient has"*).
   - Explainable visual evidence with normalized bounding box coordinates `[0.0 - 1.0]`.

6. **Deterministic Scoring Engine (`scoring.py`)**:
   - Starting baseline of 100 points with itemized deductions based on observed severity.
   - Python-driven, fully auditable, and clamped strictly between 0 and 100.
   - Labeled as **Preliminary Visual Screening Score**.

7. **Personalized Preventive Guidance (`guidance.py`)**:
   - Category-specific insights, daily lifestyle tips, and clearly labeled self-reported questionnaire context.
   - Non-prescriptive, non-diagnostic oral wellness recommendations.

8. **SQLite Longitudinal Tracking & History (`db.py` & `screenings.py`)**:
   - Lightweight zero-config SQLite persistence (`oralai.db`).
   - Stores screening summaries, findings, scores, and questionnaire responses.
   - Avoids permanent raw dental image storage to protect patient privacy.
   - Pre-seeded with baseline historical screening for instant demo comparison.

9. **Previous-vs-Current Comparison Engine (`comparison.py`)**:
   - Compares historical screenings: overall score delta (`+6`, etc.) and category-level transitions.
   - Uses objective visible change descriptions (*"More visible discoloration was observed compared with the previous screening"*), never disease progression claims (*"disease progressed"*).

10. **Dentist-Ready Report & Print View (`report.py`)**:
    - Complete structured JSON report + print-friendly HTML endpoint (`GET /api/screenings/{id}/report`).
    - Formatted for easy presentation to dental professionals.

11. **Smart Dentist Referral Workflow (`referral.py`)**:
    - Demonstrates patient-to-care journey (*"Want professional evaluation?"*).
    - Directory of local verified dental practices with 1-click appointment inquiry pre-attaching the screening report ID.

---

## 📁 Repository Structure

```text
oral/
├── frontend/                     # React + Vite web application
│   ├── src/
│   │   ├── components/           # Header, MedicalDisclaimer
│   │   ├── pages/                # Landing, Questionnaire, CameraCapture, ReviewAll, Processing, ResultsDashboard
│   │   ├── services/             # API client (analyze, screenings, compare, providers, referrals)
│   │   ├── utils/                # Sample clear & blurry dental test images
│   │   ├── App.jsx               # Main state machine & wizard router
│   │   ├── main.jsx              # Entry point
│   │   └── index.css             # High-polish design system & styles
│   ├── package.json
│   └── vite.config.js
│
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── main.py               # Application entry point, CORS, lifespan, DB init
│   │   ├── routes/
│   │   │   ├── health.py         # GET /health
│   │   │   ├── quality.py        # POST /api/quality-check
│   │   │   ├── enhancement.py    # POST /api/enhance-image
│   │   │   ├── analyze.py        # POST /api/analyze (5 views + questionnaire)
│   │   │   └── screenings.py     # History, compare, report, referral endpoints
│   │   ├── services/
│   │   │   ├── enhancement.py    # Multi-stage image enhancement pipeline
│   │   │   ├── quality.py        # Two-stage multi-signal quality assessment
│   │   │   ├── gemini.py         # Gemini Vision + deterministic mock AI
│   │   │   ├── scoring.py        # Deterministic 0-100 scoring engine
│   │   │   ├── guidance.py       # Personalized preventive guidance
│   │   │   ├── db.py             # SQLite persistence & baseline seeding
│   │   │   ├── comparison.py     # Longitudinal change comparison engine
│   │   │   ├── report.py         # Structured JSON & HTML report builder
│   │   │   └── referral.py       # Dental provider referral abstraction
│   │   └── schemas/              # Pydantic schemas (quality, analysis, score, questionnaire, retake)
│   ├── tests/                    # Comprehensive Pytest test suite (32 tests)
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── docs/                         # Technical documentation
│   ├── API_CONTRACT.md           # Complete REST API specifications
│   ├── ARCHITECTURE.md           # Architecture & data flow diagrams
│   └── DEMO.md                   # 2-minute hackathon presentation script
│
├── PRD.md                        # Product Requirements Document
├── AGENTS.md                     # Agent development instructions
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup

```bash
cd backend

# Install dependencies (Python 3.11 or 3.12 recommended)
pip install -r requirements.txt

# Run the complete test suite (32 tests)
pytest -v

# Start the FastAPI server
python -m uvicorn app.main:app --port 8000 --reload
```

- **Base URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build production bundle to verify correctness
npm run build

# Start the Vite development server
npm run dev
```

- **Frontend URL**: `http://localhost:5173`

---

## ⚙️ Environment Variables

Configure in `backend/.env`:

```env
# Gemini API Key (Required only if MOCK_AI=false)
GEMINI_API_KEY=

# Mock AI Mode: true to use deterministic sample findings without calling Gemini
MOCK_AI=true

# Gemini model identifier (used when MOCK_AI=false)
GEMINI_MODEL=gemini-2.5-flash

# Allowed CORS origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000

# Maximum file upload size in bytes (10 MB default)
MAX_IMAGE_SIZE_BYTES=10485760

# SQLite Database Location
DATABASE_URL=sqlite:///./oralai.db
```

---

## 🧪 Automated Testing

The project includes an end-to-end test suite in `backend/tests/`:

```bash
cd backend
pytest -v
```

Tests verify:
- **Quality & Multi-signal Blur**: Valid images, corrupt data, dimension constraints, auto-enhancement recovery of moderate blur, and rejection of severe blur.
- **Image Enhancement**: `enhance_image` entry point, brightness compensation, aspect ratio and dimension preservation.
- **Scoring Engine**: Clamping bounds, deterministic calculations, PRD benchmark score (82/100), and uncertain findings handling.
- **Screenings & History**: SQLite persistence, listing past records, and individual retrieval.
- **Comparison Engine**: Category-level transitions and cautious non-diagnostic language.
- **Preventive Guidance**: Customized advice generation and questionnaire labeling.
- **Retake Response**: Structured view-specific retake payloads when an image is unrecoverable.
- **Referral Workflow**: Provider listing and referral inquiry submission.

---

## 🔒 Privacy & Medical Safety Principles

1. **No Raw Dental Image Hoarding**: Raw images are processed in memory during the request for enhancement, quality assessment, and AI inspection. Only derived metadata, findings, scores, and questionnaire answers are stored in SQLite.
2. **Deterministic Python Scoring**: The AI vision model observes; Python calculates the score deterministically using an auditable ruleset.
3. **Strict Non-Diagnostic Language**: The system uses cautious observational terminology (*"possible visible staining"*, *"observed appearance"*) and explicitly disclaims clinical diagnosis.
4. **Mandatory Disclaimers**: Every screen, report, and export reminds users that preliminary screenings cannot replace professional dental examinations.
