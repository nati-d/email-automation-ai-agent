"use client";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchEmailById, fetchSentEmailById, Email } from "../../../lib/api/email";
import { formatEmailDate } from "../../../lib/utils";
import { EmailHeader } from "@/components/email/EmailHeader";
import { EmailMetadata } from "@/components/email/EmailMetadata";
import { EmailAIInsights } from "@/components/email/EmailAIInsights";
import { EmailBody } from "@/components/email/EmailBody";
import { Button } from "@/components/ui/button";
import { useComposeModal } from "@/components/email/ComposeEmail";

export default function EmailDetailPage() {
  const router = useRouter();
  const { email_id } = useParams();
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { replyToEmail } = useComposeModal();

  useEffect(() => {
    setLoading(true);
    
    const fetchEmail = async () => {
      try {
        // First try to fetch as a regular email
        const data = await fetchEmailById(email_id as string);
        setEmail(data);
        setLoading(false);
      } catch (regularError) {
        try {
          // If regular email fetch fails, try to fetch as a sent email
          console.log('Regular email fetch failed, trying sent email endpoint...');
          const data = await fetchSentEmailById(email_id as string);
          setEmail(data);
          setLoading(false);
        } catch (sentError) {
          console.error('Both email fetch attempts failed:', { regularError, sentError });
          setError(sentError.message || regularError.message || "Failed to fetch email");
          setLoading(false);
        }
      }
    };

    fetchEmail();
  }, [email_id]);

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
          <div className="text-muted-foreground text-lg font-semibold">Email not found</div>
          <p className="text-muted-foreground">The email you're looking for doesn't exist.</p>
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
        date={formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
        onBack={() => router.back()}
      />
      <main className="flex-1 overflow-y-auto">
        <div className="w-full space-y-8">
          <div className="bg-card rounded-lg p-6 space-y-6 w-full">
            <EmailMetadata
              sender={email.sender || "Unknown sender"}
              senderInitial={email.sender ? email.sender.charAt(0).toUpperCase() : "?"}
              recipients={email.recipients || []}
              date={formatEmailDate(email.sent_at || email.created_at || email.updated_at)}
              onReply={() => {
                replyToEmail({
                  id: email.id,
                  sender: email.sender || "Unknown sender",
                  subject: email.subject || "(No subject)",
                  body: email.body,
                  recipients: email.recipients
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