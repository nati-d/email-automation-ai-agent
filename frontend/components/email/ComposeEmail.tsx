import React, { useState, useContext, createContext, ReactNode } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { sendEmail, getEmailSuggestions } from "@/lib/api/email";

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
  replyData: EmailData | null;
}
const ComposeModalContext = createContext<ComposeModalContextType | undefined>(undefined);

export function ComposeModalProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [replyData, setReplyData] = useState<EmailData | null>(null);
  
  const openCompose = () => {
    setReplyData(null);
    setOpen(true);
  };
  
  const closeCompose = () => {
    setOpen(false);
    setReplyData(null);
  };
  
  const replyToEmail = (email: EmailData) => {
    setReplyData(email);
    setOpen(true);
  };
  
  return (
    <ComposeModalContext.Provider value={{ open, openCompose, closeCompose, replyToEmail, replyData }}>
      {children}
    </ComposeModalContext.Provider>
  );
}

export function useComposeModal() {
  const ctx = useContext(ComposeModalContext);
  if (!ctx) throw new Error("useComposeModal must be used within ComposeModalProvider");
  return ctx;
}

const ComposeEmail: React.FC<ComposeEmailProps> = ({ open, onClose }) => {
  const { replyData } = useComposeModal();
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

  React.useEffect(() => {
    if (!open) {
      setTo(initialState.to);
      setSubject(initialState.subject);
      setBody(initialState.body);
      setSuccess(null);
      setError(null);
      setMinimized(false);
      setMaximized(false);
      setLoading(false);
    }
  }, [open]);

  // Handle reply data when modal opens
  React.useEffect(() => {
    if (open && replyData) {
      // Pre-fill the form for reply
      setTo(replyData.sender);
      setSubject(replyData.subject.startsWith('Re:') ? replyData.subject : `Re: ${replyData.subject}`);
      
      // Add reply prefix to body
      const replyPrefix = `\n\n--- Original Message ---\nFrom: ${replyData.sender}\nSubject: ${replyData.subject}\n\n`;
      const originalBody = replyData.body || '';
      setBody(replyPrefix + originalBody);
    }
  }, [open, replyData]);

  if (!open) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(null);
    setError(null);
    try {
      await sendEmail({
        body,
        recipients: [to],
        subject,
      });
      setSuccess("Email sent successfully!");
      setTo(initialState.to);
      setSubject(initialState.subject);
      setBody(initialState.body);
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

  // Modal styles
  const baseStyle =
    "fixed z-50 flex flex-col transition-all border shadow-xl rounded-xl";
  const minimizedStyle =
    "bottom-4 right-4 w-80 h-12 cursor-pointer flex-row items-center justify-between px-4 py-2";
  const maximizedStyle =
    "top-4 left-1/2 -translate-x-1/2 w-[95vw] h-[90vh]";
  const normalStyle =
    "bottom-4 right-4 w-[28rem] max-w-[95vw] h-[32rem]";

  return (
    <div
      className={
        baseStyle +
        " " +
        (minimized
          ? minimizedStyle
          : maximized
          ? maximizedStyle
          : normalStyle)
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
        <span className="font-semibold tracking-wide">Compose</span>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            title="Minimize"
            className="text-base"
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
            title="Maximize"
            className="text-base"
            onClick={(e) => {
              e.stopPropagation();
              handleMaximize();
            }}
            style={{ display: minimized ? "none" : "inline-flex" }}
            type="button"
            disabled={loading}
          >
            {maximized ? <>&#9633;</> : <>&#9723;</>}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Close"
            className="text-base text-red-600 hover:text-red-700"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            type="button"
            disabled={loading}
          >
            &times;
          </Button>
        </div>
      </div>
      {/* Minimized view */}
      {minimized ? (
        <div className="flex-1 flex items-center justify-between w-full h-full px-2">
          <span className="text-gray-600 dark:text-gray-300">Compose</span>
          <Button
            variant="ghost"
            size="icon"
            className="text-base"
            onClick={(e) => {
              e.stopPropagation();
              setMinimized(false);
            }}
            type="button"
            disabled={loading}
          >
            &#9633;
          </Button>
        </div>
      ) : (
        <form className="flex flex-col flex-1 p-4 gap-3 overflow-auto" onSubmit={handleSend}>
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
          {error && <div className="text-red-600 text-sm mt-1">{error}</div>}
          {success && <div className="text-green-600 text-sm mt-1">{success}</div>}
          {showSuggestion && suggestion && (
            <div className="border rounded-lg p-3 bg-gray-50 dark:bg-gray-800">
              <div className="text-sm font-medium mb-2">AI Suggestion:</div>
              <div className="text-sm text-gray-700 dark:text-gray-300 mb-3 whitespace-pre-wrap">
                {suggestion}
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleApplySuggestion}
                >
                  Apply Suggestion
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSuggestion(false)}
                >
                  Close
                </Button>
              </div>
            </div>
          )}
          <div className="flex gap-2 justify-end mt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleGetSuggestions}
              disabled={loading || suggestionsLoading}
            >
              {suggestionsLoading ? "Getting Suggestions..." : "Get Suggestions"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="default"
              disabled={loading}
            >
              {loading ? "Sending..." : "Send"}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ComposeEmail; 