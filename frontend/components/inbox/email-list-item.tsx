"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  Star, 
  Paperclip, 
  Reply, 
  Archive, 
  Trash2,
  MoreHorizontal
} from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

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

interface EmailListItemProps {
  email: Email;
  isSelected: boolean;
  onSelect: () => void;
  onClick: () => void;
}

export function EmailListItem({
  email,
  isSelected,
  onSelect,
  onClick
}: EmailListItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getSenderInitials = (sender: string) => {
    const name = sender.split('@')[0];
    return name.slice(0, 2).toUpperCase();
  };

  const getSenderName = (sender: string) => {
    return sender.split('@')[0];
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + "...";
  };

  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return "Unknown";
    }
  };

  const handleStarClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    // TODO: Implement star functionality
    console.log("Star clicked for email:", email.id);
  };

  const handleActionClick = (e: React.MouseEvent, action: string) => {
    e.stopPropagation();
    console.log(`${action} clicked for email:`, email.id);
    // TODO: Implement actions
  };

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-4 hover:bg-muted/50 cursor-pointer transition-colors border-l-2",
        email.is_read ? "border-l-transparent" : "border-l-primary bg-muted/20",
        isSelected && "bg-muted"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Checkbox */}
      <div className="flex items-center pt-1">
        <Checkbox
          checked={isSelected}
          onCheckedChange={onSelect}
          onClick={(e) => e.stopPropagation()}
        />
      </div>

      {/* Avatar */}
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback className="text-xs">
          {getSenderInitials(email.sender)}
        </AvatarFallback>
      </Avatar>

      {/* Email Content */}
      <div className="flex-1 min-w-0 space-y-1">
        {/* Header Row */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className={cn(
              "font-medium text-sm truncate",
              !email.is_read && "font-semibold"
            )}>
              {getSenderName(email.sender)}
            </span>
            {!email.is_read && (
              <div className="h-2 w-2 bg-primary rounded-full flex-shrink-0" />
            )}
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-xs text-muted-foreground">
              {formatDate(email.created_at)}
            </span>
          </div>
        </div>

        {/* Subject */}
        <div className={cn(
          "text-sm",
          !email.is_read ? "font-medium" : "text-muted-foreground"
        )}>
          {truncateText(email.subject, 60)}
        </div>

        {/* Summary/Preview */}
        <div className="text-xs text-muted-foreground">
          {email.summary 
            ? truncateText(email.summary, 100)
            : truncateText(email.body.replace(/<[^>]*>/g, ''), 100)
          }
        </div>

        {/* Category Badge */}
        {email.category && (
          <Badge variant="outline" className="text-xs w-fit">
            {email.category}
          </Badge>
        )}
      </div>

      {/* Actions */}
      <div className={cn(
        "flex items-center gap-1 flex-shrink-0 transition-opacity",
        isHovered ? "opacity-100" : "opacity-0"
      )}>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={handleStarClick}
        >
          <Star className={cn(
            "h-3 w-3",
            email.is_starred && "fill-yellow-400 text-yellow-400"
          )} />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={(e) => handleActionClick(e, "reply")}
        >
          <Reply className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={(e) => handleActionClick(e, "archive")}
        >
          <Archive className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={(e) => handleActionClick(e, "delete")}
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}