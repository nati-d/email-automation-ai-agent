"use client";

import { createContext, useContext, useEffect, useRef } from "react";
import { apiClient } from "@/lib/api";
import { useAuth } from "./auth-provider";

interface SessionRefreshContextType {
  refreshSession: () => Promise<void>;
}

const SessionRefreshContext = createContext<
  SessionRefreshContextType | undefined
>(undefined);

export function SessionRefreshProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated } = useAuth();
  const refreshTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Function to refresh the session
  const refreshSession = async () => {
    if (!isAuthenticated) return;

    try {
      const result = await apiClient.refreshToken();
      console.log(
        "Token refreshed successfully, expires in:",
        result.expires_in,
        "seconds"
      );

      // Schedule next refresh for 5 minutes before expiration
      const nextRefreshTime = Math.max((result.expires_in - 300) * 1000, 60000); // At least 1 minute

      // Clear any existing timer
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }

      // Set new timer
      refreshTimerRef.current = setTimeout(refreshSession, nextRefreshTime);
    } catch (error) {
      console.error("Failed to refresh token:", error);
    }
  };

  // Set up initial refresh timer
  useEffect(() => {
    if (isAuthenticated) {
      // Check current user info to get token expiration
      const checkTokenExpiration = async () => {
        try {
          const { session_info } = await apiClient.getCurrentUser();

          if (session_info.token_expires_in) {
            // If token expires in less than 5 minutes, refresh now
            if (session_info.token_expires_in < 300) {
              refreshSession();
            } else {
              // Otherwise, schedule refresh for 5 minutes before expiration
              const nextRefreshTime =
                (session_info.token_expires_in - 300) * 1000;

              // Clear any existing timer
              if (refreshTimerRef.current) {
                clearTimeout(refreshTimerRef.current);
              }

              // Set new timer
              refreshTimerRef.current = setTimeout(
                refreshSession,
                nextRefreshTime
              );
            }
          }
        } catch (error) {
          console.error("Failed to check token expiration:", error);
        }
      };

      checkTokenExpiration();
    }

    // Clean up timer on unmount
    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [isAuthenticated]);

  return (
    <SessionRefreshContext.Provider value={{ refreshSession }}>
      {children}
    </SessionRefreshContext.Provider>
  );
}

export const useSessionRefresh = () => {
  const context = useContext(SessionRefreshContext);
  if (context === undefined) {
    throw new Error(
      "useSessionRefresh must be used within a SessionRefreshProvider"
    );
  }
  return context;
};
