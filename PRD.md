# Product Requirements Document (PRD)

## Product Name

AI Preventive Oral Health Screening

## Version

1.0 — Hackathon MVP

---

# 1. Product Overview

AI Preventive Oral Health Screening is a web application that provides users with a fast, accessible preliminary visual screening of their oral health.

The user completes a short questionnaire and captures five guided images of their mouth:

1. Front
2. Left
3. Right
4. Upper
5. Lower

The application checks image quality, analyzes the images using an AI vision model, identifies potentially visible oral-health indicators, calculates a transparent preliminary screening score, and presents the findings through an easy-to-understand visual report.

The application is a screening and awareness tool.

It is NOT a medical diagnostic system.

---

# 2. Problem

Many people do not regularly inspect their oral health or seek professional dental evaluation until they notice a significant problem.

Existing dental AI systems are often designed for:

* dental professionals
* specialized equipment
* clinical environments
* expensive imaging systems

There is an opportunity to provide a simple first-level visual screening experience using an ordinary smartphone camera.

---

# 3. Product Goal

Create a working web-based prototype that allows a user to complete an oral-health screening in approximately two minutes.

The system should:

* guide the user through image capture
* detect technically poor images
* analyze visible oral-health indicators
* communicate uncertainty
* produce an understandable preliminary score
* provide category-wise findings
* encourage appropriate professional follow-up

---

# 4. Target Users

## Primary User

General users who want a quick preliminary visual check of their oral health using a smartphone or computer.

## Secondary User

Dental organizations, dental-tech companies, and dental practices interested in accessible patient-facing screening tools.

---

# 5. Core User Journey

```text
Landing Page
     ↓
Start Screening
     ↓
Basic Questionnaire
     ↓
Capture Instructions
     ↓
Front Image
     ↓
Left Image
     ↓
Right Image
     ↓
Upper Image
     ↓
Lower Image
     ↓
Image Quality Check
     ↓
AI Analysis
     ↓
Processing Screen
     ↓
Screening Result
     ↓
Visual Findings
     ↓
Recommendations
     ↓
Disclaimer
```

---

# 6. Functional Requirements

## FR-01: Landing Page

The application shall display:

* product name
* short explanation
* approximate completion time
* five-image requirement
* AI-powered screening description
* "Start Screening" button
* visible medical disclaimer

Primary CTA:

`Start Screening`

---

## FR-02: Questionnaire

The application shall provide a short questionnaire.

Example questions:

1. Have you noticed tooth discoloration recently?
2. Have you noticed visible tooth crowding or spacing?
3. Have you noticed changes in your gums?
4. Have you noticed unusual tooth wear?
5. When was your last dental check-up?

Questionnaire answers shall be stored separately from AI visual findings.

The questionnaire must not automatically determine the AI screening score unless explicitly implemented as a separate, documented feature.

---

# 7. Image Capture Requirements

The application shall collect exactly five image views.

## Required Views

### Front

Direct front view of the teeth.

### Left

Left-side view.

### Right

Right-side view.

### Upper

View showing the upper teeth.

### Lower

View showing the lower teeth.

---

# 8. Camera Requirements

The frontend should support:

* browser camera access
* image capture
* image preview
* retaking an image
* uploading an existing image when camera access is unavailable

The interface shall display clear instructions for each view.

The application should provide a visual positioning guide.

The guide is for usability and does not represent a medically precise measurement.

---

# 9. Image State Management

Each image shall support:

```text
EMPTY
CAPTURED
CHECKING
PASSED
FAILED
RETAKE
```

The user shall not be forced to continue with a technically unusable image.

---

# 10. Image Quality Analysis

The backend shall perform basic technical quality checks.

Checks may include:

* image decoding
* dimensions
* brightness
* excessive darkness
* excessive brightness
* blur/sharpness
* file size
* supported format

Example response:

```json
{
  "passed": true,
  "quality_score": 0.91,
  "issues": []
}
```

Failure example:

```json
{
  "passed": false,
  "quality_score": 0.31,
  "issues": [
    "Image is too blurry"
  ]
}
```

The quality checker must not claim to determine whether the image contains a medically valid dental view.

---

# 11. AI Analysis

The backend shall use a vision-capable Gemini model.

The AI shall analyze only visible characteristics.

Required categories:

1. Alignment
2. Discoloration
3. Tooth Wear
4. Gum Appearance

---

# 12. Alignment Analysis

The system may identify visible indications of:

* crowding
* spacing
* crooked alignment
* obvious rotation

The system shall not diagnose orthodontic conditions.

Example:

```text
Possible mild crowding
```

---

# 13. Discoloration Analysis

The system may identify:

* visible staining
* yellow/brown areas
* unusual visible color differences

The system shall not determine the cause of discoloration.

---

# 14. Tooth Wear Analysis

The system may identify visible:

* flattening
* wear patterns
* obvious surface changes

The system shall not diagnose erosion or determine its cause.

---

# 15. Gum Appearance Analysis

The system may identify visible:

* redness
* swelling
* unusual visible appearance

The system shall not diagnose:

* gingivitis
* periodontitis
* infection
* other dental diseases

---

# 16. Structured AI Output

The AI output shall be structured JSON.

Expected structure:

```json
{
  "alignment": {
    "finding": "Possible mild crowding",
    "severity": "mild",
    "confidence": 0.81,
    "evidence": null
  },
  "discoloration": {
    "finding": "Possible visible staining",
    "severity": "mild",
    "confidence": 0.87,
    "evidence": null
  },
  "tooth_wear": {
    "finding": "No obvious visible concern",
    "severity": "none",
    "confidence": 0.76,
    "evidence": null
  },
  "gum_appearance": {
    "finding": "Possible mild redness",
    "severity": "mild",
    "confidence": 0.69,
    "evidence": null
  }
}
```

Allowed severity values:

```text
none
mild
moderate
marked
uncertain
```

Confidence must be between:

```text
0.0 and 1.0
```

---

# 17. Uncertainty

The AI must be conservative.

If an image does not provide enough visual information:

```json
{
  "severity": "uncertain",
  "finding": "Unable to reliably assess this feature from the submitted image."
}
```

The AI must not invent findings.

The AI must not fabricate confidence.

---

# 18. Visual Evidence

Where reliable localization is available, the system may return:

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

Coordinates must be normalized between 0 and 1.

If reliable localization is unavailable:

```json
"evidence": null
```

The system must never fabricate bounding boxes.

---

# 19. Preliminary Screening Score

The backend shall calculate a deterministic score from 0–100.

Initial score:

```text
100
```

Example deductions:

| Category       | None | Mild | Moderate | Marked | Uncertain |
| -------------- | ---: | ---: | -------: | -----: | --------: |
| Alignment      |    0 |    5 |       10 |     15 |         0 |
| Discoloration  |    0 |    4 |        8 |     12 |         0 |
| Tooth Wear     |    0 |    5 |       10 |     15 |         0 |
| Gum Appearance |    0 |    5 |       10 |     15 |         0 |

Final score:

```text
100 - total deductions
```

Clamp the result:

```text
0 ≤ score ≤ 100
```

These weights are prototype values and are NOT clinically validated.

The score must be called:

**Preliminary Visual Screening Score**

Never call it:

* Dental Health Score
* Medical Score
* Diagnosis Score

---

# 20. Result Dashboard

The result screen shall display:

## Main Score

```text
82 / 100
```

Label:

```text
Preliminary Visual Screening Score
```

---

# 21. Finding Cards

Display four cards:

* Alignment
* Discoloration
* Tooth Wear
* Gum Appearance

Each card should show:

* finding
* severity
* confidence
* evidence where available

---

# 22. Score Breakdown

Display the calculation transparently.

Example:

```text
Starting score       100
Alignment             -5
Discoloration         -4
Tooth wear             0
Gum appearance        -9
--------------------------------
Final score            82
```

---

# 23. Recommendations

Recommendations must be cautious and non-diagnostic.

Example:

> Consider discussing the visible findings with a dental professional, particularly if they are new, worsening, painful, or concerning to you.

Do not:

* prescribe medication
* provide a treatment plan
* diagnose disease
* claim a specific condition is present

---

# 24. Disclaimer

The application shall always display:

> This is a preliminary visual screening and not a dental diagnosis. It cannot replace an examination by a qualified dental professional.

---

# 25. Backend API

## GET `/health`

Response:

```json
{
  "status": "ok"
}
```

## POST `/api/analyze`

Input:

```text
multipart/form-data
```

Fields:

```text
front
left
right
upper
lower
```

All five images are required.

---

# 26. API Response

Example:

```json
{
  "screening_id": "scr_abc123",
  "status": "completed",
  "score": 82,
  "score_label": "Preliminary Visual Screening Score",
  "findings": {
    "alignment": {},
    "discoloration": {},
    "tooth_wear": {},
    "gum_appearance": {}
  },
  "score_breakdown": {
    "starting_score": 100,
    "alignment": 5,
    "discoloration": 4,
    "tooth_wear": 0,
    "gum_appearance": 9,
    "final_score": 82
  },
  "recommendation": "Consider discussing the visible findings with a dental professional.",
  "disclaimer": "This is a preliminary visual screening and not a dental diagnosis."
}
```

---

# 27. Technology Stack

## Frontend

* React
* Vite
* JavaScript or TypeScript
* CSS
* Browser Camera API

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* Pillow/OpenCV

## AI

* Google Gemini Vision

---

# 28. Architecture

```text
                    React
                      |
                      | HTTP
                      ↓
                  FastAPI
                      |
          ┌───────────┼───────────┐
          ↓           ↓           ↓
     Validation    Quality     AI Vision
          |           |           |
          └───────────┼───────────┘
                      ↓
              Pydantic Validation
                      ↓
              Deterministic Scoring
                      ↓
                Report Generator
                      ↓
                   React
```

---

# 29. No Database for MVP

The MVP shall not require a database.

Do not implement:

* PostgreSQL
* MongoDB
* Firebase
* Supabase

unless specifically required later.

---

# 30. No Authentication for MVP

Do not require:

* login
* signup
* password
* account creation

The user should be able to start immediately.

---

# 31. Privacy

Uploaded dental images should not be permanently stored by default.

Process images in memory where practical.

Do not collect unnecessary personal information.

Do not log:

* image contents
* API keys
* unnecessary sensitive information

---

# 32. Mock AI Mode

The backend must support:

```text
MOCK_AI=true
```

When enabled:

* Gemini is not called.
* realistic deterministic findings are returned.
* the complete application remains functional.

This is required for hackathon fallback and frontend development.

---

# 33. Real AI Mode

When:

```text
MOCK_AI=false
```

the backend shall use:

```text
GEMINI_API_KEY
```

from environment variables.

Never hardcode API keys.

---

# 34. CORS

Allow local frontend development:

```text
http://localhost:5173
```

Make allowed origins configurable.

---

# 35. Error Handling

The backend shall handle:

* missing image
* unsupported image
* invalid MIME type
* oversized image
* corrupted image
* failed quality check
* Gemini API failure
* malformed AI response
* unexpected server error

Return clean API errors.

Do not expose internal stack traces to users.

---

# 36. Testing Requirements

Backend tests shall cover:

* `/health`
* valid image handling
* invalid images
* quality checking
* scoring
* score boundaries
* mock AI pipeline
* missing image handling

The score must always satisfy:

```text
0 ≤ score ≤ 100
```

---

# 37. Frontend Requirements

The frontend must handle:

* landing page
* questionnaire
* image capture
* image upload
* preview
* retake
* progress
* quality failure
* processing
* API errors
* results
* score breakdown
* findings
* disclaimer

---

# 38. Responsive Design

The application must work on:

* smartphone
* tablet
* laptop
* desktop

Mobile camera capture is the primary interaction.

---

# 39. Accessibility

Use:

* semantic HTML
* accessible labels
* keyboard navigation
* readable text
* adequate contrast
* clear error messages
* meaningful buttons

---

# 40. Performance

The application should:

* avoid unnecessary network calls
* resize/compress large images where appropriate
* avoid storing images unnecessarily
* provide visible loading states
* handle AI processing gracefully

---

# 41. Hackathon Demo Requirements

The complete demo should be possible in approximately two minutes.

Demo sequence:

```text
Open application
      ↓
Start Screening
      ↓
Answer questions
      ↓
Capture five images
      ↓
Quality check
      ↓
AI analysis
      ↓
Result
      ↓
Show findings
      ↓
Show score breakdown
      ↓
Show disclaimer
```

A `MOCK_AI=true` fallback must exist.

---

# 42. Success Criteria

The MVP is successful when:

* user can start without authentication
* user can complete the questionnaire
* user can capture/upload five images
* image quality can be checked
* backend accepts the five images
* AI can analyze them
* AI output is structured
* invalid AI output is handled
* deterministic score is generated
* result is displayed clearly
* application works in mock mode
* application works with Gemini when configured
* frontend and backend communicate successfully
* application works on mobile-sized screens
* disclaimer is clearly visible

---

# 43. Out of Scope

Do NOT implement:

* clinical diagnosis
* medical treatment recommendations
* prescription
* patient medical records
* authentication
* payment
* complex database
* dental clinic management
* appointment management
* insurance processing
* microservices
* unnecessary cloud infrastructure

---

# 44. Future Extensions

Possible future versions may add:

* longitudinal tracking
* dentist review
* appointment integration
* secure patient accounts
* improved computer-vision models
* calibrated clinical scoring
* dental practice integration
* richer image segmentation

These are NOT required for the hackathon MVP.
