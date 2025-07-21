"use client";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Reply, ReplyAll, Forward, Calendar, Mail } from "lucide-react";
import React from "react";

interface EmailMetadataProps {
  sender: string;
  senderInitial: string;
  recipients: string[];
  date: string;
  onReply: () => void;
  onReplyAll: () => void;
  onForward: () => void;
}

export const EmailMetadata: React.FC<EmailMetadataProps> = ({ sender, senderInitial, recipients, date, onReply, onReplyAll, onForward }) => (
  <div className="flex items-start gap-4">
    <Avatar className="h-12 w-12 flex-shrink-0">
      <AvatarImage src="/placeholder.svg?height=48&width=48" alt="Sender Avatar" />
      <AvatarFallback className="bg-primary text-primary-foreground text-lg font-semibold">
        {senderInitial}
      </AvatarFallback>
    </Avatar>
    <div className="flex-1 min-w-0">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-foreground mb-1">
            {sender || "Unknown sender"}
          </h2>
          <p className="text-sm text-muted-foreground mb-2">
            {sender && `<${sender}>`}
          </p>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>{date}</span>
            </div>
            {recipients && recipients.length > 0 && (
              <div className="flex items-center gap-1">
                <Mail className="h-4 w-4" />
                <span>to {recipients.join(", ")}</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="sm" aria-label="Reply" onClick={onReply}>
                <Reply className="h-4 w-4 mr-2" />
                Reply
              </Button>
            </TooltipTrigger>
            <TooltipContent>Reply</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="sm" aria-label="Reply all" onClick={onReplyAll}>
                <ReplyAll className="h-4 w-4 mr-2" />
                Reply All
              </Button>
            </TooltipTrigger>
            <TooltipContent>Reply all</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" size="sm" aria-label="Forward" onClick={onForward}>
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
) 