import {
  ComposeEmailData,
  Email,
  EmailFilters,
  PaginatedResponse,
  User,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// Types for API responses
export interface AuthResponse {
  authorization_url: string;
  state: string;
  message: string;
}

export interface UserInfoResponse {
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    last_login: string | null;
    created_at: string;
    updated_at: string;
  };
  session_info: {
    provider: string;
    session_active: boolean;
    token_expires_in: number;
  };
}

export interface Category {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LLMResponse {
  content?: string;
  subject?: string;
  sentiment?: string;
  tone?: string;
  professionalism_score?: number;
  suggestions?: string[];
  summary?: string;
  success: boolean;
}

export const ENDPOINTS = {
  auth: "/auth/google/login",
  me: "/auth/me",
  refresh: "/auth/refresh",
  logout: "/auth/logout",
  emails: "/emails",
  email: (id: string) => `/emails/${id}`,
  emailSend: "/emails/send",
  emailDraft: "/emails",
  emailStatus: (id: string) => `/emails/${id}/status`,
  emailDelete: (id: string) => `/emails/${id}`,
  emailSummarize: (id: string) => `/emails/${id}/summarize`,
  emailSummarizeBatch: "/emails/summarize-batch",
  emailTasks: (limit: number = 50) => `/emails/tasks?limit=${limit}`,
  emailInbox: (limit: number = 50) => `/emails/inbox?limit=${limit}`,
  emailCategory: (categoryName: string, limit: number = 50) =>
    `/emails/category/${categoryName}?limit=${limit}`,
  categories: "/categories",
  category: (id: string) => `/categories/${id}`,
  createCategory: "/categories",
  updateCategory: (id: string) => `/categories/${id}`,
  deleteCategory: (id: string) => `/categories/${id}`,
  recategorizeEmails: "/categories/recategorize-emails",
  llmGenerateEmailContent: "/llm/generate-email-content",
  llmAnalyzeEmailSentiment: "/llm/analyze-email-sentiment",
  llmSuggestEmailSubject: "/llm/suggest-email-subject",
  llmSmartEmailComposer: "/llm/smart-email-composer",
  llmGenerateEmailResponse: "/llm/generate-email-response",
  llmChatStart: "/llm/chat/start",
  llmChatSend: (message: string, sessionId: string, modelName?: string) =>
    `/llm/chat/send?message=${message}&session_id=${sessionId}${
      modelName ? `&model_name=${modelName}` : ""
    }`,
  llmChatEnd: (sessionId: string) => `/llm/chat/${sessionId}`,
  llmVisionAnalyze: "/llm/vision/analyze",
  llmToolsExecute: "/llm/tools/execute",
  health: "/health",
  healthDetailed: "/health/detailed",
  users: "/users",
  user: (id: string) => `/users/${id}`,
  createUser: "/users",
  updateUser: (id: string) => `/users/${id}`,
  deleteUser: (id: string) => `/users/${id}`,
  authTestProtected: "/auth-test/protected",
  authTestOptional: "/auth-test/optional",
  authTestUserInfo: "/auth-test/user-info",
  authTestSessionStatus: "/auth-test/session-status",
} as const;

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Get session ID from localStorage for Bearer token
    const sessionId =
      typeof window !== "undefined"
        ? localStorage.getItem("auth-session-id")
        : null;

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...(sessionId && { Authorization: `Bearer ${sessionId}` }),
        ...options.headers,
      },
      credentials: "include",
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Handle authentication errors
        if (response.status === 401) {
          // Clear invalid session
          if (typeof window !== "undefined") {
            localStorage.removeItem("auth-session-id");
          }
          throw new Error("Authentication required");
        }

        throw new Error(
          errorData.detail?.message ||
            errorData.message ||
            `HTTP error! status: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Auth endpoints
  async getAuthUrl(): Promise<AuthResponse> {
    return this.request(ENDPOINTS.auth);
  }

  async getCurrentUser(): Promise<UserInfoResponse> {
    return this.request(ENDPOINTS.me);
  }

  async refreshToken(): Promise<{
    access_token: string;
    expires_in: number;
    message: string;
  }> {
    return this.request(ENDPOINTS.refresh, { method: "POST" });
  }

  async logout(): Promise<{
    success: boolean;
    token_revoked: boolean;
    message: string;
    warning?: string;
  }> {
    return this.request(ENDPOINTS.logout, { method: "POST" });
  }

  // Session management
  setSessionId(sessionId: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth-session-id", sessionId);
    }
  }

  clearSession(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth-session-id");
    }
  }

  getSessionId(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth-session-id");
    }
    return null;
  }

  // Email endpoints
  async getEmails(
    filters: EmailFilters = {},
    limit: number = 50
  ): Promise<{
    emails: Email[];
    total_count: number;
    page: number;
    page_size: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...Object.entries(filters).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key] = value.toString();
        }
        return acc;
      }, {} as Record<string, string>),
    });

    return this.request(`${ENDPOINTS.emails}?${params}`);
  }

  async getEmail(id: string): Promise<Email> {
    return this.request(ENDPOINTS.email(id));
  }

  // Send email directly (clean architecture endpoint)
  async sendEmail(
    data: ComposeEmailData
  ): Promise<{ message: string; email: Email }> {
    return this.request(ENDPOINTS.emailSend, {
      method: "POST",
      body: JSON.stringify({
        recipients: data.to,
        subject: data.subject,
        body: data.body,
        html_body: data.body, // Convert to HTML if needed
      }),
    });
  }

  // Create email draft (legacy endpoint)
  async createEmailDraft(data: ComposeEmailData): Promise<Email> {
    return this.request(ENDPOINTS.emailDraft, {
      method: "POST",
      body: JSON.stringify({
        sender: data.from || "", // Will be set by backend from auth
        recipients: data.to,
        subject: data.subject,
        body: data.body,
        html_body: data.body,
      }),
    });
  }

  // Update email status
  async updateEmailStatus(
    id: string,
    status: string
  ): Promise<{ message: string; email_id: string; status: string }> {
    return this.request(ENDPOINTS.emailStatus(id), {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  }

  // Delete email
  async deleteEmail(
    id: string
  ): Promise<{ message: string; email_id: string }> {
    return this.request(ENDPOINTS.emailDelete(id), { method: "DELETE" });
  }

  // Mark as read (using status update)
  async markAsRead(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "read");
    return this.getEmail(id); // Fetch updated email
  }

  // Mark as unread (using status update)
  async markAsUnread(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "unread");
    return this.getEmail(id); // Fetch updated email
  }

  // Star email (using status update - we'll extend this)
  async starEmail(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "starred");
    return this.getEmail(id); // Fetch updated email
  }

  // Unstar email (using status update)
  async unstarEmail(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "unstarred");
    return this.getEmail(id); // Fetch updated email
  }

  // Archive email (using status update)
  async archiveEmail(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "archived");
    return this.getEmail(id); // Fetch updated email
  }

  // Move to trash (using status update)
  async moveToTrash(id: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, "trash");
    return this.getEmail(id); // Fetch updated email
  }

  // Move to folder (using status update)
  async moveToFolder(id: string, folder: string): Promise<Email> {
    const response = await this.updateEmailStatus(id, folder);
    return this.getEmail(id); // Fetch updated email
  }

  // Email AI features
  async summarizeEmail(emailId: string): Promise<{
    message: string;
    success: boolean;
    already_summarized: boolean;
    summarization: any;
  }> {
    return this.request(ENDPOINTS.emailSummarize(emailId));
  }

  async summarizeMultipleEmails(emailIds: string[]): Promise<{
    message: string;
    success: boolean;
    total_processed: number;
    successful: number;
    already_summarized: number;
    failed: number;
    errors: string[];
  }> {
    return this.request(ENDPOINTS.emailSummarizeBatch, {
      method: "POST",
      body: JSON.stringify(emailIds),
    });
  }

  async getTaskEmails(limit: number = 50): Promise<{
    emails: Email[];
    total_count: number;
    page: number;
    page_size: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    return this.request(ENDPOINTS.emailTasks(limit));
  }

  async getInboxEmails(limit: number = 50): Promise<{
    emails: Email[];
    total_count: number;
    page: number;
    page_size: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    return this.request(ENDPOINTS.emailInbox(limit));
  }

  async getEmailsByCategory(
    categoryName: string,
    limit: number = 50
  ): Promise<{
    emails: Email[];
    total_count: number;
    page: number;
    page_size: number;
    has_next: boolean;
    has_previous: boolean;
  }> {
    return this.request(ENDPOINTS.emailCategory(categoryName, limit));
  }

  // Category management
  async getCategories(
    includeInactive: boolean = false
  ): Promise<{ categories: Category[]; total_count: number }> {
    return this.request(
      `${ENDPOINTS.categories}?include_inactive=${includeInactive}`
    );
  }

  async getCategory(categoryId: string): Promise<Category> {
    return this.request(ENDPOINTS.category(categoryId));
  }

  async createCategory(data: {
    name: string;
    description?: string;
    color?: string;
  }): Promise<Category> {
    return this.request(ENDPOINTS.createCategory, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateCategory(
    categoryId: string,
    data: {
      name?: string;
      description?: string;
      color?: string;
      is_active?: boolean;
    }
  ): Promise<Category> {
    return this.request(ENDPOINTS.updateCategory(categoryId), {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteCategory(
    categoryId: string
  ): Promise<{ message: string; category_id: string }> {
    return this.request(ENDPOINTS.deleteCategory(categoryId), {
      method: "DELETE",
    });
  }

  async recategorizeEmails(): Promise<{
    recategorized_count: number;
    message: string;
  }> {
    return this.request(ENDPOINTS.recategorizeEmails, { method: "POST" });
  }

  // LLM/AI features
  async generateEmailContent(
    prompt: string,
    context?: string
  ): Promise<LLMResponse> {
    return this.request(ENDPOINTS.llmGenerateEmailContent, {
      method: "POST",
      body: JSON.stringify({ prompt, context }),
    });
  }

  async analyzeEmailSentiment(emailContent: string): Promise<LLMResponse> {
    return this.request(ENDPOINTS.llmAnalyzeEmailSentiment, {
      method: "POST",
      body: JSON.stringify({ email_content: emailContent }),
    });
  }

  async suggestEmailSubject(
    emailContent: string,
    context?: string
  ): Promise<LLMResponse> {
    return this.request(ENDPOINTS.llmSuggestEmailSubject, {
      method: "POST",
      body: JSON.stringify({ email_content: emailContent, context }),
    });
  }

  async smartEmailComposer(data: {
    purpose: string;
    recipient_context?: string;
    tone?: string;
    include_subject?: boolean;
  }): Promise<LLMResponse> {
    return this.request(ENDPOINTS.llmSmartEmailComposer, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async generateEmailResponse(data: {
    original_email: string;
    response_type: string;
    additional_context?: string;
  }): Promise<LLMResponse> {
    return this.request(ENDPOINTS.llmGenerateEmailResponse, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async startGeminiChat(data: {
    system_instruction?: string;
    tools?: any[];
    history?: any[];
    session_id?: string;
    model_name?: string;
  }): Promise<{ session_id: string; message: string; success: boolean }> {
    return this.request(ENDPOINTS.llmChatStart, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async sendChatMessage(
    message: string,
    sessionId: string,
    modelName?: string
  ): Promise<{ session_id: string; message: string; success: boolean }> {
    const params = new URLSearchParams({
      message,
      session_id: sessionId,
      ...(modelName && { model_name: modelName }),
    });
    return this.request(ENDPOINTS.llmChatSend(message, sessionId, modelName), {
      method: "POST",
    });
  }

  async endChat(sessionId: string): Promise<{ message: string }> {
    return this.request(ENDPOINTS.llmChatEnd(sessionId), { method: "DELETE" });
  }

  async analyzeImage(data: {
    system_instruction?: string;
    query: string;
    image_base64?: string;
    image_data?: any;
    model_name?: string;
  }): Promise<{ analysis: string; success: boolean }> {
    return this.request(ENDPOINTS.llmVisionAnalyze, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async executeWithTools(data: {
    query: string;
    tools: any[];
    model_name?: string;
  }): Promise<{ result: any; success: boolean }> {
    return this.request(ENDPOINTS.llmToolsExecute, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getLLMHealth(): Promise<{
    status: string;
    model: string;
    available_models: string[];
    timestamp: string;
    error?: string;
  }> {
    return this.request(ENDPOINTS.health);
  }

  // User management
  async createUser(data: {
    email: string;
    name: string;
    role?: string;
  }): Promise<{
    id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    last_login: string | null;
    created_at: string;
    updated_at: string;
  }> {
    return this.request(ENDPOINTS.createUser, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getUser(userId: string): Promise<{
    id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    last_login: string | null;
    created_at: string;
    updated_at: string;
  }> {
    return this.request(ENDPOINTS.user(userId));
  }

  async updateUser(
    userId: string,
    data: {
      name?: string;
      role?: string;
      is_active?: boolean;
    }
  ): Promise<{
    id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    last_login: string | null;
    created_at: string;
    updated_at: string;
  }> {
    return this.request(ENDPOINTS.updateUser(userId), {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteUser(
    userId: string
  ): Promise<{ message: string; user_id: string }> {
    return this.request(ENDPOINTS.deleteUser(userId), { method: "DELETE" });
  }

  // Auth test endpoints
  async testProtectedEndpoint(): Promise<{
    message: string;
    user: any;
    session_info: string;
  }> {
    return this.request(ENDPOINTS.authTestProtected);
  }

  async testOptionalAuth(): Promise<{
    message: string;
    user: any;
    authentication_status: string;
  }> {
    return this.request(ENDPOINTS.authTestOptional);
  }

  async getUserInfo(): Promise<{
    user_id: string;
    email: string;
    name: string;
    role: string;
    is_active: boolean;
    last_login: string | null;
    oauth_info: any;
  }> {
    return this.request(ENDPOINTS.authTestUserInfo);
  }

  async checkSessionStatus(): Promise<{
    status: string;
    message: string;
    user_email: string | null;
    session_active: boolean;
  }> {
    return this.request(ENDPOINTS.authTestSessionStatus);
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request(ENDPOINTS.health);
  }

  async detailedHealthCheck(): Promise<{
    status: string;
    timestamp: string;
    service: string;
    version: string;
    uptime: string;
    dependencies: any;
    features: any;
  }> {
    return this.request(ENDPOINTS.healthDetailed);
  }
}

export const apiClient = new ApiClient();
