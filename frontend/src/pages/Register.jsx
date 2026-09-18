import React, { useState } from 'react';
import {
  User,
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
} from 'lucide-react';
import { registerUser } from '../services/api';

export default function Register({ onRegisterSuccess, onNavigateLogin, onBack }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Live password strength
  const getPasswordStrength = (pass) => {
    if (!pass) return { score: 0, label: 'None', level: 'none' };
    let count = 0;
    if (pass.length >= 8) count += 1;
    if (/[A-Z]/.test(pass) && /[a-z]/.test(pass)) count += 1;
    if (/[0-9]/.test(pass)) count += 1;
    if (/[^A-Za-z0-9]/.test(pass)) count += 1;

    switch (count) {
      case 1:
        return { score: 25, label: 'Weak (needs numbers & symbols)', level: 'weak' };
      case 2:
        return { score: 50, label: 'Fair (add special character)', level: 'fair' };
      case 3:
        return { score: 75, label: 'Good (secure passphrase)', level: 'good' };
      case 4:
      default:
        return { score: 100, label: 'Strong (excellent protection)', level: 'strong' };
    }
  };

  const pwdStrength = getPasswordStrength(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const cleanName = name.trim();
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanName || !cleanEmail || !password || !confirmPassword) {
      setError('Please complete all required fields.');
      return;
    }

    if (!cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setError('Please enter a valid email address.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (!anyHasDigit(password) || !anyHasLetter(password)) {
      setError('Password must contain both letters and numbers.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please re-enter.');
      return;
    }

    setLoading(true);
    try {
      const res = await registerUser(cleanName, cleanEmail, password);
      setSuccess('Account created successfully! Connecting your profile...');
      setTimeout(() => {
        onRegisterSuccess(res.user, res.token);
      }, 500);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const anyHasDigit = (s) => /[0-9]/.test(s);
  const anyHasLetter = (s) => /[a-zA-Z]/.test(s);

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
            <Sparkles className="w-6 h-6 text-emerald-400" />
          </div>
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">
            Join OralScreen AI to save your screenings & access preventive oral care
          </p>
        </div>

        {/* Switchable Auth Mode Tabs */}
        <div className="auth-nav-tabs">
          <button
            type="button"
            className="auth-nav-tab"
            onClick={onNavigateLogin}
          >
            Sign In
          </button>
          <button type="button" className="auth-nav-tab active">
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
            <label className="auth-label">Full Name</label>
            <div className="auth-input-container">
              <span className="auth-input-icon">
                <User className="w-4 h-4" />
              </span>
              <input
                type="text"
                required
                className="auth-input-field"
                placeholder="Jane Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
              />
            </div>
          </div>

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
            <label className="auth-label">Password (min. 8 characters)</label>
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
                autoComplete="new-password"
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

            {/* Live Password Strength Meter */}
            {password && (
              <div className="auth-strength-container">
                <div className="auth-strength-bars">
                  <div className={`auth-strength-bar ${pwdStrength.score >= 25 ? `active-${pwdStrength.level}` : ''}`}></div>
                  <div className={`auth-strength-bar ${pwdStrength.score >= 50 ? `active-${pwdStrength.level}` : ''}`}></div>
                  <div className={`auth-strength-bar ${pwdStrength.score >= 75 ? `active-${pwdStrength.level}` : ''}`}></div>
                  <div className={`auth-strength-bar ${pwdStrength.score >= 100 ? `active-${pwdStrength.level}` : ''}`}></div>
                </div>
                <div className="auth-strength-meta">
                  <span>Strength</span>
                  <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{pwdStrength.label}</span>
                </div>
              </div>
            )}
          </div>

          <div className="auth-form-group">
            <label className="auth-label">Confirm Password</label>
            <div className="auth-input-container">
              <span className="auth-input-icon">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type={showPassword ? 'text' : 'password'}
                required
                className="auth-input-field"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="auth-btn-submit"
          >
            {loading ? (
              <span>Creating Account...</span>
            ) : (
              <>
                <span>Complete Patient Registration</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?
          <button
            type="button"
            onClick={onNavigateLogin}
            className="auth-footer-btn"
          >
            Sign In here
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
    </div>
  );
}
