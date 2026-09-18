import React, { useState, useRef, useEffect } from 'react';
import {
  Camera,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  SwitchCamera,
  Sparkles,
  Info,
  Zap,
  Eye,
} from 'lucide-react';
import { checkImageQuality, enhanceDentalImage, dataURLtoBlob } from '../services/api';
import { getSampleDentalImage, getBlurrySampleDentalImage } from '../utils/sampleImages';
import MedicalDisclaimer from '../components/MedicalDisclaimer';

const VIEWS_META = [
  {
    id: 'front',
    label: 'FRONT VIEW',
    title: 'Step 1 of 5: Front Dental View',
    instruction: 'Smile naturally with teeth lightly together. Center your front upper and lower teeth in the guide.',
    hint: 'Ensure good lighting directly facing your mouth.',
    overlayType: 'front',
  },
  {
    id: 'left',
    label: 'LEFT VIEW',
    title: 'Step 2 of 5: Left-Side Dental View',
    instruction: 'Turn your head slightly to the right so the camera has a clear view of your left side teeth and bite.',
    hint: 'Gently pull your left cheek back slightly with a clean finger if needed.',
    overlayType: 'side',
  },
  {
    id: 'right',
    label: 'RIGHT VIEW',
    title: 'Step 3 of 5: Right-Side Dental View',
    instruction: 'Turn your head slightly to the left so the camera captures your right side teeth and bite.',
    hint: 'Gently pull your right cheek back slightly to expose the side teeth.',
    overlayType: 'side',
  },
  {
    id: 'upper',
    label: 'UPPER ARCH',
    title: 'Step 4 of 5: Upper Arch View',
    instruction: 'Tilt your head slightly back, open wide, and position the camera to view the upper biting surfaces.',
    hint: 'Make sure your tongue does not block the teeth.',
    overlayType: 'arch',
  },
  {
    id: 'lower',
    label: 'LOWER ARCH',
    title: 'Step 5 of 5: Lower Arch View',
    instruction: 'Tilt your chin slightly down, open wide, and point the camera to view the lower biting surfaces.',
    hint: 'Rest your tongue on the floor of your mouth.',
    overlayType: 'arch',
  },
];

export default function CameraCapture({ images, initialViewIndex = 0, onImageUpdated, onAllComplete, onBack }) {
  const [viewIndex, setViewIndex] = useState(initialViewIndex);
  const currentView = VIEWS_META[viewIndex];

  // Camera state
  const videoRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState('user');
  const [cameraError, setCameraError] = useState(null);

  // Quality check state for current view
  const [qualityStatus, setQualityStatus] = useState(null);
  const fileInputRef = useRef(null);

  const currentImageBlob = images[currentView.id];
  const [previewUrl, setPreviewUrl] = useState(null);

  // Enhancement states
  const [originalBlob, setOriginalBlob] = useState(null);
  const [enhancedBlob, setEnhancedBlob] = useState(null);
  const [enhancedUrl, setEnhancedUrl] = useState(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [activePreviewMode, setActivePreviewMode] = useState('enhanced'); // 'enhanced' | 'original'

  useEffect(() => {
    if (currentImageBlob) {
      const url = URL.createObjectURL(currentImageBlob);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
      setQualityStatus(null);
      setOriginalBlob(null);
      setEnhancedBlob(null);
      setEnhancedUrl(null);
    }
  }, [currentImageBlob]);

  // Start / Stop camera
  const startCamera = async (mode = facingMode) => {
    try {
      setCameraError(null);
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: mode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch((e) => {
          if (e.name !== 'AbortError') console.warn('Video play error:', e);
        });
        setCameraActive(true);
      }
    } catch (err) {
      console.warn('Camera access unavailable:', err);
      setCameraError('Camera access not granted or unavailable. You can upload a photo or use demo samples below.');
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  useEffect(() => {
    if (!currentImageBlob) {
      startCamera(facingMode);
    } else {
      stopCamera();
    }
    return () => stopCamera();
  }, [viewIndex, currentImageBlob, facingMode]);

  // Handle incoming image (capture or upload) with two-stage quality evaluation
  const handleImageReceived = async (blob) => {
    stopCamera();
    setOriginalBlob(blob);
    setQualityStatus({ checking: true });
    setActivePreviewMode('enhanced');

    // Call backend two-stage technical quality check
    const qResult = await checkImageQuality(blob, currentView.id);

    if (qResult.enhanced && qResult.passed) {
      // Auto-enhancement improved image quality
      try {
        setIsEnhancing(true);
        const enhRes = await enhanceDentalImage(blob, currentView.id);
        const eBlob = dataURLtoBlob(enhRes.enhanced_image_base64);
        setEnhancedBlob(eBlob);
        setEnhancedUrl(enhRes.enhanced_image_base64);
        onImageUpdated(currentView.id, eBlob);
      } catch (err) {
        console.warn('Auto enhancement preview fetch error:', err);
        onImageUpdated(currentView.id, blob);
      } finally {
        setIsEnhancing(false);
      }
    } else {
      onImageUpdated(currentView.id, blob);
    }

    setQualityStatus({
      checking: false,
      passed: qResult.passed,
      score: qResult.quality_score,
      originalScore: qResult.original_quality_score,
      enhancedScore: qResult.enhanced_quality_score,
      enhanced: qResult.enhanced,
      issues: qResult.issues || [],
    });
  };

  const handleManualEnhance = async () => {
    const targetBlob = originalBlob || currentImageBlob;
    if (!targetBlob || isEnhancing) return;
    setIsEnhancing(true);

    try {
      const enhRes = await enhanceDentalImage(targetBlob, currentView.id);
      const eBlob = dataURLtoBlob(enhRes.enhanced_image_base64);
      setEnhancedBlob(eBlob);
      setEnhancedUrl(enhRes.enhanced_image_base64);
      onImageUpdated(currentView.id, eBlob);

      setQualityStatus((prev) => ({
        ...prev,
        passed: enhRes.after_quality.passed,
        score: enhRes.after_quality.quality_score,
        originalScore: enhRes.before_quality.quality_score,
        enhancedScore: enhRes.after_quality.quality_score,
        enhanced: true,
        issues: enhRes.after_quality.issues || [],
      }));
      setActivePreviewMode('enhanced');
    } catch (err) {
      console.error('Manual enhancement error:', err);
      alert('Enhancement error: ' + (err.message || 'Check backend connection'));
    } finally {
      setIsEnhancing(false);
    }
  };

  const togglePreviewMode = (mode) => {
    setActivePreviewMode(mode);
    if (mode === 'original' && originalBlob) {
      onImageUpdated(currentView.id, originalBlob);
    } else if (mode === 'enhanced' && enhancedBlob) {
      onImageUpdated(currentView.id, enhancedBlob);
    }
  };

  const takeSnapshot = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');

    if (facingMode === 'user') {
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) handleImageReceived(blob);
    }, 'image/jpeg', 0.94);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) handleImageReceived(file);
  };

  const handleLoadDemo = async () => {
    const demoBlob = await getSampleDentalImage(currentView.id);
    handleImageReceived(demoBlob);
  };

  const handleLoadBlurryDemo = async () => {
    const blurryBlob = await getBlurrySampleDentalImage(currentView.id);
    handleImageReceived(blurryBlob);
  };

  const handleRetake = () => {
    onImageUpdated(currentView.id, null);
    setQualityStatus(null);
    setOriginalBlob(null);
    setEnhancedBlob(null);
    setEnhancedUrl(null);
    startCamera(facingMode);
  };

  const toggleFacingMode = () => {
    const nextMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(nextMode);
    startCamera(nextMode);
  };

  const handleNextView = () => {
    if (viewIndex < VIEWS_META.length - 1) {
      setViewIndex((prev) => prev + 1);
    } else {
      onAllComplete();
    }
  };

  const handlePrevView = () => {
    if (viewIndex > 0) {
      setViewIndex((prev) => prev - 1);
    } else {
      onBack();
    }
  };

  return (
    <div className="camera-page">
      {/* Stepper Bar */}
      <div className="stepper-bar">
        {VIEWS_META.map((v, i) => {
          const isDone = !!images[v.id];
          const isCurrent = i === viewIndex;
          return (
            <button
              key={v.id}
              className={`step-tab ${isCurrent ? 'active' : ''} ${isDone ? 'completed' : ''}`}
              onClick={() => setViewIndex(i)}
            >
              <div className="step-tab-num">
                {isDone ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : i + 1}
              </div>
              <span className="step-tab-label">{v.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Viewfinder Card */}
      <div className="capture-card">
        <div className="capture-header">
          <div>
            <span className="badge-step">STEP {viewIndex + 1} OF 5</span>
            <h2 className="view-main-title">{currentView.title}</h2>
          </div>
          <div className="view-quick-actions">
            <button className="btn-ghost-sm" onClick={handleLoadDemo} title="Load clear sample photo">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Sample Photo</span>
            </button>
            <button
              className="btn-ghost-sm btn-ghost-blurry"
              onClick={handleLoadBlurryDemo}
              title="Load blurry photo to test automatic enhancement"
            >
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Blurry Test Photo</span>
            </button>
          </div>
        </div>

        <p className="view-instruction">{currentView.instruction}</p>

        {/* Viewfinder Container */}
        <div className="viewfinder-container">
          {previewUrl ? (
            <div className="preview-wrap">
              <img
                src={activePreviewMode === 'enhanced' && enhancedUrl ? enhancedUrl : previewUrl}
                alt={currentView.title}
                className="preview-img"
              />

              {/* Enhancement toggle pills if enhanced version exists */}
              {enhancedUrl && (
                <div className="preview-toggle-pills">
                  <button
                    type="button"
                    className={`pill-toggle-btn ${activePreviewMode === 'enhanced' ? 'active' : ''}`}
                    onClick={() => togglePreviewMode('enhanced')}
                  >
                    <span>✓ Enhanced View</span>
                  </button>
                  <button
                    type="button"
                    className={`pill-toggle-btn ${activePreviewMode === 'original' ? 'active' : ''}`}
                    onClick={() => togglePreviewMode('original')}
                  >
                    <span>Original</span>
                  </button>
                </div>
              )}

              <div className="preview-badge">
                {activePreviewMode === 'enhanced' && enhancedUrl ? '✦ Optimized for Analysis' : 'Captured Photo'}
              </div>

              {isEnhancing && (
                <div className="enhancing-overlay">
                  <RefreshCw className="w-8 h-8 animate-spin text-cyan-400 mb-2" />
                  <span className="text-cyan-200 font-semibold text-sm">✦ Automatic Image Enhancement in progress...</span>
                  <span className="text-slate-300 text-xs mt-1">Sharpening edges, adjusting brightness, and expanding contrast</span>
                </div>
              )}
            </div>
          ) : (
            <div className="video-viewport">
              <video
                ref={videoRef}
                playsInline
                autoPlay
                muted
                className={`camera-feed ${facingMode === 'user' ? 'mirrored' : ''}`}
              />

              <div className="overlay-guide">
                <div className={`guide-stencil guide-${currentView.overlayType}`}>
                  <div className="guide-inner-arch"></div>
                </div>
                <div className="guide-text">Position teeth within guidelines</div>
              </div>

              {cameraActive && (
                <button
                  className="camera-flip-btn"
                  onClick={toggleFacingMode}
                  title="Switch camera"
                  type="button"
                >
                  <SwitchCamera className="w-5 h-5 text-white" />
                </button>
              )}

              {!cameraActive && (
                <div className="camera-fallback-box">
                  <Camera className="w-12 h-12 text-slate-500 mb-2" />
                  <p className="text-sm text-slate-300 mb-1">{cameraError || 'Camera inactive'}</p>
                  <p className="text-xs text-slate-400">Use "Upload File" or click "Sample Photo" above to proceed.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Dynamic Quality & Enhancement Feedback Banner */}
        {qualityStatus && !qualityStatus.checking && (
          <div className="quality-banner-wrapper">
            {qualityStatus.passed ? (
              qualityStatus.enhanced ? (
                /* Auto-Enhancement Succeeded Banner */
                <div className="quality-result-pass-block quality-enhanced-block">
                  <div className="flex items-start gap-2.5">
                    <Sparkles className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-cyan-200">
                        ✓ Image quality improved automatically
                      </div>
                      <div className="text-xs text-slate-300 mt-0.5">
                        ✓ Image optimized for analysis (Quality: {Math.round(qualityStatus.score * 100)}%)
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* Clear Photo Passed Directly */
                <div className="quality-result-pass-block">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                    <div>
                      <span className="font-medium text-emerald-200">✓ Image quality check passed</span>
                      <span className="text-xs text-slate-400 ml-2">({Math.round(qualityStatus.score * 100)}% clarity)</span>
                    </div>
                  </div>
                </div>
              )
            ) : (
              /* Quality Needs Improvement Banner */
              <div className="quality-result-warning-block">
                <div className="flex items-start gap-2.5">
                  <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <strong className="text-amber-200">⚠️ Image still needs improvement</strong>
                    <p className="text-xs text-slate-300 mt-1">
                      Please retake the image with better lighting and a steadier camera.
                    </p>
                    <ul className="quality-issues-list mt-1">
                      {qualityStatus.issues.map((issue, idx) => (
                        <li key={idx} className="text-xs text-amber-300">{issue}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Capture Controls */}
        <div className="capture-controls">
          {!previewUrl ? (
            <>
              <button
                className="btn-capture"
                onClick={takeSnapshot}
                disabled={!cameraActive}
                id="capture-photo-btn"
              >
                <div className="capture-ring"></div>
                <Camera className="w-6 h-6 text-white" />
                <span>Capture {currentView.label}</span>
              </button>

              <div className="upload-fallback-wrap">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                />
                <button
                  className="btn-secondary"
                  onClick={() => fileInputRef.current?.click()}
                  type="button"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload File</span>
                </button>
              </div>
            </>
          ) : (
            <div className="review-controls-row">
              <button className="btn-secondary" onClick={handleRetake}>
                <RefreshCw className="w-4 h-4" />
                <span>Retake</span>
              </button>

              <button
                className="btn-secondary btn-enhance-action"
                onClick={handleManualEnhance}
                disabled={isEnhancing}
                type="button"
                title="Sharpen and enhance contrast"
              >
                {isEnhancing ? (
                  <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                ) : (
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                )}
                <span>{isEnhancing ? 'Enhancing...' : '✦ Enhance Photo'}</span>
              </button>

              <button className="btn-primary" onClick={handleNextView} id="accept-view-btn">
                <span>
                  {viewIndex === VIEWS_META.length - 1 ? 'Review All 5 Views' : `Next (${VIEWS_META[viewIndex + 1].label})`}
                </span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Helper Hint */}
        <div className="view-hint-box">
          <Info className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span>{currentView.hint}</span>
        </div>

        {/* Stepper Footer */}
        <div className="stepper-nav-row">
          <button className="btn-ghost-sm" onClick={handlePrevView}>
            <ArrowLeft className="w-4 h-4" />
            <span>{viewIndex === 0 ? 'Back to Questionnaire' : 'Previous View'}</span>
          </button>

          <span className="stepper-count-text">
            {Object.keys(images).filter((k) => !!images[k]).length} of 5 Views Captured
          </span>
        </div>
      </div>

      <div className="mt-6">
        <MedicalDisclaimer compact={true} />
      </div>
    </div>
  );
}
