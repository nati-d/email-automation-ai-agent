"use client"

import { useEffect, useState } from "react"
import { fetchEmails, fetchEmailsByCategory, fetchInboxEmails, fetchTaskEmails, type Email as BaseEmail } from "../lib/api/email";
import { Star, StarOff, Mail, UserIcon, Tag, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatEmailDate } from "../lib/utils";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/AppContext";

interface Email extends BaseEmail {
  label?: string;
  category?: string;
  sentiment?: string;
  main_concept?: string;
  key_topics?: string[];
  summary?: string;
  sent_at?: string;
  created_at?: string;
  updated_at?: string;
  scheduled_at?: string;
  summarized_at?: string;
  categorized_at?: string;
  email_type?: string;
  status?: string;
  body?: string;
  html_body?: string;
  recipients?: string[];
  account_owner?: string;
  email_holder?: string;
  metadata?: Record<string, any>;
}

const TABS = [
  { label: "All", icon: Mail },
  { label: "Inbox", icon: Mail },
  { label: "Tasks", icon: Tag },
]

export default function Home() {
  const { user, search, currentCategory } = useApp()
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [starred, setStarred] = useState<{ [id: string]: boolean }>({})
  const [activeTab, setActiveTab] = useState("Primary")
  const router = useRouter();

  useEffect(() => {
    if (user) {
      setLoading(true)
      const fetchData = async () => {
        try {
          let data: Email[]
          if (activeTab === "All") {
            data = await fetchEmails();
          } else if (activeTab === "Inbox") {
            data = await fetchInboxEmails();
          } else if (activeTab === "Tasks") {
            data = await fetchTaskEmails();
          } else if (currentCategory) {
            data = await fetchEmailsByCategory(currentCategory);
          } else {
            data = await fetchEmails();
          }
          setEmails(data)
        } catch (err: any) {
          setError(err.message || "Failed to fetch emails")
        } finally {
          setLoading(false)
        }
      }
      fetchData()
    }
  }, [user, currentCategory, activeTab])

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
    <div className="flex flex-col min-h-0 w-full min-w-0 h-full overflow-x-hidden" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
        {/* Category Header */}
        {currentCategory && (
          <div className="flex items-center gap-2 px-6 py-3 bg-card border-b" style={{ borderColor: 'var(--border)' }}>
            <Tag className="w-4 h-4" style={{ color: 'var(--primary)' }} />
            <span className="text-sm font-medium text-foreground">
              Category: {currentCategory}
            </span>
            <span className="text-sm text-muted-foreground">
              ({filteredEmails.length} emails)
            </span>
          </div>
        )}

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
          <span className="flex-[2]">Subject</span>
          <span className="flex-1">Email Holder</span>
          <span className="w-20 text-right">Date</span>
        </div>

        {/* Email list */}
        <main className="flex-1 overflow-y-auto" style={{ background: 'var(--card)' }}>
          {loading && <div className="text-[var(--muted-foreground)] p-8">Loading emails...</div>}
          {error && <div className="text-[var(--destructive)] p-8">{error}</div>}
          {!loading && !error && filteredEmails.length === 0 && (
            <div className="text-[var(--muted-foreground)] p-8">
              {currentCategory ? `No emails found in category "${currentCategory}".` : "No emails found."}
            </div>
          )}
          <ul className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {filteredEmails.map((email) => {
              return (
                <li
                  key={email.id}
                  className={`flex flex-col px-6 py-3 hover:bg-[var(--muted)] transition-colors cursor-pointer text-sm ${email.read ? '' : 'font-bold'}`}
                  style={{ background: email.read ? 'var(--card)' : 'var(--accent-foreground)', color: 'var(--foreground)' }}
                  onClick={() => router.push(`/email/${email.id}`)}
                >
                  <div className="flex items-center w-full" onClick={e => e.stopPropagation()}>
                    <input type="checkbox" className="accent-[var(--primary)] w-4 h-4 mr-4" />
                    <button onClick={(e) => { e.stopPropagation(); toggleStar(email.id); }} className="w-6 mr-2 flex items-center justify-center">
                      {starred[email.id] ? (
                        <Star className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                      ) : (
                        <StarOff className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                      )}
                    </button>
                    <span className="flex-1 truncate">{email.sender}</span>
                    <span className="flex-[2] truncate">
                      {email.subject} <span className="text-[var(--muted-foreground)] font-normal">- {email.snippet}</span>
                    </span>
                    <span className="flex-1 truncate text-muted-foreground">{email.email_holder || '-'}</span>
                    <span className="w-20 text-right flex items-center justify-end gap-1" style={{ color: 'var(--muted-foreground)' }}>
                      {formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
                      {!email.read && <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--accent)' }} />}
                    </span>
                  </div>
                  {/* AI Insights Bar */}
                  <div className="flex flex-wrap items-center gap-2 mt-1 pl-12">
                    {/* Sentiment Dot */}
                    {email.sentiment && (
                      <span
                        className="w-2 h-2 rounded-full inline-block"
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
                        title={email.sentiment.charAt(0).toUpperCase() + email.sentiment.slice(1)}
                      />
                    )}
                    {/* Main Concept Badge */}
                    {email.main_concept && (
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold" style={{ background: 'var(--accent)', color: 'var(--accent-foreground)' }}>
                        {email.main_concept}
                      </span>
                    )}
                    {/* Key Topics Chips */}
                    {email.key_topics && Array.isArray(email.key_topics) && email.key_topics.slice(0, 3).map((topic) => (
                      <span key={topic} className="px-2 py-0.5 rounded-full text-xs font-medium" style={{ background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
                        #{topic}
                      </span>
                    ))}
                    {/* AI Summary */}
                    {email.summary && (
                      <span className="text-xs text-[var(--muted-foreground)] ml-2 truncate max-w-[60%]" title={email.summary}>
                        {email.summary}
                      </span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </main>
    </div>
  )
}
