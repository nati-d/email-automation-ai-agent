"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { apiClient } from "@/lib/api";
import { useToast } from "@/components/providers/toast-provider";
import { EmailAgentLoading } from "@/components/ui/email-agent-loading";

export default function AuthSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuth } = useAuthStore();
  const { toast } = useToast();

  useEffect(() => {
    const handleAuthSuccess = async () => {
      try {
        // Get auth data from URL params (sent by backend)
        const status = searchParams.get("status");
        const error = searchParams.get("error");
        const email = searchParams.get("email");
        const name = searchParams.get("name");
        const userId = searchParams.get("user_id");
        const sessionId = searchParams.get("session_id");
        const isNewUser = searchParams.get("is_new_user") === "true";

        if (error) {
          console.error("Auth error:", error);
          const message = searchParams.get("message") || error;
          toast.error("Authentication Error", message);
          router.push("/login?error=" + encodeURIComponent(message));
          return;
        }

        if (status === "success" && email && name && userId && sessionId) {
          // Store session ID in API client
          apiClient.setSessionId(sessionId);

          try {
            // Fetch complete user info from API
            const { user: userInfo } = await apiClient.getCurrentUser();

            // Create user object with proper structure
            const user = {
              id: userInfo.id,
              email: userInfo.email,
              name: userInfo.name,
              picture: "", // API doesn't provide picture
              created_at: userInfo.created_at,
              updated_at: userInfo.updated_at,
            };

            // Set auth in store
            setAuth(user, sessionId);

            // Show welcome message for new users
            if (isNewUser) {
              toast.success(
                "Welcome to Email-Agent!",
                "Your account has been created successfully."
              );
            } else {
              toast.success(
                "Welcome back!",
                `You're now signed in as ${userInfo.name}`
              );
            }

            // Log email import results if available
            const emailsImported = searchParams.get("emails_imported");
            const emailImportSuccess =
              searchParams.get("email_import_success") === "true";
            const emailImportError = searchParams.get("email_import_error");

            if (emailsImported && parseInt(emailsImported) > 0) {
              toast.success(
                "Email Import Complete",
                `Successfully imported ${emailsImported} emails`
              );

              if (emailImportError) {
                toast.warning("Email Import Warning", emailImportError);
              }
            }

            // Redirect to main app
            router.push("/");
          } catch (apiError) {
            console.error("Failed to get user info:", apiError);
            toast.error(
              "Authentication Error",
              "Failed to get user information. Please try again."
            );
            router.push("/login?error=user_info_failed");
          }
        } else {
          // Missing required parameters
          console.error("Missing auth parameters:", {
            status,
            email,
            name,
            userId,
            sessionId,
          });
          toast.error(
            "Authentication Error",
            "Invalid authentication response. Please try again."
          );
          router.push("/login?error=invalid_auth_response");
        }
      } catch (error) {
        console.error("Failed to process auth success:", error);
        toast.error(
          "Authentication Error",
          "Failed to process authentication. Please try again."
        );
        router.push("/login?error=auth_processing_failed");
      }
    };
    handleAuthSuccess();
  }, [router, searchParams, setAuth, toast]);

  return (
    <EmailAgentLoading
      message="Signing you in..."
      submessage="Setting up your Email-Agent experience"
    />
  );
}
