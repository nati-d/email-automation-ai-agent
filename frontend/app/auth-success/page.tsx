'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { saveUserToStorage } from '../../lib/api/auth';

function AuthSuccessContent() {
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
    const sessionId = searchParams.get('session_id'); // always camelCase for storage
    const profilePicture = searchParams.get('profile_picture');

    if (urlStatus === 'success' && name && email && userId && sessionId) {
      setStatus('success');
      setMessage(`Welcome, ${name}! Redirecting...`);
      // Store user info in localStorage with sessionId (camelCase)
      const userObj = {
        name,
        email,
        userId,
        isNewUser,
        sessionId, // always camelCase
        profilePicture
      };
      console.log('Saving user to storage:', userObj);
      saveUserToStorage(userObj);
      window.location.replace('/'); // Navigate and reload to home page
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

export default function AuthSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen w-full flex items-center justify-center bg-zinc-100 dark:bg-zinc-900">
        <div className="w-full max-w-md bg-white dark:bg-zinc-950 rounded-2xl shadow-xl px-8 py-10 flex flex-col items-center gap-6 border border-zinc-200 dark:border-zinc-800">
          <div className="text-lg font-semibold text-zinc-700 dark:text-zinc-200">Loading...</div>
        </div>
      </div>
    }>
      <AuthSuccessContent />
    </Suspense>
  );
} 