import React, { useState, useContext, createContext, ReactNode } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { sendEmail } from "@/lib/api/email";

interface ComposeEmailProps {
  open: boolean;
  onClose: () => void;
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
}
const ComposeModalContext = createContext<ComposeModalContextType | undefined>(undefined);

export function ComposeModalProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const openCompose = () => setOpen(true);
  const closeCompose = () => setOpen(false);
  return (
    <ComposeModalContext.Provider value={{ open, openCompose, closeCompose }}>
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
  const [to, setTo] = useState(initialState.to);
  const [subject, setSubject] = useState(initialState.subject);
  const [body, setBody] = useState(initialState.body);
  const [minimized, setMinimized] = useState(initialState.minimized);
  const [maximized, setMaximized] = useState(initialState.maximized);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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
          <div className="flex gap-2 justify-end mt-2">
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