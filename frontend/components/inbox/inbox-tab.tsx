"use client";

import { useState } from "react";
import { useCategories, useCategoryEmails, useAllEmails } from "@/lib/queries";
import { CategorySidebar } from "./category-sidebar";
import { EmailListView } from "./email-list-view";
import { EmailDetailModal } from "./email-detail-modal";
import { LoadingSpinner } from "@/components/ui/loading";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export function InboxTab() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  // Fetch categories
  const { data: categoriesData, isLoading: categoriesLoading, error: categoriesError } = useCategories();

  // Fetch emails based on selected category
  const { data: emailsData, isLoading: emailsLoading, error: emailsError } = selectedCategory
    ? useCategoryEmails(selectedCategory)
    : useAllEmails(); // Use all emails when no category is selected

  const handleCategorySelect = (categoryId: string | null) => {
    setSelectedCategory(categoryId);
    setSelectedEmailId(null); // Clear selected email when changing category
  };

  const handleEmailSelect = (emailId: string) => {
    setSelectedEmailId(emailId);
  };

  const handleEmailClose = () => {
    setSelectedEmailId(null);
  };

  if (categoriesError || emailsError) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load inbox data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* Category Sidebar */}
      <div className="w-64 border-r bg-muted/30 flex-shrink-0">
        <CategorySidebar
          categories={categoriesData?.categories || []}
          selectedCategory={selectedCategory}
          onCategorySelect={handleCategorySelect}
          isLoading={categoriesLoading}
        />
      </div>

      {/* Email List */}
      <div className="flex-1 min-w-0">
        <EmailListView
          emails={emailsData?.emails || []}
          selectedCategory={selectedCategory}
          onEmailSelect={handleEmailSelect}
          isLoading={emailsLoading}
          totalCount={emailsData?.total_count || 0}
        />
      </div>

      {/* Email Detail Modal */}
      {selectedEmailId && (
        <EmailDetailModal
          emailId={selectedEmailId}
          isOpen={!!selectedEmailId}
          onClose={handleEmailClose}
        />
      )}
    </div>
  );
}