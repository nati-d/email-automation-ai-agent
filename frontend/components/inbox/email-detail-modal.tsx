"use client";

import { useEmail } from "@/lib/queries";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  Reply, 
  ReplyAll, 
  Forward, 
  Archive, 
  Trash2, 
  Star,
  MoreHorizontal,
  Calendar,
  User,
  Mail
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow, format } from "date-fns";

interface EmailDetailModalProps {
  emailId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function EmailDetailModal({
  emailId,
  isOpen,
  onClose
}: EmailDetailModalProps) {
  const { data: email, isLoading, error } = useEmail(emailId);

  const getSenderInitials = (sender: string) => {
    const name = sender.split('@')[0];
    return name.slice(0, 2).toUpperCase();
  };

  const getSenderName = (sender: string) => {
    return sender.split('@')[0];
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return {
        relative: formatDistanceToNow(date, { addSuffix: true }),
        absolute: format(date, "PPP 'at' p")
      };
    } catch {
      return { relative: "Unknown", absolute: "Unknown" };
    }
  };

  const handleAction = (action: string) => {
    console.log(`${action} clicked for email:`, emailId);
    // TODO: Implement actions
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        {isLoading ? (
          <div className="flex-1 space-y-4 p-6">
            <div className="flex items-center gap-3">
              <Skeleton className="h-10 w-10 rounded-full" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-3 w-32" />
              </div>
            </div>
            <Skeleton className="h-6 w-3/4" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Failed to load email</h3>
              <p className="text-sm text-muted-foreground">
                Please try again later
              </p>
            </div>
          </div>
        ) : email ? (
          <>
            {/* Header */}
            <DialogHeader className="border-b pb-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <Avatar className="h-10 w-10 flex-shrink-0">
                    <AvatarFallback>
                      {getSenderInitials(email.sender)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <DialogTitle className="text-lg font-semibold mb-1">
                      {email.subject}
                    </DialogTitle>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <User className="h-3 w-3" />
                      <span>{getSenderName(email.sender)}</span>
                      <span>•</span>
                      <Calendar className="h-3 w-3" />
                      <span title={formatDate(email.created_at).absolute}>
                        {formatDate(email.created_at).relative}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-muted-foreground">To:</span>
                      <div className="flex flex-wrap gap-1">
                        {email.recipients.map((recipient, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {recipient.split('@')[0]}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("star")}
                  >
                    <Star className={cn(
                      "h-4 w-4",
                      email.is_starred && "fill-yellow-400 text-yellow-400"
                    )} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("reply")}
                  >
                    <Reply className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("replyAll")}
                  >
                    <ReplyAll className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("forward")}
                  >
                    <Forward className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("archive")}
                  >
                    <Archive className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAction("delete")}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </DialogHeader>

            {/* Content */}
            <ScrollArea className="flex-1 px-6">
              <div className="py-6 space-y-6">
                {/* Summary */}
                {email.summary && (
                  <div className="bg-muted/50 rounded-lg p-4">
                    <h4 className="font-medium text-sm mb-2 text-muted-foreground">
                      AI Summary
                    </h4>
                    <p className="text-sm">{email.summary}</p>
                  </div>
                )}

                {/* Category */}
                {email.category && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Category:</span>
                    <Badge variant="outline">{email.category}</Badge>
                  </div>
                )}

                {/* Email Body */}
                <div className="prose prose-sm max-w-none">
                  {email.html_body ? (
                    <div 
                      dangerouslySetInnerHTML={{ __html: email.html_body }}
                      className="email-content [&_img]:max-w-full [&_img]:h-auto [&_a]:text-primary [&_a]:underline"
                    />
                  ) : (
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {email.body}
                    </div>
                  )}
                </div>

                {/* Attachments */}
                {email.attachments && email.attachments.length > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="font-medium text-sm mb-3">
                      Attachments ({email.attachments.length})
                    </h4>
                    <div className="space-y-2">
                      {email.attachments.map((attachment, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 p-2 border rounded-md"
                        >
                          <div className="flex-1">
                            <div className="font-medium text-sm">
                              {attachment.filename}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {(attachment.size / 1024).toFixed(1)} KB
                            </div>
                          </div>
                          <Button variant="outline" size="sm">
                            Download
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Footer Actions */}
            <div className="border-t pt-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button onClick={() => handleAction("reply")}>
                  <Reply className="h-4 w-4 mr-2" />
                  Reply
                </Button>
                <Button variant="outline" onClick={() => handleAction("replyAll")}>
                  <ReplyAll className="h-4 w-4 mr-2" />
                  Reply All
                </Button>
                <Button variant="outline" onClick={() => handleAction("forward")}>
                  <Forward className="h-4 w-4 mr-2" />
                  Forward
                </Button>
              </div>
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}