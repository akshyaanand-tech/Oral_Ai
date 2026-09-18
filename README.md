# OralAI — AI-Powered Preventive Oral Health Screening & Monitoring

> ⚠️ **Medical Disclaimer:** This application is a **preliminary visual screening and monitoring tool only** and does **NOT** provide a dental diagnosis, clinical prognosis, or medical advice. It cannot replace an examination by a qualified dental professional.

---

## 🦷 Product Vision

**OralAI** is a patient-facing preliminary visual oral-health screening platform designed around an API-enhanced, privacy-first preventive care pathway:

```text
USER
  ↓
5 GUIDED ORAL IMAGES & SURVEY
  ↓
IMAGE ENHANCEMENT & QUALITY CHECK
  ↓
ML IMAGE ANALYSIS (4 CATEGORIES)
  ↓
DETERMINISTIC VISUAL SCORING (0–100)
  ↓
RULES-BASED RECOMMENDATION ENGINE
  ↓
SUGGESTED CARE PATHWAY & COST ESTIMATES (₹ INR)
  ↓
LOCAL DENTIST SEARCH & REFERRAL
  ↓
FINAL CLINICAL REPORT & OPTIONAL GEMINI EXPLANATION
```

The system allows users to complete a full screening in about **2 minutes** using a smartphone or webcam, and provides actionable preventive care pathways with realistic dental cost estimates in Indian Rupees (`₹`).

---

## ✨ Core Features & Architecture

### 1. Dual-Mode Authentication & User Profiles
* **Secure Registration & Login (`backend/app/routes/auth.py`, `backend/app/services/auth_service.py`)**:
  * SQLite persistent user management with bcrypt-hashed passwords.
  * Real-time form validation and interactive password strength meter.
  * Fast demo-mode bypass allowing guest evaluation or full user session tracking.
  * Personalized greeting banners with user avatar badges on Landing, Header, and Results screens.

### 2. Automatic Image Enhancement (`backend/app/services/enhancement.py`)
* Deterministic image processing using Pillow and NumPy (`enhance_image()`).
* Dual-stage unsharp masking, edge deblurring, gamma compensation for shadowed arches, adaptive contrast expansion, and enamel/mucosa tone normalization.
* **Strict Geometric Integrity**: Preserves original image dimensions, aspect ratio, tooth shapes, and anatomical contours without generating synthetic features.

### 3. Two-Stage Image Quality Assessment (`backend/app/services/quality.py`)
* **Stage 1 (Basic Validation)**: Validates image decodability, supported formats (JPEG, PNG, WebP), and minimum resolution (200×200px).
* **Stage 2 (Multi-Signal Usability Check)**: Computes Laplacian variance for sharpness, illumination balance, and contrast distribution before and after enhancement.
* Automatically recovers moderately blurred or low-light images; provides view-specific retake instructions when an image cannot be salvaged.

### 4. Guided 5-View Oral Capture (`frontend/src/pages/CameraCapture.jsx`)
* Guides users through 5 standardized dental views:
  1. **Front Teeth** (biting together)
  2. **Left Side** (molars and bite)
  3. **Right Side** (molars and bite)
  4. **Upper Arch** (occlusal surfaces)
  5. **Lower Arch** (occlusal surfaces)
* Live camera stream, file upload fallback, and instant sample image loader for fast testing.
* Interactive before/after visual toggle comparing original vs. enhanced captures.

### 5. Standard 6-Question Patient Survey (`frontend/src/pages/Questionnaire.jsx`)
* Captures self-reported symptoms: tooth sensitivity, pain/discomfort, gum bleeding, noticeable tooth/gum changes, last dental visit, and primary concern.
* Kept strictly independent from deterministic visual AI scoring and explicitly demarcated as user-reported context.

### 6. Multi-View ML Image Analysis (`backend/app/services/ml_service.py`, `gemini.py`)
* Evaluates 4 visible oral health categories:
  * **Alignment & Spacing**: Crowding, spacing, or overlapping.
  * **Surface Discoloration**: Extrinsic staining, localized spotting.
  * **Tooth Surface Wear**: Flattening, incisal/occlusal attrition.
  * **Gum Appearance**: Marginal erythema, swelling, or recession.
* Returns severity (`none`, `mild`, `moderate`, `marked`), confidence levels, and normalized bounding box coordinates for explainable visual evidence.
* Safe medical prompt preventing diagnostic claims (*"possible visible staining"*, *"observed appearance"*).

### 7. Deterministic Scoring Engine (`backend/app/services/scoring.py`, `scoring_service.py`)
* Auditable baseline of 100 points with itemized deductions based on observed severity.
* Clamped between 0 and 100, labeled as **Preliminary Visual Screening Score**.

### 8. Suggested Care Pathway Synthesis (`backend/app/services/care_plan_service.py`, `recommendation_service.py`)
* Maps visual indicators and questionnaire context into a prioritized care plan:
  * **Clinical Urgency**: Routine (6–12 months), Timely (3–4 weeks), or Prompt (within days).
  * **Actionable Steps**: Daily oral hygiene steps, targeted home interventions, and questions to ask during a dental visit.

### 9. Dental Cost Estimation in Indian Rupees (`₹` / `INR`) (`backend/app/services/cost_service.py`, `backend/data/costs.json`)
* Realistic procedure cost ranges tailored for Indian dental practices:
  * **Comprehensive Oral Examination**: ₹500 – ₹1,200
  * **Professional Dental Cleaning / Prophylaxis**: ₹1,000 – ₹2,500
  * **Orthodontic Evaluation & Consultation**: ₹800 – ₹2,000
  * **Periodontal Health Evaluation**: ₹600 – ₹1,500
  * **Periodontal Scaling & Root Planing**: ₹1,500 – ₹3,500
  * **Custom Night Guard / Occlusal Splint**: ₹3,000 – ₹7,000
  * **Diagnostic Dental Radiographs (IOPA / OPG)**: ₹350 – ₹1,000
* Displayed with `₹` currency symbols and Indian locale number formatting throughout the UI.

### 10. Local Dentist Search & Referral (`backend/app/services/provider_service.py`, `referral.py`)
* Real-time OpenStreetMap Overpass API queries with offline fallback data for major Indian cities (Kochi, Thiruvananthapuram, Bengaluru, Chennai, Mumbai, Delhi).
* Responsive **2-column modal layout** (constrained to 88vh):
  * **Left Column**: Location search, GPS auto-detect, quick city chips, and scrollable clinic cards with distance metrics.
  * **Right Column**: Selected clinic preview and appointment inquiry form linking the patient's screening ID.

### 11. Dentist-Ready Clinical Report & In-App Viewer (`backend/app/services/report.py`, `ResultsDashboard.jsx`)
* High-resolution, print-ready HTML summary report (`GET /api/screenings/{screening_id}/report`).
* Includes score breakdown, category findings, care pathway, INR cost estimates, and self-reported survey.
* Interactive in-app modal viewer with "Print / Save PDF" and "Open Full Page" controls, immune to browser popup blockers.
* Automatic fallback to demo/baseline screenings to guarantee zero-failure demos.

---

## 📁 Repository Structure

```text
oral/
├── frontend/                         # React + Vite frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx            # Top navbar with user profile & auth status
│   │   │   └── MedicalDisclaimer.jsx # Medical guardrail disclaimer banner
│   │   ├── pages/
│   │   │   ├── Landing.jsx           # Hero page with workflow steps & user greeting
│   │   │   ├── Login.jsx             # Sign-in portal with validation & demo bypass
│   │   │   ├── Register.jsx          # Patient registration with password strength meter
│   │   │   ├── Questionnaire.jsx     # 6-step self-reported dental survey
│   │   │   ├── CameraCapture.jsx     # 5-view guided capture with enhancement preview
│   │   │   ├── ReviewAll.jsx         # Image review and re-take grid
│   │   │   ├── Processing.jsx        # Animated analysis progress screen
│   │   │   └── ResultsDashboard.jsx  # Complete findings, care plan, costs, report & dentist finder
│   │   ├── services/
│   │   │   └── api.js                # Axios client for screening, auth, report & provider APIs
│   │   ├── utils/
│   │   │   └── sampleImages.js       # Pre-loaded clear and test dental images
│   │   ├── App.jsx                   # Application router and state management
│   │   ├── main.jsx                  # React application root
│   │   └── index.css                 # Comprehensive custom styling & responsive modals
│   ├── package.json
│   └── vite.config.js
│
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── main.py                   # FastAPI initialization, CORS, and routing
│   │   ├── routes/
│   │   │   ├── health.py             # GET /api/health
│   │   │   ├── auth.py               # Register, login, forgot-password endpoints
│   │   │   ├── quality.py            # POST /api/quality-check
│   │   │   ├── enhancement.py        # POST /api/enhance-image
│   │   │   ├── analyze.py            # POST /api/analyze (5 views + questionnaire)
│   │   │   ├── screening.py          # POST /api/screen (full pipeline)
│   │   │   ├── screenings.py         # GET report, GET screenings, referrals
│   │   │   └── providers.py          # GET /api/providers
│   │   ├── services/
│   │   │   ├── auth_service.py       # Password hashing & user validation
│   │   │   ├── enhancement.py        # Dual-stage unsharp mask & gamma enhancement
│   │   │   ├── quality.py            # Two-stage multi-signal quality assessment
│   │   │   ├── ml_service.py         # ML image analysis across 4 categories
│   │   │   ├── gemini.py             # Gemini Vision + deterministic mock engine
│   │   │   ├── gemini_service.py     # Plain-language explanation generator
│   │   │   ├── scoring.py            # Itemized deduction visual scoring
│   │   │   ├── scoring_service.py    # Scoring pipeline adapter
│   │   │   ├── recommendation_service.py # Rules-based recommendation engine
│   │   │   ├── care_plan_service.py  # Care pathway urgency & action steps
│   │   │   ├── cost_service.py       # Procedure cost estimation (INR ₹)
│   │   │   ├── provider_service.py   # Overpass API & local dentist search
│   │   │   ├── referral.py           # Patient referral request handler
│   │   │   ├── report.py             # High-resolution HTML clinical report generator
│   │   │   ├── comparison.py         # Longitudinal comparison engine
│   │   │   └── db.py                 # SQLite database & baseline seeding
│   │   └── schemas/                  # Pydantic schemas (screening, auth, quality, etc.)
│   ├── data/
│   │   ├── costs.json                # Dental procedure costs in INR (₹)
│   │   └── dentists.json             # Verified dentist dataset for Indian cities
│   ├── tests/                        # Pytest automated test suite (51 tests)
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── docs/                             # Architecture & demonstration guides
│   ├── API_CONTRACT.md               # API endpoint specifications
│   ├── ARCHITECTURE.md               # Architecture & data flow diagrams
│   └── DEMO.md                       # Hackathon demo script
│
├── PRD.md                            # Product Requirements Document
├── AGENTS.md                         # Agent development guide
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python**: 3.11 or 3.12
* **Node.js**: v18 or higher (with npm)

---

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the complete test suite (51 tests)
pytest -v

# Launch FastAPI backend with hot reload
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* **API Base URL**: `http://127.0.0.1:8000`
* **Health Check**: `http://127.0.0.1:8000/api/health`
* **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
* **Sample Clinical Report**: `http://127.0.0.1:8000/api/screenings/scr_demo/report`

---

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify production build
npm run build

# Start the Vite development server
npm run dev
```

* **Web Application**: `http://localhost:5173`

---

## ⚙️ Environment Configuration

Create or edit `backend/.env`:

```env
# Set to 'true' to use deterministic local ML findings (no API key required)
# Set to 'false' to call Google Gemini Vision API
MOCK_AI=true

# Google Gemini API key (only required when MOCK_AI=false)
GEMINI_API_KEY=

# Gemini Vision model name
GEMINI_MODEL=gemini-2.5-flash

# Allowed CORS origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000

# Maximum image upload size (10 MB)
MAX_IMAGE_SIZE_BYTES=10485760

# SQLite Database path
DATABASE_URL=sqlite:///./dental_app.db
```

---

## 🧪 Automated Testing

The backend includes a comprehensive test suite in `backend/tests/`:

```bash
cd backend
python -m pytest tests/ -v
```

### Test Coverage Highlights (51 Tests):
* **Image Quality & Recovery (`test_quality.py`, `test_two_stage_quality.py`)**: Format verification, dimension clamping, sharpness analysis, and blur recovery.
* **Enhancement Pipeline (`test_enhancement.py`)**: Dimension and aspect ratio preservation, gamma correction, and unsharp masking.
* **Scoring Rules (`test_scoring.py`)**: Itemized point deductions, boundary clamping, and PRD benchmark evaluation (82/100).
* **Care Pathway & Costs (`test_screening_pipeline.py`)**: Clinical urgency synthesis, procedure cost ranges, and INR (`₹`) validation.
* **Location-Based Dentists (`test_location_dentists.py`)**: Overpass and fallback clinic discovery across Kochi, Thiruvananthapuram, and Bengaluru with distance calculation.
* **Authentication & User Accounts (`test_auth.py`)**: Registration, password complexity validation, login token issuance, and password recovery.
* **Clinical Report & Referrals (`test_screenings_and_comparison.py`)**: HTML report generation, findings normalization, and referral inquiries.

---

## 🔒 Privacy & Medical Safety Safeguards

1. **Ephemeral Image Handling**: Raw camera captures are processed in-memory for enhancement, quality assessment, and ML scoring. Only extracted non-identifiable findings, numerical scores, and survey responses are retained.
2. **Deterministic Rules Over AI Hallucination**: AI vision detects visible visual features; scoring, recommendations, and care pathway urgencies are computed using auditable Python rulesets.
3. **Cautious Non-Diagnostic Vocabulary**: The platform enforces cautious, observational phrasing (*"possible mild crowding observed"*, *"visible surface staining"*) rather than definitive clinical diagnoses (*"patient has periodontitis"*).
4. **Universal Medical Disclaimers**: Prominently displayed across all application views, referral forms, and generated PDF/HTML reports to ensure users seek professional in-person dental care.
