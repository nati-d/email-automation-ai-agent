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
  const isLoginPage = pathname === "/login";

  return (
    <AppProvider>
      <SidebarProvider>
        <ComposeModalProvider>
          {isLoginPage ? (
            // Login page layout - no sidebar, no navbar
            <div className="min-h-screen w-full flex items-center justify-center bg-primary">
              {children}
              {/* Compose Email Modal (global) */}
              <ComposeModalRoot />
            </div>
          ) : (
            // Main app layout with sidebar and navbar
            <div className="flex h-screen w-full">
              <AppSidebar />
              <main className="flex-1 min-w-0 h-full overflow-y-auto bg-[var(--background)] flex flex-col">
                <NavBar />
                <div className="flex-1 overflow-y-auto">{children}</div>
                {/* Compose Email Modal (global) */}
                <ComposeModalRoot />
              </main>
            </div>
          )}
        </ComposeModalProvider>
      </SidebarProvider>
    </AppProvider>
  );
} 