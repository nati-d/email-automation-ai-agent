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