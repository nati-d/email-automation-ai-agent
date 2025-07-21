"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/providers/toast-provider";
import {
  X,
  Paperclip,
  File,
  FileText,
  FileImage,
  FileArchive,
  Download,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface EmailAttachment extends File {
  id?: string;
}

interface EmailAttachmentsProps {
  emailId?: string;
  attachments?: EmailAttachment[];
  onAddAttachments?: (files: EmailAttachment[]) => void;
  onRemoveAttachment?: (index: number) => void;
  maxSize?: number; // in MB
  maxFiles?: number;
  readOnly?: boolean;
}

export function EmailAttachments({
  emailId,
  attachments = [],
  onAddAttachments,
  onRemoveAttachment,
  maxSize = 25, // 25MB default
  maxFiles = 10,
  readOnly = false,
}: EmailAttachmentsProps) {
  const router = useRouter();
  const { toast } = useToast();
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>(
    {}
  );
  const [dragOver, setDragOver] = useState(false);

  const totalSizeMB = attachments.reduce(
    (acc, file) => acc + file.size / (1024 * 1024),
    0
  );

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFiles = (files: File[]) => {
    if (attachments.length + files.length > maxFiles) {
      toast.error(
        "Too Many Files",
        `You can only attach up to ${maxFiles} files`
      );
      return;
    }

    // Check total size
    const newTotalSize =
      totalSizeMB +
      files.reduce((acc, file) => acc + file.size / (1024 * 1024), 0);
    if (newTotalSize > maxSize) {
      toast.error(
        "Files Too Large",
        `Total attachments cannot exceed ${maxSize}MB`
      );
      return;
    }

    // Simulate upload progress
    const newProgress: Record<string, number> = {};
    files.forEach((file) => {
      newProgress[file.name] = 0;
    });
    setUploadProgress((prev) => ({ ...prev, ...newProgress }));

    // Simulate upload
    files.forEach((file) => {
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          const current = prev[file.name] || 0;
          const next = Math.min(current + 10, 100);

          if (next === 100) {
            clearInterval(interval);
          }

          return { ...prev, [file.name]: next };
        });
      }, 200);
    });

    if (onAddAttachments) {
      onAddAttachments(files as EmailAttachment[]);
    }
  };

  const handleRemove = (index: number) => {
    if (readOnly) return;

    if (onRemoveAttachment) {
      onRemoveAttachment(index);
    }
  };

  const handleViewImage = (file: EmailAttachment, index: number) => {
    if (readOnly && emailId && file.type.startsWith("image/")) {
      router.push(`/${emailId}/image/${file.id || index}`);
    }
  };

  const getFileIcon = (file: EmailAttachment) => {
    const type = file.type;

    if (type.startsWith("image/")) {
      return <FileImage className="h-4 w-4" />;
    } else if (type.startsWith("text/")) {
      return <FileText className="h-4 w-4" />;
    } else if (
      type.includes("zip") ||
      type.includes("compressed") ||
      type.includes("archive")
    ) {
      return <FileArchive className="h-4 w-4" />;
    } else {
      return <File className="h-4 w-4" />;
    }
  };

  return (
    <div className="w-full">
      {!readOnly && (
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors",
            dragOver
              ? "border-primary bg-primary/5"
              : "border-muted hover:border-primary/50"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => {
            const input = document.createElement("input");
            input.type = "file";
            input.multiple = true;
            input.onchange = (e) => {
              const files = Array.from(
                (e.target as HTMLInputElement).files || []
              );
              handleFiles(files);
            };
            input.click();
          }}
        >
          <div className="flex flex-col items-center gap-2">
            <Paperclip className="h-8 w-8 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">
                Drop files here or click to upload
              </p>
              <p className="text-xs text-muted-foreground">
                Maximum file size: {maxSize}MB
              </p>
            </div>
          </div>
        </div>
      )}

      {attachments.length > 0 && (
        <div className="mt-4">
          <div className="space-y-2">
            {attachments.map((file, index) => {
              const progress = uploadProgress[file.name] || 0;
              const isUploading = progress > 0 && progress < 100;

              return (
                <div
                  key={`${file.name}-${index}`}
                  className={cn(
                    "flex items-center justify-between p-2 border rounded-md",
                    file.type.startsWith("image/") &&
                      readOnly &&
                      "cursor-pointer hover:bg-muted/50"
                  )}
                  onClick={() => handleViewImage(file, index)}
                >
                  <div className="flex items-center space-x-3 overflow-hidden">
                    {getFileIcon(file)}
                    <div className="overflow-hidden">
                      <p className="text-sm font-medium truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center">
                    {isUploading ? (
                      <span className="text-xs text-muted-foreground mr-2">
                        {progress}%
                      </span>
                    ) : readOnly ? (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Download className="h-4 w-4" />
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemove(index);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
