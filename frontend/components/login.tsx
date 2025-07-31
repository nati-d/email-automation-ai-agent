'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LogIn, Info, Sparkles } from "lucide-react";
import { FcGoogle } from "react-icons/fc";
import { getGoogleAuthUrl } from '../lib/api/auth'; // updated path

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = () => {
      try {
        const userStr = localStorage.getItem("user");
        if (userStr) {
          const user = JSON.parse(userStr);
          const sessionId = user.sessionId || user.session_id;

          if (sessionId) {
            router.replace("/");
            return;
          }
        }
      } catch (error) {
        console.error("Auth check error:", error);
        localStorage.removeItem("user");
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, [router]);

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

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center" style={{ background: 'var(--background)' }}>
        <div className="text-lg" style={{ color: 'var(--foreground)' }}>Checking authentication...</div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center gap-8 border"
      style={{
        background: 'var(--card)',
        borderColor: 'var(--border)'
      }}
    >
      {/* Minimalistic icon at the top */}
      <span
        className="flex items-center justify-center w-12 h-12 rounded-full mb-2"
        style={{ background: 'var(--muted)' }}
      >
        <Sparkles className="w-7 h-7" style={{ color: 'var(--muted-foreground)' }} />
      </span>
      {/* Bold heading with accent */}
      <h1 className="text-2xl sm:text-3xl font-bold text-center leading-tight" style={{ color: 'var(--foreground)' }}>
        Joyful and productive <br /> email automation. <span className="font-extrabold" style={{ color: 'var(--primary)' }}>All in one.</span>
      </h1>
      {/* Info box */}
      <div
        className="w-full border rounded-lg px-4 py-3 flex items-start gap-3 shadow-sm"
        style={{
          background: 'var(--muted)',
          borderColor: 'var(--border)'
        }}
      >
        <Info className="w-5 h-5 mt-0.5" style={{ color: 'var(--primary)' }} />
        <div>
          <div className="font-semibold text-sm" style={{ color: 'var(--foreground)' }}>We need access to your Google account</div>
          <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Please allow all permissions to enable full AI features.</div>
        </div>
      </div>
      {/* Error message */}
      {error && (
        <div
          className="w-full border rounded-lg px-4 py-3 text-sm text-center"
          style={{
            background: 'var(--destructive)',
            borderColor: 'var(--destructive)',
            color: 'var(--destructive-foreground)'
          }}
        >
          {error}
        </div>
      )}
      {/* Success message */}
      {success && (
        <div
          className="w-full border rounded-lg px-4 py-3 text-sm text-center"
          style={{
            background: 'var(--success)',
            borderColor: 'var(--success)',
            color: 'var(--success-foreground)'
          }}
        >
          {success}
        </div>
      )}
      {/* Google button */}
      <button
        className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg font-semibold text-base shadow transition-colors border disabled:opacity-60 disabled:cursor-not-allowed"
        style={{
          background: 'var(--primary)',
          color: 'var(--primary-foreground)',
          borderColor: 'var(--primary)'
        }}
        onClick={handleGoogleLogin}
        disabled={loading}
      >
        <FcGoogle className="w-5 h-5" />
        {loading ? 'Redirecting...' : 'Continue with Google'}
      </button>
      {/* Terms note */}
      <p className="text-xs text-center mt-2" style={{ color: 'var(--muted-foreground)' }}>
        By clicking "Continue with Google", you acknowledge that you have read and agree to our Terms & Conditions and Privacy Policy.
      </p>
    </div>
  );
} 