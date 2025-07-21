"use client"

import { Search, Bell, MoreHorizontal } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useApp } from "./AppContext"

export function NavBar() {
  const { user, search, setSearch } = useApp()
  return (
    <header
      className="flex items-center justify-between px-6 py-3 border-b shadow-sm sticky top-0 z-10"
      style={{ background: 'var(--card)', color: 'var(--card-foreground)', borderColor: 'var(--border)' }}
    >
      <div className="flex items-center gap-4 flex-1">
        <Search className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
        <Input
          type="text"
          placeholder="Search mail"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-lg px-4 py-2 rounded-full border bg-[var(--muted)] text-[var(--foreground)] focus:outline-none focus:ring-2 text-base"
          style={{ borderColor: 'var(--input)', background: 'var(--muted)', color: 'var(--foreground)' }}
        />
      </div>
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="rounded-full" style={{ color: 'var(--muted-foreground)' }}>
          <Bell className="w-5 h-5" />
          <span className="sr-only">Notifications</span>
        </Button>
        <Button variant="ghost" size="icon" className="rounded-full" style={{ color: 'var(--muted-foreground)' }}>
          <MoreHorizontal className="w-5 h-5" />
          <span className="sr-only">More options</span>
        </Button>
        <Avatar className="h-8 w-8 ml-2">
          <AvatarImage src={user?.profilePicture || "/placeholder.svg"} alt={user?.name || "User"} />
          <AvatarFallback className="bg-[var(--primary)] text-[var(--primary-foreground)] text-sm font-medium">
            {user?.name ? user.name.charAt(0).toUpperCase() : "A"}
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
} 