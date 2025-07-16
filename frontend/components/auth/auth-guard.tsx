'use client'

import { useEffect } from 'react'
import { useCurrentUser } from '@/lib/queries'
import { useAuthStore } from '@/lib/store'
import { LoginPage } from './login-page'
import { Loader2 } from 'lucide-react'

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { sessionId, isAuthenticated, clearAuth } = useAuthStore()
  const { data: user, isLoading, error } = useCurrentUser()

  useEffect(() => {
    if (error && sessionId) {
      // If we have a session ID but getting an error, clear auth
      console.error('Auth error:', error)
      // Only clear auth if it's an authentication error (401/403)
      if (error.message.includes('401') || error.message.includes('403')) {
        clearAuth()
      }
    }
  }, [error, sessionId, clearAuth])

  // If no session ID, show login immediately
  if (!sessionId || !isAuthenticated) {
    return <LoginPage />
  }

  // If we have session ID but still loading user data
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // If error loading user data, show login
  if (error) {
    console.error('Auth error in AuthGuard:', error)
    return <LoginPage />
  }

  // If we have user data, show the app
  if (user) {
    return <>{children}</>
  }

  // Fallback to login
  return <LoginPage />
}