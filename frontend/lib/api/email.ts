import { apiRequest } from '../axiosConfig';

export interface Email {
  id: string;
  sender: string;
  recipients?: string[];
  subject: string;
  body?: string;
  html_body?: string;
  sent_at?: string;
  created_at?: string;
  updated_at?: string;
  summary?: string;
  main_concept?: string;
  sentiment?: string;
  key_topics?: string[];
  status?: string;
  [key: string]: any;
}

export async function fetchEmails(): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: '/emails',
    method: 'GET',
  });
  return response.data.emails;
}

export async function fetchEmailsByCategory(categoryName: string): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: `/emails/category/${encodeURIComponent(categoryName)}`,
    method: 'GET',
  });
  return response.data.emails;
}

export async function fetchEmailById(emailId: string): Promise<Email> {
  const response = await apiRequest<Email>({
    url: `/emails/${emailId}`,
    method: 'GET',
  });
  console.log(response.data);
  return response.data;
}

export async function fetchSentEmailById(emailId: string): Promise<Email> {
  const response = await apiRequest<Email>({
    url: `/emails/sent/${emailId}`,
    method: 'GET',
  });
  console.log(response.data);
  return response.data;
}

export async function fetchInboxEmails(): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: '/emails/inbox',
    method: 'GET',
  });
  console.log(response.data);
  return response.data.emails;
}

export async function fetchTaskEmails(): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: '/emails/tasks',
    method: 'GET',
  });
  console.log(response.data);
  return response.data.emails;
}

export async function fetchSentEmails(): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: '/emails/sent',
    method: 'GET',
  });
  console.log(response.data);
  return response.data.emails;
}

export async function fetchStarredEmails(): Promise<Email[]> {
  const response = await apiRequest<{ emails: Email[] }>({
    url: '/emails/starred',
    method: 'GET',
  });
  console.log(response.data);
  return response.data.emails;
}

export interface SendEmailPayload {
  body: string;
  recipients: string[];
  subject: string;
}

export async function sendEmail(payload: SendEmailPayload) {
  const response = await apiRequest({
    url: '/emails/send',
    method: 'POST',
    data: payload,
  });
  return response.data;
}

export interface EmailSuggestionsPayload {
  query: string;
}

export async function getEmailSuggestions(payload: EmailSuggestionsPayload) {
  const response = await apiRequest({
    url: '/llm/compose-email',
    method: 'POST',
    data: payload,
  });
  return response.data;
}

export interface ChatBotMessage {
  message: string;
}

export interface ChatBotResponse {
  message: string;
}

export async function sendChatBotMessage(payload: ChatBotMessage): Promise<string> {
  const response = await apiRequest<ChatBotResponse>({
    url: '/llm/email-chatbot/chat',
    method: 'POST',
    data: payload,
  });

  console.log(response.data);
  return response.data.message;
}

// Draft API functions
export interface Draft {
  id: string;
  sender: string;
  recipients: string[];
  subject: string;
  body: string;
  html_body?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
  account_owner?: string;
  gmail_draft_id?: string;
  synced_with_gmail?: boolean;
}

export interface CreateDraftPayload {
  recipients: string[];
  subject: string;
  body: string;
  html_body?: string;
  sync_with_gmail?: boolean;
}

export interface UpdateDraftPayload {
  recipients?: string[];
  subject?: string;
  body?: string;
  html_body?: string;
  sync_with_gmail?: boolean;
}

export async function fetchDrafts(): Promise<Draft[]> {
  try {
    console.log('🔍 fetchDrafts API call started');
    const response = await apiRequest<{ drafts: Draft[] }>({
      url: '/drafts/',  // Added trailing slash to avoid 307 redirect
      method: 'GET',
    });
    console.log('✅ fetchDrafts API call successful:', response.data);
    return response.data.drafts;
  } catch (error) {
    console.error('❌ fetchDrafts API call failed:', error);
    throw error;
  }
}

export async function fetchDraftById(draftId: string): Promise<Draft> {
  try {
    console.log('🔍 Fetching draft by ID:', draftId);
    const response = await apiRequest<Draft>({
      url: `/drafts/${draftId}/`,  // Added trailing slash
      method: 'GET',
    });
    console.log('✅ Draft fetched successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to fetch draft by ID:', error);
    throw error;
  }
}

export async function createDraft(payload: CreateDraftPayload): Promise<Draft> {
  try {
    console.log('🔍 Creating draft:', payload);
    const response = await apiRequest<Draft>({
      url: '/drafts/',  // Added trailing slash
      method: 'POST',
      data: payload,
    });
    console.log('✅ Draft created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to create draft:', error);
    throw error;
  }
}

export async function updateDraft(draftId: string, payload: UpdateDraftPayload): Promise<Draft> {
  try {
    console.log('🔍 Updating draft:', draftId, payload);
    const response = await apiRequest<Draft>({
      url: `/drafts/${draftId}/`,  // Added trailing slash
      method: 'PUT',
      data: payload,
    });
    console.log('✅ Draft updated successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to update draft:', error);
    throw error;
  }
}

export async function deleteDraft(draftId: string, syncWithGmail: boolean = true): Promise<{ success: boolean; message: string }> {
  try {
    console.log('🔍 Deleting draft:', draftId, 'syncWithGmail:', syncWithGmail);
    const response = await apiRequest<{ success: boolean; message: string }>({
      url: `/drafts/${draftId}/?sync_with_gmail=${syncWithGmail}`,  // Added trailing slash
      method: 'DELETE',
    });
    console.log('✅ Draft deleted successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to delete draft:', error);
    throw error;
  }
}

export async function sendDraft(draftId: string): Promise<{ success: boolean; message: string }> {
  try {
    console.log('🔍 Sending draft:', draftId);
    const response = await apiRequest<{ success: boolean; message: string }>({
      url: `/drafts/${draftId}/send/`,  // Added trailing slash
      method: 'POST',
    });
    console.log('✅ Draft sent successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to send draft:', error);
    throw error;
  }
}

export async function syncDraftsWithGmail(): Promise<Draft[]> {
  try {
    console.log('🔍 Syncing drafts with Gmail');
    const response = await apiRequest<{ drafts: Draft[] }>({
      url: '/drafts/sync-gmail/',  // Added trailing slash
      method: 'POST',
    });
    console.log('✅ Gmail sync successful:', response.data);
    return response.data.drafts;
  } catch (error) {
    console.error('❌ Failed to sync with Gmail:', error);
    throw error;
  }
}

export async function getDraftCount(): Promise<number> {
  try {
    const drafts = await fetchDrafts();
    return drafts.length;
  } catch (error) {
    console.error('Failed to get draft count:', error);
    return 0;
  }
}

export async function getInboxCount(): Promise<number> {
  try {
    const emails = await fetchInboxEmails();
    return emails.length;
  } catch (error) {
    console.error('Failed to get inbox count:', error);
    return 0;
  }
}

export async function getSentCount(): Promise<number> {
  try {
    const emails = await fetchSentEmails();
    return emails.length;
  } catch (error) {
    console.error('Failed to get sent count:', error);
    return 0;
  }
}

export async function getStarredCount(): Promise<number> {
  try {
    const emails = await fetchStarredEmails();
    return emails.length;
  } catch (error) {
    console.error('Failed to get starred count:', error);
    return 0;
  }
} 