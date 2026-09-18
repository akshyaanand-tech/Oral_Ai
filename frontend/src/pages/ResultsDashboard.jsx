import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ShieldCheck,
  Printer,
  RotateCcw,
  CheckCircle2,
  HelpCircle,
  Eye,
  ChevronDown,
  ChevronUp,
  FileText,
  Calendar,
  X,
  ExternalLink,
  MapPin,
  Phone,
  Send,
  Building2,
  Clock,
  ArrowRight,
  UserCheck,
  IndianRupee,
  Stethoscope,
  ListChecks,
  Search,
  Navigation,
  Loader2,
  AlertTriangle,
  AlertCircle,
} from 'lucide-react';
import MedicalDisclaimer from '../components/MedicalDisclaimer';
import {
  fetchProviders,
  submitReferral,
  getReportHtmlUrl,
} from '../services/api';

export default function ResultsDashboard({ report, images, questionnaire, onRestart, currentUser }) {
  const [evidenceModal, setEvidenceModal] = useState(null);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  // Dentist referral states
  const [showReferralModal, setShowReferralModal] = useState(false);
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [patientName, setPatientName] = useState(currentUser?.name || '');
  const [patientEmail, setPatientEmail] = useState(currentUser?.email || '');
  const [patientPhone, setPatientPhone] = useState('');
  const [referralSuccess, setReferralSuccess] = useState(null);
  const [isSubmittingReferral, setIsSubmittingReferral] = useState(false);

  // Auto-sync patient details when currentUser changes
  useEffect(() => {
    if (currentUser?.name && !patientName) setPatientName(currentUser.name);
    if (currentUser?.email && !patientEmail) setPatientEmail(currentUser.email);
  }, [currentUser]);

  // Location-Aware Dentist Search State
  const initialLoc = questionnaire?.location && questionnaire.location.toLowerCase() !== 'boston' ? questionnaire.location : '';
  const [dentistLocationInput, setDentistLocationInput] = useState(initialLoc);
  const [activeLocationLabel, setActiveLocationLabel] = useState(initialLoc);
  const [isSearchingDentists, setIsSearchingDentists] = useState(false);
  const [dentistSearchError, setDentistSearchError] = useState('');
  const [hasSearchedDentists, setHasSearchedDentists] = useState(false);
  const [locationPermissionDenied, setLocationPermissionDenied] = useState(false);

  const {
    screening_score,
    score: rawScore = 82,
    score_label = 'Preliminary Visual Screening Score',
    findings: rawFindings = {},
    score_breakdown = {},
    score_details = {},
    recommendation = '',
    care_pathway = [],
    estimated_costs = [],
    explanation = '',
    providers: reportProviders = [],
    screening_id = 'scr_demo',
    created_at = new Date().toISOString(),
  } = report || {};

  const score = screening_score ?? rawScore;
  const findings = Array.isArray(rawFindings)
    ? rawFindings.reduce((acc, f) => ({ ...acc, [f.category]: f }), {})
    : rawFindings || {};
  const deductions = score_details?.category_deductions || score_breakdown || {};

  // Search dentists by GPS coordinates (Option A)
  const handleUseCurrentLocation = () => {
    setDentistSearchError('');
    setLocationPermissionDenied(false);

    if (!navigator.geolocation) {
      setDentistSearchError('Geolocation is not supported by your browser. Please enter your location manually.');
      return;
    }

    setIsSearchingDentists(true);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setActiveLocationLabel(`Current Location (${latitude.toFixed(3)}°, ${longitude.toFixed(3)}°)`);
        setDentistLocationInput('');
        setHasSearchedDentists(true);
        try {
          const list = await fetchProviders({ latitude, longitude, limit: 6 });
          setProviders(list || []);
          if (list && list.length > 0) {
            setSelectedProvider(list[0]);
          } else {
            setSelectedProvider(null);
          }
        } catch (err) {
          setDentistSearchError("We couldn't find dentists for this location. Please try another location.");
          setProviders([]);
          setSelectedProvider(null);
        } finally {
          setIsSearchingDentists(false);
        }
      },
      (err) => {
        setIsSearchingDentists(false);
        if (err.code === 1) { // PERMISSION_DENIED
          setLocationPermissionDenied(true);
          setDentistSearchError('Allow location access to find dentists near you. Or enter your city manually.');
        } else if (err.code === 2) { // POSITION_UNAVAILABLE
          setDentistSearchError('Location is currently unavailable. Please enter your city manually.');
        } else if (err.code === 3) { // TIMEOUT
          setDentistSearchError('Location request timed out. Please try again or enter your location manually.');
        } else {
          setDentistSearchError('Could not retrieve location. Please enter your location manually.');
        }
      },
      { timeout: 12000, enableHighAccuracy: true }
    );
  };

  // Search dentists by manual text (Option B)
  const handleManualLocationSearch = async (e) => {
    if (e) e.preventDefault();
    const query = dentistLocationInput.trim();
    if (!query) {
      setDentistSearchError('Please enter a location or city name.');
      return;
    }

    setDentistSearchError('');
    setLocationPermissionDenied(false);
    setIsSearchingDentists(true);
    setActiveLocationLabel(query);
    setHasSearchedDentists(true);

    try {
      const list = await fetchProviders({ location: query, limit: 6 });
      setProviders(list || []);
      if (list && list.length > 0) {
        setSelectedProvider(list[0]);
      } else {
        setSelectedProvider(null);
      }
    } catch (err) {
      setDentistSearchError("We couldn't find dentists for this location. Please try another location.");
      setProviders([]);
      setSelectedProvider(null);
    } finally {
      setIsSearchingDentists(false);
    }
  };

  // Fetch providers for questionnaire location or report providers
  useEffect(() => {
    // If questionnaire specified a location (and not just default), look up real clinics for that location
    if (initialLoc) {
      setIsSearchingDentists(true);
      fetchProviders({ location: initialLoc, limit: 6 })
        .then((res) => {
          setProviders(res || []);
          if (res && res.length > 0) setSelectedProvider(res[0]);
          setHasSearchedDentists(true);
        })
        .catch(() => {
          setProviders([]);
        })
        .finally(() => {
          setIsSearchingDentists(false);
        });
    } else if (reportProviders && reportProviders.length > 0) {
      setProviders(reportProviders);
      setSelectedProvider(reportProviders[0]);
    }
  }, [screening_id]);

  const getScoreTheme = (val) => {
    if (val >= 80)
      return {
        color: '#10b981',
        text: 'Low Visible Concerns',
        desc: 'Minimal visible optical indicators detected.',
      };
    if (val >= 65)
      return {
        color: '#06b6d4',
        text: 'Mild Visible Observations',
        desc: 'A few mild visible indicators observed.',
      };
    if (val >= 45)
      return {
        color: '#f59e0b',
        text: 'Moderate Visible Observations',
        desc: 'Several visible observations noted.',
      };
    return {
      color: '#ef4444',
      text: 'Multiple Visible Observations',
      desc: 'Multiple noticeable observations flagged across views.',
    };
  };

  const scoreTheme = getScoreTheme(score);

  const getSeverityBadge = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'none':
        return <span className="badge-severity badge-none">None Observed</span>;
      case 'mild':
        return <span className="badge-severity badge-mild">Mild Indicator</span>;
      case 'moderate':
        return <span className="badge-severity badge-moderate">Moderate Indicator</span>;
      case 'marked':
        return <span className="badge-severity badge-marked">Marked Observation</span>;
      case 'uncertain':
      default:
        return <span className="badge-severity badge-uncertain">Uncertain / Insufficient View</span>;
    }
  };

  const categories = [
    { key: 'alignment', title: 'Alignment & Spacing', icon: '📐', data: findings.alignment },
    { key: 'discoloration', title: 'Surface Discoloration', icon: '✨', data: findings.discoloration },
    { key: 'tooth_wear', title: 'Tooth Surface Wear', icon: '🛡️', data: findings.tooth_wear },
    { key: 'gum_appearance', title: 'Gum Appearance', icon: '🩺', data: findings.gum_appearance },
  ];

  const handleOpenEvidence = (title, evidence) => {
    if (!evidence) return;
    setEvidenceModal({
      title,
      imageKey: evidence.image,
      region: evidence.region,
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleOpenHtmlReport = () => {
    setShowReportModal(true);
  };

  const handleOpenNewWindow = () => {
    const url = getReportHtmlUrl(screening_id);
    window.open(url, '_blank');
  };

  // Submit referral inquiry
  const handleSendReferral = async (e) => {
    e.preventDefault();
    if (!selectedProvider || !patientName || !patientEmail) {
      alert('Please provide your name and email to send the referral request.');
      return;
    }
    setIsSubmittingReferral(true);
    try {
      const res = await submitReferral({
        screening_id,
        provider_id: selectedProvider.id,
        patient_name: patientName,
        patient_email: patientEmail,
        patient_phone: patientPhone,
        notes: questionnaire?.specific_concern || '',
      });
      setReferralSuccess(res);
    } catch (err) {
      console.error('Referral submission error:', err);
      alert('Referral submission failed: ' + err.message);
    } finally {
      setIsSubmittingReferral(false);
    }
  };

  return (
    <div className="results-page">
      {/* Printable Header */}
      <div className="print-only print-header">
        <h1>OralScreen AI — Preliminary Visual Screening Summary</h1>
        <p>
          Screening ID: {screening_id} • Date: {new Date(created_at).toLocaleDateString()}
          {currentUser?.name && ` • Patient: ${currentUser.name}`}
        </p>
        <p className="print-notice">NOT A DIAGNOSIS • FOR PREVENTIVE AWARENESS ONLY</p>
      </div>

      {/* Patient Welcome Header */}
      {currentUser && (
        <div className="patient-dashboard-welcome no-print">
          <div className="welcome-user-info">
            <div className="welcome-avatar">
              {currentUser.name ? currentUser.name.slice(0, 2).toUpperCase() : 'PT'}
            </div>
            <div>
              <div className="welcome-greeting">
                Welcome, <span className="welcome-name">{currentUser.name}</span>!
              </div>
              <div className="welcome-meta">
                Patient Account: {currentUser.email} • Screening ID: {screening_id}
              </div>
            </div>
          </div>
          <div className="welcome-status-pill">
            <span className="user-status-dot"></span> Clinical Screening Saved
          </div>
        </div>
      )}

      {/* Main Score Hero Card */}
      <div className="score-hero-card">
        <div className="score-hero-top">
          <div>
            <span className="badge-id">SCREENING ID: {screening_id}</span>
            {currentUser?.name && (
              <div style={{ fontSize: '0.85rem', color: '#38bdf8', fontWeight: 700, margin: '0.2rem 0' }}>
                Screening for: {currentUser.name}
              </div>
            )}
            <h1 className="score-label-title">{score_label}</h1>
            <p className="score-summary-subtitle">{scoreTheme.desc}</p>
          </div>

          <div className="score-actions-top no-print">
            <button
              className="btn-secondary-sm"
              onClick={handleOpenHtmlReport}
              title="Open Dentist-Ready HTML Report"
            >
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Dentist Report</span>
            </button>
            <button className="btn-secondary-sm" onClick={handlePrint} title="Print or Save PDF">
              <Printer className="w-4 h-4" />
              <span>Print / PDF</span>
            </button>
            <button className="btn-primary-sm" onClick={onRestart}>
              <RotateCcw className="w-4 h-4" />
              <span>New Screening</span>
            </button>
          </div>
        </div>

        {/* Circular Score Dial */}
        <div className="score-dial-wrap">
          <div className="score-circle-outer" style={{ borderColor: scoreTheme.color }}>
            <div className="score-number-display">
              <span className="score-number-val">{score}</span>
              <span className="score-max-val">/ 100</span>
            </div>
          </div>
          <div
            className="score-tier-badge"
            style={{
              backgroundColor: `${scoreTheme.color}22`,
              color: scoreTheme.color,
              borderColor: scoreTheme.color,
            }}
          >
            <Sparkles className="w-4 h-4 mr-1 inline" />
            {scoreTheme.text}
          </div>
        </div>
      </div>

      {/* Category Finding Cards */}
      <div className="findings-section">
        <div className="section-header-row">
          <div>
            <h2 className="section-title">Visual Findings by Category</h2>
            <p className="section-subtitle">
              Based strictly on visible optical characteristics across your 5 photographs.
            </p>
          </div>
        </div>

        <div className="findings-cards-grid">
          {categories.map((cat) => {
            const item = cat.data || {};
            const hasEvidence = !!item.evidence && !!item.evidence.region;

            return (
              <div key={cat.key} className="finding-card">
                <div className="finding-card-header">
                  <div className="finding-title-group">
                    <span className="finding-cat-icon">{cat.icon}</span>
                    <h3 className="finding-cat-title">{cat.title}</h3>
                  </div>
                  {getSeverityBadge(item.severity)}
                </div>

                <p className="finding-observation-text">
                  {item.finding || 'No obvious visible concern observed.'}
                </p>

                {/* Confidence Bar */}
                <div className="confidence-row">
                  <div className="confidence-label">
                    <span>Observation Confidence</span>
                    <span className="confidence-pct">
                      {item.confidence ? `${Math.round(item.confidence * 100)}%` : '75%'}
                    </span>
                  </div>
                  <div className="confidence-track">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${item.confidence ? Math.round(item.confidence * 100) : 75}%`,
                      }}
                    ></div>
                  </div>
                </div>

                {/* Evidence Link */}
                <div className="finding-footer">
                  {hasEvidence ? (
                    <button
                      className="btn-evidence-view no-print"
                      onClick={() => handleOpenEvidence(cat.title, item.evidence)}
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>View Visual Region ({item.evidence.image} view)</span>
                    </button>
                  ) : (
                    <span className="evidence-diffuse-note">General / Non-localized observation</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Transparent Score Calculation Breakdown Table */}
      <div className="score-breakdown-card">
        <h3 className="breakdown-title">Transparent Score Calculation Breakdown</h3>
        <p className="breakdown-sub">
          The preliminary visual indicator begins at 100 points. Transparent deductions are
          deterministically subtracted according to visible severity levels.
        </p>

        <div className="breakdown-table-wrap">
          <table className="breakdown-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Observed Severity</th>
                <th className="text-right">Deduction</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-medium">Starting Reference Score</td>
                <td>Baseline</td>
                <td className="text-right text-emerald-400 font-semibold">+100</td>
              </tr>
              <tr>
                <td>Alignment & Spacing</td>
                <td>{findings.alignment?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {deductions.alignment > 0 ? `-${deductions.alignment}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Surface Discoloration</td>
                <td>{findings.discoloration?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {deductions.discoloration > 0 ? `-${deductions.discoloration}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Tooth Surface Wear</td>
                <td>{findings.tooth_wear?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {deductions.tooth_wear > 0 ? `-${deductions.tooth_wear}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Gum Appearance</td>
                <td>{findings.gum_appearance?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {deductions.gum_appearance > 0 ? `-${deductions.gum_appearance}` : '0'}
                </td>
              </tr>
              <tr className="total-row">
                <td colSpan="2" className="font-bold">
                  Final Preliminary Visual Screening Score
                </td>
                <td className="text-right font-bold text-white text-lg">{score} / 100</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Educational Explanation Layer */}
      {explanation && (
        <div className="score-breakdown-card border border-cyan-500/30 bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-950/20">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="breakdown-title text-cyan-300">Educational Screening Explanation</h3>
          </div>
          <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-line space-y-3">
            {explanation}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-400">
            <span>Non-diagnostic educational guidance generated to clarify visual indicators.</span>
            <span className="text-cyan-400 font-medium">Screening Score: {score}/100</span>
          </div>
        </div>
      )}

      {/* Suggested Care Pathway Section */}
      {care_pathway && care_pathway.length > 0 && (
        <div className="score-breakdown-card">
          <div className="flex items-center gap-2 mb-2">
            <ListChecks className="w-5 h-5 text-emerald-400" />
            <h3 className="breakdown-title">Suggested Care Pathway</h3>
          </div>
          <p className="breakdown-sub mb-4">
            Rule-based professional care steps derived from your visual indicators. Connects visible observations with appropriate dental specialties.
          </p>

          <div className="space-y-4">
            {care_pathway.map((step, idx) => (
              <div key={step.step_id || idx} className="p-4 rounded-lg bg-slate-800/80 border border-slate-700/70 hover:border-slate-600 transition-colors">
                <div className="flex items-start justify-between flex-wrap gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </span>
                    <h4 className="font-semibold text-white text-base">{step.title}</h4>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <Stethoscope className="w-3 h-3" />
                      {step.recommended_specialist}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
                      {step.urgency}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-slate-300 mb-3 ml-8">
                  {step.action}
                </p>

                {step.home_care && step.home_care.length > 0 && (
                  <div className="ml-8 pt-2 border-t border-slate-700/50">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Suggested Home Care Focus:</span>
                    <ul className="mt-1 text-xs text-slate-300 space-y-1 list-disc pl-4">
                      {step.home_care.map((tip, tIdx) => (
                        <li key={tIdx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Indicative Dental Cost Estimations */}
      {estimated_costs && estimated_costs.length > 0 && (
        <div className="score-breakdown-card">
          <div className="flex items-center gap-2 mb-2">
            <IndianRupee className="w-5 h-5 text-amber-400" />
            <h3 className="breakdown-title">Indicative Dental Cost Estimates (₹ INR)</h3>
          </div>
          <p className="breakdown-sub mb-4">
            Estimated fee ranges for care pathway procedures in Indian Rupees (₹) based on standard dental fee surveys. Displayed as indicative ranges, not guaranteed prices.
          </p>

          <div className="breakdown-table-wrap">
            <table className="breakdown-table">
              <thead>
                <tr>
                  <th>Procedure / Service</th>
                  <th>Clinical Category</th>
                  <th className="text-right">Indicative Range (₹)</th>
                </tr>
              </thead>
              <tbody>
                {estimated_costs.map((c, idx) => (
                  <tr key={idx}>
                    <td>
                      <div className="font-medium text-white">{c.service}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{c.notes}</div>
                    </td>
                    <td className="capitalize text-slate-300 text-xs">
                      {c.category ? c.category.replace('_', ' ') : 'General'}
                    </td>
                    <td className="text-right font-semibold text-emerald-400 whitespace-nowrap">
                      {c.cost_range}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-3 p-2.5 rounded bg-slate-800/60 border border-slate-700/50 text-xs text-slate-400">
            <strong>Note:</strong> Cost estimates are purely indicative ranges in Indian Rupees (₹). Actual costs depend on the specific dental clinic, clinical diagnostic findings, and individual patient coverage.
          </div>
        </div>
      )}

      {/* Smart Dentist Referral Section */}
      <div className="referral-banner-card no-print">
        <div className="flex items-start md:items-center justify-between flex-col md:flex-row gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-lg font-bold text-white">Want Professional Evaluation?</h3>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Connect this preliminary screening report directly with a qualified dental provider
              for an in-person clinical examination, x-rays, or preventive cleaning.
            </p>
            {activeLocationLabel && providers.length > 0 && (
              <p className="text-xs text-cyan-300 mt-2 flex items-center gap-1.5 font-medium">
                <MapPin className="w-3.5 h-3.5" />
                <span>
                  Found {providers.length} {providers.length === 1 ? 'dentist' : 'dentists'} near{' '}
                  <strong>{activeLocationLabel}</strong> (closest: {providers[0].name} — {providers[0].distance})
                </span>
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              className="btn-primary btn-referral-cta"
              onClick={() => setShowReferralModal(true)}
            >
              <UserCheck className="w-4 h-4" />
              <span>Connect with a Dentist</span>
            </button>
            <button className="btn-secondary" onClick={handleOpenHtmlReport}>
              <FileText className="w-4 h-4" />
              <span>Prepare Report for Dentist</span>
            </button>
          </div>
        </div>
      </div>

      {/* Questionnaire Summary Accordion */}
      {questionnaire && (
        <div className="questionnaire-summary-card">
          <button
            className="accordion-header-btn no-print"
            onClick={() => setShowQuestionnaire(!showQuestionnaire)}
            type="button"
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span className="font-medium">Self-Reported Questionnaire Context (6 Questions)</span>
            </div>
            {showQuestionnaire ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {(showQuestionnaire || true) && (
            <div className={`accordion-body ${showQuestionnaire ? 'open' : 'closed-on-screen'}`}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                <div className="q-summary-item">
                  <span className="q-label">1. Tooth Sensitivity:</span>
                  <span className="q-val capitalize">
                    {questionnaire.tooth_sensitivity || 'None'}
                  </span>
                </div>
                <div className="q-summary-item">
                  <span className="q-label">2. Pain or Discomfort:</span>
                  <span className="q-val capitalize">
                    {questionnaire.pain_discomfort || 'None'}
                  </span>
                </div>
                <div className="q-summary-item">
                  <span className="q-label">3. Gum Bleeding:</span>
                  <span className="q-val capitalize">
                    {questionnaire.gum_bleeding || 'None'}
                  </span>
                </div>
                <div className="q-summary-item">
                  <span className="q-label">4. Teeth or Gum Changes:</span>
                  <span className="q-val capitalize">
                    {questionnaire.teeth_or_gum_changes || 'None'}
                  </span>
                </div>
                <div className="q-summary-item">
                  <span className="q-label">5. Last Dental Checkup:</span>
                  <span className="q-val capitalize">
                    {questionnaire.last_dental_visit?.replace(/_/g, ' ') || '6 to 12 months'}
                  </span>
                </div>
                <div className="q-summary-item">
                  <span className="q-label">6. Specific Concern:</span>
                  <span className="q-val">
                    {questionnaire.specific_concern || 'None specified'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Medical Disclaimer Banner */}
      <div className="mt-6">
        <MedicalDisclaimer />
      </div>

      {/* Visual Evidence Modal */}
      {evidenceModal && (
        <div className="evidence-modal-backdrop" onClick={() => setEvidenceModal(null)}>
          <div className="evidence-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="evidence-modal-header">
              <h3 className="evidence-modal-title">Visual Evidence Region: {evidenceModal.title}</h3>
              <button className="btn-icon-close" onClick={() => setEvidenceModal(null)}>
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="evidence-modal-desc">
              Highlighted visible observation on the <strong>{evidenceModal.imageKey}</strong> view:
            </p>

            <div className="evidence-image-container">
              {images[evidenceModal.imageKey] ? (
                <div className="evidence-relative-wrap">
                  <img
                    src={URL.createObjectURL(images[evidenceModal.imageKey])}
                    alt="Evidence View"
                    className="evidence-base-img"
                  />
                  {evidenceModal.region && (
                    <div
                      className="evidence-bounding-box"
                      style={{
                        left: `${evidenceModal.region.x * 100}%`,
                        top: `${evidenceModal.region.y * 100}%`,
                        width: `${evidenceModal.region.width * 100}%`,
                        height: `${evidenceModal.region.height * 100}%`,
                      }}
                    >
                      <span className="evidence-box-label">{evidenceModal.title}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400">Image not available in memory.</div>
              )}
            </div>

            <div className="evidence-modal-footer">
              <span className="text-xs text-slate-400">
                Normalized Coordinates: x={evidenceModal.region?.x.toFixed(2)}, y=
                {evidenceModal.region?.y.toFixed(2)}, w={evidenceModal.region?.width.toFixed(2)}, h=
                {evidenceModal.region?.height.toFixed(2)}
              </span>
              <button className="btn-secondary-sm" onClick={() => setEvidenceModal(null)}>
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dentist Referral / Provider Connection Modal */}
      {showReferralModal && (
        <div className="evidence-modal-backdrop" onClick={() => setShowReferralModal(false)}>
          <div
            className="referral-modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="referral-modal-header">
              <div className="referral-modal-title">
                <Building2 className="w-5 h-5 text-emerald-400" />
                <span>Find & Connect with a Dental Care Provider</span>
              </div>
              <button className="btn-icon-close" onClick={() => setShowReferralModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>

            {referralSuccess ? (
              <div className="p-8 text-center space-y-4">
                <CheckCircle2 className="w-14 h-14 text-emerald-400 mx-auto" />
                <h4 className="text-xl font-bold text-white">Inquiry Sent Successfully!</h4>
                <p className="text-sm text-slate-300 max-w-md mx-auto">
                  Your screening report (ID: <strong>{referralSuccess.inquiry_id}</strong>) has been routed to{' '}
                  <strong className="text-emerald-300">{referralSuccess.provider_name}</strong>.
                </p>
                <div className="p-4 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-slate-300 max-w-md mx-auto text-left">
                  The dental clinic has received your preliminary visual findings and will contact you at{' '}
                  <strong className="text-cyan-300">{referralSuccess.patient_email}</strong> to confirm appointment availability.
                </div>
                <button
                  className="btn-primary mt-4 mx-auto px-6 py-2"
                  onClick={() => {
                    setShowReferralModal(false);
                    setReferralSuccess(null);
                  }}
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleSendReferral} className="flex flex-col flex-1 overflow-hidden">
                <div className="referral-modal-body">
                  <div className="referral-grid-layout">
                    {/* Left Column: Location Search & Clinics List */}
                    <div className="referral-col-left">
                      <div className="referral-location-box">
                        <div className="flex items-center justify-between flex-wrap gap-2">
                          <span className="referral-section-heading">
                            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                            Search Dentists Near You
                          </span>
                          <button
                            type="button"
                            className="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-medium border border-cyan-500/40 transition-colors flex items-center gap-1.5 cursor-pointer"
                            onClick={handleUseCurrentLocation}
                            disabled={isSearchingDentists}
                          >
                            <Navigation className="w-3.5 h-3.5" />
                            <span>{isSearchingDentists ? 'Detecting...' : 'Use My GPS'}</span>
                          </button>
                        </div>

                        {/* Search Input */}
                        <div className="flex items-center gap-2">
                          <div className="relative flex-1">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                            <input
                              type="text"
                              className="w-full bg-slate-800 border border-slate-700 rounded-md pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
                              placeholder="City or PIN code (e.g. Bengaluru, Kochi, 560001)"
                              value={dentistLocationInput}
                              onChange={(e) => setDentistLocationInput(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleManualLocationSearch(e);
                                }
                              }}
                            />
                          </div>
                          <button
                            type="button"
                            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md text-xs font-medium transition-colors cursor-pointer"
                            onClick={handleManualLocationSearch}
                            disabled={isSearchingDentists || !dentistLocationInput.trim()}
                          >
                            Search
                          </button>
                        </div>

                        {/* Quick Test Cities */}
                        <div className="flex items-center gap-1.5 flex-wrap text-xs text-slate-400">
                          <span className="text-[11px] text-slate-500">Quick:</span>
                          {['Bengaluru', 'Kochi', 'Thiruvananthapuram'].map((city) => (
                            <button
                              key={city}
                              type="button"
                              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300 border border-slate-700 transition-colors cursor-pointer"
                              onClick={() => {
                                setDentistLocationInput(city);
                                setDentistSearchError('');
                                setLocationPermissionDenied(false);
                                setIsSearchingDentists(true);
                                setActiveLocationLabel(city);
                                setHasSearchedDentists(true);
                                fetchProviders({ location: city, limit: 6 })
                                  .then((list) => {
                                    setProviders(list || []);
                                    setSelectedProvider(list && list.length > 0 ? list[0] : null);
                                  })
                                  .catch(() => {
                                    setDentistSearchError("We couldn't find dentists for this location. Please try another location.");
                                    setProviders([]);
                                    setSelectedProvider(null);
                                  })
                                  .finally(() => {
                                    setIsSearchingDentists(false);
                                  });
                              }}
                            >
                              {city}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Status / Errors */}
                      {isSearchingDentists && (
                        <div className="p-3 bg-cyan-950/40 border border-cyan-500/30 rounded-lg flex items-center justify-center gap-2 text-cyan-300 text-xs">
                          <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                          <span>Locating dental clinics...</span>
                        </div>
                      )}

                      {locationPermissionDenied && (
                        <div className="p-3 bg-amber-500/15 border border-amber-500/40 rounded-lg text-xs text-amber-200 flex items-start gap-2">
                          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                          <div>
                            <strong>Location Denied:</strong> Allow browser location permission or enter your city manually above.
                          </div>
                        </div>
                      )}

                      {dentistSearchError && !locationPermissionDenied && (
                        <div className="p-3 bg-red-500/15 border border-red-500/40 rounded-lg text-xs text-red-200 flex items-start gap-2">
                          <AlertCircle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
                          <span>{dentistSearchError}</span>
                        </div>
                      )}

                      {hasSearchedDentists && !isSearchingDentists && providers.length === 0 && !dentistSearchError && (
                        <div className="p-4 bg-slate-800/80 border border-slate-700 rounded-lg text-center text-xs text-slate-300">
                          No dental clinics found for <strong>{activeLocationLabel || 'your search'}</strong>. Try entering a larger nearby city.
                        </div>
                      )}

                      {/* Providers List */}
                      {providers.length > 0 && (
                        <div className="flex flex-col gap-1.5">
                          <div className="flex items-center justify-between">
                            <span className="referral-section-heading">
                              Available Clinics {activeLocationLabel ? `(${activeLocationLabel})` : ''} ({providers.length})
                            </span>
                            <span className="text-[11px] text-cyan-400 font-medium">Click a clinic to select</span>
                          </div>

                          <div className="referral-providers-scroll">
                            {providers.map((p) => {
                              const isSelected = selectedProvider?.id === p.id;
                              return (
                                <div
                                  key={p.id}
                                  className={`provider-card ${isSelected ? 'selected' : ''}`}
                                  onClick={() => setSelectedProvider(p)}
                                >
                                  <div className="flex justify-between items-start gap-2">
                                    <div className="flex-1 min-w-0">
                                      <div className="font-semibold text-sm text-white truncate">{p.name}</div>
                                      <div className="text-xs text-slate-400 truncate">{p.doctor || 'Clinical Team'} • {p.specialty || 'General Dentistry'}</div>
                                    </div>
                                    <div className="flex items-center gap-1.5 shrink-0">
                                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 whitespace-nowrap">
                                        {p.distance || 'Near you'}
                                      </span>
                                      <span className="text-xs font-bold text-emerald-400">★ {p.rating || '4.8'}</span>
                                    </div>
                                  </div>
                                  <div className="flex items-center justify-between flex-wrap gap-2 text-xs text-slate-400 mt-2">
                                    <span className="truncate max-w-[280px]"><MapPin className="w-3.5 h-3.5 inline mr-1 text-cyan-400 shrink-0" />{p.address}</span>
                                    <span className="shrink-0"><Clock className="w-3.5 h-3.5 inline mr-1 text-emerald-400 shrink-0" />{p.next_available || 'Appointments open'}</span>
                                  </div>
                                  {p.phone && p.phone !== 'Phone on file' && (
                                    <div className="text-[11px] text-slate-400 mt-1.5 flex items-center gap-1">
                                      <Phone className="w-3 h-3 text-slate-400" />
                                      <span>{p.phone}</span>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Right Column: Selected Clinic & Referral Form */}
                    <div className="referral-col-right">
                      {/* Selected Clinic Preview */}
                      <div className="referral-selected-summary">
                        <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4" />
                          Selected Dental Clinic
                        </span>
                        {selectedProvider ? (
                          <div className="mt-1">
                            <div className="font-bold text-base text-white">{selectedProvider.name}</div>
                            <div className="text-xs text-cyan-300 mt-0.5">{selectedProvider.doctor || 'Senior Dental Surgeon'} • {selectedProvider.specialty}</div>
                            <div className="text-xs text-slate-300 mt-1 flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                              <span className="truncate">{selectedProvider.address}</span>
                            </div>
                            {selectedProvider.phone && selectedProvider.phone !== 'Phone on file' && (
                              <div className="mt-2 pt-2 border-t border-emerald-500/20 flex items-center justify-between">
                                <span className="text-xs text-slate-400">Direct Line:</span>
                                <a
                                  href={`tel:${selectedProvider.phone}`}
                                  className="text-xs text-emerald-400 font-semibold hover:underline flex items-center gap-1"
                                >
                                  <Phone className="w-3 h-3" />
                                  {selectedProvider.phone}
                                </a>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-xs text-slate-400 italic py-2">
                            Please select a dental clinic from the list on the left to proceed.
                          </div>
                        )}
                      </div>

                      {/* Contact Form */}
                      <div className="referral-form-box">
                        <span className="referral-section-heading">Patient Contact Details</span>

                        <div>
                          <label className="text-xs font-semibold text-slate-300 block mb-1">
                            Full Name *
                          </label>
                          <input
                            type="text"
                            className="form-input-text"
                            required
                            placeholder="Your full name"
                            value={patientName}
                            onChange={(e) => setPatientName(e.target.value)}
                          />
                        </div>

                        <div>
                          <label className="text-xs font-semibold text-slate-300 block mb-1">
                            Email Address *
                          </label>
                          <input
                            type="email"
                            className="form-input-text"
                            required
                            placeholder="your.email@example.com"
                            value={patientEmail}
                            onChange={(e) => setPatientEmail(e.target.value)}
                          />
                        </div>

                        <div>
                          <label className="text-xs font-semibold text-slate-300 block mb-1">
                            Phone Number (Optional)
                          </label>
                          <input
                            type="tel"
                            className="form-input-text"
                            placeholder="+91 98765 43210"
                            value={patientPhone}
                            onChange={(e) => setPatientPhone(e.target.value)}
                          />
                        </div>

                        <div className="p-2.5 bg-slate-900/60 rounded border border-slate-700/60 text-[11px] text-slate-400">
                          🔒 <strong>Privacy Note:</strong> Your preliminary screening report (Score: {score}/100, ID: {screening_id}) will be shared directly with the clinic to facilitate your appointment.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Fixed Modal Footer */}
                <div className="referral-modal-footer">
                  <div className="text-xs text-slate-400">
                    {selectedProvider ? (
                      <span>Ready to refer to <strong className="text-white">{selectedProvider.name}</strong></span>
                    ) : (
                      <span className="text-amber-400">Select a clinic above to enable referral submission</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      className="btn-secondary-sm"
                      onClick={() => setShowReferralModal(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={isSubmittingReferral || !selectedProvider}
                    >
                      <Send className="w-4 h-4" />
                      <span>{isSubmittingReferral ? 'Sending...' : 'Send Screening to Clinic'}</span>
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Dentist-Ready Clinical Summary Report Modal */}
      {showReportModal && (
        <div className="evidence-modal-backdrop" onClick={() => setShowReportModal(false)}>
          <div className="report-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="report-modal-header">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                <h3 className="evidence-modal-title" style={{ margin: 0, color: '#fff' }}>
                  Dentist-Ready Clinical Summary Report
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="btn-secondary-sm flex items-center gap-1.5"
                  onClick={handlePrint}
                  title="Print Report or Save as PDF"
                >
                  <Printer className="w-4 h-4" />
                  <span>Print / PDF</span>
                </button>
                <button
                  type="button"
                  className="btn-secondary-sm flex items-center gap-1.5"
                  onClick={handleOpenNewWindow}
                  title="Open report in separate browser tab"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Open Full Page</span>
                </button>
                <button className="btn-icon-close" onClick={() => setShowReportModal(false)}>
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="report-modal-body">
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #0284c7', paddingBottom: '16px', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 800, color: '#0369a1' }}>
                    OralAI — Preventive Oral Health Screening Summary
                  </h2>
                  <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
                    Screening ID: <strong>{screening_id}</strong> • Date: {new Date(created_at).toLocaleDateString()}
                    {currentUser?.name && ` • Patient: ${currentUser.name}`}
                  </div>
                  <div style={{ fontSize: '12px', color: '#0284c7', fontWeight: 600, marginTop: '2px' }}>
                    5-View Guided Visual Screening Assessment
                  </div>
                </div>
                <div style={{ background: '#f0f9ff', border: '2px solid #0284c7', borderRadius: '8px', padding: '10px 18px', textAlign: 'center', minWidth: '90px' }}>
                  <div style={{ fontSize: '28px', fontWeight: 800, color: '#0284c7', lineHeight: 1 }}>{score}</div>
                  <div style={{ fontSize: '10px', fontWeight: 700, color: '#0369a1', textTransform: 'uppercase', marginTop: '4px' }}>
                    / 100 Score
                  </div>
                </div>
              </div>

              {/* Section 1: Visual Findings */}
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
                1. AI Visual Findings by Category
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px', fontSize: '13px' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>
                    <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '25%' }}>Category</th>
                    <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '45%' }}>Visible Observation</th>
                    <th style={{ padding: '8px 10px', textAlign: 'center', color: '#475569', width: '15%' }}>Severity</th>
                    <th style={{ padding: '8px 10px', textAlign: 'center', color: '#475569', width: '15%' }}>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map((cat) => {
                    const sev = cat.data?.severity || 'none';
                    return (
                      <tr key={cat.key} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '8px 10px', fontWeight: 600, color: '#1e293b' }}>{cat.title}</td>
                        <td style={{ padding: '8px 10px', color: '#334155' }}>{cat.data?.finding || 'No notable indicators'}</td>
                        <td style={{ padding: '8px 10px', textAlign: 'center' }}>
                          <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600, textTransform: 'capitalize', background: sev === 'none' ? '#dcfce7' : '#fef3c7', color: sev === 'none' ? '#15803d' : '#b45309' }}>
                            {sev}
                          </span>
                        </td>
                        <td style={{ padding: '8px 10px', textAlign: 'center', color: '#64748b' }}>
                          {Math.round((cat.data?.confidence || 0.85) * 100)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {/* Section 2: Care Pathway */}
              {care_pathway && care_pathway.length > 0 && (
                <>
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
                    2. Suggested Care Pathway
                  </div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>
                        <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '30%' }}>Step</th>
                        <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '22%' }}>Specialist</th>
                        <th style={{ padding: '8px 10px', textAlign: 'center', color: '#475569', width: '18%' }}>Urgency</th>
                        <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '30%' }}>Recommended Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {care_pathway.map((step, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '8px 10px', fontWeight: 600, color: '#1e293b' }}>{step.title}</td>
                          <td style={{ padding: '8px 10px', color: '#0284c7', fontWeight: 600 }}>{step.recommended_specialist}</td>
                          <td style={{ padding: '8px 10px', textAlign: 'center' }}>
                            <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600, background: '#fef3c7', color: '#92400e' }}>
                              {step.urgency}
                            </span>
                          </td>
                          <td style={{ padding: '8px 10px', color: '#334155' }}>{step.action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}

              {/* Section 3: Cost Estimates */}
              {estimated_costs && estimated_costs.length > 0 && (
                <>
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
                    3. Indicative Dental Cost Estimates (₹ INR)
                  </div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>
                        <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '45%' }}>Procedure / Service</th>
                        <th style={{ padding: '8px 10px', textAlign: 'left', color: '#475569', width: '25%' }}>Category</th>
                        <th style={{ padding: '8px 10px', textAlign: 'right', color: '#475569', width: '30%' }}>Indicative Range (₹)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {estimated_costs.map((c, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '8px 10px', fontWeight: 600, color: '#1e293b' }}>{c.service}</td>
                          <td style={{ padding: '8px 10px', color: '#64748b', textTransform: 'capitalize' }}>{(c.category || '').replace('_', ' ')}</td>
                          <td style={{ padding: '8px 10px', textAlign: 'right', fontWeight: 700, color: '#059669' }}>{c.cost_range}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}

              {/* Medical Notice */}
              <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderLeft: '4px solid #f59e0b', padding: '12px 16px', fontSize: '12px', color: '#92400e', borderRadius: '4px', marginTop: '16px' }}>
                <strong>Non-Diagnostic Medical Notice:</strong> This preliminary visual screening report was generated using photographic analysis and deterministic scoring for educational and conversational preparation with your dental provider. It is NOT a medical diagnosis and cannot substitute for an in-person dental exam, radiographs, or periodontal probing.
              </div>
            </div>

            <div className="report-modal-footer">
              <span className="text-xs text-slate-400">
                Ready to share with your dentist or save for personal records
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="btn-secondary-sm"
                  onClick={() => setShowReportModal(false)}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn-primary-sm flex items-center gap-1.5"
                  onClick={handlePrint}
                >
                  <Printer className="w-4 h-4" />
                  <span>Print / Save PDF</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
