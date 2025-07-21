"use client";
import { useState, useRef, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useSendEmail } from "@/lib/queries";
import { useEmailStore } from "@/lib/store";
import { useToast } from "@/components/providers/toast-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmailAttachments } from "./email-attachments";

import {
  Paperclip,
  X,
  Loader2,
  Minimize2,
  Maximize2,
  Bold,
  Italic,
  Underline,
  Link as LinkIcon,
  Image,
  Smile,
  MoreHorizontal,
  ChevronUp,
  Trash2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const composeSchema = z.object({
  to: z
    .string()
    .min(1, "At least one recipient is required")
    .refine((value) => {
      const emails = value
        .split(",")
        .map((e) => e.trim())
        .filter(Boolean);
      return emails.length >= 1 && emails.length <= 100;
    }, "Number of recipients must be between 1 and 100"),
  cc: z.string().optional(),
  bcc: z.string().optional(),
  subject: z
    .string()
    .min(1, "Subject is required")
    .max(200, "Subject cannot exceed 200 characters"),
  body: z
    .string()
    .min(1, "Message body is required")
    .max(50000, "Message body cannot exceed 50000 characters"),
});

type ComposeFormData = z.infer<typeof composeSchema>;

export function ComposeEmail() {
  const { isComposeOpen, closeCompose } = useEmailStore();
  const sendEmail = useSendEmail();
  const { toast } = useToast();
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [showCc, setShowCc] = useState(false);
  const [showBcc, setShowBcc] = useState(false);
  const [isRichText, setIsRichText] = useState(true);
  const editorRef = useRef<HTMLDivElement>(null);
  const toInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
    getValues,
    trigger,
  } = useForm<ComposeFormData>({
    resolver: zodResolver(composeSchema),
    defaultValues: {
      to: "",
      cc: "",
      bcc: "",
      subject: "",
      body: "",
    },
  });

  useEffect(() => {
    if (isComposeOpen && !isMinimized && toInputRef.current) {
      setTimeout(() => toInputRef.current?.focus(), 100);
    }
  }, [isComposeOpen, isMinimized]);

  const onSubmit = async (data: ComposeFormData) => {
    try {
      // Get content from rich text editor if enabled
      const bodyContent =
        isRichText && editorRef.current
          ? editorRef.current.innerHTML
          : data.body;

      const emailData = {
        recipients: data.to
          .split(",")
          .map((email) => email.trim())
          .filter(Boolean),
        cc: data.cc
          ? data.cc
              .split(",")
              .map((email) => email.trim())
              .filter(Boolean)
          : undefined,
        bcc: data.bcc
          ? data.bcc
              .split(",")
              .map((email) => email.trim())
              .filter(Boolean)
          : undefined,
        subject: data.subject,
        body: data.body,
        html_body: isRichText ? bodyContent : undefined,
        attachments: attachments.length > 0 ? attachments : undefined,
      };

      await sendEmail.mutateAsync(emailData);

      toast.success(
        "Email sent successfully!",
        `Your email "${
          data.subject
        }" has been sent to ${emailData.recipients.join(", ")}`
      );

      reset();
      setAttachments([]);
      setShowCc(false);
      setShowBcc(false);
      if (editorRef.current) {
        editorRef.current.innerHTML = "";
      }
      closeCompose();
    } catch (error) {
      console.error("Failed to send email:", error);
      toast.error(
        "Failed to send email",
        error instanceof Error ? error.message : "An unexpected error occurred"
      );
    }
  };

  const handleAddAttachments = (files: File[]) => {
    setAttachments((prev) => [...prev, ...files]);
  };

  const handleRemoveAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const handleClose = () => {
    const hasContent =
      watch("to") ||
      watch("subject") ||
      watch("body") ||
      (editorRef.current && editorRef.current.textContent?.trim());
    if (hasContent) {
      const shouldClose = confirm("Discard this draft?");
      if (!shouldClose) return;
    }
    reset();
    setAttachments([]);
    setShowCc(false);
    setShowBcc(false);
    if (editorRef.current) {
      editorRef.current.innerHTML = "";
    }
    closeCompose();
  };

  const handleSchedule = (scheduledTime: Date) => {
    toast.success(
      "Email Scheduled",
      `Your email will be sent on ${scheduledTime.toLocaleString()}`
    );
    // In a real implementation, you would save the draft with the scheduled time
  };

  // Rich text editor functions
  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
    setIsMinimized(false);
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
    setIsMaximized(false);
  };

  if (!isComposeOpen) return null;

  return (
    <div
      className={cn(
        "fixed z-50 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 shadow-2xl transition-all duration-300",
        isMaximized
          ? "inset-4 rounded-lg"
          : isMinimized
          ? "bottom-0 right-6 w-64 h-10 rounded-t-lg"
          : "bottom-10 right-6 w-[90vw] md:w-[550px] h-[70vh] md:h-[500px] max-h-[80vh] rounded-lg overflow-hidden"
      )}
    >
      {/* Gmail-style Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-t-lg border-b border-gray-200 dark:border-gray-600">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-200">
          {watch("subject") ? watch("subject") : "New Message"}
        </h3>
        <div className="flex items-center space-x-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600"
            onClick={toggleMinimize}
            title={isMinimized ? "Expand" : "Minimize"}
          >
            {isMinimized ? (
              <ChevronUp className="h-3 w-3" />
            ) : (
              <Minimize2 className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600"
            onClick={toggleMaximize}
            title={isMaximized ? "Exit full screen" : "Full screen"}
          >
            {isMaximized ? (
              <Minimize2 className="h-3 w-3" />
            ) : (
              <Maximize2 className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600"
            onClick={handleClose}
            title="Close"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {!isMinimized && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex flex-col h-full"
        >
          {/* Recipients Section */}
          <div className="px-4 py-2 space-y-1 border-b border-gray-200 dark:border-gray-600">
            {/* To Field */}
            <div className="flex items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400 w-12 flex-shrink-0">
                To
              </span>
              <div className="flex-1 flex items-center">
                <Input
                  placeholder="Recipients"
                  {...register("to", {
                    shouldUseNativeValidation: false,
                  })}
                  ref={(e) => {
                    // This handles both the react-hook-form ref and our custom ref
                    const { ref } = register("to");
                    if (typeof ref === "function") {
                      ref(e);
                    }
                    toInputRef.current = e;
                  }}
                  className="border-0 focus-visible:ring-0 px-2 py-1 text-sm"
                />
                <div className="flex items-center space-x-1 ml-2">
                  {!showCc && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-xs text-blue-600 hover:text-blue-800 p-1 h-auto"
                      onClick={() => setShowCc(true)}
                    >
                      Cc
                    </Button>
                  )}
                  {!showBcc && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="text-xs text-blue-600 hover:text-blue-800 p-1 h-auto"
                      onClick={() => setShowBcc(true)}
                    >
                      Bcc
                    </Button>
                  )}
                </div>
              </div>
            </div>
            {errors.to && (
              <p className="text-xs text-red-500 ml-12">{errors.to.message}</p>
            )}

            {/* CC Field */}
            {showCc && (
              <div className="flex items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400 w-12 flex-shrink-0">
                  Cc
                </span>
                <Input
                  placeholder="Carbon copy"
                  {...register("cc")}
                  className="border-0 focus-visible:ring-0 px-2 py-1 text-sm"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 ml-2"
                  onClick={() => setShowCc(false)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            )}

            {/* BCC Field */}
            {showBcc && (
              <div className="flex items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400 w-12 flex-shrink-0">
                  Bcc
                </span>
                <Input
                  placeholder="Blind carbon copy"
                  {...register("bcc")}
                  className="border-0 focus-visible:ring-0 px-2 py-1 text-sm"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 ml-2"
                  onClick={() => setShowBcc(false)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            )}

            {/* Subject Field */}
            <div className="flex items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400 w-12 flex-shrink-0">
                Subject
              </span>
              <Input
                placeholder="Subject"
                {...register("subject")}
                className="border-0 focus-visible:ring-0 px-2 py-1 text-sm"
              />
            </div>
            {errors.subject && (
              <p className="text-xs text-red-500 ml-12">
                {errors.subject.message}
              </p>
            )}
          </div>

          {/* Rich Text Toolbar */}
          {isRichText && (
            <div className="flex items-center px-4 py-2 border-b border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
              <div className="flex items-center space-x-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => execCommand("bold")}
                >
                  <Bold className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => execCommand("italic")}
                >
                  <Italic className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => execCommand("underline")}
                >
                  <Underline className="h-4 w-4" />
                </Button>
                <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2" />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() =>
                    execCommand("createLink", prompt("Enter URL:") || "")
                  }
                >
                  <LinkIcon className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                >
                  <Image className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                >
                  <Smile className="h-4 w-4" />
                </Button>
              </div>
              <div className="ml-auto">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="text-xs"
                  onClick={() => setIsRichText(false)}
                >
                  Plain text
                </Button>
              </div>
            </div>
          )}

          {/* Message Body */}
          <div className="flex-1 p-4">
            {isRichText ? (
              <div
                ref={editorRef}
                contentEditable
                className="w-full h-full min-h-[200px] outline-none text-sm leading-relaxed"
                style={{ wordWrap: "break-word" }}
                onInput={(e) => {
                  const content = e.currentTarget.textContent || "";
                  setValue("body", content);
                }}
                suppressContentEditableWarning={true}
              />
            ) : (
              <textarea
                {...register("body")}
                placeholder="Compose your message..."
                className="w-full h-full min-h-[200px] resize-none border-0 outline-none text-sm leading-relaxed bg-transparent"
              />
            )}
            {errors.body && (
              <p className="text-xs text-red-500 mt-2">{errors.body.message}</p>
            )}
          </div>

          {/* Attachments */}
          {attachments.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-600">
              <EmailAttachments
                attachments={attachments}
                onRemoveAttachment={handleRemoveAttachment}
                readOnly={false}
              />
            </div>
          )}

          {/* Bottom Actions */}
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
            <div className="flex items-center space-x-2 mb-8">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md text-sm font-medium"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Sending...
                  </>
                ) : (
                  "Send"
                )}
              </Button>

              <div className="flex items-center gap-1 overflow-x-auto flex-wrap md:flex-nowrap ">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 flex-shrink-0"
                  onClick={() =>
                    document.getElementById("file-upload")?.click()
                  }
                  title="Attach files"
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
                <input
                  type="file"
                  multiple
                  onChange={(e) => {
                    const files = Array.from(e.target.files || []);
                    handleAddAttachments(files);
                  }}
                  className="hidden"
                  id="file-upload"
                />

                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 flex-shrink-0 md:hidden"
                  onClick={() =>
                    document.getElementById("file-upload")?.click()
                  }
                  title="More options"
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {!isRichText && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="text-xs"
                  onClick={() => setIsRichText(true)}
                >
                  Rich formatting
                </Button>
              )}
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={handleClose}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
