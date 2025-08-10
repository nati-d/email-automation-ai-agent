"use client"

import { useEffect, useState } from "react"
import { fetchDrafts, deleteDraft, type Draft } from "../../lib/api/email";
import { FileText, Edit, Trash2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatEmailDate } from "../../lib/utils";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/AppContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useComposeModal } from "@/components/email/ComposeEmail";
import ChatBot from "@/components/ChatBot";

export default function DraftsPage() {
  console.log('🔍 DraftsPage component rendered');
  const { user, search, refreshTrigger, triggerRefresh } = useApp()
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [deletingId, setDeletingId] = useState<string | null>(null)
  const router = useRouter();
  const { openCompose, editDraft, setOnDraftSaved } = useComposeModal();

  useEffect(() => {
    console.log('🔍 DraftsPage useEffect triggered, user:', user);
    if (user) {
      // Load drafts on first load (no auto-sync)
      loadDrafts(false)
    }
  }, [user])

  // Respond to global refresh triggers (e.g., when drafts are saved)
  useEffect(() => {
    if (user && refreshTrigger > 0) {
      console.log('Refresh triggered, reloading drafts...');
      loadDrafts() // Reload drafts
    }
  }, [refreshTrigger, user])

  // Set up the callback to refresh drafts when a draft is saved
  useEffect(() => {
    setOnDraftSaved(() => loadDrafts);
    
    // Cleanup callback when component unmounts
    return () => {
      setOnDraftSaved(undefined);
    };
  }, [setOnDraftSaved]);

  const loadDrafts = async () => {
    console.log('🔍 loadDrafts called');
    setLoading(true)
    setError(null)
    try {
      console.log('📥 Fetching local drafts...');
      const data = await fetchDrafts()
      console.log('✅ Loaded drafts:', data.length);
      setDrafts(data)
    } catch (err: any) {
      console.error('❌ Failed to load drafts:', err);
      setError(err.response?.data?.detail || err.message || "Failed to fetch drafts")
      
      // Check if this is an auth error that might cause redirect
      if (err.status === 401 || err.status === 403) {
        console.error('🚨 Authentication error in loadDrafts, this might cause redirect');
      }
    } finally {
      setLoading(false)
    }
  }



  const handleDeleteDraft = async (draftId: string) => {
    if (!confirm('Are you sure you want to delete this draft?')) {
      return
    }

    console.log('Deleting draft:', draftId);
    setDeletingId(draftId)
    setError(null) // Clear any previous errors
    try {
      const result = await deleteDraft(draftId, true) // Sync with Gmail
      console.log('Draft deleted:', result);
      
      // Remove from local state immediately
      setDrafts(prev => prev.filter(draft => draft.id !== draftId))
      
      // Trigger global refresh
      triggerRefresh();
      
    } catch (err: any) {
      console.error('Failed to delete draft:', err);
      setError(err.response?.data?.detail || err.message || "Failed to delete draft")
    } finally {
      setDeletingId(null)
    }
  }

  const handleEditDraft = (draft: Draft) => {
    editDraft(draft)
  }

  const filteredDrafts = drafts.filter(
    (draft) =>
      (draft.subject || '').toLowerCase().includes(search.toLowerCase()) ||
      (draft.body || '').toLowerCase().includes(search.toLowerCase()) ||
      draft.recipients.some(recipient => recipient.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <ProtectedRoute>
      <div className="flex flex-col min-h-0 w-full min-w-0 h-full overflow-x-hidden" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
        {/* Header */}
        <div className="flex items-center justify-between gap-4 px-4 sm:px-6 py-4 bg-card border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6" style={{ color: 'var(--primary)' }} />
            <div>
              <h1 className="text-xl font-semibold text-foreground">Drafts</h1>
              <p className="text-sm text-muted-foreground">
                {filteredDrafts.length} draft{filteredDrafts.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadDrafts}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Content */}
        <main className="flex-1 overflow-y-auto" style={{ background: 'var(--card)' }}>
          {loading && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center space-y-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-muted-foreground">Loading drafts...</p>
              </div>
            </div>
          )}
          
          {error && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center space-y-4">
                <div className="text-destructive text-lg font-semibold">Error</div>
                <p className="text-muted-foreground">{error}</p>
                <Button onClick={loadDrafts}>Try Again</Button>
              </div>
            </div>
          )}
          
          {!loading && !error && filteredDrafts.length === 0 && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center space-y-4">
                <FileText className="w-16 h-16 text-muted-foreground mx-auto" />
                <div>
                  <h3 className="text-lg font-semibold text-foreground">No drafts found</h3>
                  <p className="text-muted-foreground">Use the compose button to create and save drafts.</p>
                </div>
              </div>
            </div>
          )}

          {!loading && !error && filteredDrafts.length > 0 && (
            <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
              {filteredDrafts.map((draft) => (
                <div
                  key={draft.id}
                  className="group flex flex-col px-4 sm:px-6 py-4 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => handleEditDraft(draft)}
                >
                  {/* Desktop Layout */}
                  <div className="hidden md:flex items-center justify-between w-full">
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-foreground truncate">
                          {draft.subject || '(No Subject)'}
                        </h3>
                        {draft.synced_with_gmail && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                            Gmail
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        To: {draft.recipients.join(', ')}
                      </p>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {draft.body?.substring(0, 150) || 'No content'}
                        {draft.body && draft.body.length > 150 && '...'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <span className="text-sm text-muted-foreground whitespace-nowrap">
                        {formatEmailDate(draft.updated_at || draft.created_at)}
                      </span>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditDraft(draft);
                          }}
                          className="h-8 w-8 p-0"
                          title="Edit draft"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteDraft(draft.id);
                          }}
                          disabled={deletingId === draft.id}
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          title="Delete draft"
                        >
                          {deletingId === draft.id ? (
                            <div className="w-4 h-4 border border-current border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Mobile Layout */}
                  <div className="md:hidden space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-foreground truncate">
                            {draft.subject || '(No Subject)'}
                          </h3>
                          {draft.synced_with_gmail && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                              Gmail
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          To: {draft.recipients.join(', ')}
                        </p>
                      </div>
                      <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                        {formatEmailDate(draft.updated_at || draft.created_at)}
                      </span>
                    </div>
                    
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {draft.body?.substring(0, 200) || 'No content'}
                      {draft.body && draft.body.length > 200 && '...'}
                    </p>
                    
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditDraft(draft);
                        }}
                        className="flex items-center gap-1"
                      >
                        <Edit className="w-3 h-3" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDraft(draft.id);
                        }}
                        disabled={deletingId === draft.id}
                        className="flex items-center gap-1 text-destructive hover:text-destructive"
                      >
                        {deletingId === draft.id ? (
                          <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Trash2 className="w-3 h-3" />
                        )}
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Floating ChatBot */}
      <ChatBot />
    </ProtectedRoute>
  )
}