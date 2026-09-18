import React, { useState } from 'react';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  ArrowLeft,
  X,
} from 'lucide-react';
import { loginUser, forgotPassword } from '../services/api';

export default function Login({ onLoginSuccess, onNavigateRegister, onBack }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Forgot password modal state
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotMsg, setForgotMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !password) {
      setError('Please enter both your email address and password.');
      return;
    }

    if (!cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setError('Please enter a valid email address.');
      return;
    }

    setLoading(true);
    try {
      const res = await loginUser(cleanEmail, password);
      setSuccess('Sign in successful! Connecting your clinical profile...');
      setTimeout(() => {
        onLoginSuccess(res.user, res.token);
      }, 500);
    } catch (err) {
      setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotSubmit = async (e) => {
    e.preventDefault();
    setForgotMsg('');
    if (!forgotEmail.trim() || !forgotEmail.includes('@')) {
      setForgotMsg('Please enter a valid email address.');
      return;
    }
    setForgotLoading(true);
    try {
      const res = await forgotPassword(forgotEmail.trim());
      setForgotMsg(res.message || 'Password reset instructions have been dispatched.');
    } catch (err) {
      setForgotMsg('Password reset instructions have been dispatched.');
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card-container">
        <div className="auth-glow-accent"></div>

        {onBack && (
          <button type="button" onClick={onBack} className="auth-back-btn">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Screening</span>
          </button>
        )}

        {/* Brand Header */}
        <div className="auth-header">
          <div className="auth-badge-icon">
            <Sparkles className="w-6 h-6 text-cyan-400" />
          </div>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">
            Sign in to access your OralScreen AI screening portal
          </p>
        </div>

        {/* Switchable Auth Mode Tabs */}
        <div className="auth-nav-tabs">
          <button type="button" className="auth-nav-tab active">
            Sign In
          </button>
          <button
            type="button"
            className="auth-nav-tab"
            onClick={onNavigateRegister}
          >
            Create Account
          </button>
        </div>

        {/* Validation Banners */}
        {error && (
          <div className="auth-alert-error">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="auth-alert-success">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form-group">
            <label className="auth-label">Email Address</label>
            <div className="auth-input-container">
              <span className="auth-input-icon">
                <Mail className="w-4 h-4" />
              </span>
              <input
                type="email"
                required
                className="auth-input-field"
                placeholder="patient@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
          </div>

          <div className="auth-form-group">
            <div className="auth-label-row">
              <label className="auth-label">Password</label>
              <button
                type="button"
                onClick={() => setShowForgotModal(true)}
                className="auth-link-forgot"
              >
                Forgot Password?
              </button>
            </div>
            <div className="auth-input-container">
              <span className="auth-input-icon">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showPassword ? 'text' : 'password'}
                required
                className="auth-input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="auth-input-toggle"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="auth-btn-submit"
          >
            {loading ? (
              <span>Signing In...</span>
            ) : (
              <>
                <span>Sign In to Account</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account yet?
          <button
            type="button"
            onClick={onNavigateRegister}
            className="auth-footer-btn"
          >
            Sign Up here
          </button>
        </div>

        {/* Security Trust Note */}
        <div className="auth-trust-badges">
          <div className="auth-trust-item">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>NIST-Compliant PBKDF2 Password Hashing</span>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="evidence-modal-backdrop" onClick={() => setShowForgotModal(false)}>
          <div
            className="evidence-modal-card"
            style={{ maxWidth: '420px' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="evidence-modal-header">
              <h3 className="evidence-modal-title">Reset Your Password</h3>
              <button className="btn-icon-close" onClick={() => setShowForgotModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>

            <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.5rem' }}>
              Enter your registered email address and we will dispatch password recovery instructions.
            </p>

            <form onSubmit={handleForgotSubmit} className="auth-form" style={{ marginTop: '1.25rem' }}>
              <div className="auth-form-group">
                <label className="auth-label">Email Address</label>
                <div className="auth-input-container">
                  <span className="auth-input-icon">
                    <Mail className="w-4 h-4" />
                  </span>
                  <input
                    type="email"
                    required
                    className="auth-input-field"
                    placeholder="name@example.com"
                    value={forgotEmail}
                    onChange={(e) => setForgotEmail(e.target.value)}
                  />
                </div>
              </div>

              {forgotMsg && (
                <div className="auth-alert-success" style={{ margin: '0.5rem 0' }}>
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span>{forgotMsg}</span>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setShowForgotModal(false)}
                  className="btn-secondary-sm"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="btn-primary-sm"
                >
                  {forgotLoading ? 'Sending...' : 'Send Recovery Link'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
