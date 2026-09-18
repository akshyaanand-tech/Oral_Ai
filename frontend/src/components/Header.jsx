import React from 'react';
import { Sparkles, RefreshCw, User, LogOut, LogIn, UserPlus } from 'lucide-react';

export default function Header({
  onReset,
  currentStep,
  backendStatus,
  currentUser,
  onNavigateLogin,
  onNavigateRegister,
  onLogout,
}) {
  const getInitials = (name) => {
    if (!name) return 'PT';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

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

        <div className="header-right flex items-center gap-3">
          <div className="status-indicator hidden sm:flex" title={backendStatus?.status === 'ok' ? 'Backend Online' : 'Checking Backend'}>
            <span className={`status-dot ${backendStatus?.status === 'ok' ? 'online' : 'checking'}`}></span>
            <span className="status-text">
              {backendStatus?.status === 'ok'
                ? (backendStatus.mock_ai ? 'API: Ready (Mock AI)' : 'API: Ready (Gemini Vision)')
                : 'API: Connecting...'}
            </span>
          </div>

          {/* Authentication Controls */}
          {currentUser ? (
            <div className="header-user-badge">
              <div className="header-user-avatar">
                {getInitials(currentUser.name)}
              </div>
              <span className="header-user-name" title={currentUser.email}>
                {currentUser.name}
              </span>
              <button
                type="button"
                onClick={onLogout}
                className="header-btn-logout"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="header-auth-group">
              <button
                type="button"
                onClick={onNavigateLogin}
                className="header-btn-login"
                title="Sign In to your account"
              >
                <LogIn className="w-3.5 h-3.5 text-cyan-400" />
                <span>Sign In</span>
              </button>
              <button
                type="button"
                onClick={onNavigateRegister}
                className="header-btn-register"
                title="Create a new account"
              >
                <UserPlus className="w-3.5 h-3.5" />
                <span>Sign Up</span>
              </button>
            </div>
          )}

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
