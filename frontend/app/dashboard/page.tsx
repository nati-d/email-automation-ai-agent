"use client"

import { useEffect, useState } from "react"
import { fetchEmails, fetchEmailsByCategory, fetchInboxEmails, fetchTaskEmails, fetchSentEmails, fetchStarredEmails, fetchDrafts, type Email as BaseEmail } from "../../lib/api/email";
import { Star, StarOff, Mail, Tag, Plus, Reply } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatEmailDate } from "../../lib/utils";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/AppContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useComposeModal } from "@/components/email/ComposeEmail";
import ChatBot from "@/components/ChatBot";

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
  { label: "All", value: "all", icon: Mail },
  { label: "Inbox", value: "inbox", icon: Mail },
  { label: "Tasks", value: "tasks", icon: Tag },
]

export default function Dashboard() {
  const { user, search, currentCategory, currentEmailType, setCurrentEmailType, refreshTrigger } = useApp()
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [starred, setStarred] = useState<{ [id: string]: boolean }>({})
  const [activeTab, setActiveTab] = useState("all")
  const router = useRouter();
  const { replyToEmail } = useComposeModal();

  const handleTabClick = (tabValue: string) => {
    setActiveTab(tabValue)
    // Clear currentEmailType when clicking dashboard tabs so they take precedence
    setCurrentEmailType("inbox")
  }

  useEffect(() => {
    if (user) {
      setLoading(true)
      const fetchData = async () => {
        try {
          let data: Email[]

          // If a category is selected, fetch emails by category
          if (currentCategory) {
            data = await fetchEmailsByCategory(currentCategory);
          }
          // If currentEmailType is set from sidebar (sent, starred, etc.), use that
          else if (currentEmailType && currentEmailType !== 'inbox') {
            switch (currentEmailType) {
              case "sent":
                data = await fetchSentEmails();
                // Add snippet field if missing for sent emails
                data = data.map(email => ({
                  ...email,
                  snippet: email.snippet || email.body?.substring(0, 100) || '',
                  read: email.read !== undefined ? email.read : true, // Assume sent emails are read
                }));
                break;
              case "starred":
                data = await fetchStarredEmails();
                break;
              case "tasks":
                data = await fetchTaskEmails();
                break;
              case "drafts":
                console.log('Fetching drafts for dashboard...');
                data = await fetchDrafts();
                console.log('Fetched drafts:', data.length);
                // Add snippet field if missing for drafts
                data = data.map(email => ({
                  ...email,
                  snippet: email.snippet || email.body?.substring(0, 100) || '',
                  read: email.read !== undefined ? email.read : true, // Assume drafts are read
                }));
                break;
              default:
                data = await fetchEmails();
                break;
            }
          }
          // Otherwise, fetch emails based on the active tab
          else {
            switch (activeTab) {
              case "inbox":
                data = await fetchInboxEmails();
                break;
              case "tasks":
                data = await fetchTaskEmails();
                break;
              case "all":
              default:
                data = await fetchEmails();
                break;
            }
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
  }, [user, currentCategory, currentEmailType, activeTab, refreshTrigger])

  function toggleStar(id: string) {
    setStarred((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  function handleReply(email: Email) {
    replyToEmail({
      id: email.id,
      sender: email.sender,
      subject: email.subject || "(No subject)",
      body: email.body,
      recipients: email.recipients
    });
  }

  const filteredEmails = emails.filter(
    (email) =>
      (email.subject || '').toLowerCase().includes(search.toLowerCase()) ||
      (email.sender || '').toLowerCase().includes(search.toLowerCase()) ||
      (email.snippet || '').toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <ProtectedRoute>
      <div className="flex flex-col min-h-0 w-full min-w-0 h-full overflow-x-hidden" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
        {/* Category Header */}
        {currentCategory && (
          <div className="flex items-center gap-2 px-4 sm:px-6 py-3 bg-card border-b" style={{ borderColor: 'var(--border)' }}>
            <Tag className="w-4 h-4" style={{ color: 'var(--primary)' }} />
            <span className="text-sm font-medium text-foreground">
              Category: {currentCategory}
            </span>
            <span className="text-sm text-muted-foreground hidden sm:inline">
              ({filteredEmails.length} emails)
            </span>
          </div>
        )}

        {/* Tabs */}
        <div className="flex items-center gap-2 sm:gap-4 px-4 sm:px-6 pt-4 pb-2 border-b overflow-x-auto" style={{ background: 'var(--card)', borderColor: 'var(--border)' }}>
          {TABS.map(({ label, value, icon: Icon }) => (
            <button
              key={value}
              className={`flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 rounded-t-lg text-sm font-semibold transition-colors relative whitespace-nowrap
            ${activeTab === value ? '' : ''}`}
              style={activeTab === value
                ? { color: 'var(--accent)', background: 'var(--accent-foreground)' }
                : { color: 'var(--muted-foreground)' }}
              onClick={() => handleTabClick(value)}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
              {activeTab === value && <span className="absolute bottom-0 left-0 w-full h-0.5 rounded-t-sm" style={{ background: 'var(--accent)' }} />}
            </button>
          ))}
          <Button variant="ghost" size="icon" className="ml-auto rounded-full shrink-0" style={{ color: 'var(--muted-foreground)' }}>
            <Plus className="w-4 h-4" />
            <span className="sr-only">Add tab</span>
          </Button>
        </div>

        {/* Email table header - Hidden on mobile */}
        <div className="hidden md:flex items-center px-4 sm:px-6 py-2 border-b text-xs font-semibold uppercase tracking-wide" style={{ background: 'var(--card)', color: 'var(--muted-foreground)', borderColor: 'var(--border)' }}>
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
                  className={`group flex flex-col px-4 sm:px-6 py-3 hover:bg-[var(--muted)] transition-colors cursor-pointer text-sm ${email.read ? '' : 'font-bold'}`}
                  style={{ background: email.read ? 'var(--card)' : 'var(--accent-foreground)', color: 'var(--foreground)' }}
                  onClick={() => {
                    if (email.id) {
                      router.push(`/email/${email.id}`);
                    } else {
                      console.error('Email ID is missing:', email);
                    }
                  }}
                >
                  {/* Desktop Layout */}
                  <div className="hidden md:flex items-center w-full">
                    <input 
                      type="checkbox" 
                      className="accent-[var(--primary)] w-4 h-4 mr-4" 
                      onClick={(e) => e.stopPropagation()}
                    />
                    <button 
                      onClick={(e) => { e.stopPropagation(); toggleStar(email.id); }} 
                      className="w-6 mr-2 flex items-center justify-center"
                    >
                      {starred[email.id] ? (
                        <Star className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                      ) : (
                        <StarOff className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                      )}
                    </button>
                    <span className="flex-1 truncate">{email.sender || 'Unknown sender'}</span>
                    <span className="flex-[2] truncate">
                      {email.subject || '(No subject)'} <span className="text-[var(--muted-foreground)] font-normal">- {email.snippet || ''}</span>
                    </span>
                    <span className="flex-1 truncate text-muted-foreground">{email.email_holder || '-'}</span>
                    <span className="w-20 text-right flex items-center justify-end gap-1" style={{ color: 'var(--muted-foreground)' }}>
                      {formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
                      {!email.read && <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--accent)' }} />}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReply(email);
                      }}
                      title="Reply"
                    >
                      <Reply className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Mobile Layout */}
                  <div className="md:hidden">
                    {/* Top Row: Sender, Star, Date */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <input 
                          type="checkbox" 
                          className="accent-[var(--primary)] w-4 h-4" 
                          onClick={(e) => e.stopPropagation()}
                        />
                        <button 
                          onClick={(e) => { e.stopPropagation(); toggleStar(email.id); }} 
                          className="flex items-center justify-center"
                        >
                          {starred[email.id] ? (
                            <Star className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                          ) : (
                            <StarOff className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                          )}
                        </button>
                        <span className="font-medium truncate" style={{ color: 'var(--foreground)' }}>
                          {email.sender || 'Unknown sender'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                          {formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
                        </span>
                        {!email.read && <span className="w-2 h-2 rounded-full" style={{ background: 'var(--accent)' }} />}
                      </div>
                    </div>

                    {/* Subject Line */}
                    <div className="mb-2">
                      <div className="font-medium text-sm truncate" style={{ color: 'var(--foreground)' }}>
                        {email.subject || '(No subject)'}
                      </div>
                      {email.snippet && (
                        <div className="text-xs mt-1 line-clamp-2" style={{ color: 'var(--muted-foreground)' }}>
                          {email.snippet}
                        </div>
                      )}
                    </div>

                    {/* Bottom Row: Email Holder and Reply Button */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs truncate" style={{ color: 'var(--muted-foreground)' }}>
                        {email.email_holder || 'No holder'}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 px-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleReply(email);
                        }}
                        title="Reply"
                      >
                        <Reply className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* AI Insights Bar - Responsive */}
                  <div className="flex flex-wrap items-center gap-2 mt-2 md:mt-1 md:pl-12">
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
                    {/* Key Topics Chips - Limit on mobile */}
                    {email.key_topics && Array.isArray(email.key_topics) && email.key_topics.slice(0, window.innerWidth < 768 ? 2 : 3).map((topic) => (
                      <span key={topic} className="px-2 py-0.5 rounded-full text-xs font-medium" style={{ background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
                        #{topic}
                      </span>
                    ))}
                    {/* AI Summary - Hidden on small mobile */}
                    {email.summary && (
                      <span className="hidden sm:inline text-xs text-[var(--muted-foreground)] ml-2 truncate max-w-[60%]" title={email.summary}>
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

      {/* Floating ChatBot */}
      <ChatBot />
    </ProtectedRoute>
  )
}