import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Email, Category } from "./types";
import { apiRequest } from "./axiosConfig";

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

// API endpoints - relative, axios baseURL handles prefix
const ENDPOINTS = {
  emails: `/emails`,
  inbox: `/emails/inbox`,
  tasks: `/emails/tasks`,
  sent: `/emails/sent`,
  starred: `/emails/starred`,
  categories: `/categories`,
  categoryEmails: (categoryName: string) => `/emails/category/${categoryName}`,
  recategorizeEmails: `/categories/recategorize-emails`,
  emailById: (id: string) => `/emails/${id}`,
  sentById: (id: string) => `/emails/sent/${id}`,
};

// Use axios client to benefit from interceptors
const axiosGet = async <T>(
  url: string,
  params?: Record<string, any>
): Promise<T> => {
  const res = await apiRequest<T>({ url, method: "GET", params });
  // @ts-expect-error generic axios wrapper returns data in .data
  return res.data;
};

// Fetch single email
const fetchEmail = async (emailId: string): Promise<Email> => {
  return axiosGet<Email>(ENDPOINTS.emailById(emailId));
};

// Fetch emails with limit parameter
const fetchEmails = async (
  endpoint: string,
  limit = 50
): Promise<EmailResponse> => {
  return axiosGet<EmailResponse>(endpoint, { limit });
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
    queryFn: async () =>
      axiosGet<EmailResponse>(ENDPOINTS.categoryEmails(categoryName)),
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
    queryFn: async () =>
      axiosGet<{ categories: Category[]; total_count: number }>(
        ENDPOINTS.categories,
        { include_inactive: includeInactive }
      ),
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      category: Omit<Category, "id" | "created_at" | "updated_at">
    ) => {
      const res = await apiRequest<Category>({
        url: ENDPOINTS.categories,
        method: "POST",
        data: category,
      });
      return res.data;
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
      const res = await apiRequest<Category>({
        url: `${ENDPOINTS.categories}/${categoryId}`,
        method: "PUT",
        data,
      });
      return res.data;
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
      await apiRequest({
        url: `${ENDPOINTS.categories}/${id}`,
        method: "DELETE",
      });
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
      const res = await apiRequest({
        url: ENDPOINTS.recategorizeEmails,
        method: "POST",
      });
      return res.data as any;
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

      const res = await apiRequest({
        url: `${ENDPOINTS.emails}/send`,
        method: "POST",
        data: formData,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["emails"] });
      queryClient.invalidateQueries({ queryKey: ["emails", "sent"] });
    },
  });
};

// Task Queries
export function useTasks() {
  return useQuery({
    queryKey: ["tasks"],
    queryFn: () => axiosGet(`${ENDPOINTS.tasks}`),
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
      apiRequest({
        url: `${ENDPOINTS.tasks}/${data.taskId}`,
        method: "PATCH",
        data,
      }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      apiRequest({
        url: `${ENDPOINTS.tasks}/${taskId}`,
        method: "DELETE",
      }).then((r) => r.data),
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

// Additional hooks: sent, starred, sentById
export const useSentEmails = (limit = 50) => {
  return useQuery({
    queryKey: ["emails", "sent", limit],
    queryFn: () => fetchEmails(ENDPOINTS.sent, limit),
  });
};

export const useStarredEmails = (limit = 50) => {
  return useQuery({
    queryKey: ["emails", "starred", limit],
    queryFn: () => fetchEmails(ENDPOINTS.starred, limit),
  });
};

export const useSentEmailById = (emailId: string) => {
  return useQuery({
    queryKey: ["email", "sent", emailId],
    queryFn: () => axiosGet<Email>(ENDPOINTS.sentById(emailId)),
    enabled: Boolean(emailId),
  });
};
