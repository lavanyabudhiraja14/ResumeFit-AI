import React from 'react';
import { User, LogOut, LayoutDashboard, FileText, Briefcase } from 'lucide-react';

export default function Navbar({
  backendStatus,
  user,
  currentView,
  onNavigate,
  onOpenAuth,
  onSignOut,
}) {
  const isOnline = backendStatus?.status === 'healthy';

  return (
    <header className="border-b border-[#242424] bg-[#0A0A0A]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <button
          onClick={() => onNavigate(user ? (user.onboarding_completed ? 'dashboard' : 'onboarding') : 'home')}
          className="flex items-center gap-3 cursor-pointer group text-left"
        >
          <div className="w-8 h-8 rounded-md bg-[#151515] border border-[#242424] flex items-center justify-center group-hover:border-[#FF6A00]/50 transition">
            <span className="w-2.5 h-2.5 rounded-full bg-[#FF6A00]" />
          </div>
          <div>
            <span className="text-base font-semibold tracking-tight text-[#F5F5F5]">
              RESUMEFIT
            </span>
            <span className="text-xs ml-1.5 font-mono text-[#FF6A00] tracking-wider uppercase px-1.5 py-0.5 rounded bg-[#FF6A00]/10 border border-[#FF6A00]/20">
              AI
            </span>
          </div>
        </button>

        {/* Center / Navigation links if user is authenticated and completed onboarding */}
        {user && user.onboarding_completed && (
          <nav className="hidden md:flex items-center gap-1 bg-[#151515] p-1 rounded-lg border border-[#242424] text-xs font-mono">
            <button
              onClick={() => onNavigate('dashboard')}
              className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition cursor-pointer ${
                currentView === 'dashboard'
                  ? 'bg-[#0A0A0A] text-[#FF6A00] font-semibold'
                  : 'text-[#A1A1A1] hover:text-[#F5F5F5]'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>Dashboard</span>
            </button>
            <button
              onClick={() => onNavigate('resume')}
              className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition cursor-pointer ${
                currentView === 'resume'
                  ? 'bg-[#0A0A0A] text-[#FF6A00] font-semibold'
                  : 'text-[#A1A1A1] hover:text-[#F5F5F5]'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Resume Analysis</span>
            </button>
          </nav>
        )}

        {/* Right Section: Engine Status + Auth Controls */}
        <div className="flex items-center gap-3">
          {/* Backend Engine Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-full bg-[#151515] border border-[#242424]">
            <span
              className={`w-2 h-2 rounded-full ${
                isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              }`}
            />
            <span className="text-[#A1A1A1]">
              {isOnline ? 'Engine Online' : 'Connecting...'}
            </span>
          </div>

          {user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#151515] border border-[#242424] text-xs">
                <User className="w-3.5 h-3.5 text-[#FF6A00]" />
                <span className="text-[#F5F5F5] font-medium hidden sm:inline">{user.name}</span>
              </div>
              <button
                onClick={onSignOut}
                title="Sign Out"
                className="p-2 rounded-lg bg-[#151515] border border-[#242424] text-[#A1A1A1] hover:text-red-400 hover:border-red-400/40 transition cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => onOpenAuth('login')}
                className="px-3.5 py-1.5 rounded-lg text-xs font-mono text-[#A1A1A1] hover:text-[#F5F5F5] hover:bg-[#151515] transition cursor-pointer"
              >
                Sign In
              </button>
              <button
                onClick={() => onOpenAuth('signup')}
                className="px-3.5 py-1.5 rounded-lg bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold text-xs font-mono transition shadow-sm cursor-pointer"
              >
                Get Started
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
