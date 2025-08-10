"use client";
import { useRouter, useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchDraftById, sendDraft, deleteDraft, type Draft } from "../../../lib/api/email";
import { formatEmailDate } from "../../../lib/utils";
import { EmailHeader } from "@/components/email/EmailHeader";
import { EmailMetadata } from "@/components/email/EmailMetadata";
import { EmailBody } from "@/components/email/EmailBody";
import { Button } from "@/components/ui/button";
import { useComposeModal } from "@/components/email/ComposeEmail";
import { useApp } from "@/components/AppContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { Edit, Send, Trash2, ArrowLeft } from "lucide-react";

export default function DraftDetailPage() {
  const router = useRouter();
  const { draft_id } = useParams();
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const { editDraft } = useComposeModal();
  const { triggerRefresh } = useApp();

  useEffect(() => {
    if (!draft_id) {
      setError("Invalid draft ID");
      setLoading(false);
      return;
    }

    console.log('Loading draft:', draft_id);
    setLoading(true);
    setError(null);
    
    fetchDraftById(draft_id as string)
      .then((data) => {
        console.log('Draft loaded:', data);
        setDraft(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load draft:', err);
        setError(err.response?.data?.detail || err.message || "Failed to fetch draft");
        setLoading(false);
      });
  }, [draft_id]);

  const handleSendDraft = async () => {
    if (!draft?.id) return;
    
    if (!confirm('Are you sure you want to send this draft?')) {
      return;
    }

    setActionLoading('send');
    try {
      console.log('Sending draft:', draft.id);
      const result = await sendDraft(draft.id);
      console.log('Draft sent:', result);
      
      // Trigger global refresh
      triggerRefresh();
      
      // Navigate back to drafts page
      router.push('/drafts');
    } catch (err: any) {
      console.error('Failed to send draft:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to send draft');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteDraft = async () => {
    if (!draft?.id) return;
    
    if (!confirm('Are you sure you want to delete this draft?')) {
      return;
    }

    setActionLoading('delete');
    try {
      console.log('Deleting draft:', draft.id);
      const result = await deleteDraft(draft.id, true);
      console.log('Draft deleted:', result);
      
      // Trigger global refresh
      triggerRefresh();
      
      // Navigate back to drafts page
      router.push('/drafts');
    } catch (err: any) {
      console.error('Failed to delete draft:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to delete draft');
    } finally {
      setActionLoading(null);
    }
  };

  const handleEditDraft = () => {
    if (draft) {
      editDraft(draft);
    }
  };

  const handleGoBack = () => {
    router.push('/drafts');
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col min-h-0 w-full min-w-0 h-full overflow-x-hidden" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-muted-foreground">Loading draft...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="text-destructive text-lg font-semibold">Error</div>
              <p className="text-muted-foreground">{error}</p>
              <div className="flex gap-2 justify-center">
                <Button onClick={handleGoBack} variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Drafts
                </Button>
                <Button onClick={() => window.location.reload()}>Try Again</Button>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && !draft && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <div className="text-muted-foreground text-lg font-semibold">Draft not found</div>
              <p className="text-muted-foreground">The draft you're looking for doesn't exist.</p>
              <Button onClick={handleGoBack} variant="outline">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Drafts
              </Button>
            </div>
          </div>
        )}

        {!loading && !error && draft && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between gap-4 px-4 sm:px-6 py-4 bg-card border-b" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleGoBack}
                  className="flex items-center gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Drafts
                </Button>
                <div className="h-6 w-px bg-border" />
                <div>
                  <h1 className="text-xl font-semibold text-foreground">
                    {draft.subject || "(No Subject)"}
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Draft • Last updated {formatEmailDate(draft.updated_at || draft.created_at)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleEditDraft}
                  className="flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeleteDraft}
                  disabled={actionLoading === 'delete'}
                  className="flex items-center gap-2 text-destructive hover:text-destructive"
                >
                  {actionLoading === 'delete' ? (
                    <div className="w-4 h-4 border border-current border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  Delete
                </Button>
                <Button
                  onClick={handleSendDraft}
                  disabled={actionLoading === 'send'}
                  className="flex items-center gap-2"
                >
                  {actionLoading === 'send' ? (
                    <div className="w-4 h-4 border border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Send Draft
                </Button>
              </div>
            </div>

            {/* Content */}
            <main className="flex-1 overflow-y-auto p-4 sm:p-6" style={{ background: 'var(--card)' }}>
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Draft Metadata */}
                <div className="bg-card rounded-lg border p-6 space-y-4" style={{ borderColor: 'var(--border)' }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">To:</span>
                        <span className="text-sm">{draft.recipients.join(', ')}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">From:</span>
                        <span className="text-sm">{draft.sender}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">Status:</span>
                        <span className="text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                          Draft
                        </span>
                        {draft.synced_with_gmail && (
                          <span className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                            Synced with Gmail
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-muted-foreground">Created:</span>
                        <span className="text-sm">{formatEmailDate(draft.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Draft Body */}
                <div className="bg-card rounded-lg border p-6" style={{ borderColor: 'var(--border)' }}>
                  <EmailBody htmlBody={draft.html_body} body={draft.body} />
                </div>
              </div>
            </main>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}