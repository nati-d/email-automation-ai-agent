"use client";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Email } from "../../../lib/api/email";
import { formatEmailDate } from "../../../lib/utils";
import { EmailHeader } from "@/components/email/EmailHeader";
import { EmailMetadata } from "@/components/email/EmailMetadata";
import { EmailAIInsights } from "@/components/email/EmailAIInsights";
import { EmailBody } from "@/components/email/EmailBody";
import { Button } from "@/components/ui/button";
import { useComposeModal } from "@/components/email/ComposeEmail";
import { useEmail, useSentEmailById } from "@/lib/queries";

export default function EmailDetailPage() {
  const router = useRouter();
  const { email_id } = useParams();
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { replyToEmail } = useComposeModal();

  const {
    data: normalEmail,
    isLoading: isEmailLoading,
    isError: isEmailError,
  } = useEmail(email_id as string);
  const {
    data: sentEmail,
    isLoading: isSentLoading,
    isError: isSentError,
  } = useSentEmailById(email_id as string);

  useEffect(() => {
    setLoading(isEmailLoading && isSentLoading);
    if (normalEmail) {
      setEmail(normalEmail as any);
      setError(null);
    } else if (!isEmailLoading && sentEmail) {
      setEmail(sentEmail as any);
      setError(null);
    } else if (isEmailError && isSentError) {
      setError("Failed to fetch email");
    }
  }, [
    normalEmail,
    sentEmail,
    isEmailLoading,
    isSentLoading,
    isEmailError,
    isSentError,
  ]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading email...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="text-destructive text-lg font-semibold">Error</div>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    );
  }

  if (!email) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="text-muted-foreground text-lg font-semibold">
            Email not found
          </div>
          <p className="text-muted-foreground">
            The email you're looking for doesn't exist.
          </p>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-0 w-full bg-white mt-4 rounded-tl-xl overflow-hidden">
      <EmailHeader
        subject={email.subject || "(No subject)"}
        sender={email.sender || "Unknown sender"}
        date={formatEmailDate(
          email.sent_at || email.created_at || email.updated_at
        )}
        onBack={() => router.back()}
        onPrint={() => {
          try {
            const title = (email.subject || "Email")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
            const head = `<!doctype html><html><head>
              <meta charset=\"utf-8\"/>
              <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
              <title>${title}</title>
              <style>
                @page { size: auto; margin: 12mm; }
                html, body { padding: 0; margin: 0; background: #fff; color: #000; }
                body { font: 14px/1.6 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Inter,Helvetica,Arial,sans-serif; }
                .wrap { width: 100%; box-sizing: border-box; padding: 24px; }
                h1 { font-size: 18px; margin: 0 0 8px; }
                .meta { color: #555; font-size: 12px; margin: 0 0 12px; }
                .content { width: 100%; max-width: 100%; box-sizing: border-box; }
                .content, .content * { max-width: 100% !important; overflow: visible !important; }
                img, svg, canvas, video { max-width: 100% !important; height: auto !important; }
                table { width: 100% !important; table-layout: auto !important; border-collapse: collapse; }
                td, th { word-wrap: break-word; white-space: normal; }
                pre, code { white-space: pre-wrap; word-wrap: break-word; }
                a { color: #000; text-decoration: none; }
              </style>
            </head><body>`;
            const metaLine = `${
              email.sender || "Unknown sender"
            } • ${formatEmailDate(
              email.sent_at || email.created_at || email.updated_at
            )}`;
            const content = email.html_body
              ? `<div class=\"content\">${email.html_body}</div>`
              : `<pre class=\"content\" style=\"white-space:pre-wrap;word-wrap:break-word\">${(
                  email.body || ""
                )
                  .replace(/</g, "&lt;")
                  .replace(/>/g, "&gt;")}</pre>`;
            const html = `${head}<div class=\"wrap\"><h1>${title}</h1><div class=\"meta\">${metaLine}</div>${content}</div></body></html>`;

            // Use hidden iframe to avoid popup/blank pages
            const iframe = document.createElement("iframe");
            iframe.style.position = "fixed";
            iframe.style.right = "0";
            iframe.style.bottom = "0";
            iframe.style.width = "0";
            iframe.style.height = "0";
            iframe.style.border = "0";
            iframe.style.visibility = "hidden";
            document.body.appendChild(iframe);

            const doc =
              iframe.contentDocument || iframe.contentWindow?.document;
            if (!doc) throw new Error("Print iframe document not available");
            doc.open();
            doc.write(html);
            doc.close();

            const cleanup = () => {
              try {
                document.body.removeChild(iframe);
              } catch {}
            };

            const doPrint = () => {
              try {
                iframe.contentWindow?.focus();
                // Close iframe after printing to avoid any blank page remnants
                const after = () => cleanup();
                if ("onafterprint" in iframe.contentWindow!) {
                  (iframe.contentWindow as any).onafterprint = after;
                } else {
                  setTimeout(after, 500);
                }
                iframe.contentWindow?.print();
              } catch (e) {
                cleanup();
                throw e;
              }
            };

            // Wait for layout/paint
            setTimeout(() => {
              if (doc.readyState === "complete") doPrint();
              else
                doc.addEventListener("readystatechange", () => {
                  if (doc.readyState === "complete") doPrint();
                });
            }, 200);
          } catch (e) {
            console.error(e);
            window.print();
          }
        }}
        onOpenNewWindow={() => {
          const url = window.location.href;
          window.open(url, "_blank", "noopener,noreferrer");
        }}
        onShowOriginal={() => {
          try {
            const md: any = (email as any).metadata || {};
            const possibleMsgIds = [
              md.gmail_message_id,
              md.message_id,
              md.gm_msg_id,
              md.gmail_id,
            ].filter(Boolean);
            const possibleThreadIds = [
              md.gmail_thread_id,
              md.thread_id,
              md.gm_thread_id,
            ].filter(Boolean);
            const rfc822 = md.rfc822_message_id || md["rfc822-message-id"]; // e.g. <abc@domain>

            let target = "";
            if (possibleMsgIds.length) {
              target = `https://mail.google.com/mail/u/0/#all/${encodeURIComponent(
                String(possibleMsgIds[0])
              )}`;
            } else if (possibleThreadIds.length) {
              target = `https://mail.google.com/mail/u/0/#inbox/${encodeURIComponent(
                String(possibleThreadIds[0])
              )}`;
            } else if (rfc822) {
              target = `https://mail.google.com/mail/u/0/#search/${encodeURIComponent(
                "rfc822msgid:" + rfc822
              )}`;
            } else if (email.subject) {
              const subject = `subject:\"${email.subject}\"`;
              target = `https://mail.google.com/mail/u/0/#search/${encodeURIComponent(
                subject
              )}`;
            } else if (email.sender) {
              const sender = `from:\"${email.sender}\"`;
              target = `https://mail.google.com/mail/u/0/#search/${encodeURIComponent(
                sender
              )}`;
            } else {
              target = `https://mail.google.com/mail/u/0/#inbox`;
            }

            const win = window.open(target, "_blank", "noopener,noreferrer");
            if (!win) {
              window.location.href = target;
            }
          } catch (e) {
            console.error(e);
            window.open(
              "https://mail.google.com/mail/u/0/#inbox",
              "_blank",
              "noopener,noreferrer"
            );
          }
        }}
      />
      <main className="flex-1 overflow-y-auto">
        <div className="w-full space-y-8">
          <div className="bg-card rounded-lg p-6 space-y-6 w-full">
            <EmailMetadata
              sender={email.sender || "Unknown sender"}
              senderInitial={
                email.sender ? email.sender.charAt(0).toUpperCase() : "?"
              }
              recipients={email.recipients || []}
              date={formatEmailDate(
                email.sent_at || email.created_at || email.updated_at
              )}
              onReply={() => {
                replyToEmail({
                  id: email.id,
                  sender: email.sender || "Unknown sender",
                  subject: email.subject || "(No subject)",
                  body: email.body,
                  recipients: email.recipients,
                });
              }}
              onReplyAll={() => {}}
              onForward={() => {}}
            />
            <EmailAIInsights
              sentiment={email.sentiment}
              mainConcept={email.main_concept}
              keyTopics={email.key_topics}
              summary={email.summary}
            />
          </div>
          <EmailBody htmlBody={email.html_body} body={email.body} />
        </div>
      </main>
    </div>
  );
}
