"use client";

import { useMemo } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useSentEmails } from "@/lib/queries";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Star, StarOff, Reply } from "lucide-react";
import { useComposeModal } from "@/components/email/ComposeEmail";
import { formatEmailDate } from "@/lib/utils";

export default function SentPage() {
  const { data, isLoading, isError } = useSentEmails(50);
  const router = useRouter();
  const { replyToEmail } = useComposeModal();

  const emails = useMemo(() => (data?.emails as any) || [], [data]);

  return (
    <ProtectedRoute>
      <main
        className="flex-1 overflow-y-auto"
        style={{ background: "var(--card)" }}
      >
        {isLoading && (
          <div className="text-[var(--muted-foreground)] p-8">
            Loading emails...
          </div>
        )}
        {isError && (
          <div className="text-[var(--destructive)] p-8">
            Failed to load sent.
          </div>
        )}
        {!isLoading && !isError && emails.length === 0 && (
          <div className="text-[var(--muted-foreground)] p-8">
            No emails found.
          </div>
        )}
        <ul className="divide-y" style={{ borderColor: "var(--border)" }}>
          {emails.map((email: any) => (
            <li
              key={email.id}
              className={`group flex flex-col px-4 sm:px-6 py-3 hover:bg-[var(--muted)] transition-colors cursor-pointer text-sm ${
                email.read ? "" : "font-bold"
              }`}
              style={{
                background: email.read
                  ? "var(--card)"
                  : "var(--accent-foreground)",
                color: "var(--foreground)",
              }}
              onClick={() => router.push(`/email/${email.id}`)}
            >
              <div className="hidden md:flex items-center w-full">
                <button className="w-6 mr-2 flex items-center justify-center">
                  {email.is_starred ? (
                    <Star
                      className="w-4 h-4"
                      style={{ color: "var(--accent)" }}
                    />
                  ) : (
                    <StarOff
                      className="w-4 h-4"
                      style={{ color: "var(--muted-foreground)" }}
                    />
                  )}
                </button>
                <span className="flex-1 truncate">
                  {email.sender || "Unknown sender"}
                </span>
                <span className="flex-[2] truncate">
                  {email.subject || "(No subject)"}{" "}
                  <span className="text-[var(--muted-foreground)] font-normal">
                    - {email.snippet || ""}
                  </span>
                  {email.main_concept && (
                    <span
                      className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                      style={{
                        background: "var(--accent)",
                        color: "var(--accent-foreground)",
                      }}
                    >
                      {email.main_concept}
                    </span>
                  )}
                  {email.key_topics &&
                    Array.isArray(email.key_topics) &&
                    email.key_topics.length > 0 && (
                      <span className="ml-2 text-[var(--muted-foreground)] text-xs">
                        {email.key_topics
                          .slice(0, 3)
                          .map((t: string, i: number) => (
                            <span key={t}>
                              #{t}
                              {i < Math.min(3, email.key_topics.length) - 1
                                ? " "
                                : ""}
                            </span>
                          ))}
                      </span>
                    )}
                  {email.sentiment && (
                    <span
                      className="ml-2 inline-block w-2 h-2 rounded-full align-middle"
                      style={{
                        background:
                          email.sentiment === "positive"
                            ? "#22c55e"
                            : email.sentiment === "negative"
                            ? "#ef4444"
                            : email.sentiment === "neutral"
                            ? "#facc15"
                            : "var(--muted-foreground)",
                      }}
                      title={
                        email.sentiment.charAt(0).toUpperCase() +
                        email.sentiment.slice(1)
                      }
                    />
                  )}
                  {email.summary && (
                    <span
                      className="ml-2 inline-block text-xs text-[var(--muted-foreground)] truncate align-middle max-w-[40ch]"
                      title={email.summary}
                    >
                      {email.summary}
                    </span>
                  )}
                </span>
                <span className="flex-1 truncate text-muted-foreground">
                  {email.email_holder || "-"}
                </span>
                <span
                  className="w-20 text-right flex items-center justify-end gap-1"
                  style={{ color: "var(--muted-foreground)" }}
                >
                  {formatEmailDate(
                    email.sent_at || email.created_at || email.updated_at
                  )}
                  {!email.read && (
                    <span
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ background: "var(--accent)" }}
                    />
                  )}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => {
                    e.stopPropagation();
                    replyToEmail({
                      id: email.id,
                      sender: email.sender,
                      subject: email.subject || "(No subject)",
                      body: email.body,
                      recipients: email.recipients,
                    });
                  }}
                  title="Reply"
                >
                  <Reply className="w-4 h-4" />
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </ProtectedRoute>
  );
}
