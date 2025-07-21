"use client"

import * as React from "react"
import Link from "next/link"
import {
  Inbox,
  Star,
  Tag,
  Plus,
  ChevronDown,
  LogOut,
  Settings,
  HelpCircle,
  UserIcon,
  Send,
  FileText,
  ChevronUp,
  Mail,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Define User type locally for now
interface User {
  name: string;
  email: string;
  userId: string;
  isNewUser?: string;
  sessionId: string;
  profilePicture?: string;
}

const SIDEBAR_ITEMS = [
  { label: "Inbox", icon: Inbox, count: 150, active: true, href: "#" },
  { label: "Starred", icon: Star, count: 0, href: "#" },
  { label: "Sent", icon: Send, count: 0, href: "#" },
  { label: "Drafts", icon: FileText, count: 0, href: "#" },
  { label: "Important", icon: Tag, count: 0, href: "#" },
]

const CATEGORIES = [
  { label: "Social", color: "bg-blue-500", count: 5000 },
  { label: "Promotions", color: "bg-green-500", count: 200 },
  { label: "Updates", color: "bg-indigo-500", count: 122 },
  { label: "Updates", color: "bg-indigo-500", count: 122 },
  { label: "Updates", color: "bg-indigo-500", count: 122 },
  { label: "Updates", color: "bg-indigo-500", count: 122 },
]

export function AppSidebar() {
  const { toggleSidebar } = useSidebar()
  const [user, setUser] = React.useState<User | null>(null)

  React.useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      setUser(JSON.parse(stored))
    }
  }, [])

  function handleLogout() {
    localStorage.removeItem("user")
    window.location.reload()
  }

  return (
    <Sidebar className="bg-sidebar text-sidebar-foreground border-r border-zinc-200 w-60 min-w-0 max-w-full overflow-x-hidden" collapsible="none">
      <SidebarHeader className="p-4 flex flex-col gap-4 w-full min-w-0 max-w-full overflow-x-hidden">
        <div className="flex items-center gap-2">
          {/* Email Agent logo */}
          <Mail className="w-6 h-6 text-indigo-600" />
          <span className="text-xl font-semibold text-zinc-800">Email Agent</span>
        </div>
        <Button className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold rounded-full px-6 py-3 shadow transition text-base">
          <Plus className="w-5 h-5 mr-2" /> COMPOSE
        </Button>
      </SidebarHeader>
      <SidebarContent className="flex-1 overflow-y-auto p-2 w-full min-w-0 max-w-full overflow-x-hidden scrollbar-none hide-scrollbar">
        <SidebarGroup>
          <SidebarMenu>
            {SIDEBAR_ITEMS.map(({ label, icon: Icon, count, active, href }) => (
              <SidebarMenuItem key={label}>
                <SidebarMenuButton asChild isActive={active}>
                  <Link href={href} className="flex items-center w-full max-w-full justify-between gap-2 truncate">
                    <span className="flex items-center gap-2 truncate">
                      <Icon className="w-5 h-5 shrink-0" />
                      <span className="truncate">{label}</span>
                    </span>
                    {count > 0 && (
                      <span className="bg-zinc-200 text-zinc-700 rounded-full px-2 py-0.5 text-xs font-semibold truncate max-w-[48px] text-ellipsis overflow-hidden">
                        {count}
                      </span>
                    )}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>

        <SidebarSeparator className="my-4" />

        <Collapsible defaultOpen className="group/collapsible">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex items-center justify-between w-full text-xs font-semibold uppercase tracking-wide text-zinc-500 hover:text-zinc-700 px-2 py-2 rounded-md">
                Categories
                <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent className="mt-2">
                <SidebarMenu>
                  {CATEGORIES.map(({ label, color, count }) => (
                    <SidebarMenuItem key={label}>
                      <SidebarMenuButton asChild>
                        <Link href="#" className="flex items-center w-full max-w-full justify-between gap-2 truncate">
                          <span className="flex items-center gap-2 truncate">
                            <span className={`w-2 h-2 rounded-full ${color}`} />
                            <span className="truncate">{label}</span>
                          </span>
                          <span className="ml-auto bg-blue-100 text-blue-700 rounded-full px-2 py-0.5 text-xs font-semibold truncate max-w-[48px] text-ellipsis overflow-hidden">
                            {count.toLocaleString()}
                          </span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
      </SidebarContent>
      <SidebarFooter className="p-2 border-t border-zinc-200 w-full min-w-0 max-w-full overflow-x-hidden">
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={user?.profilePicture || "/placeholder.svg"} alt={user?.name || "User"} />
                    <AvatarFallback className="bg-zinc-200 text-zinc-700 text-xs font-medium">
                      {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
                    </AvatarFallback>
                  </Avatar>
                  <span className="truncate">{user?.name || "Guest User"}</span>
                  <ChevronUp className="ml-auto h-4 w-4" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent side="top" align="start" className="w-[--radix-popper-anchor-width]">
                <DropdownMenuItem>
                  <UserIcon className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <HelpCircle className="mr-2 h-4 w-4" />
                  <span>Help</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
} 