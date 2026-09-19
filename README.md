# 🦷 OralScreen Ai

### DSOLVE 2026 · DRISHTI . College of Engineering Trivandrum (CET)

> **BUILD. SOLVE. DEMONSTRATE.**

|                  |                                                          |
| ---------------- | -------------------------------------------------------- |
| **Problem**      | **Problem 1 — Oral Health Screening Widget**             |
| **Team Name**    | **ASTRAX**                                               |
| **Team Members** | Adithya K B · Aleesha K R · Ainjana Jomon · Akshya Anand |
| **Institution**  | Christ College of Engineering                            |
| **Live Demo**    | https://oral-ai-sigma.vercel.app/                        |
| **Source Code**  | https://github.com/akshyaanand-tech/Oral_Ai              |
| **Pitch Video**  | *https://lnkd.in/p/gME8P3AF*                                            |

---

## 📋 Table of Contents

* [Problem Statement](#-problem-statement)
* [Our Solution](#-our-solution)
* [How It Works](#-how-it-works)
* [Key Features](#-key-features)
* [Demo](#-demo)
* [Tech Stack](#-tech-stack)
* [Architecture](#-architecture)
* [Getting Started](#-getting-started)
* [Environment Variables](#-environment-variables)
* [Usage / Demo Script](#-usage--demo-script)
* [Limitations & Future Scope](#-limitations--future-scope)
* [Medical Disclaimer](#-medical-disclaimer)
* [Team](#-team)
* [Deployment](#-deployment)

---

# 🎯 Problem Statement

## Problem 1: Oral Health Screening Widget

Develop a free, two-minute oral health screening widget for web or smartphones that guides patients through a simple set of prompts and captures five quick images of their teeth.

The solution should analyse these images and generate an instant visual report highlighting potential oral health concerns such as crooked teeth, tooth wear, or discoloration. The goal is to provide patients with an easy, accessible way to get an initial visual assessment of their oral health and understand whether they may need to consult a dentist.

---

## Why This Matters

Many people do not regularly monitor their oral health and may only visit a dentist after symptoms become noticeable.

A first-level screening experience can help bridge this gap by giving users an accessible way to:

* Capture standardized images of their mouth.
* Identify potentially visible oral-health concerns.
* Understand their preliminary screening results.
* Receive practical next steps.
* Find nearby dental care when appropriate.

**OralScreen Ai** is designed as an accessible first step — not as a replacement for professional dental examination.

---

# 💡 Our Solution

**OralScreen Ai** is an AI-assisted oral health screening platform that guides a user through a structured five-image capture workflow and generates a preliminary visual screening report.

The platform combines:

1. A guided patient questionnaire.
2. Five standardized oral images.
3. Automated image quality assessment.
4. Image enhancement.
5. AI-assisted visual analysis.
6. A deterministic preliminary screening score.
7. Category-level findings.
8. A suggested care pathway.
9. Dental cost estimates in Indian Rupees.
10. Nearby dentist/provider discovery.
11. A dentist-ready screening report.

The goal is to transform a collection of ordinary smartphone/webcam images into an understandable, structured screening experience.

### Our core idea

> **Capture → Check → Analyse → Explain → Guide**

Instead of simply showing an AI prediction, OralScreen Ai creates a complete user journey from image capture to an understandable screening report and potential next step.

---

# 🔄 How It Works

```text
                 ORALSCREEN AI
                      │
                      ▼
             ┌─────────────────┐
             │  User Onboards  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  Questionnaire  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Capture 5 Views │
             └────────┬────────┘
                      │
                      ▼
          ┌────────────────────────┐
          │ Image Quality Checking │
          └────────────┬───────────┘
                       │
              ┌────────┴────────┐
              │                 │
          Poor Quality       Usable
              │                 │
              ▼                 ▼
          Retake /        Enhancement
          Guidance             │
                                ▼
                     ┌─────────────────┐
                     │ AI Visual       │
                     │ Analysis        │
                     └────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Preliminary      │
                    │ Visual Score     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Screening Report │
                    └────────┬─────────┘
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
             Findings    Care Path    Dentist Search
                 │           │           │
                 └───────────┴───────────┘
                             │
                             ▼
                    Patient Next Steps
```

---

# ✨ Key Features

## 1. 🧑‍💻 Guided Oral Screening

Users are guided through a structured screening workflow rather than being asked to upload arbitrary photographs.

The flow includes:

* Patient questionnaire
* Five oral image captures
* Image review
* Processing
* Results dashboard

---

## 2. 📸 Five-View Oral Capture

The application guides users through five standardized views:

1. **Front Teeth**
2. **Left Side**
3. **Right Side**
4. **Upper Arch**
5. **Lower Arch**

Users can capture images using:

* Device camera
* Webcam
* Image upload

The interface also provides image review before analysis.

---

## 3. 🔍 Image Quality Assessment

Before analysis, images go through quality checks.

The backend evaluates signals including:

* Image decodability
* Image dimensions
* Sharpness
* Illumination
* Contrast
* Overall usability

When an image is unsuitable, the application can provide guidance to capture another image rather than blindly processing a poor-quality input.

---

## 4. 🪄 Image Enhancement

The system uses deterministic image-processing techniques to improve the usability of captured images.

The enhancement pipeline can include:

* Contrast adjustment
* Gamma compensation
* Sharpening
* Edge enhancement
* Image normalization

The goal is to improve visual quality without generating artificial anatomical structures.

---

## 5. 🤖 AI-Assisted Visual Analysis

The screening pipeline analyses visible oral-health characteristics across the captured views.

The current analysis focuses on categories such as:

* Alignment & spacing
* Surface discoloration
* Tooth surface wear
* Gum appearance

The system produces structured findings with severity information and visual evidence where available.

---

## 6. 📊 Preliminary Visual Screening Score

The platform converts the screening findings into an interpretable preliminary visual score.

The score is designed to summarize the screening output rather than function as a medical diagnosis.

Results are presented alongside the underlying category findings so users are not given a score without context.

---

## 7. 📝 Patient Questionnaire

The screening includes self-reported information such as:

* Tooth sensitivity
* Pain or discomfort
* Gum bleeding
* Noticeable tooth/gum changes
* Last dental visit
* Primary concern

The questionnaire information is kept distinct from the visual analysis.

---

## 8. 🩺 Suggested Care Pathway

Based on the screening output and user-provided context, OralScreen Ai provides suggested next steps.

Examples include:

* Routine dental follow-up
* Timely dental evaluation
* Prompt professional evaluation
* Daily oral-hygiene actions
* Questions to discuss with a dentist

These suggestions are intended as guidance and not as medical prescriptions.

---

## 9. 💰 Dental Cost Estimates

The platform provides indicative cost ranges for selected dental services in **Indian Rupees (₹)**.

Examples include:

* Oral examination
* Professional cleaning
* Orthodontic evaluation
* Periodontal evaluation
* Scaling and root planing
* Diagnostic radiographs
* Night guards

These are indicative estimates and can vary significantly between clinics, locations, providers and individual cases.

---

## 10. 📍 Nearby Dentist Discovery

Users can search for dental providers based on location.

The provider workflow can support:

* Location search
* GPS-based discovery
* Nearby provider listings
* Distance information
* Provider selection
* Appointment inquiry

The purpose is to help users move from screening information toward professional care when appropriate.

---

## 11. 📄 Dentist-Ready Screening Report

The platform generates a structured report containing information such as:

* Preliminary screening score
* Visual findings
* Category breakdown
* Questionnaire responses
* Suggested care pathway
* Indicative cost information

The report can be viewed within the application and prepared for printing/saving.

---

## 12. 🔐 Authentication

The application includes:

* User registration
* Login
* Password hashing
* Session/authentication handling
* User-specific screening context

Authentication is handled by the FastAPI backend.

---

# Demo

## Live Application

👉 **https://oral-ai-sigma.vercel.app/**

## Suggested Demo Flow

```text
Landing Page
     ↓
Registration / Login
     ↓
Patient Questionnaire
     ↓
Five Oral Images
     ↓
Image Quality Check
     ↓
Image Review
     ↓
AI Processing
     ↓
Screening Results
     ↓
Care Guidance
     ↓
Dentist Discovery
     ↓
Screening Report
```

### Pitch Video

> **Pitch video:** *Add the final >30-second English pitch video link here.*

---

# 🧰 Tech Stack

| Layer            | Technology               | Purpose                                |
| ---------------- | ------------------------ | -------------------------------------- |
| Frontend         | React                    | Interactive patient-facing application |
| Frontend Tooling | Vite                     | Development and production build       |
| Styling          | CSS                      | Responsive application interface       |
| Backend          | FastAPI                  | REST API and application backend       |
| Language         | Python                   | Backend processing and services        |
| AI               | Google Gemini            | AI-assisted visual analysis            |
| Image Processing | Pillow + NumPy           | Image validation and enhancement       |
| Database         | SQLite                   | User/application data                  |
| Authentication   | JWT + password hashing   | Authentication and authorization       |
| Location         | OpenStreetMap / Overpass | Provider discovery                     |
| Frontend Hosting | Vercel                   | Production frontend deployment         |
| Backend Hosting  | Render                   | Production API deployment              |

---

# 🏗️ Architecture

```text
┌──────────────────────────────┐
│          USER                │
│     Browser / Smartphone    │
└──────────────┬───────────────┘
               │
               │ HTTPS
               ▼
┌──────────────────────────────┐
│          VERCEL              │
│     React + Vite Frontend    │
│                              │
│ • Questionnaire              │
│ • Camera Capture             │
│ • Image Review               │
│ • Processing UI              │
│ • Results Dashboard          │
│ • Dentist Search             │
└──────────────┬───────────────┘
               │
               │ REST API
               ▼
┌──────────────────────────────┐
│           RENDER             │
│        FastAPI Backend       │
│                              │
│ • Authentication             │
│ • Quality Check              │
│ • Image Enhancement          │
│ • Screening Pipeline         │
│ • AI Analysis                │
│ • Scoring                    │
│ • Care Pathway               │
│ • Provider Search            │
│ • Report Generation          │
└───────┬──────────┬───────────┘
        │          │
        │          │
        ▼          ▼
┌────────────┐  ┌────────────────┐
│   SQLite   │  │  Gemini API    │
│   Storage  │  │ AI Analysis    │
└────────────┘  └────────────────┘
                       │
                       ▼
                Structured Findings
                       │
                       ▼
                Results Dashboard
```

---

# 📁 Repository Structure

```text
Oral_Ai/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── data/
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
├── PRD.md
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure the following are installed:

* Git
* Node.js
* npm
* Python 3.11+ recommended
* A Google Gemini API key for live AI analysis

---

## 1. Clone the Repository

```bash
git clone https://github.com/akshyaanand-tech/Oral_Ai.git
cd Oral_Ai
```

---

# 🖥️ Frontend Setup

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a frontend environment file:

```text
.env
```

Add:

```env
VITE_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🐍 Backend Setup

Open another terminal and move into the backend:

```bash
cd backend
```

Create a virtual environment:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create:

```text
backend/.env
```

Use the provided environment template as a reference:

```text
backend/.env.example
```

Then start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 🔐 Environment Variables

## Backend

The exact variables should be configured using `backend/.env.example`.

Typical production configuration includes:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
MOCK_AI=false
ALLOWED_ORIGINS=https://oral-ai-sigma.vercel.app
```

## Frontend

```env
VITE_API_URL=http://localhost:8000
```

For production:

```env
VITE_API_URL=https://your-render-backend-url
```

### ⚠️ Security

**Never commit real API keys or secrets.**

Do not commit:

```text
.env
```

Only commit:

```text
.env.example
```

---

# 🎬 Usage / Demo Script

The following flow is designed for a 3–5 minute hackathon demonstration.

## 1. Introduce the Problem

Start on the OralScreen Ai landing page.

Explain:

> Oral health problems can go unnoticed until symptoms become significant. OralScreen Ai provides a quick, accessible first-level visual screening experience using five guided oral images.

---

## 2. Start Screening

Open the screening flow.

Show the user questionnaire.

Briefly explain that the application collects both:

* Visual information
* Self-reported patient context

---

## 3. Capture Five Images

Demonstrate the five guided views:

```text
1. Front
2. Left
3. Right
4. Upper
5. Lower
```

Explain that standardized views help create more consistent screening inputs.

---

## 4. Demonstrate Image Quality

Show the quality-check stage.

Explain that the system checks whether the captured image is sufficiently usable before continuing.

This reduces the risk of producing results from unusable photographs.

---

## 5. AI Analysis

Start the analysis.

Explain:

> The backend processes the images and uses AI-assisted visual analysis to identify visible characteristics across several oral-health categories.

---

## 6. Show Results

Open the Results Dashboard.

Highlight:

* Preliminary visual score
* Category findings
* Severity information
* Visual evidence
* Patient-reported information
* Suggested next steps

---

## 7. Show Care Pathway

Explain that the application converts the screening output into understandable next steps.

The system can indicate whether the user should consider:

* Routine follow-up
* Timely evaluation
* Prompt professional evaluation

---

## 8. Show Dentist Discovery

Open the provider/dentist search.

Demonstrate location-based discovery and provider selection.

Explain:

> The goal is to reduce the gap between identifying a potential concern and finding an appropriate dental care option.

---

## 9. Show the Report

Open the screening report.

Highlight the structured information that can be shared with or discussed with a dental professional.

---

## 10. Closing

End with:

> OralScreen Ai does not replace a dentist. It makes the first step toward understanding and acting on oral-health concerns easier, faster and more accessible.

---

# ⚠️ Limitations & Future Scope

## Known Limitations

### 1. Visual Screening Is Not Diagnosis

The system works from photographs and user-provided information.

It cannot perform:

* Physical examination
* Dental probing
* Radiographic examination
* Clinical diagnosis
* Definitive treatment planning

---

### 2. Image Quality Affects Results

Poor lighting, blur, obstruction or incomplete views can affect visual analysis.

The application therefore includes image-quality validation and retake guidance.

---

### 3. AI Analysis Has Uncertainty

AI-generated visual observations can be imperfect.

Results should be treated as preliminary screening information rather than definitive clinical conclusions.

---

### 4. Cost Estimates Are Indicative

Dental treatment costs vary based on:

* Location
* Clinic
* Dentist
* Treatment complexity
* Materials
* Individual patient requirements

The displayed amounts should therefore be considered indicative ranges rather than quotations.

---

### 5. Provider Availability

Nearby provider information depends on the underlying location/provider data sources and may not represent every dental practice in an area.

---

# 🔮 Future Scope

## 1. Clinical Validation

Work with dental professionals and validated datasets to evaluate screening performance across diverse populations and real-world image conditions.

---

## 2. Expanded Oral-Health Categories

Future versions could investigate additional visible characteristics while maintaining strict clinical safety boundaries.

---

## 3. Longitudinal Monitoring

Allow users to perform screenings periodically and compare changes over time.

```text
Screening 1
     ↓
Screening 2
     ↓
Screening 3
     ↓
Visual Trend
```

This could help users monitor changes and encourage appropriate professional follow-up.

---

## 4. Dentist Integration

Future versions could provide deeper integration with dental practices for:

* Appointment scheduling
* Secure report sharing
* Referral workflows
* Patient follow-up
* Practice-side dashboards

---

## 5. Multilingual Accessibility

Expand the application to support regional Indian languages and voice-guided screening to improve accessibility.

---

## 6. Improved Mobile Experience

A dedicated mobile application could provide:

* Better camera controls
* Guided positioning
* Offline capture
* Push reminders
* Longitudinal monitoring

---

## 7. Privacy-Preserving AI

Future versions could investigate additional privacy-preserving architectures for handling sensitive oral-health imagery.

---

# 🩺 Medical Disclaimer

> **OralScreen Ai is a preliminary visual screening and monitoring tool. It does not provide a dental diagnosis, clinical prognosis, or medical advice.**
>
> The results generated by the application are based on user-provided information and visual image analysis and may be inaccurate or incomplete.
>
> OralScreen Ai does not replace examination, diagnosis or treatment by a qualified dental professional.
>
> Users should consult a qualified dentist or healthcare professional for persistent symptoms, pain, bleeding, swelling, visible changes, or any other health concern.

---

# ☁️ Deployment

## Frontend

The production frontend is deployed using **Vercel**.

```text
React + Vite
     ↓
Vercel
     ↓
https://oral-ai-sigma.vercel.app/
```

## Backend

The production backend is deployed using **Render**.

```text
FastAPI
   ↓
Render
   ↓
Production REST API
```

## AI

The backend communicates with the configured AI service for visual analysis.

Secrets and API keys are maintained through deployment environment variables rather than committed to the repository.

---

# 👥 Team

## ASTRAX

**Christ College of Engineering**

| Name              | Role               | GitHub                                                     | Email                                                                   |
| ----------------- | ------------------ | ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Adithya K B**   | Backend Developer  | [@adithyakb](https://github.com/adithyakb)       | [adithyabijeev@gmail.com](mailto:adithyabijeev@gmail.com)                       |
| **Aleesha K R**   | Frontend Developer | [@aleesharaphycodes](https://github.com/aleesharaphycodes) | [aleesharaphy.tech@gmail.com](mailto:aleesharaphy.tech@gmail.com)       |
| **Ainjana Jomon** | Frontend Developer | [@ainjana](https://github.com/ainjana)                   | [ainjanaj@gmail.com](mailto:ainjanaj@gmail.com)                 |
| **Akshya Anand**  | Backend Developer  | [@akshyaanand-tech](https://github.com/akshyaanand-tech)   | [akshyaanand.official@gmail.com](mailto:akshyaanand.official@gmail.com) |

---

# 🔗 Project Links

### Live Demo

**https://oral-ai-sigma.vercel.app/**

### GitHub Repository

**https://github.com/akshyaanand-tech/Oral_Ai**

### Backend API

**Render deployment:** **https://oralscreen-ai-backend.onrender.com**

### Pitch Video

**Pitch video:** *https://lnkd.in/p/gME8P3AF*

---

# ❤️ Built for DSOLVE 2026

**Team ASTRAX**
**Christ College of Engineering**

### OralScreen Ai

> **Capture. Check. Analyse. Understand. Act.**

---
