"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { EmailApp } from "@/components/email/email-app";

export default function RootPage() {
  return (
    <ProtectedRoute>
      <EmailApp />
    </ProtectedRoute>
  );
}
