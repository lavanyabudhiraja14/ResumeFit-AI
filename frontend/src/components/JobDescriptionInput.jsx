import React, { useState } from 'react';
import { Briefcase, Sparkles, AlertCircle } from 'lucide-react';

const SAMPLE_JOB_DESCRIPTION = `Senior Full-Stack Engineer

About the Role:
We are seeking a Full-Stack Software Engineer to build scalable web applications and microservices.

Key Requirements:
- 3+ years of experience with React, TypeScript, and modern JavaScript
- Strong backend experience with Node.js, Express, or FastAPI
- Proven database expertise in MongoDB and PostgreSQL
- Hands-on experience with Docker containerization and Kubernetes
- Cloud infrastructure knowledge with AWS (EC2, S3, Lambda)
- Familiarity with Redis caching and CI/CD pipelines
- Strong problem-solving and communication skills`;

export default function JobDescriptionInput({ onAnalyzeMatch, isMatching, error, setError }) {
  const [jobText, setJobText] = useState('');

  const handleSampleClick = () => {
    setJobText(SAMPLE_JOB_DESCRIPTION);
    setError(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!jobText.trim() || isMatching) return;

    if (jobText.trim().length < 20) {
      setError('Job description is too short. Please provide at least 20 characters.');
      return;
    }

    onAnalyzeMatch(jobText.trim());
  };

  return (
    <section className="mt-12 pt-10 border-t border-[#242424] animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h2 className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] mb-1">
            Step 2
          </h2>
          <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
            Job Description
          </h3>
        </div>

        <button
          type="button"
          id="load-sample-jd-btn"
          onClick={handleSampleClick}
          disabled={isMatching}
          className="text-xs font-mono text-[#A1A1A1] hover:text-[#FF6A00] flex items-center gap-1.5 transition-colors self-start sm:self-auto cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#FF6A00]" />
          <span>Load Sample Job Description</span>
        </button>
      </div>

      <div className="rounded-xl border border-[#242424] bg-[#151515] p-5">
        <textarea
          id="job-description-textarea"
          rows={7}
          value={jobText}
          onChange={(e) => {
            setJobText(e.target.value);
            if (error) setError(null);
          }}
          placeholder="Paste your job description here..."
          className="w-full bg-[#0A0A0A] border border-[#242424] rounded-lg p-4 text-sm text-[#F5F5F5] placeholder-[#666666] focus:outline-none focus:border-[#FF6A00] transition-colors resize-y leading-relaxed font-sans"
        />

        <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#242424]/60">
          <span className="text-xs font-mono text-[#666666]">
            {jobText.length} characters
          </span>

          <button
            type="button"
            id="analyze-match-btn"
            onClick={handleSubmit}
            disabled={!jobText.trim() || isMatching}
            className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2.5 ${
              !jobText.trim() || isMatching
                ? 'bg-[#1E1E1E] text-[#666666] cursor-not-allowed border border-[#2A2A2A]'
                : 'bg-[#FF6A00] text-black hover:bg-[#FF7A1A] cursor-pointer shadow-sm hover:shadow-[#FF6A00]/20'
            }`}
          >
            {isMatching && (
              <svg
                className="animate-spin -ml-1 h-4 w-4 text-[#FF6A00]"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            )}
            <span>{isMatching ? 'Analyzing Match...' : 'Analyze Match'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3.5 rounded-lg bg-red-950/30 border border-red-900/40 text-red-400 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </section>
  );
}
