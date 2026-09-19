import React from 'react';
import { Lightbulb, ArrowUpRight, Sparkles, AlertCircle } from 'lucide-react';

export default function ImprovementSuggestionsView({ suggestionsData }) {
  if (!suggestionsData || !suggestionsData.suggestions || suggestionsData.suggestions.length === 0) {
    return null;
  }

  const { suggestions, total_suggestions } = suggestionsData;

  const getPriorityColor = (priority) => {
    if (priority === 'High Impact') {
      return 'text-[#FF6A00] bg-[#FF6A00]/10 border-[#FF6A00]/30';
    }
    return 'text-[#A1A1A1] bg-[#1F1F1F] border-[#333333]';
  };

  return (
    <div className="p-6 rounded-xl bg-[#151515] border border-[#242424] animate-fade-in mt-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-[#242424] gap-4">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] block mb-1">
            Grounded Guidance
          </span>
          <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-[#FF6A00]" />
            Resume Improvement Suggestions
          </h3>
          <p className="text-xs text-[#A1A1A1] mt-1">
            Actionable enhancements based solely on your existing content (no fabricated facts or metrics)
          </p>
        </div>

        <div className="flex items-center gap-1.5 self-start sm:self-auto bg-[#111111] px-3.5 py-1.5 rounded-lg border border-[#242424]">
          <span className="text-xs font-mono text-[#FF6A00] font-semibold">
            {total_suggestions}
          </span>
          <span className="text-xs font-mono text-[#A1A1A1]">Action Items</span>
        </div>
      </div>

      {/* Suggestion Cards */}
      <div className="space-y-4">
        {suggestions.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-xl bg-[#111111] border border-[#242424] hover:border-[#333333] transition-colors"
          >
            <div className="flex items-center justify-between gap-3 mb-2.5">
              <span className="text-xs font-mono font-medium text-[#F5F5F5] uppercase tracking-wider bg-[#1A1A1A] px-2.5 py-1 rounded border border-[#2A2A2A]">
                {item.category}
              </span>
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${getPriorityColor(item.priority)}`}>
                {item.priority}
              </span>
            </div>

            {/* Problem & Explanation */}
            <div className="mb-3">
              <p className="text-sm font-medium text-[#F5F5F5] mb-1">
                {item.problem}
              </p>
              <p className="text-xs text-[#A1A1A1] leading-relaxed">
                {item.explanation}
              </p>
            </div>

            {/* Suggested Improvement */}
            <div className="pt-3 border-t border-[#242424]/70 bg-[#151515]/60 p-3 rounded-lg border border-[#242424]/50">
              <span className="text-[11px] font-mono uppercase tracking-widest text-[#FF6A00] block mb-1">
                Actionable Recommendation
              </span>
              <p className="text-xs text-[#E5E5E5] leading-relaxed font-sans">
                {item.suggested_improvement}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
