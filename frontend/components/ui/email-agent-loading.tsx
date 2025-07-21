'use client'

import { Loader2 } from 'lucide-react'

export function EmailAgentLoading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="w-16 h-16 mb-4 bg-purple-500 rounded-full flex items-center justify-center">
        <svg className="w-8 h-8 text-white animate-pulse" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
        </svg>
      </div>
      <div className="flex items-center space-x-2">
        <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
        <h2 className="text-xl font-medium text-gray-700 dark:text-gray-300">Loading Email Agent...</h2>
      </div>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Please wait while we prepare your inbox</p>
    </div>
  )
}