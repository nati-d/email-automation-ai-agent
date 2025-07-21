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
    <div className="flex h-screen overflow-x-hidden w-full">
      <AppSidebar />
      <div className="flex-1 flex flex-col min-h-0 w-full min-w-0">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-zinc-100 shadow-sm sticky top-0 z-10">
          <div className="flex items-center gap-4 flex-1">
            <Search className="w-5 h-5 text-zinc-400" />
            <Input
              type="text"
              placeholder="Search mail"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full max-w-lg px-4 py-2 rounded-full border border-zinc-200 bg-zinc-100 text-zinc-800 focus:outline-none focus:ring-2 focus:ring-blue-400 text-base"
            />
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="rounded-full">
              <Bell className="w-5 h-5 text-zinc-500" />
              <span className="sr-only">Notifications</span>
            </Button>
            <Button variant="ghost" size="icon" className="rounded-full">
              <MoreHorizontal className="w-5 h-5 text-zinc-500" />
              <span className="sr-only">More options</span>
            </Button>
            <Avatar className="h-8 w-8 ml-2">
              <AvatarImage src={user?.profilePicture || "/placeholder.svg"} alt={user?.name || "User"} />
              <AvatarFallback className="bg-blue-500 text-white text-sm font-medium">
                {user?.name ? user.name.charAt(0).toUpperCase() : "A"}
              </AvatarFallback>
            </Avatar>
          </div>
        </header>

        {/* Tabs */}
        <div className="flex items-center gap-4 px-6 pt-4 pb-2 bg-white border-b border-zinc-100">
          {TABS.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm font-semibold transition-colors relative
            ${activeTab === label ? "text-blue-700" : "text-zinc-500 hover:text-zinc-700"}`}
              onClick={() => setActiveTab(label)}
            >
              <Icon className="w-4 h-4" /> {label}
              {activeTab === label && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500 rounded-t-sm" />}
            </button>
          ))}
          <Button variant="ghost" size="icon" className="ml-auto rounded-full text-zinc-500 hover:text-zinc-700">
            <Plus className="w-4 h-4" />
            <span className="sr-only">Add tab</span>
          </Button>
        </div>

        {/* Email table header */}
        <div className="flex items-center px-6 py-2 bg-white border-b border-zinc-100 text-xs text-zinc-500 font-semibold uppercase tracking-wide">
          <input type="checkbox" className="accent-blue-500 w-4 h-4 mr-4" />
          <span className="w-6 mr-2 flex items-center justify-center">
            <StarOff className="w-4 h-4 text-zinc-400" />
          </span>
          <span className="flex-1">From</span>
          <span className="w-32">Label</span>
          <span className="flex-[2]">Subject</span>
          <span className="w-20 text-right">Date</span>
        </div>

        {/* Email list */}
        <main className="flex-1 overflow-y-auto bg-white">
          {loading && <div className="text-zinc-500 p-8">Loading emails...</div>}
          {error && <div className="text-red-600 p-8">{error}</div>}
          {!loading && !error && filteredEmails.length === 0 && <div className="text-zinc-500 p-8">No emails found.</div>}
          <ul className="divide-y divide-zinc-100">
            {filteredEmails.map((email) => (
              <li
                key={email.id}
                className={`flex items-center px-6 py-3 hover:bg-zinc-50 transition-colors cursor-pointer text-sm
              ${email.read ? "bg-white" : "bg-blue-50 font-bold"}`}
              >
                <input type="checkbox" className="accent-blue-500 w-4 h-4 mr-4" />
                <button onClick={() => toggleStar(email.id)} className="w-6 mr-2 flex items-center justify-center">
                  {starred[email.id] ? (
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  ) : (
                    <StarOff className="w-4 h-4 text-zinc-400" />
                  )}
                </button>
                <span className="flex-1 truncate text-zinc-800">{email.sender}</span>
                <span className="w-32 truncate text-zinc-500">{email.label || "Client work"}</span>
                <span className="flex-[2] truncate text-zinc-700">
                  {email.subject} <span className="text-zinc-400 font-normal">- {email.snippet}</span>
                </span>
                <span className="w-20 text-right text-zinc-400 flex items-center justify-end gap-1">
                  {new Date(email.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  {!email.read && <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />}
                </span>
              </li>
            ))}
          </ul>
        </main>
      </div>
    </div>
  )
}
