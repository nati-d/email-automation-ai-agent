import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Email, Category } from "./types";

interface EmailResponse {
  emails: Email[];
  total_count: number;
  has_next: boolean;
  has_previous: boolean;
}

interface SendEmailData {
  recipients: string[]; // Array of 1-100 recipients
  subject: string; // 1-200 characters
  body: string; // 1-50000 characters
  html_body?: string; // Optional HTML body
  metadata?: Record<string, any>; // Optional metadata
  cc?: string[];
  bcc?: string[];
  attachments?: File[];
}

// API endpoints - point to backend server
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const ENDPOINTS = {
  emails: `${API_BASE}/emails`,
  inbox: `${API_BASE}/emails/inbox`,
  tasks: `${API_BASE}/emails/tasks`,
  categories: `${API_BASE}/categories`,
  categoryEmails: (categoryName: string) =>
    `${API_BASE}/emails/category/${categoryName}`,
  recategorizeEmails: `${API_BASE}/categories/recategorize-emails`,
};

// Helper function to get auth headers
const getAuthHeaders = () => {
  const sessionId =
    typeof window !== "undefined"
      ? localStorage.getItem("auth-session-id")
      : null;
  return {
    "Content-Type": "application/json",
    ...(sessionId && { Authorization: `Bearer ${sessionId}` }),
  };
};

// Helper function for authenticated fetch
const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
  const sessionId =
    typeof window !== "undefined"
      ? localStorage.getItem("auth-session-id")
      : null;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
    ...(sessionId && { Authorization: `Bearer ${sessionId}` }),
  };

  // Don't set Content-Type for FormData (let browser set it with boundary)
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  return fetch(url, {
    ...options,
    headers,
  });
};

// Fetch single email
const fetchEmail = async (emailId: string): Promise<Email> => {
  const response = await authenticatedFetch(`${ENDPOINTS.emails}/${emailId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch email");
  }
  return response.json();
};

// Fetch emails with limit parameter
const fetchEmails = async (
  endpoint: string,
  limit = 50
): Promise<EmailResponse> => {
  const response = await authenticatedFetch(`${endpoint}?limit=${limit}`);
  if (!response.ok) {
    throw new Error("Failed to fetch emails");
  }
  return response.json();
};

// Query hooks
export const useEmail = (emailId: string) => {
  return useQuery({
    queryKey: ["email", emailId],
    queryFn: () => fetchEmail(emailId),
  });
};

// Clean up email queries to use proper endpoints
export const useInboxEmails = (limit = 50) => {
  return useQuery({
    queryKey: ["emails", "inbox", limit],
    queryFn: () => fetchEmails(ENDPOINTS.inbox, limit),
  });
};

export const useTaskEmails = (limit = 50) => {
  return useQuery({
    queryKey: ["emails", "tasks", limit],
    queryFn: () => fetchEmails(ENDPOINTS.tasks, limit),
  });
};

// Generic emails query for all emails
export const useAllEmails = (limit = 50) => {
  return useQuery({
    queryKey: ["emails", "all", limit],
    queryFn: () => fetchEmails(ENDPOINTS.emails, limit),
  });
};
export const useCategoryEmails = (categoryName: string) => {
  return useQuery({
    queryKey: ["emails", "category", categoryName],
    queryFn: async () => {
      const response = await authenticatedFetch(
        ENDPOINTS.categoryEmails(categoryName)
      );
      if (!response.ok) {
        throw new Error("Failed to fetch category emails");
      }
      return response.json() as Promise<EmailResponse>;
    },
  });
};

// Email summarization
export const useSummarizeEmail = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (emailId: string) => {
      const response = await authenticatedFetch(
        `${ENDPOINTS.emails}/${emailId}/summarize`,
        {
          method: "POST",
        }
      );
      if (!response.ok) {
        throw new Error("Failed to summarize email");
      }
      return response.json();
    },
    onSuccess: (_, emailId) => {
      queryClient.invalidateQueries({ queryKey: ["email", emailId] });
    },
  });
};

// Category CRUD operations
export const useCategories = (includeInactive = false) => {
  return useQuery({
    queryKey: ["categories", includeInactive],
    queryFn: async () => {
      const response = await authenticatedFetch(
        `${ENDPOINTS.categories}?include_inactive=${includeInactive}`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch categories");
      }
      const data = await response.json();
      return data; // Returns { categories: Category[], total_count: number }
    },
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      category: Omit<Category, "id" | "created_at" | "updated_at">
    ) => {
      const response = await authenticatedFetch(ENDPOINTS.categories, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(category),
      });
      if (!response.ok) {
        throw new Error("Failed to create category");
      }
      return response.json() as Promise<Category>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      categoryId,
      data,
    }: {
      categoryId: string;
      data: Partial<Category>;
    }) => {
      const response = await authenticatedFetch(
        `${ENDPOINTS.categories}/${categoryId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );
      if (!response.ok) {
        throw new Error("Failed to update category");
      }
      return response.json() as Promise<Category>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
};

export const useDeleteCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await authenticatedFetch(
        `${ENDPOINTS.categories}/${id}`,
        {
          method: "DELETE",
        }
      );
      if (!response.ok) {
        throw new Error("Failed to delete category");
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

export const useRecategorizeEmails = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await authenticatedFetch(ENDPOINTS.recategorizeEmails, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to recategorize emails");
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

// Email actions (placeholder for future implementation)
// These will be implemented when the backend supports these operations
export const useMarkAsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      // TODO: Implement when backend endpoint is available
      console.log("Mark as read:", emailId);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

export const useStarEmail = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      // TODO: Implement when backend endpoint is available
      console.log("Star email:", emailId);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

export const useUnstarEmail = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      // TODO: Implement when backend endpoint is available
      console.log("Unstar email:", emailId);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

export const useArchiveEmail = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      // TODO: Implement when backend endpoint is available
      console.log("Archive email:", emailId);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

export const useDeleteEmail = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      // TODO: Implement when backend endpoint is available
      console.log("Delete email:", emailId);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

// Add useSendEmail hook
export const useSendEmail = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: SendEmailData) => {
      // Create FormData to handle file uploads
      const formData = new FormData();

      // Add basic fields
      formData.append("recipients", JSON.stringify(data.recipients));
      formData.append("subject", data.subject);
      formData.append("body", data.body);

      // Add optional fields
      if (data.html_body) {
        formData.append("html_body", data.html_body);
      }
      if (data.metadata) {
        formData.append("metadata", JSON.stringify(data.metadata));
      }
      if (data.cc?.length) {
        formData.append("cc", JSON.stringify(data.cc));
      }
      if (data.bcc?.length) {
        formData.append("bcc", JSON.stringify(data.bcc));
      }

      // Add attachments if any
      if (data.attachments?.length) {
        data.attachments.forEach((file, index) => {
          formData.append(`attachments`, file);
        });
      }

      const response = await authenticatedFetch(`${ENDPOINTS.emails}/send`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to send email");
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
    },
  });
};

// Task Queries
export function useTasks() {
  return useQuery({
    queryKey: ["tasks"],
    queryFn: () => authenticatedFetch(`${ENDPOINTS.tasks}`),
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      taskId: string;
      description?: string;
      dueDate?: string | null;
      isCompleted?: boolean;
    }) =>
      authenticatedFetch(`${ENDPOINTS.tasks}/${data.taskId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      authenticatedFetch(`${ENDPOINTS.tasks}/${taskId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

// Mock data for email accounts
const MOCK_EMAIL_ACCOUNTS = [
  {
    id: "1",
    email: "john.doe@gmail.com",
    provider: "gmail",
    isConnected: true,
    lastSynced: "2024-03-20T10:30:00Z",
  },
  {
    id: "2",
    email: "john.work@outlook.com",
    provider: "outlook",
    isConnected: true,
    lastSynced: "2024-03-20T09:15:00Z",
  },
];

// Email Accounts Queries
export function useEmailAccounts() {
  return useQuery({
    queryKey: ["emailAccounts"],
    queryFn: () => Promise.resolve({ accounts: MOCK_EMAIL_ACCOUNTS }),
  });
}

export function useRemoveEmailAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accountId: string) =>
      // Mock API call
      new Promise((resolve) => {
        setTimeout(() => {
          resolve({ success: true, message: "Account removed successfully" });
        }, 500);
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emailAccounts"] });
    },
  });
}
