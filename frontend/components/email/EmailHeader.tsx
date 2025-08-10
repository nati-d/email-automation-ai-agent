"use client";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ArrowLeft, Archive, Trash, MailOpen, MoreVertical, Star, Printer, ExternalLink, Info } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import React from "react";

interface EmailHeaderProps {
  subject: string;
  sender: string;
  date: string;
  onBack: () => void;
  isDraft?: boolean;
}

export const EmailHeader: React.FC<EmailHeaderProps> = ({ subject, sender, date, onBack, isDraft = false }) => (
  <header className="flex items-center justify-between py-4 px-2 bg-card shadow-sm">
    <div className="flex items-center gap-4">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Back to inbox"
            onClick={onBack}
            className="rounded-full p-0 w-10 h-10 flex items-center justify-center hover:bg-muted focus:ring-2 focus:ring-primary/50"
            style={{ marginLeft: '-4px' }}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Back to inbox</TooltipContent>
      </Tooltip>
      <div className="flex flex-col">
        <h1 className="text-xl font-semibold text-foreground truncate max-w-[calc(100vw-400px)] md:max-w-2xl">
          {subject || "(No subject)"}
        </h1>
        <p className="text-sm text-muted-foreground">
          {isDraft ? `Draft • ${date}` : `${sender} • ${date}`}
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
); 