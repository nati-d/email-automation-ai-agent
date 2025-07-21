'use client'

import { useAuth } from '@/components/providers/auth-provider'
import { EmailAgentLoading } from '@/components/ui/email-agent-loading'
import { LoginPage } from './login-page'

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <EmailAgentLoading message="Loading Email-Agent..." submessage="Getting your emails ready" />
  }

  if (!isAuthenticated) {
    return <LoginPage />
  }

  return <>{children}</>
}