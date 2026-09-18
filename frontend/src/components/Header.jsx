import React from 'react';
import { Sparkles, ShieldAlert, RefreshCw } from 'lucide-react';

export default function Header({ onReset, currentStep, backendStatus }) {
  return (
    <header className="site-header">
      <div className="header-container">
        <div className="brand" onClick={onReset} role="button" tabIndex={0}>
          <div className="brand-icon">
            <Sparkles className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <span className="brand-title">OralScreen AI</span>
            <span className="brand-badge">PREVENTIVE MVP</span>
          </div>
        </div>

        <div className="header-right">
          <div className="status-indicator" title={backendStatus?.status === 'ok' ? 'Backend Online' : 'Checking Backend'}>
            <span className={`status-dot ${backendStatus?.status === 'ok' ? 'online' : 'checking'}`}></span>
            <span className="status-text">
              {backendStatus?.status === 'ok'
                ? (backendStatus.mock_ai ? 'API: Ready (Mock AI)' : 'API: Ready (Gemini Vision)')
                : 'API: Connecting...'}
            </span>
          </div>

          {currentStep !== 'landing' && (
            <button className="btn-ghost-sm" onClick={onReset} title="Start Over">
              <RefreshCw className="w-4 h-4" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
