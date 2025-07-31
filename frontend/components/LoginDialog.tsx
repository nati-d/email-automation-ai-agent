"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Mail, Info, Sparkles, Loader2 } from "lucide-react"
import { FcGoogle } from "react-icons/fc"
import { useRouter } from "next/navigation"
import { getGoogleAuthUrl } from '../lib/api/auth'

interface LoginDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LoginDialog({ open, onOpenChange }: LoginDialogProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  async function handleGoogleLogin() {
    setError(null)
    setLoading(true)
    try {
      const url = await getGoogleAuthUrl()
      if (url) {
        window.location.href = url
      } else {
        throw new Error('No authorization URL received from server')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to initiate login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="text-center">
          <div className="flex justify-center mb-4">
            <span 
              className="flex items-center justify-center w-12 h-12 rounded-full"
              style={{ background: 'var(--muted)' }}
            >
              <Sparkles className="w-7 h-7" style={{ color: 'var(--muted-foreground)' }} />
            </span>
          </div>
          <DialogTitle className="text-2xl font-bold leading-tight">
            Joyful and productive <br /> email automation.{" "}
            <span className="font-extrabold text-blue-600">All in one.</span>
          </DialogTitle>
          <DialogDescription className="sr-only">
            Sign in with Google to get started with EmailAI
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
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
              <div className="font-semibold text-sm" style={{ color: 'var(--foreground)' }}>
                We need access to your Google account
              </div>
              <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                Please allow all permissions to enable full AI features.
              </div>
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

          {/* Google button */}
          <Button
            className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg font-semibold text-base shadow transition-colors border disabled:opacity-60 disabled:cursor-not-allowed"
            style={{
              background: 'var(--primary)',
              color: 'var(--primary-foreground)',
              borderColor: 'var(--primary)'
            }}
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Redirecting...
              </>
            ) : (
              <>
                <FcGoogle className="w-5 h-5" />
                Continue with Google
              </>
            )}
          </Button>

          {/* Terms note */}
          <p className="text-xs text-center" style={{ color: 'var(--muted-foreground)' }}>
            By clicking "Continue with Google", you acknowledge that you have read and agree to our Terms & Conditions and Privacy Policy.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}