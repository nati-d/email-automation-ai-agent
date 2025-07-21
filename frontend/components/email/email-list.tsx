"use client";

import { useState } from "react";
import { useInboxEmails, useTaskEmails } from "@/lib/queries";
import { useEmailStore } from "@/lib/store";
import { EmailListItem } from "./email-list-item";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  RefreshCw,
  Archive,
  Trash2,
  Star,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  CheckSquare,
  Inbox,
  Tag,
} from "lucide-react";
import { cn } from "@/lib/utils"; // Used in className

interface EmailListProps {
  onEmailSelect: (emailId: string) => void;
  selectedEmailId?: string;
  emailType: string;
}

export function EmailList({
  onEmailSelect,
  selectedEmailId,
  emailType,
}: EmailListProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const { selectedEmails, toggleEmailSelection, clearSelection } =
    useEmailStore();

  // Use different hooks based on email type
  const { data, isLoading, error, refetch } =
    emailType === "tasks" ? useTaskEmails() : useInboxEmails();

  const getFolderIcon = () => {
    switch (emailType) {
      case "inbox":
        return <Inbox className="h-5 w-5" />;
      case "tasks":
        return <CheckSquare className="h-5 w-5" />;
      case "starred":
        return <Star className="h-5 w-5" />;
      case "sent":
        return <Archive className="h-5 w-5" />;
      case "trash":
        return <Trash2 className="h-5 w-5" />;
      default:
        if (emailType.startsWith("category-")) {
          return <Tag className="h-5 w-5" />;
        }
        return <Inbox className="h-5 w-5" />;
    }
  };

  const getFolderTitle = () => {
    if (emailType.startsWith("category-")) {
      return (
        emailType.replace("category-", "").charAt(0).toUpperCase() +
        emailType.slice(9)
      );
    }
    return emailType.charAt(0).toUpperCase() + emailType.slice(1);
  };

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleBulkAction = (action: string) => {
    // TODO: Implement bulk actions
    console.log(`Bulk action: ${action} on emails:`, selectedEmails);
    clearSelection();
  };

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
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {getFolderIcon()}
            <h2 className="text-lg font-semibold">{getFolderTitle()}</h2>
            {data && (
              <Badge variant="secondary" className="ml-2">
                {data.total_count}
              </Badge>
            )}
          </div>
          <Button variant="outline" size="icon" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>

        {/* Bulk actions */}
        {selectedEmails.length > 0 && (
          <div className="flex items-center gap-2 py-2">
            <Badge variant="secondary">{selectedEmails.length} selected</Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("archive")}
            >
              <Archive className="mr-1 h-3 w-3" />
              Archive
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("delete")}
            >
              <Trash2 className="mr-1 h-3 w-3" />
              Delete
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("star")}
            >
              <Star className="mr-1 h-3 w-3" />
              Star
            </Button>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>
        )}
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
            <div className="w-16 h-16 mb-4 text-muted-foreground">
              {getFolderIcon()}
            </div>
            <div className="text-lg font-medium mb-2">
              No emails in {getFolderTitle()}
            </div>
            <div className="text-sm text-muted-foreground">
              Messages that appear here will be shown in your{" "}
              {getFolderTitle().toLowerCase()}
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
  );
}
