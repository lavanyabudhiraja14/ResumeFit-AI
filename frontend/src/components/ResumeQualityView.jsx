import React from 'react';
import { Check, AlertTriangle, ShieldCheck, BarChart3 } from 'lucide-react';

export default function ResumeQualityView({ qualityData }) {
  if (!qualityData || qualityData.overall_score === undefined) return null;

  const {
    overall_score,
    breakdown,
    strengths = [],
    weak_areas = [],
    word_count,
    metrics_detected_count,
  } = qualityData;

  const dimensions = [
    { label: 'Structure', score: breakdown.structure, desc: 'Section completeness & flow' },
    { label: 'Skills', score: breakdown.skills, desc: 'Technical depth & category breadth' },
    { label: 'Experience', score: breakdown.experience, desc: 'Action verbs & measurable outcomes' },
    { label: 'Projects', score: breakdown.projects, desc: 'Portfolio depth & tech integration' },
    { label: 'Readability', score: breakdown.readability, desc: 'Content density & bullet hygiene' },
  ];

  return (
    <div className="p-6 rounded-xl bg-[#151515] border border-[#242424] animate-fade-in mt-8">
      {/* Header & Overall Score */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-[#242424] gap-4">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] block mb-1">
            Deterministic Evaluation
          </span>
          <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-[#FF6A00]" />
            Resume Quality Score
          </h3>
          <p className="text-xs text-[#A1A1A1] mt-1">
            Explainable assessment across 5 structural and technical dimensions
          </p>
        </div>

        <div className="flex items-baseline gap-1.5 self-start sm:self-auto bg-[#111111] px-5 py-2.5 rounded-lg border border-[#242424]">
          <span className="text-4xl font-extrabold font-mono text-[#FF6A00]">
            {overall_score}
          </span>
          <span className="text-sm font-mono text-[#666666]">/ 100</span>
        </div>
      </div>

      {/* 5 Dimensional Progress Bars */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {dimensions.map((dim) => (
          <div
            key={dim.label}
            className="p-3.5 rounded-lg bg-[#111111] border border-[#242424]/80 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium text-[#F5F5F5]">
                {dim.label}
              </span>
              <span className="text-xs font-mono font-semibold text-[#FF6A00]">
                {dim.score}
              </span>
            </div>

            <div className="w-full h-1.5 bg-[#1F1F1F] rounded-full overflow-hidden my-2">
              <div
                className="h-full bg-gradient-to-r from-[#FF6A00] to-[#FF7A1A] rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, dim.score))}%` }}
              />
            </div>

            <span className="text-[10px] text-[#666666] leading-tight line-clamp-1">
              {dim.desc}
            </span>
          </div>
        ))}
      </div>

      {/* Evidence Reasons: Strengths & Weak Areas ("Why?") */}
      <div className="pt-4 border-t border-[#242424]/60">
        <h4 className="text-xs font-mono uppercase tracking-widest text-[#A1A1A1] mb-4">
          Score Breakdown & Evidence
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Observed Strengths */}
          <div className="space-y-2">
            <span className="text-[11px] font-mono text-emerald-400 font-medium block mb-1">
              Observed Strengths
            </span>
            {strengths.map((str, i) => (
              <div
                key={i}
                className="flex items-start gap-2 text-[#D1D1D1] bg-[#111111] p-2.5 rounded-lg border border-emerald-950/40"
              >
                <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span className="leading-relaxed">{str}</span>
              </div>
            ))}
          </div>

          {/* Weak Areas & Identified Gaps */}
          <div className="space-y-2">
            <span className="text-[11px] font-mono text-amber-400 font-medium block mb-1">
              Identified Weak Areas & Gaps
            </span>
            {weak_areas.length > 0 ? (
              weak_areas.map((weak, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-[#D1D1D1] bg-[#111111] p-2.5 rounded-lg border border-amber-950/40"
                >
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{weak}</span>
                </div>
              ))
            ) : (
              <div className="text-emerald-400 text-xs font-mono p-3 bg-[#111111] rounded-lg border border-emerald-950/40">
                ✓ No critical structural gaps detected.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
