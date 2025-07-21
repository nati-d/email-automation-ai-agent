import { ProtectedRoute } from "@/components/auth/protected-route";

export default function InboxLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="h-screen overflow-hidden">
        {children}
      </div>
    </ProtectedRoute>
  );
}