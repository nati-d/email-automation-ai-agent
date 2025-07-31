// This file contains additional query hooks to be added to the existing queries.ts file

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './api'

// LLM/AI features
export function useGenerateEmailContent() {
  return useMutation({
    mutationFn: ({ prompt, context }: { prompt: string; context?: string }) => 
      apiClient.generateEmailContent(prompt, context),
  })
}

export function useAnalyzeEmailSentiment() {
  return useMutation({
    mutationFn: (emailContent: string) => apiClient.analyzeEmailSentiment(emailContent),
  })
}

export function useSuggestEmailSubject() {
  return useMutation({
    mutationFn: ({ emailContent, context }: { emailContent: string; context?: string }) => 
      apiClient.suggestEmailSubject(emailContent, context),
  })
}

export function useSmartEmailComposer() {
  return useMutation({
    mutationFn: (data: {
      purpose: string
      recipient_context?: string
      tone?: string
      include_subject?: boolean
    }) => apiClient.smartEmailComposer(data),
  })
}

export function useGenerateEmailResponse() {
  return useMutation({
    mutationFn: (data: {
      original_email: string
      response_type: string
      additional_context?: string
    }) => apiClient.generateEmailResponse(data),
  })
}

// Category management
export function useCategories(includeInactive: boolean = false) {
  return useQuery({
    queryKey: ['categories', includeInactive],
    queryFn: () => apiClient.getCategories(includeInactive),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useCreateCategory() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: { name: string; description?: string; color?: string }) => 
      apiClient.createCategory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })
}

export function useUpdateCategory() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ categoryId, data }: { 
      categoryId: string; 
      data: { name?: string; description?: string; color?: string; is_active?: boolean } 
    }) => apiClient.updateCategory(categoryId, data),
    onSuccess: (data, { categoryId }) => {
      queryClient.setQueryData(['category', categoryId], data)
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })
}

export function useDeleteCategory() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (categoryId: string) => apiClient.deleteCategory(categoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useRecategorizeEmails() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: () => apiClient.recategorizeEmails(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

// Email operations
export function useEmailsByCategory(categoryName: string) {
  return useQuery({
    queryKey: ['emails', 'category', categoryName],
    queryFn: () => apiClient.getEmailsByCategory(categoryName),
    staleTime: 30 * 1000,
    enabled: !!categoryName,
  })
}

export function useTaskEmails() {
  return useQuery({
    queryKey: ['emails', 'tasks'],
    queryFn: () => apiClient.getTaskEmails(),
    staleTime: 30 * 1000,
  })
}

export function useInboxEmails() {
  return useQuery({
    queryKey: ['emails', 'inbox'],
    queryFn: () => apiClient.getInboxEmails(),
    staleTime: 30 * 1000,
  })
}

export function useSummarizeEmail() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (emailId: string) => apiClient.summarizeEmail(emailId),
    onSuccess: (data, emailId) => {
      queryClient.invalidateQueries({ queryKey: ['email', emailId] })
    },
  })
}

export function useSummarizeMultipleEmails() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (emailIds: string[]) => apiClient.summarizeMultipleEmails(emailIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

// Email status operations
export function useMarkAsRead() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.markAsRead(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useMarkAsUnread() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.markAsUnread(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useStarEmail() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.starEmail(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useUnstarEmail() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.unstarEmail(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useArchiveEmail() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.archiveEmail(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export function useMoveToTrash() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiClient.moveToTrash(id),
    onSuccess: (data, id) => {
      queryClient.setQueryData(['email', id], data)
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}