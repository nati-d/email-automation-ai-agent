"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { InboxTab } from "./inbox-tab";
import { TasksTab } from "./tasks-tab";
import { Inbox, CheckSquare } from "lucide-react";

export function InboxManagement() {
  const [activeTab, setActiveTab] = useState("inbox");

  return (
    <div className="h-screen flex flex-col bg-background">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        {/* Tab Navigation */}
        <div className="border-b bg-background px-6 py-3">
          <TabsList className="grid w-fit grid-cols-2">
            <TabsTrigger value="inbox" className="flex items-center gap-2">
              <Inbox className="h-4 w-4" />
              Inbox
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex items-center gap-2">
              <CheckSquare className="h-4 w-4" />
              Tasks
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          <TabsContent value="inbox" className="h-full m-0">
            <InboxTab />
          </TabsContent>
          <TabsContent value="tasks" className="h-full m-0">
            <TasksTab />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}