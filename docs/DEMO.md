# OralAI — Hackathon Presentation & Demo Script

This script outlines an engaging 2-minute live demonstration flow showcasing the complete preventive oral care journey:
**SCAN → ENHANCE → QUALITY CHECK → ANALYSE → SCORE → UNDERSTAND → TRACK → REPORT → CONNECT**.

---

## 1. Setup & Verification

Ensure both backend and frontend are active:

```bash
# Terminal 1 - Backend (port 8000)
cd backend
python -m uvicorn app.main:app --port 8000 --reload

# Terminal 2 - Frontend (port 5173)
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 2. Walkthrough Sequence

### Step 1: Landing Page (15 seconds)
- **Key Talking Point**: *"OralAI is not just an image classifier. It's a complete preventive oral health screening and longitudinal monitoring workflow that bridges patient awareness with professional dental care."*
- Highlight the **9-step care pathway banner**: *SCAN → ENHANCE → QUALITY CHECK → ANALYSE → SCORE → UNDERSTAND → TRACK → REPORT → CONNECT*.
- Point out the feature pills: ~2 Minutes, 5 Guided Views, Auto-Enhancement, Longitudinal History, Dentist Referral.
- Click **"Start Screening"**.

### Step 2: Questionnaire (15 seconds)
- **Key Talking Point**: *"Before capture, the user completes a brief 6-question triage survey covering sensitivity, pain, bleeding, changes, last visit, and personal concerns."*
- Select:
  - Sensitivity: *Mild sensitivity occasionally*
  - Pain: *None*
  - Gum bleeding: *Minor bleeding occasionally when flossing*
  - Changes: *Slight changes*
  - Last visit: *6 to 12 months ago*
  - Specific concern: *"Check lower anterior crowding and slight surface staining"*
- Emphasize: *"Questionnaire responses are stored as clinical context and kept strictly independent from computer vision scoring."*
- Click **"Proceed to Guided Camera"**.

### Step 3: Guided Capture & Automatic Image Enhancement (30 seconds)
- Walk through the 5 steps: **Front**, **Left**, **Right**, **Upper Arch**, **Lower Arch**.
- Demonstrate **Automatic Image Enhancement**:
  - On Step 1 (Front View), click **"Blurry Test Photo"**.
  - Show the notification: *"✓ Image quality improved automatically. Image optimized for analysis."*
  - Toggle between **"✓ Enhanced View"** and **"Original"** to demonstrate how local contrast and sharpness were recovered without hallucinating artificial dental features.
  - Click **"Next (LEFT VIEW)"**.
- For remaining views (Left, Right, Upper, Lower), click **"Sample Photo"** and proceed.
- On the Review screen, click **"Submit for AI Screening"**.

### Step 4: Animated Processing Screen (10 seconds)
- Watch the 6 transparent pipeline stages execute:
  1. *✓ Images received*
  2. *✓ Images optimized (adaptive deblurring & contrast balancing)*
  3. *✓ Image quality checked (multi-signal sharpness validation)*
  4. *✓ Visual analysis (cautious non-diagnostic screening)*
  5. *✓ Generating screening score (deterministic 0–100 indicator)*
  6. *✓ Preparing your report (dentist-ready summary & guidance)*

### Step 5: Results Dashboard & Evidence (20 seconds)
- **Preliminary Visual Screening Score**: Show **82 / 100** with the green dial.
- **Category Finding Cards**:
  - Alignment: Mild crowding.
  - Discoloration: Mild surface staining.
  - Tooth Wear: None observed.
  - Gum Appearance: Mild redness.
- Click **"View Visual Region (front view)"** under Alignment to open the interactive **Evidence Modal**, displaying the normalized bounding box over the lower incisors.
- Show the **Transparent Score Calculation Breakdown** table (Starting 100, itemized deductions).
- Show the **Personalized Preventive Guidance** section with daily wellness tips and labeled questionnaire context.

### Step 6: Longitudinal History & Comparison (15 seconds)
- Scroll to **"Longitudinal Screening History"**.
- Point out the timeline with past screenings (e.g. baseline from 6 months prior).
- Select the prior screening and click **"Compare Screenings"**.
- Show the **Comparison Modal**:
  - Prior Score: 76 vs Current Score: 82 (Delta: **+6**).
  - Category transitions with cautious non-diagnostic language (*"Visible gum margins appear clearer with less redness than in the previous screening"*).

### Step 7: Dentist-Ready Report & Referral (15 seconds)
- Click **"Dentist Report"** to show the print-friendly clinical summary export.
- Click **"Connect with a Dentist"**:
  - Show the local dental clinic directory (e.g., *Beacon Dental Care*).
  - Enter patient contact details and click **"Send Screening to Clinic"**.
  - Show the confirmed inquiry ID linking the patient to professional in-person care.
- Conclude: *"OralAI turns standard smartphone photos into actionable preventive awareness, tracks changes over time, and connects patients directly into the dental care pathway."*
