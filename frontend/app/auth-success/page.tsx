'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { Loader2 } from 'lucide-react'

export default function AuthSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { setAuth } = useAuthStore()

  useEffect(() => {
    const handleAuthSuccess = async () => {
      try {
        // Get auth data from URL params (sent by backend)
        const status = searchParams.get('status')
        const error = searchParams.get('error')
        const email = searchParams.get('email')
        const name = searchParams.get('name')
        const userId = searchParams.get('user_id')
        const sessionId = searchParams.get('session_id')
        const isNewUser = searchParams.get('is_new_user') === 'true'

        if (error) {
          console.error('Auth error:', error)
          const message = searchParams.get('message') || error
          router.push('/login?error=' + encodeURIComponent(message))
          return
        }

        if (status === 'success' && email && name && userId && sessionId) {
          const user = {
            id: userId,
            email: email,
            name: name,
            picture: '', // Will be loaded later if needed
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          
          setAuth(user, sessionId)
          
          // Show welcome message for new users
          if (isNewUser) {
            console.log('Welcome new user!')
          }
          
          router.push('/')
        } else {
          // Missing required parameters
          console.error('Missing auth parameters')
          router.push('/login?error=invalid_auth_response')
        }
      } catch (error) {
        console.error('Failed to process auth success:', error)
        router.push('/login?error=auth_processing_failed')
      }
    }

    handleAuthSuccess()
  }, [router, searchParams, setAuth])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Completing sign in...</p>
      </div>
    </div>
  )
}