import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  FileText, 
  Search, 
  Settings2, 
  Briefcase, 
  Filter, 
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  UploadCloud,
  Loader2,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  MapPin
} from 'lucide-react';
import JobCard from './JobCard';
import JobDetailsModal from './JobDetailsModal';
import { getRecommendedJobs, analyzeResume, saveUserResume } from '../../services/api';

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

export default function DashboardView({
  user,
  onNavigateToResume,
  onEditInterests,
  onUserUpdate,
}) {
  const greeting = getGreeting();
  const interestsList = user?.interests || [];
  const hasResume = Boolean(user?.resume_skills && user.resume_skills.length > 0);

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedWorkType, setSelectedWorkType] = useState('any');
  const [selectedMinMatch, setSelectedMinMatch] = useState('all');
  const [selectedDataMode, setSelectedDataMode] = useState('live');
  const [feedMeta, setFeedMeta] = useState({ source: 'Public Live Feeds', data_mode: 'live' });

  // Job Details Modal
  const [selectedJobItem, setSelectedJobItem] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  // Resume upload state
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);

    try {
      // Determine interest filter: if user chose a specific domain, pass that; otherwise pass all user interests
      let activeInterests = interestsList;
      if (selectedDomain !== 'all') {
        activeInterests = [selectedDomain];
      }

      const params = {
        interests: activeInterests,
        search: search.trim(),
        location: selectedLocation !== 'all' ? selectedLocation : '',
        work_type: selectedWorkType,
        data_mode: selectedDataMode,
      };

      if (hasResume && selectedMinMatch !== 'all') {
        params.min_match = parseInt(selectedMinMatch, 10);
      }

      const data = await getRecommendedJobs(params);
      setJobs(data.results || []);
      setFeedMeta({
        source: data.source || 'Public Live Job Feeds',
        data_mode: data.data_mode || selectedDataMode,
      });
    } catch (err) {
      setError(err.message || 'Failed to load personalized jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [user?.interests, user?.resume_skills, selectedDomain, selectedLocation, selectedWorkType, selectedMinMatch, selectedDataMode]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchJobs();
  };

  const handleViewDetails = (item) => {
    setSelectedJobItem(item);
    setModalOpen(true);
  };

  // Direct resume upload handler
  const handleResumeFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingResume(true);
    setUploadError(null);

    try {
      const parsed = await analyzeResume(file);
      const rawSkills = parsed.raw_skills || [];

      // Persist to user profile
      const updatedUser = await saveUserResume(file.name, rawSkills);
      if (onUserUpdate) {
        onUserUpdate(updatedUser);
      }

      // Re-fetch jobs with fresh resume skills
      await fetchJobs();
    } catch (err) {
      setUploadError(err.message || 'Failed to analyze and save resume.');
    } finally {
      setUploadingResume(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-5xl w-full mx-auto px-6 py-12 space-y-8">
      {/* Hidden File Input for Resume Upload */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleResumeFileSelect}
        accept=".pdf,.docx,.jpg,.jpeg,.png"
        className="hidden"
      />

      {/* Top Header Card */}
      <div className="border border-[#242424] bg-[#151515] rounded-2xl p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#FF6A00]" />
              <span className="text-xs font-mono uppercase tracking-widest text-[#FF6A00]">
                Personalized Career Hub
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F5F5F5] tracking-tight mt-1.5">
              {greeting} 👋 {user?.name ? user.name.split(' ')[0] : ''}
            </h1>
            <p className="text-sm text-[#A1A1A1] mt-1">
              Live match benchmarks and curated roles tailored to your career focus.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={onEditInterests}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#0A0A0A] border border-[#242424] text-xs font-mono text-[#A1A1A1] hover:text-[#F5F5F5] hover:border-[#FF6A00]/50 transition cursor-pointer"
            >
              <Settings2 className="w-3.5 h-3.5 text-[#FF6A00]" />
              <span>Edit Interests</span>
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingResume}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono transition cursor-pointer disabled:opacity-50"
            >
              {uploadingResume ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <UploadCloud className="w-3.5 h-3.5" />
              )}
              <span>{hasResume ? 'Update Resume' : 'Upload Resume'}</span>
            </button>
          </div>
        </div>

        {/* User Saved Interests Bar */}
        <div className="mt-6 pt-5 border-t border-[#242424]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2.5">
            <span className="text-xs font-mono uppercase tracking-wider text-[#A1A1A1]">
              Your Interests
            </span>
            <span className="text-[11px] font-mono text-[#666666]">
              Matching any of your {interestsList.length} chosen fields
            </span>
          </div>

          {interestsList.length > 0 ? (
            <div className="flex flex-wrap items-center gap-2">
              {interestsList.map((interest) => (
                <span
                  key={interest}
                  className="px-3 py-1.5 rounded-md bg-[#0A0A0A] border border-[#FF6A00]/30 text-[#F5F5F5] text-xs font-mono tracking-wide flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#FF6A00]" />
                  <span className="capitalize">{interest.replace(/([a-z])([A-Z])/g, '$1 $2')}</span>
                </span>
              ))}
            </div>
          ) : (
            <button
              onClick={onEditInterests}
              className="text-xs text-[#FF6A00] hover:underline"
            >
              + Select your career interests to personalize your feed
            </button>
          )}
        </div>

        {/* Active Resume Status Pill */}
        {hasResume && (
          <div className="mt-4 pt-4 border-t border-[#242424]/60 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2 text-[#D1D1D1]">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Active Resume: <strong>{user.resume_filename || 'Uploaded Document'}</strong></span>
              <span className="text-[#666666]">•</span>
              <span className="text-emerald-400 font-semibold">{user.resume_skills.length} skills analyzed</span>
            </div>
            <button
              onClick={onNavigateToResume}
              className="text-[#FF6A00] hover:underline text-[11px]"
            >
              Full Analysis & Quality Score →
            </button>
          </div>
        )}

        {/* Upload Error Banner */}
        {uploadError && (
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Honest Data Disclosure Notice (Step 2 compliance) */}
      <div className="p-3.5 rounded-xl bg-[#111111] border border-[#242424] flex items-center justify-between gap-4 text-xs font-mono text-[#888888]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          <span>
            <strong>Data Mode:</strong> Displaying curated development tech listings linking to official careers pages. Provider ready for live API integration.
          </span>
        </div>
        <span className="hidden sm:inline text-[11px] text-[#555555]">
          Curated Tech Provider
        </span>
      </div>

      {/* No Resume Callout Banner (if candidate hasn't uploaded yet) */}
      {!hasResume && (
        <div className="p-5 rounded-xl bg-[#151515] border border-[#FF6A00]/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#FF6A00]/10 border border-[#FF6A00]/20 flex items-center justify-center shrink-0 text-[#FF6A00]">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-[#F5F5F5] tracking-tight">
                Unlock Real ResumeFit Matching
              </h4>
              <p className="text-xs text-[#A1A1A1] mt-0.5 leading-relaxed">
                Upload your resume to benchmark your exact skills against every listing and calculate real percentage matches.
              </p>
            </div>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingResume}
            className="px-4 py-2 rounded-lg bg-[#0A0A0A] border border-[#FF6A00]/40 text-[#FF6A00] hover:bg-[#FF6A00]/10 font-mono text-xs transition shrink-0 cursor-pointer flex items-center gap-1.5"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload Resume Now</span>
          </button>
        </div>
      )}

      {/* Filters Toolbar */}
      <div className="space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#666666] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by job title, company, or technical skills..."
              className="w-full pl-10 pr-4 py-2.5 bg-[#151515] border border-[#242424] rounded-xl text-xs sm:text-sm text-[#F5F5F5] placeholder-[#666666] focus:border-[#FF6A00] outline-none transition"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-[#1A1A1A] hover:bg-[#222222] border border-[#242424] text-xs font-mono text-[#F5F5F5] rounded-xl transition cursor-pointer"
          >
            Search
          </button>
        </form>

        {/* Dropdown Filters & Domain Pills */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
          {/* Domain Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setSelectedDomain('all')}
              className={`px-3 py-1.5 rounded-lg border transition cursor-pointer ${
                selectedDomain === 'all'
                  ? 'bg-[#FF6A00] text-black border-[#FF6A00] font-semibold'
                  : 'bg-[#151515] text-[#A1A1A1] border-[#242424] hover:border-[#383838]'
              }`}
            >
              All My Interests
            </button>
            {interestsList.map((interest) => (
              <button
                key={interest}
                onClick={() => setSelectedDomain(interest)}
                className={`px-3 py-1.5 rounded-lg border transition capitalize cursor-pointer ${
                  selectedDomain === interest
                    ? 'bg-[#FF6A00] text-black border-[#FF6A00] font-semibold'
                    : 'bg-[#151515] text-[#A1A1A1] border-[#242424] hover:border-[#383838]'
                }`}
              >
                {interest}
              </button>
            ))}
          </div>

          {/* Right-aligned dropdown filters */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Location Selector */}
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-[#151515] border border-[#242424] text-[#A1A1A1] focus:border-[#FF6A00] outline-none cursor-pointer"
            >
              <option value="all">All Locations</option>
              <option value="Remote">Remote</option>
              <option value="Bengaluru">Bengaluru</option>
              <option value="Hyderabad">Hyderabad</option>
              <option value="Delhi NCR">Delhi NCR</option>
              <option value="Mumbai">Mumbai</option>
              <option value="Pune">Pune</option>
              <option value="Chennai">Chennai</option>
            </select>

            {/* Work Type Selector */}
            <select
              value={selectedWorkType}
              onChange={(e) => setSelectedWorkType(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-[#151515] border border-[#242424] text-[#A1A1A1] focus:border-[#FF6A00] outline-none cursor-pointer"
            >
              <option value="any">Work Type: Any</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
            </select>

            {/* Resume Match Filter (ONLY shown when resume exists) */}
            {hasResume && (
              <select
                value={selectedMinMatch}
                onChange={(e) => setSelectedMinMatch(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-[#151515] border border-[#FF6A00]/40 text-[#FF6A00] focus:border-[#FF6A00] outline-none cursor-pointer"
              >
                <option value="all">Match: Any %</option>
                <option value="50">50%+ Match</option>
                <option value="60">60%+ Match</option>
                <option value="70">70%+ Match</option>
                <option value="80">80%+ Match</option>
              </select>
            )}
          </div>
        </div>
      </div>

      {/* Live Data Disclosure & Mode Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 rounded-xl bg-[#111111] border border-[#242424] text-xs font-mono">
        <div className="flex items-center gap-2">
          {feedMeta.data_mode === 'live' ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
              <span className="text-[#F5F5F5] font-medium">Live Listings</span>
              <span className="text-[#555555]">•</span>
              <span className="text-[#888888] text-[11px]">
                Aggregated from public career and job feeds (Greenhouse, Lever, Ashby, Jobicy)
              </span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0"></span>
              <span className="text-[#F5F5F5] font-medium">Curated Sample Listings</span>
              <span className="text-[#555555]">•</span>
              <span className="text-[#888888] text-[11px]">Development & testing mode</span>
            </>
          )}
        </div>

        {/* Data Mode Switcher */}
        <div className="flex items-center gap-1 p-0.5 rounded-lg bg-[#0A0A0A] border border-[#242424]">
          <button
            onClick={() => setSelectedDataMode('live')}
            className={`px-2.5 py-1 rounded text-[11px] font-mono transition cursor-pointer ${
              selectedDataMode === 'live'
                ? 'bg-[#1A1A1A] text-emerald-400 font-semibold border border-emerald-900/50'
                : 'text-[#888888] hover:text-[#D1D1D1]'
            }`}
          >
            Live Feeds
          </button>
          <button
            onClick={() => setSelectedDataMode('curated')}
            className={`px-2.5 py-1 rounded text-[11px] font-mono transition cursor-pointer ${
              selectedDataMode === 'curated'
                ? 'bg-[#1A1A1A] text-amber-400 font-semibold border border-amber-900/50'
                : 'text-[#888888] hover:text-[#D1D1D1]'
            }`}
          >
            Curated Dev
          </button>
        </div>
      </div>

      {/* Feed Header */}
      <div className="flex items-center justify-between pt-4 border-t border-[#242424]">
        <h2 className="text-lg font-bold text-[#F5F5F5] tracking-tight flex items-center gap-2">
          <span>Personalized Tech Jobs</span>
          <span className="text-xs font-mono font-normal px-2 py-0.5 rounded-full bg-[#1A1A1A] border border-[#242424] text-[#A1A1A1]">
            {jobs.length} roles found
          </span>
        </h2>

        <button
          onClick={fetchJobs}
          title="Refresh listings"
          className="p-1.5 rounded-lg bg-[#151515] border border-[#242424] text-[#A1A1A1] hover:text-[#F5F5F5] transition cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 text-[#A1A1A1] space-y-3">
          <Loader2 className="w-7 h-7 animate-spin text-[#FF6A00]" />
          <span className="text-xs font-mono">Curating jobs matching your interests...</span>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="p-6 rounded-xl bg-red-950/20 border border-red-900/40 text-red-400 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchJobs}
            className="px-3 py-1 bg-red-900/30 rounded hover:bg-red-900/50 transition cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty State: No Interests */}
      {!loading && !error && interestsList.length === 0 && (
        <div className="p-12 rounded-2xl bg-[#151515] border border-dashed border-[#282828] text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#0A0A0A] border border-[#242424] flex items-center justify-center mx-auto text-[#FF6A00]">
            <Briefcase className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-[#F5F5F5]">
            Tell us what you're interested in
          </h3>
          <p className="text-xs text-[#A1A1A1] max-w-sm mx-auto">
            Select your technical career interests so ResumeFit can filter and rank the most relevant tech roles for you.
          </p>
          <button
            onClick={onEditInterests}
            className="px-5 py-2.5 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono transition cursor-pointer"
          >
            Choose Interests
          </button>
        </div>
      )}

      {/* Empty State: No Matching Jobs for Filter or Live Unavailable */}
      {!loading && !error && interestsList.length > 0 && jobs.length === 0 && (
        <div className="p-12 rounded-2xl bg-[#151515] border border-dashed border-[#282828] text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#0A0A0A] border border-[#242424] flex items-center justify-center mx-auto text-[#A1A1A1]">
            <Search className="w-6 h-6" />
          </div>

          {feedMeta.data_mode === 'live' && !search && selectedLocation === 'all' && selectedWorkType === 'any' && selectedDomain === 'all' ? (
            <>
              <h3 className="text-lg font-bold text-[#F5F5F5]">
                Live job listings are temporarily unavailable
              </h3>
              <p className="text-xs text-[#A1A1A1] max-w-md mx-auto">
                The public career feeds may be experiencing high latency or temporary downtime. You can retry or switch to curated development listings.
              </p>
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={fetchJobs}
                  className="px-4 py-2 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono transition cursor-pointer"
                >
                  Retry Feeds
                </button>
                <button
                  onClick={() => setSelectedDataMode('curated')}
                  className="px-4 py-2 rounded-lg bg-[#0A0A0A] border border-[#242424] text-xs font-mono text-[#F5F5F5] hover:border-[#FF6A00] transition cursor-pointer"
                >
                  Switch to Curated Dev
                </button>
              </div>
            </>
          ) : (
            <>
              <h3 className="text-lg font-bold text-[#F5F5F5]">
                No jobs found for your current filters
              </h3>
              <p className="text-xs text-[#A1A1A1] max-w-md mx-auto">
                Try adjusting your search keywords, broadening your location/work type filters, or adding more career interests.
              </p>
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={() => {
                    setSearch('');
                    setSelectedDomain('all');
                    setSelectedLocation('all');
                    setSelectedWorkType('any');
                    setSelectedMinMatch('all');
                  }}
                  className="px-4 py-2 rounded-lg bg-[#0A0A0A] border border-[#242424] text-xs font-mono text-[#F5F5F5] hover:border-[#FF6A00] transition cursor-pointer"
                >
                  Reset Filters
                </button>
                <button
                  onClick={onEditInterests}
                  className="px-4 py-2 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono transition cursor-pointer"
                >
                  Edit Interests
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Jobs Grid */}
      {!loading && !error && jobs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {jobs.map((item) => (
            <JobCard
              key={item.job.id}
              item={item}
              hasResume={hasResume}
              onViewDetails={handleViewDetails}
              onUploadResumeClick={() => fileInputRef.current?.click()}
            />
          ))}
        </div>
      )}

      {/* Job Details Modal */}
      <JobDetailsModal
        item={selectedJobItem}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedJobItem(null);
        }}
      />
    </div>
  );
}
