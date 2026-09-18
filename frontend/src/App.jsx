import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Landing from './pages/Landing';
import Questionnaire from './pages/Questionnaire';
import CameraCapture from './pages/CameraCapture';
import ReviewAll from './pages/ReviewAll';
import Processing from './pages/Processing';
import ResultsDashboard from './pages/ResultsDashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import { checkHealth, analyzeDentalImages, screenOralHealth, getCurrentUser } from './services/api';
import { getAllSampleDentalImages } from './utils/sampleImages';
import { AlertCircle, X } from 'lucide-react';

export default function App() {
  const [step, setStep] = useState('landing'); // 'landing' | 'questionnaire' | 'capture' | 'review' | 'processing' | 'results' | 'login' | 'register'
  const [backendStatus, setBackendStatus] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // User authentication state
  const [currentUser, setCurrentUser] = useState(null);
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('oral_ai_token'));

  // Load user profile on mount if token exists
  useEffect(() => {
    if (authToken) {
      getCurrentUser(authToken)
        .then((res) => {
          if (res?.user) {
            setCurrentUser(res.user);
          }
        })
        .catch(() => {
          localStorage.removeItem('oral_ai_token');
          setAuthToken(null);
          setCurrentUser(null);
        });
    }
  }, [authToken]);

  const handleLoginSuccess = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    localStorage.setItem('oral_ai_token', token);
    setStep('landing');
  };

  const handleRegisterSuccess = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    localStorage.setItem('oral_ai_token', token);
    setStep('landing');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setAuthToken(null);
    localStorage.removeItem('oral_ai_token');
  };

  // Questionnaire responses with City/PIN code support
  const [questionnaire, setQuestionnaire] = useState({
    tooth_sensitivity: 'none',
    pain_discomfort: 'none',
    gum_bleeding: 'none',
    teeth_or_gum_changes: 'none',
    last_dental_visit: '6_to_12_months',
    specific_concern: '',
    location: '',
  });

  // 5 Dental images
  const [images, setImages] = useState({
    front: null,
    left: null,
    right: null,
    upper: null,
    lower: null,
  });

  // Final screening report
  const [report, setReport] = useState(null);

  // Health check on initial load
  useEffect(() => {
    checkHealth().then(setBackendStatus);
  }, []);

  const handleStart = () => {
    setErrorMsg(null);
    setStep('questionnaire');
  };

  const handleQuestionnaireComplete = (answers) => {
    setQuestionnaire(answers);
    setStep('capture');
  };

  const handleImageUpdated = (view, blob) => {
    setImages((prev) => ({ ...prev, [view]: blob }));
  };

  const handleAllCaptured = () => {
    setStep('review');
  };

  const [activeCaptureIndex, setActiveCaptureIndex] = useState(0);

  const handleRetakeView = (index = 0) => {
    setActiveCaptureIndex(index);
    setStep('capture');
  };

  const handleFillMissingWithDemo = async () => {
    const samples = await getAllSampleDentalImages();
    setImages((prev) => ({
      front: prev.front || samples.front,
      left: prev.left || samples.left,
      right: prev.right || samples.right,
      upper: prev.upper || samples.upper,
      lower: prev.lower || samples.lower,
    }));
  };

  // Quick 1-Click Demo flow for hackathon judges & instant preview
  const handleQuickDemo = async () => {
    setErrorMsg(null);
    setStep('processing');

    try {
      const samples = await getAllSampleDentalImages();
      setImages(samples);

      // Submit sample images + location to /api/screen endpoint
      const loc = questionnaire.location || '';
      let result;
      try {
        result = await screenOralHealth(samples, loc, questionnaire);
      } catch (screenErr) {
        console.warn('screenOralHealth fallback to analyzeDentalImages:', screenErr);
        result = await analyzeDentalImages(samples, questionnaire);
      }

      setReport(result);
      setStep('results');
    } catch (err) {
      console.error('Quick demo error:', err);
      setErrorMsg(err.message || 'Quick demo could not connect to backend.');
      setStep('landing');
    }
  };

  // Submit all 5 images for full analysis
  const handleSubmitScreening = async () => {
    setErrorMsg(null);
    setStep('processing');

    try {
      const loc = questionnaire.location || '';
      let result;
      try {
        result = await screenOralHealth(images, loc, questionnaire);
      } catch (screenErr) {
        if (screenErr.retake) throw screenErr;
        console.warn('screenOralHealth fallback to analyzeDentalImages:', screenErr);
        result = await analyzeDentalImages(images, questionnaire);
      }

      setReport(result);
      setStep('results');
    } catch (err) {
      console.error('Screening submission error:', err);
      if (err.retake && err.retake.length > 0) {
        const failedView = err.retake[0].view;
        const viewMap = { front: 0, left: 1, right: 2, upper: 3, lower: 4 };
        const failedIdx = viewMap[failedView] ?? 0;
        setErrorMsg(`⚠️ Retake required for ${failedView.toUpperCase()} view: ${err.retake[0].reason}`);
        handleRetakeView(failedIdx);
      } else {
        setErrorMsg(err.message || 'Unable to complete screening. Please check your photos and backend server.');
        setStep('review');
      }
    }
  };

  const handleReset = () => {
    setStep('landing');
    setImages({ front: null, left: null, right: null, upper: null, lower: null });
    setReport(null);
    setErrorMsg(null);
  };

  return (
    <div className="app-root">
      <Header
        onReset={handleReset}
        currentStep={step}
        backendStatus={backendStatus}
        currentUser={currentUser}
        onNavigateLogin={() => setStep('login')}
        onNavigateRegister={() => setStep('register')}
        onLogout={handleLogout}
      />

      {/* Global Error Notice */}
      {errorMsg && (
        <div className="global-error-banner">
          <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <span className="error-text">{errorMsg}</span>
          <button className="btn-close-error" onClick={() => setErrorMsg(null)}>
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <main className="main-content">
        {step === 'login' && (
          <Login
            onLoginSuccess={handleLoginSuccess}
            onNavigateRegister={() => setStep('register')}
            onBack={() => setStep('landing')}
          />
        )}

        {step === 'register' && (
          <Register
            onRegisterSuccess={handleRegisterSuccess}
            onNavigateLogin={() => setStep('login')}
            onBack={() => setStep('landing')}
          />
        )}

        {step === 'landing' && (
          <Landing
            currentUser={currentUser}
            onStart={handleStart}
            onQuickDemo={handleQuickDemo}
          />
        )}

        {step === 'questionnaire' && (
          <Questionnaire
            initialAnswers={questionnaire}
            onComplete={handleQuestionnaireComplete}
            onBack={() => setStep('landing')}
          />
        )}

        {step === 'capture' && (
          <CameraCapture
            images={images}
            initialViewIndex={activeCaptureIndex}
            onImageUpdated={handleImageUpdated}
            onAllComplete={handleAllCaptured}
            onBack={() => setStep('questionnaire')}
          />
        )}

        {step === 'review' && (
          <ReviewAll
            images={images}
            onRetakeView={handleRetakeView}
            onSubmit={handleSubmitScreening}
            onBack={() => setStep('capture')}
            onFillMissingWithDemo={handleFillMissingWithDemo}
          />
        )}

        {step === 'processing' && <Processing />}

        {step === 'results' && (
          <ResultsDashboard
            currentUser={currentUser}
            report={report}
            images={images}
            questionnaire={questionnaire}
            onRestart={handleReset}
          />
        )}
      </main>
    </div>
  );
}
