// Email types
export interface Email {
  id: string
  sender: string
  recipients: string[]
  subject: string
  body: string
  html_body?: string
  status: string
  scheduled_at?: string
  sent_at?: string
  created_at: string
  updated_at: string
  date: string // For display purposes
  
  // AI Summarization fields
  summary?: string
  main_concept?: string
  sentiment?: string
  key_topics?: string[]
  summarized_at?: string
  
  // Email categorization
  email_type?: string
  category?: string
  categorized_at?: string
  color?: string // Category color
  
  // UI state
  is_read: boolean
  is_starred: boolean
  is_important: boolean
  
  // Attachments
  attachments?: Array<{
    id: string
    filename: string
    size: number
    content_type: string
    url?: string
  }>
  
  // Metadata
  metadata?: Record<string, any>
}

export interface PaginatedResponse<T> {
  data: T[]
  total_count: number
  page: number
  page_size: number
  has_next: boolean
  has_previous: boolean
}

export interface EmailFilters {
  search?: string
  status?: string
  category?: string
  from?: string
  to?: string
  start_date?: string
  end_date?: string
  is_read?: boolean
  is_starred?: boolean
  is_important?: boolean
}

export interface ComposeEmailData {
  to: string[]
  cc?: string[]
  bcc?: string[]
  subject: string
  body: string
  html_body?: string
  attachments?: File[]
  scheduled_at?: Date
  from?: string
}

// Category types
export interface Category {
  id: string
  user_id: string
  name: string
  description?: string
  color?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// LLM response types
export interface LLMResponse {
  content?: string
  subject?: string
  sentiment?: string
  tone?: string
  professionalism_score?: number
  suggestions?: string[]
  summary?: string
  success: boolean
}

// User types
export interface User {
  id: string
  email: string
  name: string
  role: string
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

// Auth types
export interface AuthResponse {
  authorization_url: string
  state: string
  message: string
}

export interface UserInfoResponse {
  user: User
  session_info: {
    provider: string
    session_active: boolean
    token_expires_in: number
  }
}
// 
Chat types
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

export interface ChatSession {
  id: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export type EmailFolder = 'inbox' | 'starred' | 'important' | 'sent' | 'drafts' | 'spam' | 'trash'