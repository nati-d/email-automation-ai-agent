"use client"

import { useEffect, useState } from "react"
import { fetchEmails, type Email as BaseEmail } from "../lib/api/email";
import { Search, Bell, MoreHorizontal, Star, StarOff, Mail, UserIcon, Tag, Plus } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { AppSidebar } from "@/components/AppSidebar";

// Define User type locally
interface User {
  name: string;
  email: string;
  userId: string;
  isNewUser?: string;
  sessionId: string;
  profilePicture?: string;
}

interface Email extends BaseEmail {
  label?: string;
}

const TABS = [
  { label: "Primary", icon: Mail },
  { label: "Social", icon: UserIcon },
  { label: "Updates", icon: Tag },
]

export default function Home() {
  const [user, setUser] = useState<User | null>(null)
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [starred, setStarred] = useState<{ [id: string]: boolean }>({})
  const [activeTab, setActiveTab] = useState("Primary")

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      setUser(JSON.parse(stored))
    }
  }, [])

  useEffect(() => {
    if (user) {
      setLoading(true)
      fetchEmails()
        .then(setEmails)
        .catch((err) => setError(err.message || "Failed to fetch emails"))
        .finally(() => setLoading(false))
    }
  }, [user])

  function toggleStar(id: string) {
    setStarred((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const filteredEmails = emails.filter(
    (email) =>
      email.subject.toLowerCase().includes(search.toLowerCase()) ||
      email.sender.toLowerCase().includes(search.toLowerCase()) ||
      email.snippet.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="flex h-screen overflow-x-hidden w-full" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      <AppSidebar />
      <div className="flex-1 flex flex-col min-h-0 w-full min-w-0" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
        {/* Top bar */}
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

        {/* Tabs */}
        <div className="flex items-center gap-4 px-6 pt-4 pb-2 border-b" style={{ background: 'var(--card)', borderColor: 'var(--border)' }}>
          {TABS.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm font-semibold transition-colors relative
            ${activeTab === label ? '' : ''}`}
              style={activeTab === label
                ? { color: 'var(--accent)', background: 'var(--accent-foreground)' }
                : { color: 'var(--muted-foreground)' }}
              onClick={() => setActiveTab(label)}
            >
              <Icon className="w-4 h-4" /> {label}
              {activeTab === label && <span className="absolute bottom-0 left-0 w-full h-0.5 rounded-t-sm" style={{ background: 'var(--accent)' }} />}
            </button>
          ))}
          <Button variant="ghost" size="icon" className="ml-auto rounded-full" style={{ color: 'var(--muted-foreground)' }}>
            <Plus className="w-4 h-4" />
            <span className="sr-only">Add tab</span>
          </Button>
        </div>

        {/* Email table header */}
        <div className="flex items-center px-6 py-2 border-b text-xs font-semibold uppercase tracking-wide" style={{ background: 'var(--card)', color: 'var(--muted-foreground)', borderColor: 'var(--border)' }}>
          <input type="checkbox" className="accent-[var(--primary)] w-4 h-4 mr-4" />
          <span className="w-6 mr-2 flex items-center justify-center">
            <StarOff className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
          </span>
          <span className="flex-1">From</span>
          <span className="w-32">Label</span>
          <span className="flex-[2]">Subject</span>
          <span className="w-20 text-right">Date</span>
        </div>

        {/* Email list */}
        <main className="flex-1 overflow-y-auto" style={{ background: 'var(--card)' }}>
          {loading && <div className="text-[var(--muted-foreground)] p-8">Loading emails...</div>}
          {error && <div className="text-[var(--destructive)] p-8">{error}</div>}
          {!loading && !error && filteredEmails.length === 0 && <div className="text-[var(--muted-foreground)] p-8">No emails found.</div>}
          <ul className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {filteredEmails.map((email) => (
              <li
                key={email.id}
                className={`flex items-center px-6 py-3 hover:bg-[var(--muted)] transition-colors cursor-pointer text-sm
              ${email.read ? '' : 'font-bold'}`}
                style={{ background: email.read ? 'var(--card)' : 'var(--accent-foreground)', color: 'var(--foreground)' }}
              >
                <input type="checkbox" className="accent-[var(--primary)] w-4 h-4 mr-4" />
                <button onClick={() => toggleStar(email.id)} className="w-6 mr-2 flex items-center justify-center">
                  {starred[email.id] ? (
                    <Star className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                  ) : (
                    <StarOff className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                  )}
                </button>
                <span className="flex-1 truncate">{email.sender}</span>
                <span className="w-32 truncate" style={{ color: 'var(--muted-foreground)' }}>{email.label || "Client work"}</span>
                <span className="flex-[2] truncate">
                  {email.subject} <span className="text-[var(--muted-foreground)] font-normal">- {email.snippet}</span>
                </span>
                <span className="w-20 text-right flex items-center justify-end gap-1" style={{ color: 'var(--muted-foreground)' }}>
                  {new Date(email.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  {!email.read && <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--accent)' }} />}
                </span>
              </li>
            ))}
          </ul>
        </main>
      </div>
    </div>
  )
}
