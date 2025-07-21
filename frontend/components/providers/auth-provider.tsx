"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { User } from "@/lib/types";
import { useToast } from "./toast-provider";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUserInfo: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { toast } = useToast();
  const { user, isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);

        // Check if we have a session ID
        const sessionId = apiClient.getSessionId();

        if (!sessionId) {
          // No session ID, clear auth state
          clearAuth();
          setIsLoading(false);
          return;
        }

        // We have a session ID, try to get user info
        const { user: userInfo, session_info } =
          await apiClient.getCurrentUser();

        // Check if session is active
        if (!session_info.session_active) {
          console.warn("Session is not active, clearing auth state");
          clearAuth();
          apiClient.clearSession();
          setIsLoading(false);
          return;
        }

        // Session is active, update auth state
        setAuth(
          {
            id: userInfo.id,
            email: userInfo.email,
            name: userInfo.name,
            picture: "", // API doesn't provide picture
            created_at: userInfo.created_at,
            updated_at: userInfo.updated_at,
          },
          sessionId
        );

        // Check if token needs refresh soon (less than 5 minutes)
        if (session_info.token_expires_in < 300) {
          console.log("Token expires soon, refreshing...");
          await apiClient.refreshToken();
        }
      } catch (error) {
        console.error("Failed to check auth status:", error);
        clearAuth();
        apiClient.clearSession();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [clearAuth, setAuth]);

  // Handle public/protected routes
  useEffect(() => {
    // Skip during loading
    if (isLoading) return;

    // Public routes that don't require authentication
    const publicRoutes = ["/login", "/auth-success"];
    const isPublicRoute = publicRoutes.includes(pathname);

    if (!isAuthenticated && !isPublicRoute) {
      // Not authenticated and trying to access protected route
      router.push("/login");
    } else if (isAuthenticated && pathname === "/login") {
      // Already authenticated and trying to access login page
      router.push("/");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  // Login function
  const login = async () => {
    try {
      const { authorization_url } = await apiClient.getAuthUrl();
      window.location.href = authorization_url;
    } catch (error) {
      console.error("Failed to get auth URL:", error);
      toast.error(
        "Authentication Error",
        "Failed to start login process. Please try again."
      );
    }
  };

  // Logout function
  const logout = async () => {
    try {
      if (isAuthenticated) {
        await apiClient.logout();
      }
    } catch (error) {
      console.error("Failed to logout:", error);
    } finally {
      clearAuth();
      apiClient.clearSession();
      router.push("/login");
    }
  };

  // Refresh user info
  const refreshUserInfo = async () => {
    try {
      const { user: userInfo } = await apiClient.getCurrentUser();

      if (userInfo) {
        setAuth(
          {
            id: userInfo.id,
            email: userInfo.email,
            name: userInfo.name,
            picture: "", // API doesn't provide picture
            created_at: userInfo.created_at,
            updated_at: userInfo.updated_at,
          },
          apiClient.getSessionId() || ""
        );
      }
    } catch (error) {
      console.error("Failed to refresh user info:", error);
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refreshUserInfo,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
