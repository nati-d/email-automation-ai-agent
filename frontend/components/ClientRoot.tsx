"use client";
import { AppProvider } from "@/components/AppContext";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { NavBar } from "@/components/NavBar";
import ComposeEmail, { ComposeModalProvider, useComposeModal } from "@/components/email/ComposeEmail";
import { usePathname } from "next/navigation";
import React from "react";

function ComposeModalRoot() {
  const { open, closeCompose } = useComposeModal();
  return <ComposeEmail open={open} onClose={closeCompose} />;
}

export default function ClientRoot({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDashboardRoute = pathname?.startsWith("/dashboard") || pathname?.startsWith("/email") || pathname?.startsWith("/drafts");

  return (
    <AppProvider>
      <SidebarProvider>
        <ComposeModalProvider>
          {isDashboardRoute ? (
            // Dashboard layout with sidebar and navbar
            <div className="flex h-screen w-full">
              <AppSidebar />
              <main className="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background)] flex flex-col">
                <NavBar />
                <div className="flex-1 overflow-y-auto">{children}</div>
                {/* Compose Email Modal (global) */}
                <ComposeModalRoot />
              </main>
            </div>
          ) : (
            // Landing page layout - no sidebar, no navbar
            <div className="min-h-screen w-full">
              {children}
              {/* Compose Email Modal (global) */}
              <ComposeModalRoot />
            </div>
          )}
        </ComposeModalProvider>
      </SidebarProvider>
    </AppProvider>
  );
} 