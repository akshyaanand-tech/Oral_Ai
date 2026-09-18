import React from 'react';
import {
  Camera,
  Clock,
  Sparkles,
  ChevronRight,
  Eye,
  BarChart3,
  IndianRupee,
  Building2,
  FileCheck2,
} from 'lucide-react';
import MedicalDisclaimer from '../components/MedicalDisclaimer';

export default function Landing({ onStart, onQuickDemo, currentUser }) {
  const workflowSteps = [
    { num: '01', title: 'SCAN', desc: '5 guided smartphone views' },
    { num: '02', title: 'ENHANCE', desc: 'Automatic deblurring & contrast' },
    { num: '03', title: 'QUALITY CHECK', desc: 'Multi-signal clarity validation' },
    { num: '04', title: 'ANALYSE', desc: 'Cautious Gemini vision screening' },
    { num: '05', title: 'SCORE', desc: 'Deterministic 0–100 indicator' },
    { num: '06', title: 'UNDERSTAND', desc: 'Educational screening explanation' },
    { num: '07', title: 'ESTIMATE', desc: 'Procedure cost ranges (₹)' },
    { num: '08', title: 'REPORT', desc: 'Dentist-ready clinical summary' },
    { num: '09', title: 'CONNECT', desc: 'Smart dental clinic referral' },
  ];

  const views = [
    { id: 'front', label: 'Front View', desc: 'Direct front bite alignment' },
    { id: 'left', label: 'Left View', desc: 'Left cheek & premolar/molar bite' },
    { id: 'right', label: 'Right View', desc: 'Right cheek & premolar/molar bite' },
    { id: 'upper', label: 'Upper Arch', desc: 'Tilted back, upper occlusal surfaces' },
    { id: 'lower', label: 'Lower Arch', desc: 'Tilted down, lower arch chewing edges' },
  ];

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        {currentUser && (
          <div className="landing-welcome-banner">
            <div className="welcome-user-info">
              <div className="welcome-avatar">
                {currentUser.name ? currentUser.name.slice(0, 2).toUpperCase() : 'PT'}
              </div>
              <div style={{ textAlign: 'left' }}>
                <div className="welcome-greeting">
                  Welcome back, <span className="welcome-name">{currentUser.name}</span>!
                </div>
                <div className="welcome-meta">
                  Patient Account: {currentUser.email} • Profile Active
                </div>
              </div>
            </div>
            <div className="welcome-status-pill">
              <span className="user-status-dot"></span> Active Patient Session
            </div>
          </div>
        )}

        <div className="hero-badge">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>Preventive Oral Health Screening & Care Guidance</span>
        </div>

        <h1 className="hero-title">
          OralAI — Preventive <span className="gradient-text">Oral Health Screening</span>
        </h1>

        <p className="hero-subtitle">
          An accessible visual oral health screening tool powered by vision AI, automatic image enhancement,
          and deterministic scoring. Receive indicative cost estimates (₹), generate a dentist-ready summary, and connect
          with professional dental care.
        </p>

        {/* Feature Pills */}
        <div className="feature-pills">
          <div className="feature-pill">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>~2 Minutes</span>
          </div>
          <div className="feature-pill">
            <Camera className="w-4 h-4 text-emerald-400" />
            <span>5 Guided Views</span>
          </div>
          <div className="feature-pill">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Auto-Enhancement</span>
          </div>
          <div className="feature-pill">
            <BarChart3 className="w-4 h-4 text-violet-400" />
            <span>0–100 Screening Score</span>
          </div>
          <div className="feature-pill">
            <IndianRupee className="w-4 h-4 text-sky-400" />
            <span>Cost Estimates (₹)</span>
          </div>
          <div className="feature-pill">
            <Building2 className="w-4 h-4 text-rose-400" />
            <span>Dentist Referral</span>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="hero-actions">
          <button className="btn-primary" onClick={onStart} id="start-screening-btn">
            <span>Start Real Screening</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* End-to-End Care Pathway Section */}
      <section className="workflow-pipeline-section my-8">
        <div className="section-header text-center">
          <h2 className="section-title">The Complete Preventive Care Workflow</h2>
          <p className="section-subtitle">
            More than photo prediction: an integrated journey from smart capture to professional dental care.
          </p>
        </div>

        <div className="workflow-steps-grid">
          {workflowSteps.map((s) => (
            <div key={s.num} className="workflow-step-card">
              <span className="workflow-step-num">{s.num}</span>
              <h4 className="workflow-step-title">{s.title}</h4>
              <p className="workflow-step-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 5 Views Preview Grid */}
      <section className="views-section">
        <div className="section-header">
          <h2 className="section-title">5 Guided Dental Views</h2>
          <p className="section-subtitle">
            Our interactive camera guide assists you in capturing each specific angle with automatic sharpness and lighting validation.
          </p>
        </div>

        <div className="views-grid">
          {views.map((v, i) => (
            <div key={v.id} className="view-card">
              <div className="view-step-number">{i + 1}</div>
              <div className="view-card-body">
                <h3 className="view-card-title">{v.label}</h3>
                <p className="view-card-desc">{v.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4 Screening Categories */}
      <section className="categories-section">
        <div className="section-header">
          <h2 className="section-title">What We Visually Inspect</h2>
          <p className="section-subtitle">
            The AI analyzes strictly visible optical features across 4 defined categories without diagnosing disease:
          </p>
        </div>

        <div className="categories-grid">
          <div className="category-pill-card">
            <div className="cat-icon cat-align">📐</div>
            <div>
              <h4>Alignment & Spacing</h4>
              <p>Observes visible crowding, spacing, or tooth rotation.</p>
            </div>
          </div>

          <div className="category-pill-card">
            <div className="cat-icon cat-disco">✨</div>
            <div>
              <h4>Surface Discoloration</h4>
              <p>Identifies visible surface staining or unusual color variation.</p>
            </div>
          </div>

          <div className="category-pill-card">
            <div className="cat-icon cat-wear">🛡️</div>
            <div>
              <h4>Tooth Surface Wear</h4>
              <p>Observes visible surface flattening or wear patterns on biting edges.</p>
            </div>
          </div>

          <div className="category-pill-card">
            <div className="cat-icon cat-gum">🩺</div>
            <div>
              <h4>Gum Appearance</h4>
              <p>Notes visible redness, margins, or swelling without diagnosing gingivitis.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Medical Disclaimer Banner */}
      <section className="disclaimer-section">
        <MedicalDisclaimer />
      </section>
    </div>
  );
}
