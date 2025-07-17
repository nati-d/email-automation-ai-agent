'use client'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useEmailStore } from '@/lib/store'
import { EmailFolder } from '@/lib/types'
import {
  Inbox,
  Send,
  FileText,
  Trash2,
  Star,
  AlertCircle,
  Archive,
  Edit,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const folderIcons = {
  inbox: Inbox,
  sent: Send,
  drafts: FileText,
  trash: Trash2,
  spam: AlertCircle,
  starred: Star,
  important: AlertCircle,
}

const folderLabels = {
  inbox: 'Inbox',
  sent: 'Sent',
  drafts: 'Drafts',
  trash: 'Trash',
  spam: 'Spam',
  starred: 'Starred',
  important: 'Important',
}

interface EmailSidebarProps {
  className?: string
}

export function EmailSidebar({ className }: EmailSidebarProps) {
  const { selectedFolder, setSelectedFolder, openCompose } = useEmailStore()

  const folders: EmailFolder[] = ['inbox', 'starred', 'important', 'sent', 'drafts', 'spam', 'trash']

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="p-4">
        <Button onClick={openCompose} className="w-full" size="lg">
          <Edit className="mr-2 h-4 w-4" />
          Compose
        </Button>
      </div>

      <Separator />

      <div className="flex-1 overflow-auto">
        <div className="p-2 space-y-1">
          {folders.map((folder) => {
            const Icon = folderIcons[folder]
            const isSelected = selectedFolder === folder
            
            return (
              <Button
                key={folder}
                variant={isSelected ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start',
                  isSelected && 'bg-secondary'
                )}
                onClick={() => setSelectedFolder(folder)}
              >
                <Icon className="mr-3 h-4 w-4" />
                <span className="flex-1 text-left">{folderLabels[folder]}</span>
                {folder === 'inbox' && (
                  <Badge variant="secondary" className="ml-auto">
                    12
                  </Badge>
                )}
              </Button>
            )
          })}
        </div>

        <Separator className="my-4" />

        <div className="p-2">
          <div className="text-xs font-medium text-muted-foreground mb-2 px-2">
            LABELS
          </div>
          <div className="space-y-1">
            <Button variant="ghost" className="w-full justify-start text-sm">
              <div className="w-3 h-3 rounded-full bg-red-500 mr-3" />
              Work
            </Button>
            <Button variant="ghost" className="w-full justify-start text-sm">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-3" />
              Personal
            </Button>
            <Button variant="ghost" className="w-full justify-start text-sm">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-3" />
              Projects
            </Button>
          </div>
        </div>
      </div>

      <Separator />

      <div className="p-2">
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="mr-3 h-4 w-4" />
          Settings
        </Button>
      </div>
    </div>
  )
}