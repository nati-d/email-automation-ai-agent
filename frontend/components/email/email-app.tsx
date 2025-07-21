"use client";

import { useState } from "react";
import { useInboxEmails, useTaskEmails } from "@/lib/queries";
import { useEmailStore } from "@/lib/store";
import { EmailList } from "./email-list";
import { EmailView } from "./email-view";
import { ComposeEmail } from "./compose-email";
import { ChatBot } from "./chat-bot";
import { SidebarNav } from "./sidebar-nav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageSquare, Menu, Search } from "lucide-react";

export function EmailApp() {
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);
  const [selectedFolder, setSelectedFolder] = useState("inbox");
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { openCompose } = useEmailStore();

  const handleEmailSelect = (emailId: string) => {
    setSelectedEmailId(emailId);
  };

  const handleBackToList = () => {
    setSelectedEmailId(null);
  };

  const handleFolderSelect = (folder: string) => {
    if (folder === "compose") {
      openCompose();
    } else {
      setSelectedFolder(folder);
      setSelectedEmailId(null);
    }
  };

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // TODO: Implement search
    console.log("Search:", searchQuery);
  };

  return (
    <div className="relative flex flex-col h-screen overflow-hidden bg-background">
      {/* Header */}
      <header className="flex-none h-14 border-b flex items-center gap-4 px-4 bg-background z-10">
        <Button variant="ghost" size="icon" className="shrink-0">
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="Logo" className="h-8 w-8" />
          <h1 className="text-xl font-semibold">Email Agent</h1>
        </div>
        <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search in emails"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 w-full bg-secondary"
            />
          </div>
        </form>
        <div className="flex items-center gap-2">
          <Button
            variant={isChatOpen ? "default" : "outline"}
            size="sm"
            onClick={toggleChat}
            className={isChatOpen ? "bg-primary" : ""}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            AI Chat
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex min-h-0">
        {/* Sidebar */}
        <SidebarNav
          selectedFolder={selectedFolder}
          onFolderSelect={handleFolderSelect}
          className="flex-none w-64 border-r bg-background"
        />

        {/* Email Content */}
        <div className="flex-1 flex min-w-0">
          {/* Email List */}
          <div
            className={`${
              selectedEmailId ? "w-[400px] border-r" : "flex-1"
            } overflow-hidden flex flex-col bg-background`}
          >
            <EmailList
              onEmailSelect={handleEmailSelect}
              selectedEmailId={selectedEmailId || undefined}
              emailType={selectedFolder}
            />
          </div>

          {/* Email View */}
          {selectedEmailId ? (
            <div className="flex-1 overflow-hidden bg-background">
              <EmailView emailId={selectedEmailId} onBack={handleBackToList} />
            </div>
          ) : (
            <div className="hidden md:flex flex-1 items-center justify-center bg-background">
              <div className="text-center text-muted-foreground">
                <div className="w-24 h-24 mx-auto mb-4 bg-primary/10 rounded-full flex items-center justify-center">
                  <Search className="w-12 h-12 text-primary" />
                </div>
                <h3 className="text-lg font-medium mb-2">
                  Select an email to read
                </h3>
                <p className="text-sm">
                  Choose an email from your {selectedFolder} to view its
                  contents
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Chat Panel */}
        {isChatOpen && (
          <div className="flex-none w-80 border-l bg-background overflow-hidden">
            <ChatBot />
          </div>
        )}
      </div>

      {/* Compose Modal */}
      <ComposeEmail />
    </div>
  );
}
