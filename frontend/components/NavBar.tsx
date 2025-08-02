"use client"

import { Search, Menu } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useSidebar } from "@/components/ui/sidebar"
import { useApp } from "./AppContext"

export function NavBar() {
  const { user, search, setSearch } = useApp()
  const { toggleSidebar } = useSidebar()
  
  return (
    <header
      className="flex items-center justify-between px-4 sm:px-6 py-3 border-b shadow-sm sticky top-0 z-10"
      style={{ background: 'var(--card)', color: 'var(--card-foreground)', borderColor: 'var(--border)' }}
    >
      <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
        {/* Sidebar Toggle Button */}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={toggleSidebar}
          className="rounded-lg h-8 w-8 sm:h-9 sm:w-9 shrink-0" 
          style={{ color: 'var(--muted-foreground)' }}
        >
          <Menu className="w-4 h-4 sm:w-5 sm:h-5" />
          <span className="sr-only">Toggle sidebar</span>
        </Button>
        
        <Search className="w-4 h-4 sm:w-5 sm:h-5 shrink-0" style={{ color: 'var(--muted-foreground)' }} />
        <Input
          type="text"
          placeholder="Search mail"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-none sm:max-w-lg px-3 sm:px-4 py-2 rounded-full border bg-[var(--muted)] text-[var(--foreground)] focus:outline-none focus:ring-2 text-sm sm:text-base"
          style={{ borderColor: 'var(--input)', background: 'var(--muted)', color: 'var(--foreground)' }}
        />
      </div>
      <div className="flex items-center shrink-0">
        {/* User Avatar with Hover Tooltip */}
        <div className="relative group">
          <Avatar className="h-8 w-8 sm:h-9 sm:w-9 cursor-pointer transition-transform hover:scale-105">
            <AvatarImage src={user?.profilePicture || "/placeholder.svg"} alt={user?.name || "User"} />
            <AvatarFallback className="bg-[var(--primary)] text-[var(--primary-foreground)] text-sm font-medium">
              {user?.name ? user.name.charAt(0).toUpperCase() : "A"}
            </AvatarFallback>
          </Avatar>
          
          {/* Hover Tooltip */}
          <div className="absolute right-0 top-full mt-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
            <div className="font-medium">{user?.name || "User"}</div>
            <div className="text-gray-300 text-xs">{user?.email || "No email"}</div>
            {/* Tooltip Arrow */}
            <div className="absolute -top-1 right-3 w-2 h-2 bg-gray-900 rotate-45"></div>
          </div>
        </div>
      </div>
    </header>
  )
} 