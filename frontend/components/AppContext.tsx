"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

// Define User type
interface User {
  name: string;
  email: string;
  userId: string;
  isNewUser?: string;
  sessionId: string;
  profilePicture?: string;
}

interface AppContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  search: string;
  setSearch: (search: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [search, setSearch] = useState("")

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      setUser(JSON.parse(stored))
    }
  }, [])

  return (
    <AppContext.Provider value={{ user, setUser, search, setSearch }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider")
  }
  return context
} 