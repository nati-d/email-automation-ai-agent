"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { EmailListItem } from "./email-list-item";
import { 
  Search, 
  RefreshCw, 
  Filter,
  Mail,
  MoreHorizontal,
  Archive,
  Trash2,
  Star
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Email {
  id: string;
  sender: string;
  recipients: string[];
  subject: string;
  body: string;
  summary?: string;
  created_at: string;
  is_read: boolean;
  is_starred: boolean;
  category?: string;
}

interface EmailListViewProps {
  emails: Email[];
  selectedCategory: string | null;
  onEmailSelect: (emailId: string) => void;
  isLoading: boolean;
  totalCount: number;
}

export function EmailListView({
  emails,
  selectedCategory,
  onEmailSelect,
  isLoading,
  totalCount
}: EmailListViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEmails, setSelectedEmails] = useState<string[]>([]);

  const filteredEmails = emails.filter(email =>
    email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
    email.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
    email.body.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleEmailToggle = (emailId: string) => {
    setSelectedEmails(prev =>
      prev.includes(emailId)
        ? prev.filter(id => id !== emailId)
        : [...prev, emailId]
    );
  };

  const handleSelectAll = () => {
    if (selectedEmails.length === filteredEmails.length) {
      setSelectedEmails([]);
    } else {
      setSelectedEmails(filteredEmails.map(email => email.id));
    }
  };

  const handleBulkAction = (action: string) => {
    console.log(`Bulk action: ${action} on emails:`, selectedEmails);
    // TODO: Implement bulk actions
    setSelectedEmails([]);
  };

  const getCategoryTitle = () => {
    if (!selectedCategory) return "All Emails";
    return selectedCategory;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b bg-background p-4 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">{getCategoryTitle()}</h1>
            <Badge variant="secondary" className="text-xs">
              {totalCount}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search emails..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Bulk Actions */}
        {selectedEmails.length > 0 && (
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
            <Badge variant="secondary">
              {selectedEmails.length} selected
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("archive")}
            >
              <Archive className="h-3 w-3 mr-1" />
              Archive
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("star")}
            >
              <Star className="h-3 w-3 mr-1" />
              Star
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleBulkAction("delete")}
            >
              <Trash2 className="h-3 w-3 mr-1" />
              Delete
            </Button>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>
        )}
      </div>

      {/* Email List */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3 p-3">
                <Skeleton className="h-4 w-4 rounded" />
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-16" />
                  </div>
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : filteredEmails.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {searchQuery ? "No emails found" : "No emails"}
              </h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery 
                  ? "Try adjusting your search terms"
                  : "Emails will appear here when they arrive"
                }
              </p>
            </div>
          </div>
        ) : (
          <ScrollArea className="h-full">
            <div className="divide-y">
              {filteredEmails.map((email) => (
                <EmailListItem
                  key={email.id}
                  email={email}
                  isSelected={selectedEmails.includes(email.id)}
                  onSelect={() => handleEmailToggle(email.id)}
                  onClick={() => onEmailSelect(email.id)}
                />
              ))}
            </div>
          </ScrollArea>
        )}
      </div>

      {/* Footer with select all */}
      {!isLoading && filteredEmails.length > 0 && (
        <div className="border-t p-3 bg-background">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSelectAll}
            className="text-xs"
          >
            {selectedEmails.length === filteredEmails.length ? "Deselect All" : "Select All"}
          </Button>
        </div>
      )}
    </div>
  );
}