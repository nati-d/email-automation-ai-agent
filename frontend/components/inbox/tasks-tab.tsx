"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckSquare, Clock, AlertCircle } from "lucide-react";

export function TasksTab() {
  return (
    <div className="h-full flex items-center justify-center p-6">
      <Card className="max-w-md text-center">
        <CardHeader>
          <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
            <CheckSquare className="h-6 w-6 text-primary" />
          </div>
          <CardTitle>Tasks Coming Soon</CardTitle>
          <CardDescription>
            Task extraction and management features will be implemented in the next phase.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>Automatic task detection from emails</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              <span>Priority and deadline tracking</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckSquare className="h-4 w-4" />
              <span>Task completion management</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}