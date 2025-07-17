'use client'

import { useState } from 'react'
import { useEmails } from '@/lib/queries'
import { useEmailStore } from '@/lib/store'
import { EmailListItem } from './email-list-item'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Search,
  RefreshCw,
  Archive,
  Trash2,
  Star,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface EmailListProps {
  onEmailSelect: (emailId: string) => void
  selectedEmailId?: string
}

export function EmailList({ onEmailSelect, selectedEmailId }: EmailListProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const { selectedFolder, searchQuery, setSearchQuery, selectedEmails, clearSelection } = useEmailStore()
  
  const { data, isLoading, error, refetch } = useEmails(
    { folder: selectedFolder, search: searchQuery || undefined },
    50
  )

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setCurrentPage(1)
  }

  const handleRefresh = () => {
    refetch()
  }

  const handleBulkAction = (action: string) => {
    // TODO: Implement bulk actions
    console.log(`Bulk action: ${action} on emails:`, selectedEmails)
    clearSelection()
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <div className="text-muted-foreground mb-4">
          Failed to load emails. Please try again.
        </div>
        <Button onClick={handleRefresh} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-4">
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search emails..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </form>
          <Button variant="outline" size="icon" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>

        {/* Bulk actions */}
        {selectedEmails.length > 0 && (
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary">
              {selectedEmails.length} selected
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction('archive')}
            >
              <Archive className="mr-1 h-3 w-3" />
              Archive
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction('delete')}
            >
              <Trash2 className="mr-1 h-3 w-3" />
              Delete
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction('star')}
            >
              <Star className="mr-1 h-3 w-3" />
              Star
            </Button>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>
        )}

        {/* Folder info */}
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span className="capitalize">{selectedFolder}</span>
          {data && (
            <span>
              {data.emails.length} of {data.total_count} emails
            </span>
          )}
        </div>
      </div>

      {/* Email list */}
      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="p-4 space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="p-4 border-b">
                <div className="flex items-start gap-3">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-1/4" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                  <Skeleton className="h-3 w-16" />
                </div>
              </div>
            ))}
          </div>
        ) : data?.emails.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <div className="text-muted-foreground mb-2">
              No emails found
            </div>
            <div className="text-sm text-muted-foreground">
              {searchQuery ? 'Try adjusting your search terms' : `Your ${selectedFolder} is empty`}
            </div>
          </div>
        ) : (
          <div>
            {data?.emails.map((email) => (
              <EmailListItem
                key={email.id}
                email={email}
                isSelected={selectedEmailId === email.id}
                onClick={() => onEmailSelect(email.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {data && data.has_next && (
        <>
          <Separator />
          <div className="p-4 flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {data.emails.length} of {data.total_count} emails
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={!data.has_previous}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={!data.has_next}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}