'use client';

import { useEffect, useState } from 'react';
import Image from "next/image";

interface User {
  name: string;
  email: string;
  userId: string;
  isNewUser?: string;
  sessionId: string;
  profilePicture?: string;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  function handleLogout() {
    localStorage.removeItem('user');
    window.location.reload();
  }

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        {user ? (
          <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-xl p-8 flex flex-col items-center gap-4 border border-zinc-200 dark:border-zinc-800 min-w-[320px]">
            {user.profilePicture && (
              <img src={user.profilePicture} alt="Profile" className="w-20 h-20 rounded-full border-4 border-indigo-400 mb-2" />
            )}
            <div className="text-xl font-bold text-zinc-800 dark:text-zinc-100">Welcome, {user.name}!</div>
            <div className="text-zinc-600 dark:text-zinc-300 text-sm">{user.email}</div>
            <div className="text-zinc-400 dark:text-zinc-500 text-xs">Session ID: {user.sessionId}</div>
            <button
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="text-lg text-zinc-700 dark:text-zinc-200 font-semibold">You are not logged in. <a href="/login" className="text-indigo-600 dark:text-sky-400 underline">Login with Google</a></div>
        )}
      </main>
    </div>
  );
}
