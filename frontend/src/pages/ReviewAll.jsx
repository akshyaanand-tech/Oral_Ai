import React from 'react';
import { CheckCircle2, AlertCircle, RefreshCw, ArrowRight, ArrowLeft, Sparkles } from 'lucide-react';
import MedicalDisclaimer from '../components/MedicalDisclaimer';

const VIEWS_INFO = [
  { id: 'front', label: 'Front View' },
  { id: 'left', label: 'Left View' },
  { id: 'right', label: 'Right View' },
  { id: 'upper', label: 'Upper Arch' },
  { id: 'lower', label: 'Lower Arch' },
];

export default function ReviewAll({ images, onRetakeView, onSubmit, onBack, onFillMissingWithDemo }) {
  const missingViews = VIEWS_INFO.filter((v) => !images[v.id]);
  const allCaptured = missingViews.length === 0;

  return (
    <div className="review-page">
      <div className="review-card">
        <div className="review-header">
          <div>
            <div className="badge-step">FINAL REVIEW</div>
            <h2 className="review-title">Review Captured Dental Views</h2>
          </div>
        </div>

        <p className="review-sub">
          Check each angle before starting the AI analysis. All 5 views are evaluated together for a comprehensive visual screening.
        </p>

        {/* 5-Images Grid */}
        <div className="review-images-grid">
          {VIEWS_INFO.map((v, idx) => {
            const blob = images[v.id];
            const url = blob ? URL.createObjectURL(blob) : null;

            return (
              <div key={v.id} className="review-item-card">
                <div className="review-item-header">
                  <span className="review-item-index">{idx + 1}</span>
                  <span className="review-item-name">{v.label}</span>
                </div>

                <div className="review-thumb-box">
                  {url ? (
                    <img src={url} alt={v.label} className="review-thumb-img" />
                  ) : (
                    <div className="review-thumb-empty">
                      <AlertCircle className="w-8 h-8 text-amber-400 mb-1" />
                      <span>Not Captured</span>
                    </div>
                  )}
                </div>

                <div className="review-item-footer">
                  <button
                    className="btn-retake-link"
                    onClick={() => onRetakeView(idx)}
                    type="button"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>{blob ? 'Retake' : 'Capture Now'}</span>
                  </button>
                  {blob && (
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        className="btn-enhance-mini"
                        onClick={() => onRetakeView(idx)}
                        title="Review and enhance sharpness/contrast with AI"
                      >
                        <Sparkles className="w-3 h-3 text-cyan-400" />
                        <span>Enhance</span>
                      </button>
                      <span className="tag-ready">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 inline mr-1" />
                        Ready
                      </span>
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>

        {/* Status notice */}
        {!allCaptured ? (
          <div className="warning-box">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <div>
              <strong>Missing Views: </strong>
              <span>
                Please go back and capture the remaining views ({missingViews.map((m) => m.label).join(', ')}) before submitting.
              </span>
            </div>
          </div>
        ) : (
          <div className="ready-box">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <div>
              <strong>All 5 Views Ready: </strong>
              <span>Images are verified and ready for AI vision analysis.</span>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="review-actions-row">
          <button className="btn-secondary" onClick={onBack}>
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Camera</span>
          </button>

          <button
            className="btn-primary"
            onClick={onSubmit}
            disabled={!allCaptured}
            id="submit-screening-btn"
          >
            <Sparkles className="w-4 h-4 text-emerald-300" />
            <span>Submit for AI Visual Screening</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mt-6">
        <MedicalDisclaimer compact={true} />
      </div>
    </div>
  );
}
