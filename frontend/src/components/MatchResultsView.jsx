import React from 'react';
import { Check, X, ExternalLink, PlayCircle, Clock, Award } from 'lucide-react';

export default function MatchResultsView({ matchData }) {
  if (!matchData) return null;

  const {
    match_percentage,
    matched_skills,
    missing_skills,
    recommendations,
    score_breakdown,
  } = matchData;

  return (
    <section className="mt-14 pt-12 border-t border-[#242424] animate-fade-in">
      {/* 1. Main Match Score Hero (Visually Focused) */}
      <div className="flex flex-col items-center justify-center text-center py-8">
        <div className="relative flex items-center justify-center mb-3">
          <span className="text-7xl md:text-8xl font-black tracking-tighter text-[#FF6A00] font-mono">
            {match_percentage}%
          </span>
        </div>

        <p className="text-sm font-mono tracking-widest uppercase text-[#A1A1A1] mb-6">
          Job Match
        </p>

        <div className="w-48 h-[1px] bg-gradient-to-r from-transparent via-[#FF6A00]/40 to-transparent mb-6" />

        {/* Explainable Score Summary */}
        {score_breakdown?.formula_explanation && (
          <p className="max-w-xl text-xs sm:text-sm text-[#A1A1A1] leading-relaxed bg-[#151515] px-5 py-3 rounded-lg border border-[#242424]">
            {score_breakdown.formula_explanation}
          </p>
        )}
      </div>

      {/* 2. Skills You Have vs Skills Missing (Clean Typography & Whitespace) */}
      <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Skills You Have */}
        <div className="p-6 rounded-xl bg-[#151515] border border-[#242424]">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#242424]">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-emerald-950/80 border border-emerald-600/30 flex items-center justify-center">
                <Check className="w-3 h-3 text-emerald-400" />
              </div>
              <h3 className="text-sm font-semibold text-[#F5F5F5] uppercase tracking-wider">
                Skills You Have
              </h3>
            </div>
            <span className="text-xs font-mono text-[#A1A1A1]">
              {matched_skills.length} matched
            </span>
          </div>

          {matched_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {matched_skills.map((skill) => (
                <div
                  key={skill.name}
                  className="px-3 py-1.5 rounded-lg bg-[#111111] border border-emerald-900/30 text-xs font-mono text-[#F5F5F5] flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span>{skill.name}</span>
                  {skill.match_type === 'semantic' && skill.transferred_from && (
                    <span className="text-[10px] text-[#A1A1A1] opacity-70">
                      (via {skill.transferred_from})
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#666666] font-mono py-2">
              No direct or transferable skills found for this role.
            </p>
          )}
        </div>

        {/* Skills Missing */}
        <div className="p-6 rounded-xl bg-[#151515] border border-[#242424]">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#242424]">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-red-950/80 border border-red-600/30 flex items-center justify-center">
                <X className="w-3 h-3 text-red-400" />
              </div>
              <h3 className="text-sm font-semibold text-[#F5F5F5] uppercase tracking-wider">
                Skills Missing
              </h3>
            </div>
            <span className="text-xs font-mono text-[#A1A1A1]">
              {missing_skills.length} missing
            </span>
          </div>

          {missing_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2.5">
              {missing_skills.map((skill) => (
                <div
                  key={skill.name}
                  className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#2E2E2E] text-xs font-mono text-[#A1A1A1] flex items-center gap-1.5"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#FF6A00]" />
                  <span>{skill.name}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-emerald-400 font-mono py-2">
              Outstanding match! You possess all required technical skills.
            </p>
          )}
        </div>
      </div>

      {/* 3. Upskilling Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="mt-14">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] mb-1">
                Bridge The Gap
              </h2>
              <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
                Upskill Yourself
              </h3>
            </div>
            <span className="text-xs font-mono text-[#A1A1A1] bg-[#151515] px-3 py-1 rounded border border-[#242424]">
              Free Learning Resources
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec, idx) => (
              <div
                key={`${rec.skill}-${idx}`}
                className="p-5 rounded-xl bg-[#151515] border border-[#242424] hover:border-[#FF6A00]/40 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2.5">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono text-[#FF6A00] bg-[#FF6A00]/10 border border-[#FF6A00]/20">
                      Missing Skill: {rec.skill}
                    </span>
                    <span className="text-[11px] font-mono text-[#666666] flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {rec.duration}
                    </span>
                  </div>

                  <h4 className="text-sm font-medium text-[#F5F5F5] group-hover:text-[#FF6A00] transition-colors line-clamp-2 mb-1.5">
                    {rec.title}
                  </h4>

                  <p className="text-xs text-[#A1A1A1]">
                    By {rec.creator} • {rec.platform}
                  </p>
                </div>

                <div className="mt-5 pt-3 border-t border-[#242424] flex items-center justify-between">
                  <span className="text-xs text-[#666666]">
                    {rec.level || 'Free Video Course'}
                  </span>
                  <a
                    href={rec.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#FF6A00] hover:text-[#FF7A1A] transition-colors"
                  >
                    <span>Watch Course</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
