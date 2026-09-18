# System Architecture — OralAI

## High-Level Architecture

```text
               ┌─────────────────────────────────────────────────────────────┐
               │                  React + Vite Frontend                      │
               │  - 6-Question Survey (Patient self-reported triage)         │
               │  - 5-View Guided Capture (Camera & upload + guide overlay)  │
               │  - Instant Enhancement feedback (auto-deblur status)        │
               │  - Preliminary Visual Screening Dashboard (0–100 score)     │
               │  - Explainable visual evidence viewer (normalized boxes)    │
               │  - Longitudinal history & previous-vs-current comparison    │
               │  - Dentist-ready print/PDF report                           │
               │  - Smart dental clinic referral workflow                    │
               └──────────────────────────────┬──────────────────────────────┘
                                              │
                                              │ HTTP Multipart / JSON
                                              ▼
               ┌─────────────────────────────────────────────────────────────┐
               │                 FastAPI Backend Application                 │
               │                                                             │
               │  1. Stage 1: Basic validation (MIME, sizes, decode, dims)   │
               │  2. Stage 2: Automatic image enhancement (Pillow / NumPy)   │
               │     ├── Brightness & adaptive exposure                      │
               │     ├── Gamma correction for arch shadow recovery           │
               │     ├── Local & global contrast expansion                   │
               │     ├── Multi-scale unsharp masking & edge sharpening       │
               │     └── Mucosal & enamel natural color normalization        │
               │  3. Multi-Signal Quality Engine (Laplacian, lighting, etc.) │
               │     └── Retake router (view-specific retake payloads)       │
               │  4. Gemini Vision AI (with deterministic MOCK_AI fallback)  │
               │  5. Pydantic Structured Findings Validation                 │
               │  6. Deterministic 0–100 Python Scoring Engine               │
               │  7. Personalized Preventive Guidance Generator              │
               │  8. SQLite Longitudinal Tracking Engine (oralai.db)         │
               │  9. Previous-vs-Current Comparison Engine                   │
               │ 10. Dentist Report & Referral Management Router             │
               └─────────────────────────────────────────────────────────────┘
```

---

## Detailed Data Flow

1. **Patient Intake & Capture**:
   - The user completes a 6-question clinical background survey (tooth sensitivity, pain, gum bleeding, noticeable changes, last checkup, specific concern). Survey answers are stored as separate context and do NOT alter the visual score.
   - The user captures or uploads 5 guided views (**Front**, **Left**, **Right**, **Upper Arch**, **Lower Arch**) with visual stencil overlays.
   - Each view is verified with `POST /api/quality-check`. If the smartphone photo is moderately blurry or dim, automatic enhancement improves clarity, displaying *"✓ Image quality improved automatically"*.

2. **Submission & Processing Pipeline**:
   - The frontend submits the 5 images and survey responses to `POST /api/analyze`.
   - **Stage 1**: Decodability and minimum dimension checks.
   - **Stage 2**: Automatic enhancement is applied to sub-optimal photos, keeping both `original_images` and `enhanced_images` in memory.
   - If any view cannot be made technically usable, a structured `retake_required` response instructs the user which view needs to be retaken and why, without discarding the other valid views.
   - The enhanced images are passed to Google Gemini Vision (or mock AI) using a strict non-diagnostic prompt.
   - Structured JSON observations with normalized bounding boxes `[0.0 - 1.0]` are validated via Pydantic.
   - Deterministic 0–100 scoring is calculated in Python by deducting points from 100 based on observed severity.
   - Non-prescriptive personalized preventive guidance is assembled.
   - Complete screening record is saved to the SQLite database (`oralai.db`).

3. **Results & Longitudinal Monitoring**:
   - The dashboard presents the **Preliminary Visual Screening Score (0–100)**, 4 Category Cards, interactive bounding box evidence preview, score deduction breakdown, and personalized guidance.
   - Historical screenings are loaded from SQLite. The user can compare current results against past screenings to observe category-level transitions (*"More visible discoloration was observed compared with the previous screening"*).
   - The user can export or print a **Dentist-Ready Summary** (`GET /api/screenings/{id}/report`).
   - The user can connect with verified local dental providers via the built-in referral interface.

---

## Security, Privacy & Integrity Guarantees

- **No Permanent Raw Image Storage**: To protect personal privacy, raw dental photos are processed in memory during request execution and discarded. Only derived metadata, findings, scores, and survey answers are stored in SQLite.
- **Strict Non-Diagnostic Scope**: Observations use cautious screening language (*"possible visible staining"*) and never clinical diagnoses (*"caries"*, *"periodontitis"*).
- **Zero Generative AI Hallucinations in Image Enhancement**: Enhancement operations are purely deterministic signal processing (unsharp masking, gamma, contrast expansion, color stabilization). Generative tooth reconstruction or synthetic tissue generation is strictly prohibited.
