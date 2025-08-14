import React, { useState, useContext, createContext, ReactNode } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  getEmailSuggestions,
  createDraft,
  updateDraft,
  deleteDraft,
  type Draft,
} from "@/lib/api/email";
import { useSendEmail } from "@/lib/queries";
import AttachmentUpload from "@/components/email/AttachmentUpload";
import { Send, Save, Wand2 } from "lucide-react";
import { useApp } from "@/components/AppContext";

interface ComposeEmailProps {
  open: boolean;
  onClose: () => void;
}

interface EmailData {
  id: string;
  sender: string;
  subject: string;
  body?: string;
  recipients?: string[];
}

interface DraftData extends Draft {
  // Additional properties if needed
}

const initialState = {
  to: "",
  subject: "",
  body: "",
  minimized: false,
  maximized: false,
};

// Compose Modal Context
interface ComposeModalContextType {
  open: boolean;
  openCompose: () => void;
  closeCompose: () => void;
  replyToEmail: (email: EmailData) => void;
  editDraft: (draft: DraftData) => void;
  replyData: EmailData | null;
  draftData: DraftData | null;
  onDraftSaved?: () => void;
  setOnDraftSaved: (callback: (() => void) | undefined) => void;
}
const ComposeModalContext = createContext<ComposeModalContextType | undefined>(
  undefined
);

export function ComposeModalProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [replyData, setReplyData] = useState<EmailData | null>(null);
  const [draftData, setDraftData] = useState<DraftData | null>(null);
  const [onDraftSaved, setOnDraftSaved] = useState<(() => void) | undefined>(
    undefined
  );

  const openCompose = () => {
    setReplyData(null);
    setDraftData(null);
    setOpen(true);
  };

  const closeCompose = () => {
    setOpen(false);
    setReplyData(null);
    setDraftData(null);
  };

  const replyToEmail = (email: EmailData) => {
    setReplyData(email);
    setDraftData(null);
    setOpen(true);
  };

  const editDraft = (draft: DraftData) => {
    setDraftData(draft);
    setReplyData(null);
    setOpen(true);
  };

  return (
    <ComposeModalContext.Provider
      value={{
        open,
        openCompose,
        closeCompose,
        replyToEmail,
        editDraft,
        replyData,
        draftData,
        onDraftSaved,
        setOnDraftSaved,
      }}
    >
      {children}
    </ComposeModalContext.Provider>
  );
}

export function useComposeModal() {
  const ctx = useContext(ComposeModalContext);
  if (!ctx)
    throw new Error("useComposeModal must be used within ComposeModalProvider");
  return ctx;
}

const ComposeEmail: React.FC<ComposeEmailProps> = ({ open, onClose }) => {
  const { replyData, draftData, onDraftSaved } = useComposeModal();
  const { triggerRefresh } = useApp();
  const sendEmailMutation = useSendEmail();
  const [to, setTo] = useState(initialState.to);
  const [subject, setSubject] = useState(initialState.subject);
  const [body, setBody] = useState(initialState.body);
  const [minimized, setMinimized] = useState(initialState.minimized);
  const [maximized, setMaximized] = useState(initialState.maximized);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [showSuggestion, setShowSuggestion] = useState(false);
  const [isDraft, setIsDraft] = useState(false);
  const [draftId, setDraftId] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);

  React.useEffect(() => {
    if (!open) {
      setTo(initialState.to);
      setSubject(initialState.subject);
      setBody(initialState.body);
      setAttachments([]);
      setSuccess(null);
      setError(null);
      setMinimized(false);
      setMaximized(false);
      setLoading(false);
      setIsDraft(false);
      setDraftId(null);
      // Auto-save timer removed
    }
  }, [open]);

  // Handle reply data when modal opens
  React.useEffect(() => {
    if (open && replyData) {
      // Pre-fill the form for reply
      setTo(replyData.sender);
      setSubject(
        replyData.subject.startsWith("Re:")
          ? replyData.subject
          : `Re: ${replyData.subject}`
      );

      // Add reply prefix to body
      const replyPrefix = `\n\n--- Original Message ---\nFrom: ${replyData.sender}\nSubject: ${replyData.subject}\n\n`;
      const originalBody = replyData.body || "";
      setBody(replyPrefix + originalBody);
      setIsDraft(false);
      setDraftId(null);
    }
  }, [open, replyData]);

  // Handle draft data when modal opens
  React.useEffect(() => {
    if (open && draftData) {
      console.log(
        "📝 Opening draft for editing:",
        draftData.id,
        draftData.subject
      );
      // Pre-fill the form for draft editing
      setTo(draftData.recipients.join(", "));
      setSubject(draftData.subject);
      setBody(draftData.body);
      setIsDraft(true);
      setDraftId(draftData.id);
      setAttachments([]);
    }
  }, [open, draftData]);

  // Manual save draft functionality only

  const handleSaveDraft = async () => {
    setLoading(true);
    setError(null);
    try {
      const recipients = to
        .split(",")
        .map((email) => email.trim())
        .filter((email) => email);
      if (recipients.length === 0) {
        setError("Please enter at least one recipient");
        return;
      }

      if (isDraft && draftId) {
        // Update existing draft
        await updateDraft(draftId, {
          recipients,
          subject: subject || "No Subject",
          body: body || "",
        });
        setSuccess("Draft updated successfully!");
      } else {
        // Create new draft
        const draft = await createDraft({
          recipients,
          subject: subject || "No Subject",
          body: body || "",
        });
        setIsDraft(true);
        setDraftId(draft.id);
        setSuccess("Draft saved successfully!");
      }

      // Call the callback to refresh drafts list
      if (onDraftSaved) {
        onDraftSaved();
      }

      // Trigger global refresh for dashboard and other components
      triggerRefresh();

      setTimeout(() => {
        setSuccess(null);
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to save draft");
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(null);
    setError(null);

    const currentDraftId = draftId; // Store current draft ID before reset
    const wasDraft = isDraft; // Store draft status before reset

    try {
      const recipients = to
        .split(",")
        .map((email) => email.trim())
        .filter((email) => email);

      await sendEmailMutation.mutateAsync({
        body,
        recipients,
        subject: subject || "No Subject",
        attachments: attachments.length ? attachments : undefined,
      });

      // If this was a draft being sent, delete it from the database
      if (wasDraft && currentDraftId) {
        try {
          console.log("🗑️ Deleting sent draft from database:", currentDraftId);
          await deleteDraft(currentDraftId, false); // Don't sync with Gmail since it's local only
          console.log("✅ Draft deleted from database after sending");

          // Call the callback to refresh drafts list
          if (onDraftSaved) {
            onDraftSaved();
          }

          // Trigger global refresh for dashboard and other components
          triggerRefresh();
        } catch (deleteError: any) {
          console.warn("⚠️ Failed to delete draft from database:", deleteError);
          // Don't fail the send operation if draft deletion fails
        }
      }

      setSuccess(
        wasDraft
          ? "Draft sent successfully and removed from drafts!"
          : "Email sent successfully!"
      );

      // Reset form
      setTo(initialState.to);
      setSubject(initialState.subject);
      setBody(initialState.body);
      setIsDraft(false);
      setDraftId(null);

      setTimeout(() => {
        setSuccess(null);
        onClose();
      }, 1200);
    } catch (err: any) {
      setError(err.message || err.data?.detail || "Failed to send email");
    } finally {
      setLoading(false);
    }
  };

  const handleMinimize = () => setMinimized(true);
  const handleMaximize = () => setMaximized((m) => !m);
  const handleRestore = () => setMinimized(false);

  const handleGetSuggestions = async () => {
    if (!body.trim()) {
      setError("Please enter some text to get suggestions");
      return;
    }
    setSuggestionsLoading(true);
    setError(null);
    try {
      const response = await getEmailSuggestions({ query: body });
      setSuggestion(response.body || null);
      setShowSuggestion(true);
    } catch (err: any) {
      setError(err.message || err.data?.detail || "Failed to get suggestions");
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const handleApplySuggestion = () => {
    if (suggestion) {
      setBody(suggestion);
      setShowSuggestion(false);
      setSuggestion(null);
    }
  };

  // Early return after all hooks
  if (!open) return null;

  // Modal styles
  const baseStyle =
    "fixed z-50 flex flex-col transition-all border shadow-xl rounded-xl";
  const minimizedStyle =
    "bottom-4 right-4 w-80 h-12 cursor-pointer flex-row items-center justify-between px-4 py-2";
  const maximizedStyle = "top-4 left-1/2 -translate-x-1/2 w-[95vw] h-[90vh]";
  const normalStyle = "bottom-4 right-4 w-[28rem] max-w-[95vw] h-[32rem]";

  return (
    <div
      className={
        baseStyle +
        " " +
        (minimized ? minimizedStyle : maximized ? maximizedStyle : normalStyle)
      }
      style={{
        background: "var(--background)",
        color: "var(--foreground)",
        borderColor: "var(--modal-border, var(--sidebar-border, #e5e7eb))",
        boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
        ...(minimized ? { cursor: "pointer" } : {}),
      }}
      onClick={minimized ? handleRestore : undefined}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-2 rounded-t-xl border-b"
        style={{
          background: "var(--sidebar)",
          color: "var(--sidebar-foreground)",
          borderColor: "var(--modal-border, var(--sidebar-border, #e5e7eb))",
        }}
      >
        <div className="flex items-center gap-2">
          <span className="font-semibold tracking-wide">
            {isDraft ? "✏️ Edit Draft" : replyData ? "↩️ Reply" : "✉️ Compose"}
          </span>
          {isDraft && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              Draft
            </span>
          )}
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            title="Minimize"
            className="text-base hover:bg-white/20"
            onClick={(e) => {
              e.stopPropagation();
              handleMinimize();
            }}
            style={{ display: minimized ? "none" : "inline-flex" }}
            type="button"
            disabled={loading}
          >
            &#8211;
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title={maximized ? "Restore" : "Maximize"}
            className="text-base hover:bg-white/20"
            onClick={(e) => {
              e.stopPropagation();
              handleMaximize();
            }}
            style={{ display: minimized ? "none" : "inline-flex" }}
            type="button"
            disabled={loading}
          >
            {maximized ? <>⧉</> : <>⛶</>}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Close"
            className="text-base hover:bg-red-500/20 hover:text-red-300"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            type="button"
            disabled={loading}
          >
            ✕
          </Button>
        </div>
      </div>
      {/* Minimized view */}
      {minimized ? (
        <div className="flex-1 flex items-center justify-between w-full h-full px-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">
              {isDraft ? "✏️ Draft" : replyData ? "↩️ Reply" : "✉️ Compose"}
            </span>
            {subject && (
              <span className="text-xs text-gray-500 truncate max-w-32">
                {subject}
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-xs px-2 py-1 h-6"
            onClick={(e) => {
              e.stopPropagation();
              setMinimized(false);
            }}
            type="button"
            disabled={loading}
          >
            Restore
          </Button>
        </div>
      ) : (
        <form
          className="flex flex-col flex-1 p-4 gap-3 overflow-auto"
          onSubmit={handleSend}
        >
          <Input
            type="email"
            placeholder="To"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            required
            className=""
            disabled={loading}
          />
          <Input
            type="text"
            placeholder="Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className=""
            disabled={loading}
          />
          <Textarea
            placeholder="Message..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
            required
            className="flex-1 min-h-[8rem] resize-none"
            disabled={loading}
          />
          <AttachmentUpload
            files={attachments}
            onChange={setAttachments}
            disabled={loading}
          />
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-sm flex items-center gap-2">
              <span>⚠️</span>
              <span>
                {typeof error === "string"
                  ? error
                  : (() => {
                      try {
                        return JSON.stringify(error);
                      } catch {
                        return "An error occurred";
                      }
                    })()}
              </span>
            </div>
          )}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-3 py-2 rounded-lg text-sm flex items-center gap-2">
              <span>✅</span>
              <span>{success}</span>
            </div>
          )}
          {showSuggestion && suggestion && (
            <div className="border rounded-lg p-3 bg-blue-50 dark:bg-blue-900/20 border-blue-200">
              <div className="text-sm font-medium mb-2 flex items-center gap-2">
                <span>✨</span>
                <span>AI Suggestion</span>
              </div>
              <div className="text-sm text-gray-700 dark:text-gray-300 mb-3 whitespace-pre-wrap max-h-32 overflow-y-auto">
                {suggestion}
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="default"
                  size="sm"
                  onClick={handleApplySuggestion}
                >
                  ✓ Use This
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSuggestion(false)}
                >
                  ✕ Close
                </Button>
              </div>
            </div>
          )}
          <div className="flex gap-2 justify-between mt-2">
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleGetSuggestions}
                disabled={loading || suggestionsLoading}
                size="sm"
                className="gap-2"
              >
                <Wand2 className="w-4 h-4" />
                {suggestionsLoading
                  ? "Getting suggestion..."
                  : "Get suggestion"}
              </Button>
            </div>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleSaveDraft}
                disabled={loading}
                size="sm"
                className="gap-2"
              >
                <Save className="w-4 h-4" />
                {isDraft ? "Update draft" : "Save as draft"}
              </Button>
              <Button
                type="submit"
                variant="default"
                disabled={loading}
                className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                <Send className="w-4 h-4" />
                {loading ? "Sending..." : isDraft ? "Send draft" : "Send"}
              </Button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default ComposeEmail;
