# AGENTS.md

## Project

AI Preventive Oral Health Screening

This file contains the engineering instructions for AI coding agents working on this repository.

The complete product requirements are defined in:

```text
PRD.md
```

The agent must read and follow `PRD.md` before implementing features.

---

# 1. PRIMARY OBJECTIVE

Build and maintain a complete working hackathon MVP.

The agent must prioritize:

1. Working functionality
2. Correct frontend/backend integration
3. Reliable AI output
4. Clear UX
5. Error handling
6. Testability
7. Simple architecture

Do not over-engineer.

---

# 2. DEVELOPMENT PHILOSOPHY

This is a 20-hour hackathon project.

Prefer:

```text
simple + reliable + demonstrable
```

over:

```text
complex + theoretical + over-engineered
```

Do not introduce architecture that is unnecessary for the MVP.

---

# 3. SOURCE OF TRUTH

The following priority applies:

```text
PRD.md
   ↓
AGENTS.md
   ↓
Existing implementation
```

When implementing a feature:

1. Read the relevant PRD section.
2. Inspect existing code.
3. Preserve working functionality.
4. Make the smallest clean change necessary.
5. Test the change.

Never rewrite the entire project unnecessarily.

---

# 4. ARCHITECTURE

Use a single application architecture:

```text
React
  ↓
FastAPI
  ↓
Validation
  ↓
Image Quality
  ↓
Gemini Vision
  ↓
Structured Output
  ↓
Scoring
  ↓
Report
  ↓
React
```

Do NOT create microservices.

Do NOT create separate servers for:

* quality
* AI
* scoring
* reports

These should be Python modules inside the FastAPI backend.

---

# 5. DIRECTORY STRUCTURE

Maintain:

```text
oral-health-screening/
│
├── frontend/
│
├── backend/
│
├── docs/
│
├── PRD.md
├── AGENTS.md
└── README.md
```

Backend:

```text
backend/
└── app/
    ├── main.py
    ├── routes/
    ├── services/
    └── schemas/
```

---

# 6. FRONTEND RULES

Use React + Vite.

Keep components modular.

Recommended structure:

```text
frontend/src/
├── components/
├── pages/
├── services/
├── hooks/
├── utils/
├── App.jsx
└── main.jsx
```

Do not place the entire application inside `App.jsx`.

---

# 7. BACKEND RULES

Use:

* FastAPI
* Pydantic
* Pillow/OpenCV where required
* Uvicorn
* environment variables

Keep responsibilities separated.

Required services:

```text
quality.py
gemini.py
scoring.py
report.py
```

---

# 8. SERVICE CONTRACTS

Maintain these interfaces.

## Quality

```python
quality_check(image)
```

Returns quality information.

---

## Gemini

```python
analyze_images(images)
```

Returns validated structured findings.

---

## Scoring

```python
calculate_score(findings)
```

Returns deterministic scoring information.

---

## Report

```python
generate_report(...)
```

Returns frontend-ready response.

Do not make these functions tightly coupled.

---

# 9. API CONTRACT

The primary endpoint is:

```text
POST /api/analyze
```

Input:

```text
front
left
right
upper
lower
```

All five images are required.

Do not change field names without updating:

* frontend
* backend
* API documentation
* PRD

---

# 10. API RESPONSE

Maintain this high-level structure:

```json
{
  "screening_id": "...",
  "status": "completed",
  "score": 82,
  "score_label": "Preliminary Visual Screening Score",
  "findings": {},
  "score_breakdown": {},
  "recommendation": "...",
  "disclaimer": "..."
}
```

Do not return raw Gemini output directly to the frontend.

---

# 11. AI SAFETY RULES

The AI is performing visual screening only.

It must NEVER claim:

```text
"You have X disease."
```

It should instead use:

```text
"Possible visible indication of X."
```

The AI must distinguish:

```text
visible observation
```

from:

```text
medical diagnosis
```

---

# 12. GEMINI OUTPUT

Gemini must return structured JSON.

Do not rely on free-form text parsing where structured output is possible.

Validate AI output using Pydantic.

Expected severity:

```text
none
mild
moderate
marked
uncertain
```

Confidence:

```text
0.0 <= confidence <= 1.0
```

If parsing fails:

* handle the error
* do not crash
* do not silently invent data

---

# 13. UNCERTAINTY

The AI must be conservative.

When evidence is insufficient:

```text
uncertain
```

must be used.

Do not force:

```text
none
```

or a positive finding merely to complete the JSON.

---

# 14. EVIDENCE

Evidence must never be fabricated.

If reliable image coordinates are available:

```json
{
  "image": "front",
  "region": {
    "x": 0.42,
    "y": 0.35,
    "width": 0.18,
    "height": 0.22
  }
}
```

Otherwise:

```json
"evidence": null
```

---

# 15. SCORING RULES

The scoring engine must be deterministic.

Gemini observes.

Python scores.

Never allow Gemini to directly choose the final 0–100 score.

Initial score:

```text
100
```

Apply documented deductions.

Clamp:

```text
0–100
```

The scoring weights are prototype values.

Do not describe them as clinically validated.

---

# 16. MOCK MODE

Always maintain:

```text
MOCK_AI=true
```

as a valid development mode.

When enabled:

* Gemini must not be called
* realistic deterministic findings should be returned
* complete frontend flow must work

This mode is required for:

* local development
* testing
* hackathon fallback
* frontend integration

---

# 17. ENVIRONMENT VARIABLES

Use:

```text
GEMINI_API_KEY=
MOCK_AI=true
ALLOWED_ORIGINS=http://localhost:5173
```

Never hardcode credentials.

Never commit `.env`.

Ensure `.gitignore` contains:

```text
.env
venv/
__pycache__/
node_modules/
dist/
```

---

# 18. IMAGE HANDLING

Accept:

```text
JPEG
JPG
PNG
WEBP
```

Validate:

* MIME type
* file size
* decodability
* dimensions

Do not permanently store images by default.

Avoid logging image contents.

---

# 19. PRIVACY

Do not collect unnecessary personal information.

Do not implement authentication for MVP.

Do not permanently save dental images unless explicitly required.

Do not log:

* API keys
* image bytes
* unnecessary personal information

---

# 20. ERROR HANDLING

Every external operation can fail.

Handle:

```text
invalid upload
corrupted image
quality failure
Gemini failure
JSON parsing failure
validation failure
unexpected exception
```

The backend must return clean API responses.

The frontend must display human-readable error messages.

Never expose stack traces to the user.

---

# 21. FRONTEND ERROR UX

Never show raw backend errors such as:

```text
500 Internal Server Error
```

Instead show useful messages.

Examples:

```text
We couldn't process one of your images.
Please try again.
```

or:

```text
This image appears too blurry.
Please retake it.
```

---

# 22. CAMERA UX

The capture experience is a core product feature.

Each capture step must clearly display:

* current view
* instructions
* progress
* camera/upload controls
* preview
* retake

Example:

```text
Step 2 of 5

LEFT VIEW

Turn your mouth slightly to the left.

[ Camera Preview ]

[ Capture ]
```

---

# 23. MOBILE-FIRST

The application will primarily be demonstrated on a smartphone-sized screen.

Prioritize:

* large controls
* simple navigation
* readable typography
* camera experience
* minimal typing

Desktop must still work.

---

# 24. RESULT UI

The result screen should visually communicate:

```text
Preliminary Visual Screening Score

82 / 100
```

Then:

```text
Alignment
Discoloration
Tooth Wear
Gum Appearance
```

Then:

```text
Score Breakdown
```

Then:

```text
Recommendation
```

Then:

```text
Disclaimer
```

---

# 25. NO MEDICAL OVERCLAIMS

Do not add copy such as:

```text
Your teeth are healthy.
You have gum disease.
You have cavities.
You are at high risk of disease.
```

Use cautious language.

---

# 26. DEPENDENCY RULES

Do not add a dependency unless it solves a real requirement.

Before adding a package, ask:

1. Is it necessary?
2. Can the existing stack do this?
3. Will it complicate deployment?
4. Is it stable?

Prefer lightweight dependencies.

---

# 27. NO DATABASE

Do not introduce a database for the MVP.

Do not add:

```text
PostgreSQL
MongoDB
Firebase
Supabase
```

unless explicitly requested.

---

# 28. NO AUTHENTICATION

Do not add:

```text
login
signup
password
OAuth
JWT authentication
```

unless explicitly requested.

---

# 29. TESTING

After every significant backend change:

Run tests.

At minimum:

```bash
pytest
```

Test:

* health endpoint
* image validation
* quality checker
* scoring
* score boundaries
* mock AI

---

# 30. LOCAL DEVELOPMENT

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Expected:

```text
Frontend:
http://localhost:5173

Backend:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs
```

If ports differ, update the relevant configuration.

---

# 31. DEVELOPMENT WORKFLOW

Before implementing a feature:

```text
1. Read PRD
2. Inspect repository
3. Identify affected files
4. Implement
5. Run tests
6. Run application
7. Verify behavior
8. Fix errors
9. Continue
```

Do not blindly generate large amounts of code.

---

# 32. INTEGRATION WORKFLOW

Build in this order:

## Phase 1

```text
FastAPI
+
React
+
health endpoint
```

## Phase 2

```text
Five-image upload
```

## Phase 3

```text
Image quality
```

## Phase 4

```text
MOCK_AI pipeline
```

## Phase 5

```text
Gemini
```

## Phase 6

```text
Structured AI validation
```

## Phase 7

```text
Scoring
```

## Phase 8

```text
Report
```

## Phase 9

```text
Full frontend integration
```

## Phase 10

```text
Testing + polish
```

---

# 33. DO NOT BUILD EVERYTHING AT ONCE

When possible, work incrementally.

A working application with mock AI is more valuable than an incomplete application with partially implemented real AI.

Always maintain a runnable state.

---

# 34. GIT RULES

Do not assume GitHub collaboration is required.

The project must work locally without GitHub.

Do not require:

* GitHub Actions
* CI/CD
* pull requests
* multiple repositories

unless explicitly requested.

---

# 35. CODE QUALITY

Prefer readable code.

Use meaningful names.

Avoid:

```python
x
data2
thing
temp
foo
```

when a meaningful name is possible.

Keep functions focused.

Add comments only where they provide useful context.

Do not fill the code with unnecessary comments.

---

# 36. SECURITY

Never:

* hardcode API keys
* commit secrets
* log credentials
* expose internal exceptions
* store uploaded images unnecessarily

---

# 37. DOCUMENTATION

Keep these updated when architecture changes:

```text
README.md
docs/API_CONTRACT.md
docs/ARCHITECTURE.md
docs/DEMO.md
```

Documentation must describe the actual implementation.

Do not document functionality that does not exist.

---

# 38. COMPLETION CHECKLIST

Before declaring the project complete, verify:

## Frontend

* [ ] Landing page
* [ ] Questionnaire
* [ ] Camera
* [ ] Upload fallback
* [ ] Five image views
* [ ] Preview
* [ ] Retake
* [ ] Progress
* [ ] Processing screen
* [ ] Results
* [ ] Score breakdown
* [ ] Recommendations
* [ ] Disclaimer
* [ ] Responsive design

## Backend

* [ ] FastAPI starts
* [ ] `/health`
* [ ] `/api/analyze`
* [ ] image validation
* [ ] quality checking
* [ ] mock AI
* [ ] Gemini integration
* [ ] Pydantic validation
* [ ] deterministic scoring
* [ ] report generation
* [ ] error handling
* [ ] CORS

## Testing

* [ ] backend tests pass
* [ ] frontend builds
* [ ] mock mode works
* [ ] five-image upload works
* [ ] complete screening works
* [ ] invalid image handling works
* [ ] API errors are handled

## Security

* [ ] `.env` ignored
* [ ] API key not hardcoded
* [ ] no unnecessary image storage
* [ ] no sensitive logging

---

# 39. AGENT BEHAVIOR

When asked to implement a feature:

Do not respond with only instructions.

Actually modify the code.

When an error occurs:

```text
Diagnose
→ Fix
→ Test
→ Continue
```

When requirements are ambiguous:

Prefer the simplest implementation consistent with `PRD.md`.

Do not invent unnecessary requirements.

---

# 40. PRIORITY ORDER

When trade-offs are necessary:

```text
1. Core functionality
2. Correctness
3. Safety
4. Integration
5. UX
6. Performance
7. Code elegance
8. Extra features
```

Do not sacrifice core functionality for visual polish.

---

# 41. HACKATHON FALLBACK

The application MUST remain demonstrable if Gemini fails.

The fallback is:

```text
MOCK_AI=true
```

The frontend should still demonstrate:

```text
Capture
→ Upload
→ Processing
→ Analysis
→ Score
→ Report
```

---

# 42. FINAL PRINCIPLE

Build the smallest complete product that convincingly demonstrates the concept.

The target is NOT:

```text
production clinical software
```

The target is:

```text
a polished, functional, technically credible hackathon MVP
```

Every implementation decision should support that goal.
