"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Inbox,
  Send,
  Archive,
  Trash2,
  Star,
  AlertCircle,
  Clock,
  Tag,
  CheckSquare,
  Plus,
  ChevronDown,
  Mail,
  PenSquare,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { CategoryManagement } from "./category-management";
import { useCategoryStore } from "@/lib/stores/category-store";
import { useEmailStore } from '@/lib/store'

interface SidebarNavProps {
  className?: string;
  selectedFolder: string;
  onFolderSelect: (folder: string) => void;
}

interface NavItem {
  icon: React.ElementType;
  label: string;
  value: string;
  count?: number;
  color?: string;
}

const mainFolders: NavItem[] = [
  { icon: Inbox, label: "Inbox", value: "inbox", count: 12 },
  { icon: Star, label: "Starred", value: "starred" },
  { icon: Clock, label: "Snoozed", value: "snoozed" },
  { icon: Send, label: "Sent", value: "sent" },
  { icon: Archive, label: "Archive", value: "archive" },
  { icon: Trash2, label: "Trash", value: "trash" },
  { icon: AlertCircle, label: "Spam", value: "spam" },
];

export function SidebarNav({
  className,
  selectedFolder,
  onFolderSelect,
}: SidebarNavProps) {
  const { categories } = useCategoryStore();
  const { openCompose } = useEmailStore()

  const folders = [
    {
      id: 'compose',
      label: 'Compose',
      icon: PenSquare,
      onClick: openCompose,
    },
    {
      id: 'inbox',
      label: 'Inbox',
      icon: Inbox,
    },
    {
      id: 'tasks',
      label: 'Tasks',
      icon: CheckSquare,
      href: '/tasks',
    },
    {
      id: 'sent',
      label: 'Sent',
      icon: Send,
    },
    {
      id: 'starred',
      label: 'Starred',
      icon: Star,
    },
    {
      id: 'archive',
      label: 'Archive',
      icon: Archive,
    },
    {
      id: 'trash',
      label: 'Trash',
      icon: Trash2,
    },
  ]

  const bottomItems = [
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      href: '/settings',
    },
  ]

  return (
    <div className={cn("pb-12 w-60", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3">
          <Button
            className="w-full justify-start gap-2"
            size="lg"
            onClick={() => onFolderSelect("compose")}
          >
            <Plus className="h-4 w-4" />
            <span>Compose</span>
          </Button>
        </div>
        <ScrollArea className="h-[calc(100vh-8rem)]">
          <div className="space-y-1 px-3">
            {folders.map((folder) => {
              const Icon = folder.icon
              return (
                <Button
                  key={folder.id}
                  variant="ghost"
                  className={cn(
                    'w-full justify-start',
                    selectedFolder === folder.id && 'bg-muted'
                  )}
                  onClick={() => folder.onClick ? folder.onClick() : onFolderSelect(folder.id)}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {folder.label}
                </Button>
              )
            })}
          </div>
          <Separator className="my-4" />
          <div className="px-3">
            <CategoryManagement />
          </div>
        </ScrollArea>
      </div>

      <div className="py-4 border-t">
        {bottomItems.map((item) => {
          const Icon = item.icon
          return (
            <Button
              key={item.id}
              variant="ghost"
              className="w-full justify-start"
              onClick={() => {
                if (item.href) {
                  window.location.href = item.href
                }
              }}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          )
        })}
      </div>
    </div>
  );
}
