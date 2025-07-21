'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/auth-provider'
import { EmailAgentLoading } from '@/components/ui/email-agent-loading'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <EmailAgentLoading 
        message="Loading Email-Agent..." 
        submessage="Checking authentication status" 
      />
    )
  }

  if (!isAuthenticated) {
    return null // Will redirect in the useEffect
  }

  return <>{children}</>
}