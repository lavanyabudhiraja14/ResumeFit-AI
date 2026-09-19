import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/auth/AuthModal';
import InterestSelectionView from './components/onboarding/InterestSelectionView';
import DashboardView from './components/dashboard/DashboardView';
import ResumeUploader from './components/ResumeUploader';
import ExtractedSkillsView from './components/ExtractedSkillsView';
import ResumeQualityView from './components/ResumeQualityView';
import JobDescriptionInput from './components/JobDescriptionInput';
import MatchResultsView from './components/MatchResultsView';
import { 
  checkBackendHealth, 
  analyzeResume, 
  analyzeMatch, 
  getCurrentUser, 
  clearToken,
  saveUserResume
} from './services/api';

export default function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  // Active view: 'home' | 'onboarding' | 'dashboard' | 'resume'
  const [currentView, setCurrentView] = useState('home');

  // Auth modal state
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('signup');

  // Resume analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [resumeError, setResumeError] = useState(null);

  // Job matching state
  const [isMatching, setIsMatching] = useState(false);
  const [matchData, setMatchData] = useState(null);
  const [matchError, setMatchError] = useState(null);

  // Check health and load authenticated user on mount
  useEffect(() => {
    checkBackendHealth().then(setBackendStatus);
    const interval = setInterval(() => {
      checkBackendHealth().then(setBackendStatus);
    }, 15000);

    getCurrentUser()
      .then((currentUser) => {
        if (currentUser) {
          setUser(currentUser);
          if (currentUser.onboarding_completed) {
            setCurrentView('dashboard');
          } else {
            setCurrentView('onboarding');
          }
        } else {
          setCurrentView('home');
        }
      })
      .catch(() => {
        setCurrentView('home');
      })
      .finally(() => {
        setLoadingUser(false);
      });

    return () => clearInterval(interval);
  }, []);

  const handleOpenAuth = (mode) => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  const handleAuthSuccess = (authUser, token) => {
    setUser(authUser);
    if (!authUser.onboarding_completed) {
      setCurrentView('onboarding');
    } else {
      setCurrentView('dashboard');
    }
  };

  const handleSignOut = () => {
    clearToken();
    setUser(null);
    setCurrentView('home');
  };

  const handleOnboardingComplete = (updatedInterestsData) => {
    setUser((prev) => ({
      ...prev,
      interests: updatedInterestsData.interests,
      onboarding_completed: true,
    }));
    setCurrentView('dashboard');
  };

  const handleAnalyzeResume = async (file) => {
    setIsAnalyzing(true);
    setResumeError(null);
    setMatchData(null);

    try {
      const result = await analyzeResume(file);
      setResumeData(result);

      if (user) {
        try {
          const updatedUser = await saveUserResume(file.name, result.raw_skills || []);
          setUser(updatedUser);
        } catch (e) {
          console.warn('Failed to persist resume skills to user profile:', e);
        }
      }
    } catch (err) {
      setResumeError(err.message || 'Error parsing resume file.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyzeMatch = async (jobDescription) => {
    if (!resumeData || !resumeData.raw_skills) return;

    setIsMatching(true);
    setMatchError(null);

    try {
      const result = await analyzeMatch(resumeData.raw_skills, jobDescription);
      setMatchData(result);

      setTimeout(() => {
        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: 'smooth',
        });
      }, 100);
    } catch (err) {
      setMatchError(err.message || 'Error analyzing job match.');
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F5] flex flex-col font-sans selection:bg-[#FF6A00]/30 selection:text-white">
      <Navbar
        backendStatus={backendStatus}
        user={user}
        currentView={currentView}
        onNavigate={setCurrentView}
        onOpenAuth={handleOpenAuth}
        onSignOut={handleSignOut}
      />

      {/* Main View Router */}
      <main className="flex-1 flex flex-col">
        {/* Onboarding View: Interest Selection */}
        {currentView === 'onboarding' && (
          <InterestSelectionView
            initialInterests={user?.interests || []}
            onComplete={handleOnboardingComplete}
          />
        )}

        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <DashboardView
            user={user}
            onNavigateToResume={() => setCurrentView('resume')}
            onEditInterests={() => setCurrentView('onboarding')}
            onUserUpdate={(updated) => setUser(updated)}
          />
        )}

        {/* Resume Analysis View (Accessible to unauthenticated or authenticated users) */}
        {(currentView === 'home' || currentView === 'resume') && (
          <div className="max-w-4xl w-full mx-auto px-6 py-12 sm:py-16">
            {/* Hero Section */}
            <div className="text-center mb-16">
              <p className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] mb-3">
                Intelligent Skill Alignment
              </p>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-[#F5F5F5] mb-4">
                Your resume.<br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#F5F5F5] via-[#D1D1D1] to-[#A1A1A1]">
                  Your next opportunity.
                </span>
              </h1>
              <p className="text-base sm:text-lg text-[#A1A1A1] max-w-xl mx-auto leading-relaxed">
                Extract your technical skills against any job description, pinpoint
                missing requirements, and access targeted free courses.
              </p>

              {!user && (
                <div className="mt-8 flex items-center justify-center gap-3">
                  <button
                    onClick={() => handleOpenAuth('signup')}
                    className="py-2.5 px-5 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono uppercase tracking-wider transition shadow-lg shadow-[#FF6A00]/20 cursor-pointer"
                  >
                    Create Free Profile
                  </button>
                  <button
                    onClick={() => handleOpenAuth('login')}
                    className="py-2.5 px-5 rounded-lg bg-[#151515] border border-[#242424] hover:border-[#383838] text-[#F5F5F5] text-xs font-mono uppercase tracking-wider transition cursor-pointer"
                  >
                    Sign In
                  </button>
                </div>
              )}
            </div>

            {/* Step 1: Upload Resume */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono uppercase tracking-widest text-[#A1A1A1]">
                  Step 1: Upload Resume
                </span>
              </div>
              <ResumeUploader
                onAnalyze={handleAnalyzeResume}
                isAnalyzing={isAnalyzing}
                error={resumeError}
                setError={setResumeError}
              />
            </div>

            {/* Extracted Skills */}
            {resumeData && <ExtractedSkillsView resumeData={resumeData} />}

            {/* Resume Quality Score */}
            {resumeData && resumeData.quality && (
              <ResumeQualityView qualityData={resumeData.quality} />
            )}

            {/* Step 2: Job Description Input */}
            {resumeData && (
              <JobDescriptionInput
                onAnalyzeMatch={handleAnalyzeMatch}
                isMatching={isMatching}
                error={matchError}
                setError={setMatchError}
              />
            )}

            {/* Step 3: Match Results & Free Learning Recommendations */}
            {matchData && <MatchResultsView matchData={matchData} />}
          </div>
        )}
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        initialMode={authModalMode}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Minimal Developer Footer */}
      <footer className="border-t border-[#242424] py-8 mt-20 text-center text-xs text-[#666666] font-mono">
        <div className="max-w-4xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>ResumeFit AI • 100% Local & Privacy-Preserving</span>
          <span>FastAPI • React • SQLite • PBKDF2</span>
        </div>
      </footer>
    </div>
  );
}
