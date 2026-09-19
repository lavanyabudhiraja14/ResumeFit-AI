import React from 'react';
import { 
  Building2, 
  MapPin, 
  Briefcase, 
  Clock, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  UploadCloud 
} from 'lucide-react';

export default function JobCard({
  item,
  hasResume,
  onViewDetails,
  onUploadResumeClick,
}) {
  const { job, match_percentage, matched_skills = [], missing_skills = [] } = item;

  const formatWorkType = (type) => {
    if (!type) return 'Remote';
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const formatExp = (exp) => {
    if (!exp || exp === 'any') return 'All levels';
    return exp.charAt(0).toUpperCase() + exp.slice(1);
  };

  return (
    <div className="p-6 rounded-xl bg-[#151515] border border-[#242424] hover:border-[#383838] transition flex flex-col justify-between group">
      <div>
        {/* Top Header: Title, Company, Honest Data Badge */}
        <div className="flex items-start justify-between gap-4 mb-2.5">
          <div className="min-w-0">
            <h3 className="text-lg font-bold text-[#F5F5F5] tracking-tight group-hover:text-[#FF6A00] transition-colors truncate">
              {job.title}
            </h3>
            <div className="flex items-center gap-2 mt-0.5 text-xs text-[#A1A1A1]">
              <span className="font-semibold text-[#D1D1D1]">{job.company}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-[#666666]" />
                {job.location}
              </span>
            </div>
          </div>

          {/* Honest Data Badge */}
          {job.data_mode === 'live' ? (
            <span className="shrink-0 flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono tracking-wider uppercase bg-emerald-950/40 border border-emerald-800/40 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live listing
            </span>
          ) : (
            <span className="shrink-0 px-2 py-0.5 rounded text-[10px] font-mono tracking-wider uppercase bg-[#1A1A1A] border border-[#242424] text-[#888888]">
              Sample listing
            </span>
          )}
        </div>

        {/* Metadata Chips: Work Type, Experience, Job Type, Source, Posted Date */}
        <div className="flex flex-wrap items-center gap-2 my-3 text-xs font-mono text-[#888888]">
          <span className="px-2 py-0.5 rounded bg-[#0A0A0A] border border-[#242424]">
            {formatWorkType(job.work_type)}
          </span>
          <span className="px-2 py-0.5 rounded bg-[#0A0A0A] border border-[#242424]">
            {formatExp(job.experience_level)}
          </span>
          {job.job_type && (
            <span className="px-2 py-0.5 rounded bg-[#0A0A0A] border border-[#242424] capitalize">
              {job.job_type}
            </span>
          )}
          {job.source && (
            <span className="px-2 py-0.5 rounded bg-[#0A0A0A] border border-[#242424] text-[#A1A1A1]">
              Source: {job.source}
            </span>
          )}
          {job.posted_date && job.posted_date !== "Recent" && (
            <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#0A0A0A] border border-[#242424] text-[#888888]">
              <Clock className="w-3 h-3 text-[#666666]" />
              {job.posted_date}
            </span>
          )}
        </div>

        {/* Short Description */}
        <p className="text-xs text-[#A1A1A1] line-clamp-2 leading-relaxed mb-4">
          {job.description}
        </p>

        {/* Relevant Interest Domains */}
        {job.interest_domains && job.interest_domains.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 mb-4">
            <span className="text-[11px] font-mono text-[#666666] mr-1">Domains:</span>
            {job.interest_domains.map((domain) => (
              <span
                key={domain}
                className="px-2 py-0.5 rounded text-[11px] font-mono text-[#F5F5F5] bg-[#0A0A0A] border border-[#2E2E2E]"
              >
                {domain}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Resume Match or Recommendation Banner */}
      <div className="pt-4 border-t border-[#242424] mt-2">
        {hasResume && match_percentage !== null && match_percentage !== undefined ? (
          <div className="space-y-3">
            {/* Match Score */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="px-2.5 py-1 rounded bg-[#FF6A00]/10 border border-[#FF6A00]/30 text-[#FF6A00] text-xs font-mono font-bold">
                  {match_percentage}% Resume Match
                </div>
              </div>
              <span className="text-[11px] font-mono text-[#666666]">
                {matched_skills.length} matched • {missing_skills.length} missing
              </span>
            </div>

            {/* Matched Skills */}
            {matched_skills.length > 0 && (
              <div className="text-xs">
                <span className="text-[11px] font-mono text-emerald-400 block mb-1">
                  ✓ Matched:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {matched_skills.slice(0, 5).map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#111111] border border-emerald-900/40 text-emerald-300"
                    >
                      {s}
                    </span>
                  ))}
                  {matched_skills.length > 5 && (
                    <span className="text-[10px] font-mono text-[#666666] self-center">
                      +{matched_skills.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {missing_skills.length > 0 && (
              <div className="text-xs">
                <span className="text-[11px] font-mono text-amber-400 block mb-1">
                  ⚠ Missing:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {missing_skills.slice(0, 4).map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#111111] border border-amber-900/40 text-amber-300"
                    >
                      {s}
                    </span>
                  ))}
                  {missing_skills.length > 4 && (
                    <span className="text-[10px] font-mono text-[#666666] self-center">
                      +{missing_skills.length - 4} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-[#0A0A0A] border border-[#242424]">
            <div className="flex items-center gap-2 text-xs">
              <Sparkles className="w-4 h-4 text-[#FF6A00] shrink-0" />
              <span className="text-[#D1D1D1] font-medium">
                Recommended for your interests
              </span>
            </div>
            <button
              onClick={onUploadResumeClick}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono text-[#FF6A00] hover:bg-[#FF6A00]/10 border border-[#FF6A00]/30 transition cursor-pointer"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload Resume</span>
            </button>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between gap-3 mt-5 pt-3 border-t border-[#1F1F1F]">
          <button
            onClick={() => onViewDetails(item)}
            className="text-xs font-mono text-[#A1A1A1] hover:text-[#F5F5F5] underline underline-offset-4 transition cursor-pointer"
          >
            View Full Requirements
          </button>

          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0A0A0A] border border-[#242424] hover:border-[#FF6A00] text-xs font-mono text-[#F5F5F5] hover:text-[#FF6A00] transition cursor-pointer"
          >
            <span>View Job</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
