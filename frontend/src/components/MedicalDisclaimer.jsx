import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export default function MedicalDisclaimer({ compact = false }) {
  if (compact) {
    return (
      <div className="disclaimer-compact">
        <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span>
          <strong>Preliminary Visual Screening Only:</strong> This tool does not provide a dental diagnosis or medical advice.
        </span>
      </div>
    );
  }

  return (
    <div className="disclaimer-card">
      <div className="disclaimer-icon-wrap">
        <AlertTriangle className="w-6 h-6 text-amber-400" />
      </div>
      <div className="disclaimer-content">
        <h4 className="disclaimer-title">Important Medical & Regulatory Notice</h4>
        <p className="disclaimer-text">
          This application is a <strong>preliminary visual screening and awareness tool</strong> and does <strong>NOT</strong> constitute a dental or medical diagnosis. It cannot detect conditions not visible to a camera and cannot replace an in-person examination, professional cleaning, or x-rays performed by a licensed dental professional.
        </p>
        <p className="disclaimer-sub">
          If you are experiencing tooth pain, bleeding, swelling, or persistent discomfort, please consult a qualified dentist promptly.
        </p>
      </div>
    </div>
  );
}
