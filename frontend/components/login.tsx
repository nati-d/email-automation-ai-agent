'use client';

import { useState } from "react";
import { LogIn, Info, Sparkles } from "lucide-react";
import { FcGoogle } from "react-icons/fc";
import { getGoogleAuthUrl } from '../lib/api/auth'; // updated path

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleGoogleLogin() {
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const url = await getGoogleAuthUrl();
      if (url) {
        window.location.href = url;
      } else {
        throw new Error('No authorization URL received from server');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to initiate login');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-zinc-100 dark:bg-zinc-900">
      <div className="w-full max-w-md bg-white dark:bg-zinc-950 rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center gap-8 border border-zinc-200 dark:border-zinc-800">
        {/* Minimalistic icon at the top */}
        <span className="flex items-center justify-center w-12 h-12 rounded-full bg-zinc-200 dark:bg-zinc-800 mb-2">
          <Sparkles className="w-7 h-7 text-zinc-700 dark:text-zinc-300" />
        </span>
        {/* Bold heading with accent */}
        <h1 className="text-2xl sm:text-3xl font-bold text-center text-zinc-800 dark:text-zinc-100 leading-tight">
          Joyful and productive <br /> email automation. <span className="font-extrabold text-indigo-600 dark:text-sky-400">All in one.</span>
        </h1>
        {/* Info box */}
        <div className="w-full bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg px-4 py-3 flex items-start gap-3 shadow-sm">
          <Info className="w-5 h-5 mt-0.5 text-indigo-600 dark:text-sky-400" />
          <div>
            <div className="font-semibold text-zinc-800 dark:text-zinc-100 text-sm">We need access to your Google account</div>
            <div className="text-xs text-zinc-500 dark:text-zinc-400">Please allow all permissions to enable full AI features.</div>
          </div>
        </div>
        {/* Error message */}
        {error && (
          <div className="w-full bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3 text-red-700 dark:text-red-200 text-sm text-center">
            {error}
          </div>
        )}
        {/* Success message */}
        {success && (
          <div className="w-full bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-800 rounded-lg px-4 py-3 text-green-700 dark:text-green-200 text-sm text-center">
            {success}
          </div>
        )}
        {/* Google button */}
        <button
          className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg font-semibold text-base shadow hover:bg-zinc-800 dark:hover:bg-white transition-colors border border-zinc-900/10 dark:border-zinc-100/10 disabled:opacity-60 disabled:cursor-not-allowed"
          onClick={handleGoogleLogin}
          disabled={loading}
        >
          <FcGoogle className="w-5 h-5" />
          {loading ? 'Redirecting...' : 'Continue with Google'}
        </button>
        {/* Terms note */}
        <p className="text-xs text-zinc-500 dark:text-zinc-400 text-center mt-2">
          By clicking "Continue with Google", you acknowledge that you have read and agree to our Terms & Conditions and Privacy Policy.
        </p>
      </div>
    </div>
  );
} 