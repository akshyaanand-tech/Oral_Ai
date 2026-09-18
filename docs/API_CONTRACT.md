# OralAI — API Contract

## Base URL
```text
http://127.0.0.1:8000
```

---

## 1. Operational Health Check

### `GET /health`
Returns system status, service identity, and mock AI configuration.

**Response `200 OK`**:
```json
{
  "status": "ok",
  "service": "dental-screening-backend",
  "mock_ai": true,
  "version": "1.0.0"
}
```

---

## 2. Two-Stage Technical Quality Check

### `POST /api/quality-check`
Performs Stage 1 basic validation and Stage 2 multi-signal quality assessment. Auto-enhances sub-optimal images to evaluate post-enhancement clarity.

**Request**: `multipart/form-data`
- `image`: Image file (JPEG, PNG, WEBP, max 10 MB)
- `view`: (Optional) string angle (`front`, `left`, `right`, `upper`, `lower`)

**Response `200 OK` (Auto-Enhanced Pass)**:
```json
{
  "passed": true,
  "quality_score": 0.88,
  "original_quality_score": 0.54,
  "enhanced_quality_score": 0.88,
  "enhanced": true,
  "issues": []
}
```

**Response `200 OK` (Unnecessary Enhancement)**:
```json
{
  "passed": true,
  "quality_score": 0.92,
  "original_quality_score": 0.92,
  "enhanced_quality_score": 0.92,
  "enhanced": false,
  "issues": []
}
```

**Response `200 OK` (Unrecoverable Blur / Needs Retake)**:
```json
{
  "passed": false,
  "quality_score": 0.32,
  "original_quality_score": 0.25,
  "enhanced_quality_score": 0.32,
  "enhanced": true,
  "issues": [
    "Image remains too blurry after automatic enhancement — please hold the camera steady and retake"
  ]
}
```

---

## 3. Dedicated Image Enhancement

### `POST /api/enhance-image`
Applies deterministic multi-stage sharpening, contrast expansion, and lighting balance.

**Request**: `multipart/form-data`
- `image`: Dental photograph file
- `view`: View angle name

**Response `200 OK`**:
```json
{
  "success": true,
  "view": "front",
  "enhanced_image_base64": "data:image/jpeg;base64,...",
  "before_quality": {
    "passed": true,
    "quality_score": 0.54,
    "original_quality_score": 0.54,
    "enhanced_quality_score": 0.88,
    "enhanced": false,
    "issues": []
  },
  "after_quality": {
    "passed": true,
    "quality_score": 0.88,
    "original_quality_score": 0.54,
    "enhanced_quality_score": 0.88,
    "enhanced": true,
    "issues": []
  },
  "improvements": [
    "Adjusted brightness (+25%) for shadowed oral regions",
    "Enhanced local contrast to clearly delineate tooth boundaries",
    "Applied edge deblurring and sharpness enhancement",
    "Preserved 100% original composition and aspect ratio"
  ]
}
```

---

## 4. Full Screening Analysis

### `POST /api/analyze`
Main screening pipeline. Validates 5 views, automatically enhances sub-optimal photos, executes Gemini Vision (or mock AI), computes deterministic 0–100 score, builds guidance, and persists to SQLite.

**Request**: `multipart/form-data`
- `front`: Front view photo (required)
- `left`: Left side photo (required)
- `right`: Right side photo (required)
- `upper`: Upper arch photo (required)
- `lower`: Lower arch photo (required)
- `questionnaire`: (Optional) JSON string containing self-reported answers

**Response `200 OK` (Completed Screening)**:
```json
{
  "screening_id": "scr_9cf34ab0",
  "created_at": "2026-09-18T06:18:26.089218+00:00",
  "status": "completed",
  "score": 82,
  "score_label": "Preliminary Visual Screening Score",
  "findings": {
    "alignment": {
      "finding": "Possible mild crowding visible in the lower anterior teeth",
      "severity": "mild",
      "confidence": 0.82,
      "evidence": {
        "image": "front",
        "region": { "x": 0.38, "y": 0.52, "width": 0.24, "height": 0.22 }
      }
    },
    "discoloration": {
      "finding": "Possible visible surface staining observed along outer tooth surfaces",
      "severity": "mild",
      "confidence": 0.85,
      "evidence": {
        "image": "front",
        "region": { "x": 0.44, "y": 0.36, "width": 0.16, "height": 0.18 }
      }
    },
    "tooth_wear": {
      "finding": "No obvious visible surface flattening or significant wear patterns detected",
      "severity": "none",
      "confidence": 0.78,
      "evidence": null
    },
    "gum_appearance": {
      "finding": "Possible mild redness visible along the gum margins",
      "severity": "mild",
      "confidence": 0.71,
      "evidence": null
    }
  },
  "score_breakdown": {
    "starting_score": 100,
    "alignment": 5,
    "discoloration": 4,
    "tooth_wear": 0,
    "gum_appearance": 9,
    "final_score": 82,
    "details": {
      "alignment": { "severity": "mild", "deduction": 5 },
      "discoloration": { "severity": "mild", "deduction": 4 },
      "tooth_wear": { "severity": "none", "deduction": 0 },
      "gum_appearance": { "severity": "mild", "deduction": 9 }
    }
  },
  "recommendation": "A few mild visual indicators were observed. Consider discussing these visible observations with a dental professional at your next visit.",
  "guidance": {
    "category_guidance": {
      "alignment": "Visible crowding or spacing was noted...",
      "discoloration": "Some areas appear visibly different in colour...",
      "tooth_wear": "No obvious visible flattening detected...",
      "gum_appearance": "Some visible gum changes were noted..."
    },
    "lifestyle_tips": [
      "Pay extra attention when brushing and flossing crowded teeth...",
      "Rinsing with water after consuming staining beverages..."
    ],
    "user_reported_notes": [
      "User-reported: You noted tooth sensitivity (mild)..."
    ]
  },
  "questionnaire": {
    "tooth_sensitivity": "mild",
    "pain_discomfort": "none",
    "gum_bleeding": "flossing",
    "teeth_or_gum_changes": "slight",
    "last_dental_visit": "6_to_12_months",
    "specific_concern": "Check front alignment"
  },
  "disclaimer": "This is a preliminary visual screening and not a dental diagnosis. It cannot replace an examination by a qualified dental professional."
}
```

**Response `422 Unprocessable Entity` (Retake Required)**:
```json
{
  "status": "retake_required",
  "retake": [
    {
      "view": "right",
      "reason": "Image remains too blurry after automatic enhancement. Please hold the camera steady and retake the right-side image."
    }
  ],
  "message": "One or more images could not be made technically usable. Please retake the indicated views."
}
```

---

## 5. Longitudinal Screening History

### `GET /api/screenings`
Returns chronological list of stored screening summaries.

**Response `200 OK`**:
```json
[
  {
    "screening_id": "scr_9cf34ab0",
    "date": "2026-09-18",
    "created_at": "2026-09-18T06:18:26.089218+00:00",
    "score": 82,
    "score_label": "Preliminary Visual Screening Score"
  },
  {
    "screening_id": "scr_baseline_prior",
    "date": "2026-03-15",
    "created_at": "2026-03-15T10:30:00Z",
    "score": 76,
    "score_label": "Preliminary Visual Screening Score"
  }
]
```

### `GET /api/screenings/{screening_id}`
Returns complete stored screening record including findings, score breakdown, and linked questionnaire.

---

## 6. Longitudinal Comparison

### `POST /api/screenings/compare`
Compares two screenings and evaluates score delta and category transitions using non-diagnostic language.

**Request `application/json`**:
```json
{
  "previous_screening_id": "scr_baseline_prior",
  "current_screening_id": "scr_9cf34ab0"
}
```

**Response `200 OK`**:
```json
{
  "overall": {
    "previous_screening_id": "scr_baseline_prior",
    "current_screening_id": "scr_9cf34ab0",
    "previous_date": "2026-03-15",
    "current_date": "2026-09-18",
    "previous_score": 76,
    "current_score": 82,
    "change": 6
  },
  "categories": {
    "alignment": {
      "previous": "mild",
      "current": "mild",
      "change": "No major visible change observed"
    },
    "discoloration": {
      "previous": "mild",
      "current": "mild",
      "change": "No major visible change observed"
    },
    "tooth_wear": {
      "previous": "none",
      "current": "none",
      "change": "No major visible change observed"
    },
    "gum_appearance": {
      "previous": "moderate",
      "current": "mild",
      "change": "Visible gum margins appear clearer with less redness than in the previous screening"
    }
  },
  "disclaimer": "Comparisons reflect photographic visual differences across submitted angles and lighting. They do not constitute a clinical progression assessment. Please consult a dentist for professional evaluation."
}
```

---

## 7. Dentist-Ready HTML Report

### `GET /api/screenings/{screening_id}/report`
Renders high-resolution, print-ready HTML designed for sharing with a dentist or generating PDF exports.

**Response `200 OK`**: `text/html`

---

## 8. Dental Providers & Referrals

### `GET /api/providers`
Lists verified dental clinics and practices available for appointment referrals.

### `POST /api/referrals`
Submits an appointment inquiry linking the screening report with a selected clinic.

**Request `application/json`**:
```json
{
  "screening_id": "scr_9cf34ab0",
  "provider_id": "prov_101",
  "patient_name": "Alex Morgan",
  "patient_email": "alex@example.com",
  "patient_phone": "(555) 123-4567",
  "preferred_time": "Morning",
  "notes": "Check lower anterior alignment and discoloration"
}
```

**Response `200 OK`**:
```json
{
  "inquiry_id": "inq_7f8a9b2c",
  "screening_id": "scr_9cf34ab0",
  "provider_id": "prov_101",
  "provider_name": "Beacon Dental Care & Preventive Clinic",
  "patient_name": "Alex Morgan",
  "patient_email": "alex@example.com",
  "status": "pending_provider_confirmation",
  "report_attached": true
}
```
