"use client";

import { TaskList } from "@/components/tasks/task-list";
import { ProtectedRoute } from "@/components/auth/protected-route";

export default function TasksPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8 max-w-3xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold mb-1">Tasks</h1>
            <p className="text-sm text-muted-foreground">
              Manage tasks extracted from your emails
            </p>
          </div>
        </div>
        <TaskList />
      </div>
    </ProtectedRoute>
  );
}
