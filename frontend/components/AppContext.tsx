"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { usePathname } from "next/navigation";

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
  refreshTrigger: number;
  triggerRefresh: () => void;
  isNavigating: boolean;
  setIsNavigating: (val: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [search, setSearch] = useState("");
  const [currentCategory, setCurrentCategory] = useState<string | null>(null);
  const [currentEmailType, setCurrentEmailType] = useState<string>("inbox"); // Default to inbox
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isNavigating, setIsNavigating] = useState(false);
  const pathname = usePathname();

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  // Clear navigating flag on route change complete
  useEffect(() => {
    if (isNavigating) {
      // allow a tick to render the destination, then clear
      const t = setTimeout(() => setIsNavigating(false), 50);
      return () => clearTimeout(t);
    }
  }, [pathname]);

  return (
    <AppContext.Provider
      value={{
        user,
        setUser,
        search,
        setSearch,
        currentCategory,
        setCurrentCategory,
        currentEmailType,
        setCurrentEmailType,
        refreshTrigger,
        triggerRefresh,
        isNavigating,
        setIsNavigating,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
