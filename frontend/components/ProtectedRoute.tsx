"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      console.log('🔍 ProtectedRoute: checkAuth called');
      try {
        const userStr = localStorage.getItem("user");
        if (!userStr) {
          console.log('❌ ProtectedRoute: No user in localStorage, redirecting to /');
          router.replace("/");
          return;
        }

        const user = JSON.parse(userStr);
        const sessionId = user.sessionId || user.session_id;

        if (!sessionId) {
          console.log('❌ ProtectedRoute: No sessionId found, redirecting to /');
          localStorage.removeItem("user");
          router.replace("/");
          return;
        }

        console.log('✅ ProtectedRoute: Authentication successful');
        setIsAuthenticated(true);
      } catch (error) {
        console.error("❌ ProtectedRoute: Auth check error:", error);
        localStorage.removeItem("user");
        router.replace("/");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to 
  }

  return <>{children}</>;
} 