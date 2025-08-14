"use client";
import { AppProvider } from "@/components/AppContext";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { NavBar } from "@/components/NavBar";
import ComposeEmail, {
  ComposeModalProvider,
  useComposeModal,
} from "@/components/email/ComposeEmail";
import { usePathname } from "next/navigation";
import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useApp } from "@/components/AppContext";

function ComposeModalRoot() {
  const { open, closeCompose } = useComposeModal();
  return <ComposeEmail open={open} onClose={closeCompose} />;
}

function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDashboardRoute =
    pathname?.startsWith("/dashboard") ||
    pathname?.startsWith("/email") ||
    pathname?.startsWith("/drafts");
  const { isNavigating } = useApp();
  return (
    <SidebarProvider>
      <ComposeModalProvider>
        {isDashboardRoute ? (
          <div className="flex h-screen w-full">
            <AppSidebar />
            <main className="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background)] flex flex-col">
              <NavBar />
              {isNavigating && (
                <div className="w-full h-1 bg-transparent">
                  <div className="h-1 w-full bg-[var(--primary)]" />
                </div>
              )}
              <div className="flex-1 overflow-y-auto">{children}</div>
              <ComposeModalRoot />
            </main>
          </div>
        ) : (
          <div className="min-h-screen w-full">
            {isNavigating && (
              <div className="w-full h-1 bg-transparent">
                <div className="h-1 w-full bg-[var(--primary)]" />
              </div>
            )}
            {children}
            <ComposeModalRoot />
          </div>
        )}
      </ComposeModalProvider>
    </SidebarProvider>
  );
}

export default function ClientRoot({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = React.useState(() => new QueryClient());
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <AppShell>{children}</AppShell>
      </AppProvider>
    </QueryClientProvider>
  );
}
