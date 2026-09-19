import React from 'react';
import { CheckCircle2, AlertCircle, Mail, Phone, Linkedin, Github, FileCheck2 } from 'lucide-react';

export default function ATSCompatibilityView({ atsData }) {
  if (!atsData || atsData.compatibility_score === undefined) return null;

  const {
    compatibility_score,
    contact = {},
    sections = {},
    positive_signals = [],
    potential_issues = [],
    missing_job_keywords = [],
  } = atsData;

  const contactItems = [
    { label: 'Email', present: contact.email, icon: Mail },
    { label: 'Phone', present: contact.phone, icon: Phone },
    { label: 'LinkedIn', present: contact.linkedin, icon: Linkedin },
    { label: 'GitHub / Portfolio', present: contact.github, icon: Github },
  ];

  return (
    <div className="p-6 rounded-xl bg-[#151515] border border-[#242424] animate-fade-in mt-8">
      {/* Header & ATS Score */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-6 border-b border-[#242424] gap-4">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-[#FF6A00] block mb-1">
            Parser Readiness
          </span>
          <h3 className="text-xl font-semibold text-[#F5F5F5] tracking-tight flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-[#FF6A00]" />
            ATS Compatibility Analysis
          </h3>
          <p className="text-xs text-[#A1A1A1] mt-1">
            Structural heading hygiene, contact verification, and keyword readiness
          </p>
        </div>

        <div className="flex items-baseline gap-1.5 self-start sm:self-auto bg-[#111111] px-5 py-2.5 rounded-lg border border-[#242424]">
          <span className="text-4xl font-extrabold font-mono text-[#FF6A00]">
            {compatibility_score}%
          </span>
        </div>
      </div>

      {/* Contact Information Verification Checklist */}
      <div className="mb-6">
        <span className="text-xs font-mono uppercase tracking-widest text-[#A1A1A1] block mb-3">
          Contact Details Detection
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {contactItems.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className={`p-3 rounded-lg border text-xs font-mono flex items-center justify-between transition-colors ${
                  item.present
                    ? 'bg-[#111111] border-emerald-950/60 text-[#F5F5F5]'
                    : 'bg-[#111111] border-[#2A2A2A] text-[#666666]'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${item.present ? 'text-emerald-400' : 'text-[#666666]'}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.present ? (
                  <span className="text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded ml-1">
                    Found
                  </span>
                ) : (
                  <span className="text-[10px] text-amber-400/80 bg-amber-950/30 px-1.5 py-0.5 rounded ml-1">
                    Missing
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Positive Signals & Potential ATS Issues */}
      <div className="pt-4 border-t border-[#242424]/60">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Positive Signals */}
          <div className="space-y-2">
            <span className="text-[11px] font-mono text-emerald-400 font-medium block mb-1">
              Confirmed Compatible Signals
            </span>
            {positive_signals.map((sig, i) => (
              <div
                key={i}
                className="flex items-start gap-2 text-[#D1D1D1] bg-[#111111] p-2.5 rounded-lg border border-emerald-950/40"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span className="leading-relaxed">{sig}</span>
              </div>
            ))}
          </div>

          {/* Potential Issues */}
          <div className="space-y-2">
            <span className="text-[11px] font-mono text-amber-400 font-medium block mb-1">
              Potential ATS Issues to Address
            </span>
            {potential_issues.length > 0 ? (
              potential_issues.map((issue, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-[#D1D1D1] bg-[#111111] p-2.5 rounded-lg border border-amber-950/40"
                >
                  <AlertCircle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{issue}</span>
                </div>
              ))
            ) : (
              <div className="text-emerald-400 text-xs font-mono p-3 bg-[#111111] rounded-lg border border-emerald-950/40">
                ✓ No critical ATS parsing obstacles detected.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
