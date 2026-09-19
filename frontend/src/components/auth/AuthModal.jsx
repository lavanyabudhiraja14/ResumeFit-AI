import React, { useState } from 'react';
import { X, Lock, Mail, User, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { signup, login } from '../../services/api';

export default function AuthModal({ isOpen, onClose, initialMode = 'signup', onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(initialMode === 'login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let result;
      if (isLogin) {
        result = await login(email, password);
      } else {
        if (!name.trim()) {
          throw new Error('Please provide your full name.');
        }
        result = await signup(name, email, password);
      }
      onAuthSuccess(result.user, result.access_token);
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-[#151515] border border-[#242424] rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/80">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-[#A1A1A1] hover:text-[#F5F5F5] transition"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="mb-6">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#FF6A00]/10 border border-[#FF6A00]/20 text-[#FF6A00] text-xs font-mono mb-3">
            <span>RESUMEFIT ACCOUNT</span>
          </div>
          <h2 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">
            {isLogin ? 'Welcome back' : 'Create your account'}
          </h2>
          <p className="text-sm text-[#A1A1A1] mt-1">
            {isLogin
              ? 'Enter your credentials to access your dashboard and saved interests.'
              : 'Sign up to personalize your skills matching and career feed.'}
          </p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-5 p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start gap-2.5 text-red-400 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-[#A1A1A1] mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#A1A1A1] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required={!isLogin}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Jane Doe"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#0A0A0A] border border-[#242424] rounded-lg text-sm text-[#F5F5F5] placeholder-[#666666] focus:border-[#FF6A00] focus:ring-1 focus:ring-[#FF6A00] outline-none transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[#A1A1A1] mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#A1A1A1] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-[#0A0A0A] border border-[#242424] rounded-lg text-sm text-[#F5F5F5] placeholder-[#666666] focus:border-[#FF6A00] focus:ring-1 focus:ring-[#FF6A00] outline-none transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-[#A1A1A1] mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#A1A1A1] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-[#0A0A0A] border border-[#242424] rounded-lg text-sm text-[#F5F5F5] placeholder-[#666666] focus:border-[#FF6A00] focus:ring-1 focus:ring-[#FF6A00] outline-none transition"
              />
            </div>
            {!isLogin && (
              <span className="text-[11px] text-[#666666] mt-1 block">
                Must be at least 6 characters.
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 bg-[#FF6A00] hover:bg-[#E55F00] text-black font-semibold rounded-lg flex items-center justify-center gap-2 text-sm transition shadow-lg shadow-[#FF6A00]/20 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{isLogin ? 'Sign In' : 'Create Account'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Toggle between Signup and Login */}
        <div className="mt-6 pt-5 border-t border-[#242424] text-center">
          <p className="text-xs text-[#A1A1A1]">
            {isLogin ? "Don't have an account yet?" : 'Already have an account?'}{' '}
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
              }}
              className="text-[#FF6A00] hover:underline font-medium ml-1 cursor-pointer"
            >
              {isLogin ? 'Sign Up' : 'Log In'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
