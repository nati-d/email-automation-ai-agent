"use client";

import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Archive,
  Trash,
  MailOpen,
  MoreVertical,
  Reply,
  ReplyAll,
  Forward,
  Star,
  Printer,
  ExternalLink,
  Info,
  Calendar,
  User,
  Mail,
  Tag,
} from "lucide-react";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchEmailById, Email } from "../../../lib/api/email";
import { formatEmailDate } from "../../../lib/utils";

export default function EmailDetailPage() {
  const router = useRouter();
  const { email_id } = useParams();
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchEmailById(email_id as string)
      .then((data) => {
        setEmail(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch email");
        setLoading(false);
      });
  }, [email_id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading email...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="text-destructive text-lg font-semibold">Error</div>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    );
  }
  
  if (!email) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="text-muted-foreground text-lg font-semibold">Email not found</div>
          <p className="text-muted-foreground">The email you're looking for doesn't exist.</p>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="flex flex-col min-h-0 w-full bg-white mt-4 rounded-tl-xl overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between py-4 px-2   bg-card shadow-sm">
          <div className="flex items-center gap-4">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Back to inbox"
                  onClick={() => router.back()}
                  className="rounded-full p-0 w-10 h-10 flex items-center justify-center hover:bg-muted hover:text-primary focus:ring-2 focus:ring-primary/50"
                  style={{ marginLeft: '-4px' }}
                >
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Back to inbox</TooltipContent>
            </Tooltip>
            <div className="flex flex-col">
              <h1 className="text-xl font-semibold text-foreground truncate max-w-[calc(100vw-400px)] md:max-w-2xl">
                {email.subject || "(No subject)"}
              </h1>
              <p className="text-sm text-muted-foreground">
                {email.sender} • {formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Archive" className="hover:bg-muted">
                  <Archive className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Archive</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Delete" className="hover:bg-muted">
                  <Trash className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Delete</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Mark as unread" className="hover:bg-muted">
                  <MailOpen className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Mark as unread</TooltipContent>
            </Tooltip>
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" aria-label="More options" className="hover:bg-muted">
                      <MoreVertical className="h-5 w-5" />
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent>More options</TooltipContent>
              </Tooltip>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <Star className="mr-2 h-4 w-4" />
                  <span>Add to Starred</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Printer className="mr-2 h-4 w-4" />
                  <span>Print</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  <span>Open in new window</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Info className="mr-2 h-4 w-4" />
                  <span>Show original</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Email Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="w-full  space-y-8">
            {/* Email Metadata */}
            <div className="bg-card rounded-lg  p-6 space-y-6 w-full">
              {/* Sender and Recipient Info */}
              <div className="flex items-start gap-4">
                <Avatar className="h-12 w-12 flex-shrink-0">
                  <AvatarImage src="/placeholder.svg?height=48&width=48" alt="Sender Avatar" />
                  <AvatarFallback className="bg-primary text-primary-foreground text-lg font-semibold">
                    {email.sender?.charAt(0).toUpperCase() || "?"}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h2 className="text-lg font-semibold text-foreground mb-1">
                        {email.sender || "Unknown sender"}
                      </h2>
                      <p className="text-sm text-muted-foreground mb-2">
                        {email.sender && `<${email.sender}>`}
                      </p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{formatEmailDate(email.sent_at || email.created_at || email.updated_at)}</span>
                        </div>
                        {email.recipients && email.recipients.length > 0 && (
                          <div className="flex items-center gap-1">
                            <Mail className="h-4 w-4" />
                            <span>to {email.recipients.join(", ")}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="outline" size="sm" aria-label="Reply">
                            <Reply className="h-4 w-4 mr-2" />
                            Reply
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Reply</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="outline" size="sm" aria-label="Reply all">
                            <ReplyAll className="h-4 w-4 mr-2" />
                            Reply All
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Reply all</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="outline" size="sm" aria-label="Forward">
                            <Forward className="h-4 w-4 mr-2" />
                            Forward
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Forward</TooltipContent>
                      </Tooltip>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Insights */}
              {(email.sentiment || email.main_concept || email.key_topics || email.summary) && (
                <>
                  <Separator />
                  <div className="space-y-4">
                    <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <Tag className="h-4 w-4" />
                      AI Insights
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {email.sentiment && (
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-muted-foreground">Sentiment:</span>
                          <span
                            className="w-3 h-3 rounded-full"
                            style={{
                              background:
                                email.sentiment === 'positive'
                                  ? '#22c55e'
                                  : email.sentiment === 'negative'
                                  ? '#ef4444'
                                  : email.sentiment === 'neutral'
                                  ? '#facc15'
                                  : 'var(--muted-foreground)',
                            }}
                          />
                          <span className="text-sm font-medium capitalize">{email.sentiment}</span>
                        </div>
                      )}
                      {email.main_concept && (
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-muted-foreground">Main Concept:</span>
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary">
                            {email.main_concept}
                          </span>
                        </div>
                      )}
                    </div>
                    {email.key_topics && Array.isArray(email.key_topics) && email.key_topics.length > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Key Topics:</span>
                        <div className="flex flex-wrap gap-1">
                          {email.key_topics.slice(0, 5).map((topic) => (
                            <span key={topic} className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                              #{topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {email.summary && (
                      <div className="bg-muted/50 rounded-lg p-3">
                        <p className="text-sm text-muted-foreground mb-1 font-medium">Summary:</p>
                        <p className="text-sm text-foreground">{email.summary}</p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Email Body */}
            <div className="bg-card rounded-lg  p-6 w-full">
              <div className="prose prose-sm max-w-none">
                {email.html_body ? (
                  <div 
                    className="email-content"
                    dangerouslySetInnerHTML={{ __html: email.html_body }}
                    style={{
                      fontSize: '14px',
                      lineHeight: '1.6',
                      color: 'var(--foreground)',
                    }}
                  />
                ) : email.body ? (
                  <div 
                    className="email-content whitespace-pre-wrap"
                    style={{
                      fontSize: '14px',
                      lineHeight: '1.6',
                      color: 'var(--foreground)',
                    }}
                  >
                    {email.body}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No content available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </TooltipProvider>
  );
} 