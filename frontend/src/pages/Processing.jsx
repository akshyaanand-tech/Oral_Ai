import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, Sparkles, ShieldCheck } from 'lucide-react';

const STEPS = [
  'Images received',
  'Images optimized (adaptive deblurring & contrast balancing)',
  'Image quality checked (multi-signal sharpness validation)',
  'Visual analysis (cautious non-diagnostic screening)',
  'Generating screening score (deterministic 0–100 indicator)',
  'Preparing your report (dentist-ready summary & guidance)',
];

export default function Processing() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="processing-page">
      <div className="processing-card">
        {/* Animated Scanner Graphic */}
        <div className="scanner-graphic-box">
          <div className="radar-circle">
            <div className="radar-sweep"></div>
            <div className="radar-center-icon">
              <Sparkles className="w-10 h-10 text-emerald-400 animate-pulse" />
            </div>
          </div>
        </div>

        <h2 className="processing-title">Preparing your screening...</h2>
        <p className="processing-subtitle">
          Executing image enhancement, two-stage technical quality check, and AI visual screening across all 5 views.
        </p>

        {/* Steps List */}
        <div className="processing-steps-list">
          {STEPS.map((step, idx) => {
            const isCompleted = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`processing-step-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
              >
                <div className="step-status-icon">
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
                  ) : (
                    <div className="step-pending-dot"></div>
                  )}
                </div>
                <span className="step-status-text">
                  {isCompleted ? `✓ ${step}` : step}
                </span>
              </div>
            );
          })}
        </div>

        {/* Safe non-diagnostic reminder */}
        <div className="processing-safety-badge">
          <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>Preliminary visual screening only • Not a medical diagnosis</span>
        </div>
      </div>
    </div>
  );
}
