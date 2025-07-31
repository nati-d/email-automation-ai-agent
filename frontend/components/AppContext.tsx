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
  currentCategory: string | null;
  setCurrentCategory: (category: string | null) => void;
  currentEmailType: string;
  setCurrentEmailType: (emailType: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [search, setSearch] = useState("")
  const [currentCategory, setCurrentCategory] = useState<string | null>(null)
  const [currentEmailType, setCurrentEmailType] = useState<string>("inbox") // Default to inbox

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      setUser(JSON.parse(stored))
    }
  }, [])

  return (
    <AppContext.Provider value={{ 
      user, 
      setUser, 
      search, 
      setSearch, 
      currentCategory, 
      setCurrentCategory,
      currentEmailType,
      setCurrentEmailType
    }}>
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