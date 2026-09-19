import React, { useState, useEffect } from 'react';
import { Check, ArrowRight, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { getInterestsTaxonomy, updateUserInterests } from '../../services/api';

export default function InterestSelectionView({ initialInterests = [], onComplete }) {
  const [taxonomy, setTaxonomy] = useState(null);
  const [selectedInterests, setSelectedInterests] = useState(new Set(initialInterests));
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    getInterestsTaxonomy()
      .then((data) => {
        if (mounted) {
          setTaxonomy(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || 'Failed to load interest categories.');
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  const toggleInterest = (id) => {
    setSelectedInterests((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleContinue = async () => {
    if (selectedInterests.size === 0) {
      setError('Please choose at least one field of interest to continue.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const interestsArray = Array.from(selectedInterests);
      const result = await updateUserInterests(interestsArray);
      onComplete(result);
    } catch (err) {
      setError(err.message || 'Failed to save interests. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const selectedCount = selectedInterests.size;

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* Top Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#151515] border border-[#242424] text-xs font-mono text-[#A1A1A1] mb-4">
          <span className="w-1.5 h-1.5 rounded-full bg-[#FF6A00]" />
          <span>STEP 2 OF 2 • ONBOARDING</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F5F5F5] tracking-tight">
          What are you interested in?
        </h1>
        <p className="text-base text-[#A1A1A1] mt-3 leading-relaxed">
          Choose as many fields as you want. We'll use your interests to personalize your job feed.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-2xl mx-auto mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-2 text-red-400 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16 text-[#A1A1A1] space-y-3">
          <Loader2 className="w-6 h-6 animate-spin text-[#FF6A00]" />
          <span className="text-xs font-mono">Loading career interests...</span>
        </div>
      )}

      {/* Categorized Taxonomy */}
      {taxonomy && (
        <div className="space-y-8">
          {taxonomy.categories.map((category) => (
            <div key={category.category} className="space-y-3">
              <div className="flex items-baseline justify-between border-b border-[#242424] pb-2">
                <h3 className="text-sm font-mono uppercase tracking-wider text-[#A1A1A1]">
                  {category.category}
                </h3>
                <span className="text-xs text-[#666666] hidden sm:inline">
                  {category.description}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {category.items.map((item) => {
                  const isSelected = selectedInterests.has(item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggleInterest(item.id)}
                      className={`group relative text-left p-4 rounded-xl border transition-all duration-150 cursor-pointer flex items-start justify-between gap-3 ${
                        isSelected
                          ? 'bg-[#FF6A00]/10 border-[#FF6A00] text-[#F5F5F5] shadow-sm'
                          : 'bg-[#151515] border-[#242424] text-[#A1A1A1] hover:border-[#383838] hover:text-[#F5F5F5]'
                      }`}
                    >
                      <div className="min-w-0 pr-2">
                        <div className="text-sm font-semibold tracking-tight text-[#F5F5F5]">
                          {item.name}
                        </div>
                        {item.description && (
                          <div className="text-xs text-[#888888] mt-1 line-clamp-2 leading-relaxed">
                            {item.description}
                          </div>
                        )}
                      </div>

                      {/* Selection Indicator Checkbox */}
                      <div
                        className={`w-5 h-5 rounded flex items-center justify-center shrink-0 mt-0.5 border transition ${
                          isSelected
                            ? 'bg-[#FF6A00] border-[#FF6A00] text-black'
                            : 'border-[#333333] group-hover:border-[#555555]'
                        }`}
                      >
                        {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Floating Bottom Sticky Bar */}
      <div className="sticky bottom-6 mt-12 pt-4">
        <div className="max-w-2xl mx-auto p-4 rounded-2xl bg-[#151515]/95 backdrop-blur-md border border-[#242424] shadow-2xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-[#F5F5F5]">
            <span className="font-mono font-bold text-[#FF6A00] px-2 py-0.5 rounded bg-[#FF6A00]/10 border border-[#FF6A00]/20">
              {selectedCount}
            </span>
            <span className="text-xs sm:text-sm text-[#A1A1A1]">
              {selectedCount === 1 ? 'interest selected' : 'interests selected'}
            </span>
          </div>

          <button
            type="button"
            disabled={selectedCount === 0 || submitting}
            onClick={handleContinue}
            className="py-2.5 px-5 bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-sm rounded-lg flex items-center gap-2 transition disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-[#FF6A00]/20 cursor-pointer"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
