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
  History,
  GitCompare,
  ExternalLink,
  MapPin,
  Phone,
  Send,
  Building2,
  Clock,
  ArrowRight,
  UserCheck,
} from 'lucide-react';
import MedicalDisclaimer from '../components/MedicalDisclaimer';
import {
  fetchScreenings,
  compareScreenings,
  fetchProviders,
  submitReferral,
  getReportHtmlUrl,
} from '../services/api';

export default function ResultsDashboard({ report, images, questionnaire, onRestart }) {
  const [evidenceModal, setEvidenceModal] = useState(null);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  // Longitudinal history & comparison states
  const [historyList, setHistoryList] = useState([]);
  const [selectedPastScreeningId, setSelectedPastScreeningId] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [showComparisonModal, setShowComparisonModal] = useState(false);

  // Dentist referral states
  const [showReferralModal, setShowReferralModal] = useState(false);
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [patientName, setPatientName] = useState('');
  const [patientEmail, setPatientEmail] = useState('');
  const [patientPhone, setPatientPhone] = useState('');
  const [referralSuccess, setReferralSuccess] = useState(null);
  const [isSubmittingReferral, setIsSubmittingReferral] = useState(false);

  const {
    score = 82,
    score_label = 'Preliminary Visual Screening Score',
    findings = {},
    score_breakdown = {},
    recommendation = '',
    guidance = {},
    screening_id = 'scr_demo',
    created_at = new Date().toISOString(),
  } = report || {};

  // Fetch past screenings on mount for longitudinal tracking
  useEffect(() => {
    fetchScreenings().then((list) => {
      setHistoryList(list || []);
      // Pre-select the earlier screening if one exists that is different from current
      const past = list.find((s) => s.screening_id !== screening_id);
      if (past) {
        setSelectedPastScreeningId(past.screening_id);
      }
    });

    fetchProviders().then((res) => {
      setProviders(res || []);
      if (res && res.length > 0) setSelectedProvider(res[0]);
    });
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
    const url = getReportHtmlUrl(screening_id);
    window.open(url, '_blank');
  };

  // Run previous-vs-current comparison
  const handleCompare = async () => {
    if (!selectedPastScreeningId) return;
    setIsComparing(true);
    try {
      const res = await compareScreenings(selectedPastScreeningId, screening_id);
      setComparisonResult(res);
      setShowComparisonModal(true);
    } catch (err) {
      console.error('Comparison error:', err);
      alert('Could not generate comparison: ' + err.message);
    } finally {
      setIsComparing(false);
    }
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
        </p>
        <p className="print-notice">NOT A DIAGNOSIS • FOR PREVENTIVE AWARENESS ONLY</p>
      </div>

      {/* Main Score Hero Card */}
      <div className="score-hero-card">
        <div className="score-hero-top">
          <div>
            <span className="badge-id">SCREENING ID: {screening_id}</span>
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
                  {score_breakdown.alignment > 0 ? `-${score_breakdown.alignment}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Surface Discoloration</td>
                <td>{findings.discoloration?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {score_breakdown.discoloration > 0 ? `-${score_breakdown.discoloration}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Tooth Surface Wear</td>
                <td>{findings.tooth_wear?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {score_breakdown.tooth_wear > 0 ? `-${score_breakdown.tooth_wear}` : '0'}
                </td>
              </tr>
              <tr>
                <td>Gum Appearance</td>
                <td>{findings.gum_appearance?.severity || 'none'}</td>
                <td className="text-right text-amber-400">
                  {score_breakdown.gum_appearance > 0 ? `-${score_breakdown.gum_appearance}` : '0'}
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

      {/* Personalized Preventive Guidance Card */}
      <div className="recommendation-card">
        <div className="rec-icon-box">
          <Sparkles className="w-6 h-6 text-cyan-400" />
        </div>
        <div className="rec-body">
          <h3 className="rec-title">Personalized Preventive Guidance</h3>
          <p className="rec-text">{recommendation}</p>

          {/* Category-Specific Guidance */}
          {guidance.category_guidance && (
            <div className="mt-4 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Category Insights
              </h4>
              <ul className="text-xs text-slate-300 space-y-1.5 list-disc pl-4">
                {Object.entries(guidance.category_guidance).map(([k, text]) => (
                  <li key={k}>
                    <strong className="text-cyan-300 capitalize">{k.replace('_', ' ')}:</strong>{' '}
                    {text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Lifestyle Wellness Tips */}
          {guidance.lifestyle_tips && guidance.lifestyle_tips.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Daily Oral Wellness Tips
              </h4>
              <ul className="rec-bullet-list">
                {guidance.lifestyle_tips.map((tip, idx) => (
                  <li key={idx}>{tip}</li>
                ))}
              </ul>
            </div>
          )}

          {/* User-Reported Context Label */}
          {guidance.user_reported_notes && guidance.user_reported_notes.length > 0 && (
            <div className="mt-4 p-3 bg-slate-800/80 border border-slate-700 rounded-md">
              <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider mb-1">
                Context from Your Questionnaire (Self-Reported)
              </h4>
              <ul className="text-xs text-slate-300 space-y-1">
                {guidance.user_reported_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Longitudinal Tracking & Comparison Section */}
      <div className="tracking-section-card no-print">
        <div className="flex items-center justify-between flex-wrap gap-4 border-b border-slate-700/60 pb-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-bold text-white">Longitudinal Screening History</h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Track visible changes across your oral health screenings over time.
            </p>
          </div>

          {/* Compare Selector & Action */}
          {historyList.length > 1 && (
            <div className="flex items-center gap-2">
              <select
                className="history-select"
                value={selectedPastScreeningId}
                onChange={(e) => setSelectedPastScreeningId(e.target.value)}
              >
                <option value="">Select past screening to compare</option>
                {historyList
                  .filter((s) => s.screening_id !== screening_id)
                  .map((s) => (
                    <option key={s.screening_id} value={s.screening_id}>
                      {s.date} (Score: {s.score})
                    </option>
                  ))}
              </select>

              <button
                className="btn-secondary-sm btn-compare"
                onClick={handleCompare}
                disabled={!selectedPastScreeningId || isComparing}
              >
                <GitCompare className="w-4 h-4" />
                <span>{isComparing ? 'Comparing...' : 'Compare Screenings'}</span>
              </button>
            </div>
          )}
        </div>

        {/* History Timeline Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {historyList.map((item) => {
            const isCurrent = item.screening_id === screening_id;
            return (
              <div
                key={item.screening_id}
                className={`history-card ${isCurrent ? 'current-screening' : ''}`}
              >
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold text-slate-400">{item.date}</span>
                  {isCurrent && <span className="badge-pill badge-after">Current</span>}
                </div>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-2xl font-extrabold text-white">{item.score}</span>
                  <span className="text-xs text-slate-400">/ 100</span>
                </div>
                <div className="text-xs text-slate-400 mt-1 truncate">ID: {item.screening_id}</div>
              </div>
            );
          })}
        </div>
      </div>

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

      {/* Comparison Modal */}
      {showComparisonModal && comparisonResult && (
        <div className="evidence-modal-backdrop" onClick={() => setShowComparisonModal(false)}>
          <div
            className="evidence-modal-card comparison-modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="evidence-modal-header">
              <div className="flex items-center gap-2">
                <GitCompare className="w-5 h-5 text-cyan-400" />
                <h3 className="evidence-modal-title">Screening Comparison</h3>
              </div>
              <button className="btn-icon-close" onClick={() => setShowComparisonModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Score Delta Row */}
            <div className="grid grid-cols-3 gap-3 p-3 bg-slate-800/80 rounded-lg border border-slate-700 text-center my-3">
              <div>
                <span className="text-xs text-slate-400">
                  Previous ({comparisonResult.overall.previous_date || 'Earlier'})
                </span>
                <div className="text-xl font-bold text-slate-200">
                  {comparisonResult.overall.previous_score}
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-400">
                  Current ({comparisonResult.overall.current_date || 'Today'})
                </span>
                <div className="text-xl font-bold text-white">
                  {comparisonResult.overall.current_score}
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-400">Score Delta</span>
                <div
                  className={`text-xl font-bold ${
                    comparisonResult.overall.change >= 0 ? 'text-emerald-400' : 'text-amber-400'
                  }`}
                >
                  {comparisonResult.overall.change >= 0
                    ? `+${comparisonResult.overall.change}`
                    : comparisonResult.overall.change}
                </div>
              </div>
            </div>

            {/* Category Transitions Table */}
            <div className="comparison-categories-table-wrap">
              <table className="breakdown-table">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Previous</th>
                    <th>Current</th>
                    <th>Visible Change</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(comparisonResult.categories).map(([cat, info]) => (
                    <tr key={cat}>
                      <td className="font-semibold capitalize text-slate-200">
                        {cat.replace('_', ' ')}
                      </td>
                      <td>
                        <span className="badge-severity badge-mild capitalize">
                          {info.previous}
                        </span>
                      </td>
                      <td>
                        <span className="badge-severity badge-none capitalize">
                          {info.current}
                        </span>
                      </td>
                      <td className="text-xs text-slate-300">{info.change}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-3 p-2 bg-amber-500/10 border border-amber-500/30 rounded text-xs text-amber-200">
              <strong>Notice:</strong> {comparisonResult.disclaimer}
            </div>

            <div className="evidence-modal-footer mt-4">
              <button className="btn-secondary-sm" onClick={() => setShowComparisonModal(false)}>
                Close Comparison
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dentist Referral / Provider Connection Modal */}
      {showReferralModal && (
        <div className="evidence-modal-backdrop" onClick={() => setShowReferralModal(false)}>
          <div
            className="evidence-modal-card referral-modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="evidence-modal-header">
              <div className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-emerald-400" />
                <h3 className="evidence-modal-title">Connect with a Dental Care Provider</h3>
              </div>
              <button className="btn-icon-close" onClick={() => setShowReferralModal(false)}>
                <X className="w-5 h-5" />
              </button>
            </div>

            {referralSuccess ? (
              <div className="p-6 text-center space-y-3">
                <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
                <h4 className="text-lg font-bold text-white">Inquiry Sent Successfully!</h4>
                <p className="text-sm text-slate-300">
                  Your inquiry (ID: <strong>{referralSuccess.inquiry_id}</strong>) has been routed to{' '}
                  <strong>{referralSuccess.provider_name}</strong> with your preliminary screening report
                  attached.
                </p>
                <div className="p-3 bg-slate-800 rounded-md text-xs text-slate-400 text-left">
                  The dental clinic will reach out to <strong>{referralSuccess.patient_email}</strong> to
                  confirm your appointment.
                </div>
                <button
                  className="btn-primary mt-4 mx-auto"
                  onClick={() => {
                    setShowReferralModal(false);
                    setReferralSuccess(null);
                  }}
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleSendReferral} className="p-2 space-y-4">
                <p className="text-xs text-slate-300">
                  Select a dental practice to share your preliminary screening findings (Screening ID:{' '}
                  {screening_id}) for professional in-person clinical review.
                </p>

                {/* Provider Picker */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase">
                    Select Dental Clinic
                  </label>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {providers.map((p) => {
                      const isSelected = selectedProvider?.id === p.id;
                      return (
                        <div
                          key={p.id}
                          className={`provider-card ${isSelected ? 'selected' : ''}`}
                          onClick={() => setSelectedProvider(p)}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-semibold text-sm text-white">{p.name}</div>
                              <div className="text-xs text-slate-400">{p.doctor} • {p.specialty}</div>
                            </div>
                            <span className="text-xs font-bold text-emerald-400">★ {p.rating}</span>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
                            <span><MapPin className="w-3.5 h-3.5 inline mr-1 text-cyan-400" />{p.address} ({p.distance})</span>
                            <span><Clock className="w-3.5 h-3.5 inline mr-1 text-emerald-400" />{p.next_available}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Patient Information Inputs */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      className="form-input-text"
                      required
                      placeholder="Jane Doe"
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
                      placeholder="jane@example.com"
                      value={patientEmail}
                      onChange={(e) => setPatientEmail(e.target.value)}
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="text-xs font-semibold text-slate-300 block mb-1">
                      Phone Number (Optional)
                    </label>
                    <input
                      type="tel"
                      className="form-input-text"
                      placeholder="(555) 000-0000"
                      value={patientPhone}
                      onChange={(e) => setPatientPhone(e.target.value)}
                    />
                  </div>
                </div>

                <div className="evidence-modal-footer mt-4">
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
                    disabled={isSubmittingReferral}
                  >
                    <Send className="w-4 h-4" />
                    <span>{isSubmittingReferral ? 'Submitting...' : 'Send Screening to Clinic'}</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
