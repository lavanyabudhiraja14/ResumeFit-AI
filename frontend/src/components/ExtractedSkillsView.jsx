import React from 'react';
import { CheckCircle2, Layers } from 'lucide-react';

export default function ExtractedSkillsView({ resumeData }) {
  if (!resumeData || !resumeData.raw_skills || resumeData.raw_skills.length === 0) {
    return null;
  }

  const { total_skills_count, skills_by_category, raw_skills, filename } = resumeData;

  return (
    <section className="mt-12 pt-10 border-t border-[#242424] animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h2 className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] mb-1">
            Step 1 Complete
          </h2>
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight">
              Your Skills
            </h3>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-[#1A1A1A] border border-[#242424] text-[#A1A1A1]">
              {total_skills_count} detected
            </span>
          </div>
        </div>
        <p className="text-xs text-[#A1A1A1] font-mono truncate max-w-xs">
          Source: {filename}
        </p>
      </div>

      {/* Categorized Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(skills_by_category).map(([category, skills]) => (
          <div
            key={category}
            className="p-4 rounded-xl bg-[#151515] border border-[#242424] hover:border-[#333333] transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-[#A1A1A1] tracking-wide">
                {category}
              </span>
              <span className="text-[11px] font-mono text-[#666666]">
                {skills.length}
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <span
                  key={skill}
                  className="px-2.5 py-1 rounded-md text-xs font-mono text-[#F5F5F5] bg-[#111111] border border-[#242424] hover:border-[#FF6A00]/40 transition-colors"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
