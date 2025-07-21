'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { saveUserToStorage } from '../../lib/auth';

export default function AuthSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    // Parse query params
    const urlStatus = searchParams.get('status');
    const error = searchParams.get('error');
    const name = searchParams.get('name');
    const email = searchParams.get('email');
    const userId = searchParams.get('user_id');
    const isNewUser = searchParams.get('is_new_user');
    const sessionId = searchParams.get('session_id');
    const profilePicture = searchParams.get('profile_picture');

    if (urlStatus === 'success' && name && email && userId && sessionId) {
      setStatus('success');
      setMessage(`Welcome, ${name}! Redirecting...`);
      // Store user info in localStorage
      saveUserToStorage({
        name,
        email,
        userId,
        isNewUser,
        sessionId,
        profilePicture
      });
      setTimeout(() => {
        router.replace('/');
      }, 2000);
    } else if (error) {
      setStatus('error');
      setMessage(`Authentication failed: ${error}`);
    } else {
      setStatus('error');
      setMessage('Authentication failed: Missing required information.');
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-zinc-100 dark:bg-zinc-900">
      <div className="w-full max-w-md bg-white dark:bg-zinc-950 rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center gap-6 border border-zinc-200 dark:border-zinc-800">
        {status === 'loading' && (
          <div className="text-lg font-semibold text-zinc-700 dark:text-zinc-200">{message}</div>
        )}
        {status === 'success' && (
          <div className="text-lg font-semibold text-green-600 dark:text-green-400">{message}</div>
        )}
        {status === 'error' && (
          <div className="text-lg font-semibold text-red-600 dark:text-red-400">{message}</div>
        )}
      </div>
    </div>
  );
} 