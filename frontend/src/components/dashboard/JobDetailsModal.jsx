import React from 'react';
import { X, ExternalLink, MapPin, Building2, Briefcase, Calendar, Check, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function JobDetailsModal({ item, isOpen, onClose }) {
  if (!isOpen || !item) return null;

  const { job, match_percentage, matched_skills = [], missing_skills = [] } = item;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-[#151515] border border-[#242424] rounded-2xl p-6 sm:p-8 shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-[#A1A1A1] hover:text-[#F5F5F5] transition cursor-pointer"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="border-b border-[#242424] pb-6 mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            {job.data_mode === 'live' ? (
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-emerald-950/40 border border-emerald-800/40 text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Live listing • {job.source}
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-[#1A1A1A] border border-[#242424] text-[#888888]">
                Sample listing • {job.source}
              </span>
            )}
            {job.posted_date && job.posted_date !== 'Recent' && (
              <span className="px-2 py-0.5 rounded text-[10px] font-mono text-[#888888] bg-[#111111] border border-[#242424]">
                Posted: {job.posted_date}
              </span>
            )}
            {job.interest_domains && job.interest_domains.map((d) => (
              <span key={d} className="px-2 py-0.5 rounded text-[10px] font-mono text-[#FF6A00] bg-[#FF6A00]/10 border border-[#FF6A00]/20">
                {d}
              </span>
            ))}
          </div>

          <h2 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">
            {job.title}
          </h2>

          <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-[#A1A1A1] font-mono">
            <span className="text-[#F5F5F5] font-semibold">{job.company}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-[#666666]" />
              {job.location}
            </span>
            <span>•</span>
            <span className="capitalize">{job.work_type}</span>
            <span>•</span>
            <span className="capitalize">{job.experience_level} level</span>
          </div>
        </div>

        {/* Resume Fit Match Breakdown if available */}
        {match_percentage !== null && match_percentage !== undefined && (
          <div className="mb-6 p-4 rounded-xl bg-[#0A0A0A] border border-[#242424]">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-[#FF6A00]" />
                <span className="text-xs font-mono uppercase tracking-wider text-[#F5F5F5]">
                  ResumeFit Alignment
                </span>
              </div>
              <span className="text-sm font-mono font-bold text-[#FF6A00]">
                {match_percentage}% Match
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              {/* Matched */}
              <div>
                <span className="text-[11px] font-mono text-emerald-400 block mb-1.5">
                  ✓ Matched Skills ({matched_skills.length}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {matched_skills.length > 0 ? (
                    matched_skills.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#151515] border border-emerald-900/40 text-emerald-300"
                      >
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-[#666666] font-mono">None</span>
                  )}
                </div>
              </div>

              {/* Missing */}
              <div>
                <span className="text-[11px] font-mono text-amber-400 block mb-1.5">
                  ⚠ Missing Skills ({missing_skills.length}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {missing_skills.length > 0 ? (
                    missing_skills.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#151515] border border-amber-900/40 text-amber-300"
                      >
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-emerald-400 font-mono">None! All requirements matched</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Job Description */}
        <div className="space-y-4 text-sm text-[#D1D1D1] leading-relaxed">
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#A1A1A1] mb-2">
              Job Description & Requirements
            </h4>
            <p className="bg-[#0A0A0A] p-4 rounded-xl border border-[#242424] text-xs text-[#A1A1A1] leading-relaxed whitespace-pre-line font-sans">
              {job.description}
            </p>
          </div>

          {/* Extracted Required Skills */}
          {job.skills && job.skills.length > 0 && (
            <div>
              <h4 className="text-xs font-mono uppercase tracking-wider text-[#A1A1A1] mb-2">
                Identified Technical Requirements
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {job.skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded text-xs font-mono text-[#F5F5F5] bg-[#0A0A0A] border border-[#2E2E2E]"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-8 pt-5 border-t border-[#242424] flex items-center justify-between gap-4">
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-lg border border-[#242424] hover:bg-[#1A1A1A] text-xs font-mono text-[#A1A1A1] hover:text-[#F5F5F5] transition cursor-pointer"
          >
            Close
          </button>

          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono uppercase tracking-wider transition shadow-md shadow-[#FF6A00]/20 cursor-pointer"
          >
            <span>Open Job Listing</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
