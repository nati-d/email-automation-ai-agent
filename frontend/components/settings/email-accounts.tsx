'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useEmailAccounts, useRemoveEmailAccount } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useToast } from '@/components/providers/toast-provider'
import { formatDistanceToNow } from 'date-fns'
import { Mail, Loader2, Plus, Trash2, AlertCircle } from 'lucide-react'

export function EmailAccounts() {
  const router = useRouter()
  const { toast } = useToast()
  const { data, isLoading } = useEmailAccounts()
  const removeAccount = useRemoveEmailAccount()
  const [accountToRemove, setAccountToRemove] = useState<string | null>(null)

  const handleAddAccount = () => {
    // In a real app, this would redirect to OAuth flow
    // For now, we'll just show a toast
    toast.info(
      'Add Account',
      'This would typically start the OAuth flow to connect a new email account.'
    )
  }

  const handleRemoveAccount = async () => {
    if (!accountToRemove) return

    try {
      await removeAccount.mutateAsync(accountToRemove)
      toast.success('Success', 'Email account removed successfully')
    } catch (error) {
      toast.error('Error', 'Failed to remove email account')
    }
    setAccountToRemove(null)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  const accounts = data?.accounts || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Email Accounts</h2>
          <p className="text-sm text-muted-foreground">
            Manage your connected email accounts
          </p>
        </div>
        <Button onClick={handleAddAccount}>
          <Plus className="mr-2 h-4 w-4" />
          Add Account
        </Button>
      </div>

      {accounts.length === 0 ? (
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
              <Mail className="h-6 w-6 text-muted-foreground" />
            </div>
            <CardTitle>No email accounts connected</CardTitle>
            <CardDescription>
              Connect your first email account to start managing your emails
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center pb-6">
            <Button onClick={handleAddAccount}>
              <Plus className="mr-2 h-4 w-4" />
              Add Account
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <Card key={account.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-base">{account.email}</CardTitle>
                    <CardDescription>
                      Connected via {account.provider}
                      {account.lastSynced && (
                        <> · Last synced {formatDistanceToNow(new Date(account.lastSynced))} ago</>
                      )}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => setAccountToRemove(account.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}

      <AlertDialog open={!!accountToRemove} onOpenChange={() => setAccountToRemove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Email Account</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove this email account? This will disconnect
              the account and stop syncing new emails. Your existing emails will remain
              in the system.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRemoveAccount}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Remove Account
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
} 