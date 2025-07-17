'use client'

import { createContext, useContext, ReactNode } from 'react'
import { ToastContainer, useToast as useToastHook } from '@/components/ui/toast'

const ToastContext = createContext<ReturnType<typeof useToastHook> | undefined>(undefined)

export function ToastProvider({ children }: { children: ReactNode }) {
  const toastUtils = useToastHook()

  return (
    <ToastContext.Provider value={toastUtils}>
      {children}
      <ToastContainer toasts={toastUtils.toasts} onRemove={toastUtils.removeToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}