'use client'

import { useEmail, useMarkAsRead, useStarEmail, useUnstarEmail, useDeleteEmail, useSummarizeEmail } from '@/lib/queries'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/components/providers/toast-provider'
import {
  Star,
  Reply,
  ReplyAll,
  Forward,
  Archive,
  Trash2,
  MoreHorizontal,
  Download,
  Paperclip,
  ArrowLeft,
} from 'lucide-react'
import { formatDate, cn } from '@/lib/utils'

interface EmailViewProps {
  emailId: string
  onBack: () => void
}

export function EmailView({ emailId, onBack }: EmailViewProps) {
  const { data: email, isLoading, error } = useEmail(emailId)
  const markAsRead = useMarkAsRead()
  const starEmail = useStarEmail()
  const unstarEmail = useUnstarEmail()
  const deleteEmail = useDeleteEmail()
  const summarizeEmail = useSummarizeEmail()
  const { toast } = useToast()

  if (isLoading) {
    return (
      <div className="flex flex-col h-full">
        <div className="p-4 border-b">
          <div className="flex items-center gap-2 mb-4">
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-4 w-20" />
          </div>
          <Skeleton className="h-6 w-3/4 mb-2" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <div className="flex-1 p-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !email) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <div className="text-muted-foreground mb-4">
          Failed to load email
        </div>
        <Button onClick={onBack} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to list
        </Button>
      </div>
    )
  }

  const handleStarClick = () => {
    if (email.is_starred) {
      unstarEmail.mutate(email.id)
    } else {
      starEmail.mutate(email.id)
    }
  }

  const handleDelete = () => {
    deleteEmail.mutate(email.id, {
      onSuccess: () => onBack()
    })
  }

  const senderName = email.sender.split('@')[0] || email.sender
  const senderInitials = senderName.slice(0, 2).toUpperCase()

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-4">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleStarClick}
            >
              <Star className={cn(
                'h-4 w-4',
                email.is_starred && 'fill-yellow-400 text-yellow-400'
              )} />
            </Button>
            <Button variant="ghost" size="icon">
              <Archive className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleDelete}>
              <Trash2 className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => {
                summarizeEmail.mutate(email.id, {
                  onSuccess: () => {
                    toast.success('Email Summarized', 'AI has analyzed and summarized this email');
                  },
                  onError: (error) => {
                    toast.error('Summarization Failed', error instanceof Error ? error.message : 'Failed to summarize email');
                  }
                });
              }}
              title="Summarize with AI"
            >
              <span className="text-xs font-semibold">AI</span>
            </Button>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-xl font-semibold">
            {email.subject || '(no subject)'}
          </h1>
          
          <div className="flex items-center gap-2">
            {email.is_important && (
              <Badge variant="destructive" className="text-xs">
                Important
              </Badge>
            )}
            {!email.is_read && (
              <Badge variant="secondary" className="text-xs">
                Unread
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Email content */}
      <div className="flex-1 overflow-auto">
        <div className="p-4">
          {/* Sender info */}
          <div className="flex items-start gap-3 mb-6">
            <Avatar className="h-10 w-10">
              <AvatarFallback>
                {senderInitials}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium">{senderName}</span>
                <span className="text-sm text-muted-foreground">
                  &lt;{email.sender}&gt;
                </span>
              </div>
              
              <div className="text-sm text-muted-foreground mb-2">
                to {email.recipients.join(', ')}
              </div>
              
              <div className="text-xs text-muted-foreground">
                {formatDate(email.created_at)}
              </div>
            </div>
          </div>

          {/* Attachments - Removed since Email type doesn't have attachments */}

          {/* AI Insights */}
          {(email.summary || email.sentiment || email.key_topics || email.main_concept) && (
            <div className="mb-6 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-md border border-purple-100 dark:border-purple-800/30">
              <div className="flex items-center mb-2">
                <Badge className="mr-2 bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">AI Insights</Badge>
              </div>
              
              {email.summary && (
                <div className="mb-2">
                  <div className="text-xs font-medium text-purple-700 dark:text-purple-400 mb-1">Summary</div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{email.summary}</p>
                </div>
              )}
              
              <div className="flex flex-wrap gap-4">
                {email.main_concept && (
                  <div className="flex-1 min-w-[200px]">
                    <div className="text-xs font-medium text-purple-700 dark:text-purple-400 mb-1">Main Concept</div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{email.main_concept}</p>
                  </div>
                )}
                
                {email.sentiment && (
                  <div className="flex-1 min-w-[150px]">
                    <div className="text-xs font-medium text-purple-700 dark:text-purple-400 mb-1">Sentiment</div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 capitalize">{email.sentiment}</p>
                  </div>
                )}
                
                {email.key_topics && email.key_topics.length > 0 && (
                  <div className="flex-1 min-w-[200px]">
                    <div className="text-xs font-medium text-purple-700 dark:text-purple-400 mb-1">Key Topics</div>
                    <div className="flex flex-wrap gap-1">
                      {Array.isArray(email.key_topics) ? (
                        email.key_topics.map((topic, index) => (
                          <Badge key={index} variant="outline" className="text-xs bg-white dark:bg-gray-800">
                            {topic}
                          </Badge>
                        ))
                      ) : (
                        <p className="text-sm text-gray-700 dark:text-gray-300">{email.key_topics}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Email body */}
          <div 
            className="prose prose-sm max-w-none dark:prose-invert"
            dangerouslySetInnerHTML={{ __html: email.body }}
          />
        </div>
      </div>

      {/* Actions */}
      <Separator />
      <div className="p-4">
        <div className="flex items-center gap-2">
          <Button className="bg-purple-500 hover:bg-purple-600 text-white">
            <Reply className="mr-2 h-4 w-4" />
            Reply
          </Button>
          <Button variant="outline">
            <ReplyAll className="mr-2 h-4 w-4" />
            Reply All
          </Button>
          <Button variant="outline">
            <Forward className="mr-2 h-4 w-4" />
            Forward
          </Button>
          
   
        </div>
      </div>
    </div>
  )
}