import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User, EmailFolder, EmailFilters } from "./types";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (user: User, sessionId: string) => void;
  clearAuth: () => void;
  getSessionId: () => string | null;
}

interface EmailState {
  selectedEmails: string[];
  searchQuery: string;
  filters: EmailFilters;
  isComposeOpen: boolean;
  toggleEmailSelection: (emailId: string) => void;
  clearSelection: () => void;
  setSearchQuery: (query: string) => void;
  setFilters: (filters: EmailFilters) => void;
  openCompose: () => void;
  closeCompose: () => void;
}

interface UIState {
  sidebarCollapsed: boolean;
  theme: "light" | "dark" | "system";
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: "light" | "dark" | "system") => void;
}

// Auth store
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setAuth: (user, sessionId) => {
        // Store session ID in localStorage for API client
        if (typeof window !== "undefined") {
          localStorage.setItem("auth-session-id", sessionId);
        }
        set({ user, isAuthenticated: true });
      },
      clearAuth: () => {
        // Clear session ID from localStorage
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth-session-id");
        }
        set({ user: null, isAuthenticated: false });
      },
      getSessionId: () => {
        if (typeof window !== "undefined") {
          return localStorage.getItem("auth-session-id");
        }
        return null;
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Email store
export const useEmailStore = create<EmailState>()((set, get) => ({
  selectedEmails: [],
  searchQuery: "",
  filters: {},
  isComposeOpen: false,
  toggleEmailSelection: (emailId) => {
    const { selectedEmails } = get();
    const isSelected = selectedEmails.includes(emailId);
    if (isSelected) {
      set({ selectedEmails: selectedEmails.filter((id) => id !== emailId) });
    } else {
      set({ selectedEmails: [...selectedEmails, emailId] });
    }
  },
  clearSelection: () => set({ selectedEmails: [] }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setFilters: (filters) => set({ filters }),
  openCompose: () => set({ isComposeOpen: true }),
  closeCompose: () => set({ isComposeOpen: false }),
}));
// UI store
export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: "system",
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: "ui-storage",
    }
  )
);
