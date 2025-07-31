// This file contains additional API methods to be added to the existing api.ts file

// LLM/AI features
async generateEmailContent(prompt: string, context?: string): Promise<LLMResponse> {
  return this.request('/llm/generate-email-content', {
    method: 'POST',
    body: JSON.stringify({ prompt, context })
  });
}

async analyzeEmailSentiment(emailContent: string): Promise<LLMResponse> {
  return this.request('/llm/analyze-email-sentiment', {
    method: 'POST',
    body: JSON.stringify({ email_content: emailContent })
  });
}

async suggestEmailSubject(emailContent: string, context?: string): Promise<LLMResponse> {
  return this.request('/llm/suggest-email-subject', {
    method: 'POST',
    body: JSON.stringify({ email_content: emailContent, context })
  });
}

async smartEmailComposer(data: {
  purpose: string
  recipient_context?: string
  tone?: string
  include_subject?: boolean
}): Promise<LLMResponse> {
  return this.request('/llm/smart-email-composer', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async generateEmailResponse(data: {
  original_email: string
  response_type: string
  additional_context?: string
}): Promise<LLMResponse> {
  return this.request('/llm/generate-email-response', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// Category management
async getCategories(includeInactive: boolean = false): Promise<{ categories: Category[], total_count: number }> {
  return this.request(`/categories?include_inactive=${includeInactive}`);
}

async getCategory(categoryId: string): Promise<Category> {
  return this.request(`/categories/${categoryId}`);
}

async createCategory(data: {
  name: string
  description?: string
  color?: string
}): Promise<Category> {
  return this.request('/categories', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async updateCategory(categoryId: string, data: {
  name?: string
  description?: string
  color?: string
  is_active?: boolean
}): Promise<Category> {
  return this.request(`/categories/${categoryId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

async deleteCategory(categoryId: string): Promise<{ message: string, category_id: string }> {
  return this.request(`/categories/${categoryId}`, { method: 'DELETE' });
}

async recategorizeEmails(): Promise<{ recategorized_count: number, message: string }> {
  return this.request('/categories/recategorize-emails', { method: 'POST' });
}

// Email operations
async getTaskEmails(limit: number = 50): Promise<{ emails: Email[], total_count: number, page: number, page_size: number, has_next: boolean, has_previous: boolean }> {
  return this.request(`/emails/tasks?limit=${limit}`);
}

async getInboxEmails(limit: number = 50): Promise<{ emails: Email[], total_count: number, page: number, page_size: number, has_next: boolean, has_previous: boolean }> {
  return this.request(`/emails/inbox?limit=${limit}`);
}

async getEmailsByCategory(categoryName: string, limit: number = 50): Promise<{ emails: Email[], total_count: number, page: number, page_size: number, has_next: boolean, has_previous: boolean }> {
  return this.request(`/emails/category/${categoryName}?limit=${limit}`);
}

async summarizeEmail(emailId: string): Promise<{
  message: string
  success: boolean
  already_summarized: boolean
  summarization: any
}> {
  return this.request(`/emails/${emailId}/summarize`, { method: 'POST' });
}

async summarizeMultipleEmails(emailIds: string[]): Promise<{
  message: string
  success: boolean
  total_processed: number
  successful: number
  already_summarized: number
  failed: number
  errors: string[]
}> {
  return this.request('/emails/summarize-batch', {
    method: 'POST',
    body: JSON.stringify(emailIds)
  });
}

// Email status operations
async markAsRead(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'read');
  return this.getEmail(id); // Fetch updated email
}

async markAsUnread(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'unread');
  return this.getEmail(id); // Fetch updated email
}

async starEmail(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'starred');
  return this.getEmail(id); // Fetch updated email
}

async unstarEmail(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'unstarred');
  return this.getEmail(id); // Fetch updated email
}

async archiveEmail(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'archived');
  return this.getEmail(id); // Fetch updated email
}

async moveToTrash(id: string): Promise<Email> {
  const response = await this.updateEmailStatus(id, 'trash');
  return this.getEmail(id); // Fetch updated email
}

async updateEmailStatus(id: string, status: string): Promise<{ message: string, email_id: string, status: string }> {
  return this.request(`/emails/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}