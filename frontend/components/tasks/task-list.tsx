"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTasks, useUpdateTask, useDeleteTask } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { format } from "date-fns";
import { CalendarIcon, Pencil, Trash2, Mail, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Task {
  id: string;
  description: string;
  emailId: string;
  emailSubject: string;
  dueDate: string | null;
  isCompleted: boolean;
  createdAt: string;
}

export function TaskList() {
  const router = useRouter();
  const { data: tasksData, isLoading } = useTasks();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editedDescription, setEditedDescription] = useState("");
  const [editedDueDate, setEditedDueDate] = useState<Date | null>(null);

  const handleEditStart = (task: Task) => {
    setEditingTaskId(task.id);
    setEditedDescription(task.description);
    setEditedDueDate(task.dueDate ? new Date(task.dueDate) : null);
  };

  const handleEditSave = async (taskId: string) => {
    await updateTask.mutateAsync({
      taskId,
      description: editedDescription,
      dueDate: editedDueDate?.toISOString() || null,
    });
    setEditingTaskId(null);
  };

  const handleToggleComplete = async (taskId: string, isCompleted: boolean) => {
    await updateTask.mutateAsync({
      taskId,
      isCompleted: !isCompleted,
    });
  };

  const handleDelete = async (taskId: string) => {
    await deleteTask.mutateAsync(taskId);
  };

  const handleEmailClick = (emailId: string) => {
    router.push(`/${emailId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const tasks = tasksData?.tasks || [];

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <Mail className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No tasks found</h3>
        <p className="text-sm text-muted-foreground">
          Tasks will appear here when they are extracted from your emails
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task: Task) => (
        <Card key={task.id} className={cn(task.isCompleted && "opacity-60")}>
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-2">
                <Checkbox
                  checked={task.isCompleted}
                  onCheckedChange={() =>
                    handleToggleComplete(task.id, task.isCompleted)
                  }
                  className="mt-1"
                />
                {editingTaskId === task.id ? (
                  <div className="space-y-2">
                    <Input
                      value={editedDescription}
                      onChange={(e) => setEditedDescription(e.target.value)}
                      className="w-full"
                    />
                    <div className="flex items-center gap-2">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className={cn(
                              "justify-start text-left font-normal",
                              !editedDueDate && "text-muted-foreground"
                            )}
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {editedDueDate
                              ? format(editedDueDate, "PPP")
                              : "Set due date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={editedDueDate}
                            onSelect={setEditedDueDate}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                      <Button
                        size="sm"
                        onClick={() => handleEditSave(task.id)}
                        disabled={updateTask.isPending}
                      >
                        Save
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingTaskId(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <CardTitle
                      className={cn(
                        "text-base",
                        task.isCompleted && "line-through"
                      )}
                    >
                      {task.description}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {task.dueDate && (
                        <span className="mr-2">
                          Due {format(new Date(task.dueDate), "PPP")}
                        </span>
                      )}
                      <Button
                        variant="link"
                        className="h-auto p-0 text-xs"
                        onClick={() => handleEmailClick(task.emailId)}
                      >
                        From: {task.emailSubject}
                      </Button>
                    </CardDescription>
                  </div>
                )}
              </div>
              {!editingTaskId && (
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEditStart(task)}
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(task.id)}
                    disabled={deleteTask.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}
