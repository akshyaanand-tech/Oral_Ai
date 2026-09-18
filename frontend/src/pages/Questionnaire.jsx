import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Check, Sparkles, AlertCircle } from 'lucide-react';
import MedicalDisclaimer from '../components/MedicalDisclaimer';

const QUESTIONS = [
  {
    id: 'tooth_sensitivity',
    question: '1. Have you noticed tooth sensitivity?',
    desc: 'Sensitivity to hot, cold, sweet, or acidic foods and drinks.',
    type: 'choice',
    options: [
      { value: 'none', label: 'No sensitivity noticed' },
      { value: 'mild', label: 'Mild sensitivity occasionally (e.g. ice water)' },
      { value: 'frequent', label: 'Frequent or sharp sensitivity when eating/drinking' },
      { value: 'severe', label: 'Severe or lingering sensitivity lasting several minutes' },
    ],
  },
  {
    id: 'pain_discomfort',
    question: '2. Are you currently experiencing dental pain or discomfort?',
    desc: 'Any aching, throbbing, soreness, or pain when chewing.',
    type: 'choice',
    options: [
      { value: 'none', label: 'No pain or discomfort' },
      { value: 'occasional', label: 'Occasional mild dull ache' },
      { value: 'chewing', label: 'Discomfort mainly when biting or chewing' },
      { value: 'constant', label: 'Persistent or throbbing pain' },
    ],
  },
  {
    id: 'gum_bleeding',
    question: '3. Have you noticed bleeding from your gums?',
    desc: 'During brushing, flossing, or spontaneously.',
    type: 'choice',
    options: [
      { value: 'none', label: 'No bleeding observed (gums firm and pink)' },
      { value: 'flossing', label: 'Minor bleeding occasionally when flossing' },
      { value: 'brushing', label: 'Frequent bleeding while brushing teeth' },
      { value: 'spontaneous', label: 'Frequent bleeding, puffiness, or tenderness' },
    ],
  },
  {
    id: 'teeth_or_gum_changes',
    question: '4. Have you noticed changes in your teeth or gums?',
    desc: 'Such as visible shifting, gum recession, roughness, or new spots.',
    type: 'choice',
    options: [
      { value: 'none', label: 'No noticeable changes' },
      { value: 'slight', label: 'Slight changes (minor spacing, slight staining)' },
      { value: 'moderate', label: 'Noticeable shifting, chipping, or gum recession' },
      { value: 'marked', label: 'Significant visible changes or loose tooth sensation' },
    ],
  },
  {
    id: 'last_dental_visit',
    question: '5. When was your last in-person dental visit?',
    desc: 'Routine professional exams and cleanings are recommended every 6 months.',
    type: 'choice',
    options: [
      { value: 'under_6_months', label: 'Less than 6 months ago' },
      { value: '6_to_12_months', label: '6 to 12 months ago' },
      { value: '1_to_2_years', label: '1 to 2 years ago' },
      { value: 'over_2_years', label: 'More than 2 years ago / Never' },
    ],
  },
  {
    id: 'specific_concern',
    question: '6. Is there any specific oral-health concern you want to check?',
    desc: 'Optional: share any specific tooth, area, or concern you would like the report to highlight.',
    type: 'text',
    placeholder: 'e.g., Lower front teeth crowding, stain on upper right incisor, night grinding wear...',
  },
  {
    id: 'location',
    question: '7. What is your City or Postal/PIN Code?',
    desc: 'Used to locate verified dental practices and regional cost ranges (no GPS required).',
    type: 'text',
    placeholder: 'e.g., Boston, New York, San Francisco, 560001, 10001...',
  },
];

export default function Questionnaire({ initialAnswers, onComplete, onBack }) {
  const [answers, setAnswers] = useState(
    initialAnswers || {
      tooth_sensitivity: 'none',
      pain_discomfort: 'none',
      gum_bleeding: 'none',
      teeth_or_gum_changes: 'none',
      last_dental_visit: '6_to_12_months',
      specific_concern: '',
      location: '',
    }
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const currentQ = QUESTIONS[currentIndex];
  const progressPercent = Math.round(((currentIndex + 1) / QUESTIONS.length) * 100);

  const handleSelect = (val) => {
    setAnswers((prev) => ({ ...prev, [currentQ.id]: val }));
  };

  const handleTextChange = (e) => {
    setAnswers((prev) => ({ ...prev, [currentQ.id]: e.target.value }));
  };

  const handleNext = () => {
    if (currentIndex < QUESTIONS.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      onComplete(answers);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    } else {
      onBack();
    }
  };

  return (
    <div className="questionnaire-page">
      <div className="wizard-card">
        {/* Progress Bar */}
        <div className="wizard-progress-header">
          <div className="step-label">
            <span>QUESTION {currentIndex + 1} OF {QUESTIONS.length}</span>
            <span className="percent-text">{progressPercent}%</span>
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
          </div>
        </div>

        {/* Question Header */}
        <div className="question-header">
          <h2 className="question-text">{currentQ.question}</h2>
          {currentQ.desc && <p className="question-desc">{currentQ.desc}</p>}
        </div>

        {/* Options / Input Body */}
        {currentQ.type === 'choice' ? (
          <div className="options-list">
            {currentQ.options.map((opt) => {
              const isSelected = answers[currentQ.id] === opt.value;
              return (
                <button
                  key={opt.value}
                  className={`option-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelect(opt.value)}
                  type="button"
                >
                  <div className="option-radio">
                    {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                  </div>
                  <span className="option-label">{opt.label}</span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="question-text-area-wrap">
            <textarea
              className="question-textarea"
              rows={4}
              placeholder={currentQ.placeholder}
              value={answers[currentQ.id] || ''}
              onChange={handleTextChange}
            />
            <span className="text-xs text-slate-400 mt-2 block">
              This will be included under patient-reported context in your dentist summary report.
            </span>
          </div>
        )}

        {/* Separation Note */}
        <div className="question-disclaimer-note">
          <Sparkles className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span>
            Questionnaire responses provide self-reported context for personalized guidance and are kept strictly independent from AI visual scoring.
          </span>
        </div>

        {/* Navigation Buttons */}
        <div className="wizard-actions">
          <button className="btn-secondary" onClick={handlePrev}>
            <ArrowLeft className="w-4 h-4" />
            <span>{currentIndex === 0 ? 'Back' : 'Previous'}</span>
          </button>

          <button className="btn-primary" onClick={handleNext}>
            <span>{currentIndex === QUESTIONS.length - 1 ? 'Proceed to Guided Camera' : 'Next Question'}</span>
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
