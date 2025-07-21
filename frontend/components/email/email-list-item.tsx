'use client'

import { useState } from 'react'
import { Email } from '@/lib/types'
import { useEmailStore } from '@/lib/store'
import { useMarkAsRead, useStarEmail, useUnstarEmail } from '@/lib/queries'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Star, Paperclip } from 'lucide-react'
import { cn, formatRelativeTime, truncateText } from '@/lib/utils'

interface EmailListItemProps {
  email: Email
  isSelected: boolean
  onClick: () => void
}

export function EmailListItem({ email, isSelected, onClick }: EmailListItemProps) {
  const { selectedEmails, toggleEmailSelection } = useEmailStore()
  const markAsRead = useMarkAsRead()
  const starEmail = useStarEmail()
  const unstarEmail = useUnstarEmail()
  
  const [isHovered, setIsHovered] = useState(false)
  const isChecked = selectedEmails.includes(email.id)

  const handleClick = () => {
    if (!email.is_read) {
      markAsRead.mutate(email.id)
    }
    onClick()
  }

  const handleStarClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (email.is_starred) {
      unstarEmail.mutate(email.id)
    } else {
      starEmail.mutate(email.id)
    }
  }

  const handleCheckboxChange = (e: React.MouseEvent) => {
    e.stopPropagation()
    toggleEmailSelection(email.id)
  }

  const senderName = email.sender.split('@')[0] || email.sender
  const senderInitials = senderName.slice(0, 2).toUpperCase()

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 border-b cursor-pointer transition-colors hover:bg-muted/50',
        isSelected && 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
        !email.is_read && 'bg-purple-50/50 dark:bg-purple-950/20'
      )}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Checkbox */}
      <div className="flex items-center pt-1">
        <Checkbox
          checked={isChecked}
          onClick={handleCheckboxChange}
          className={cn(
            'transition-opacity',
            !isHovered && !isChecked && 'opacity-0'
          )}
        />
      </div>

      {/* Avatar */}
      <Avatar className="h-8 w-8 mt-1">
        <AvatarFallback className="text-xs">
          {senderInitials}
        </AvatarFallback>
      </Avatar>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className={cn(
            'font-medium text-sm truncate',
            !email.is_read && 'font-semibold'
          )}>
            {senderName}
          </span>
          {email.is_important && (
            <Badge variant="destructive" className="text-xs px-1 py-0">
              Important
            </Badge>
          )}
          {email.attachments && email.attachments.length > 0 && (
            <Paperclip className="h-3 w-3 text-muted-foreground" />
          )}
        </div>
        
        <div className={cn(
          'text-sm mb-1 truncate',
          !email.is_read ? 'font-medium' : 'text-muted-foreground'
        )}>
          {email.subject || '(no subject)'}
        </div>
        
        <div className="flex items-center gap-2">
          {email.category && (
            <Badge className="text-xs px-1.5 py-0.5" style={{
              backgroundColor: email.color ? `${email.color}20` : '#6366f120',
              color: email.color || '#6366f1',
              borderColor: email.color ? `${email.color}30` : '#6366f130'
            }}>
              {email.category}
            </Badge>
          )}
          
          <div className="text-xs text-muted-foreground truncate flex-1">
            {email.summary ? (
              <span className="flex items-center">
                <Badge className="mr-1 h-4 px-1 bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">AI</Badge>
                {email.summary}
              </span>
            ) : (
              truncateText(email.body.replace(/<[^>]*>/g, ''), 100)
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-1">
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            'h-6 w-6 transition-opacity',
            !isHovered && !email.is_starred && 'opacity-0'
          )}
          onClick={handleStarClick}
        >
          <Star className={cn(
            'h-3 w-3',
            email.is_starred && 'fill-yellow-400 text-yellow-400'
          )} />
        </Button>
        
        <div className="text-xs text-muted-foreground whitespace-nowrap">
          {formatRelativeTime(email.created_at)}
        </div>
      </div>
    </div>
  )
}