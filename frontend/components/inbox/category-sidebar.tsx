"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryCRUD } from "./category-crud";
import { 
  Inbox, 
  Plus, 
  Settings, 
  Tag,
  ChevronRight,
  Folder
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Category {
  id: string;
  name: string;
  description?: string;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface CategorySidebarProps {
  categories: Category[];
  selectedCategory: string | null;
  onCategorySelect: (categoryName: string | null) => void;
  isLoading: boolean;
}

export function CategorySidebar({
  categories,
  selectedCategory,
  onCategorySelect,
  isLoading
}: CategorySidebarProps) {
  const [showCRUD, setShowCRUD] = useState(false);

  const activeCategories = categories.filter(cat => cat.is_active);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
            Categories
          </h2>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => setShowCRUD(!showCRUD)}
          >
            <Settings className="h-3 w-3" />
          </Button>
        </div>

        {/* All Emails Option */}
        <Button
          variant={selectedCategory === null ? "secondary" : "ghost"}
          className="w-full justify-start gap-2 mb-2"
          onClick={() => onCategorySelect(null)}
        >
          <Inbox className="h-4 w-4" />
          <span>All Emails</span>
        </Button>
      </div>

      {/* Categories List */}
      <ScrollArea className="flex-1 px-4">
        <div className="space-y-1 py-2">
          {isLoading ? (
            // Loading skeleton
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2 p-2">
                <Skeleton className="h-3 w-3 rounded-full" />
                <Skeleton className="h-4 flex-1" />
              </div>
            ))
          ) : activeCategories.length === 0 ? (
            // Empty state
            <div className="text-center py-8">
              <Folder className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground mb-3">
                No categories yet
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCRUD(true)}
                className="gap-2"
              >
                <Plus className="h-3 w-3" />
                Create Category
              </Button>
            </div>
          ) : (
            // Categories list
            activeCategories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.name ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start gap-2 h-auto py-2 px-2",
                  selectedCategory === category.name && "bg-secondary"
                )}
                onClick={() => onCategorySelect(category.name)}
              >
                <div
                  className="h-3 w-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: category.color || "#6366f1" }}
                />
                <div className="flex-1 text-left min-w-0">
                  <div className="font-medium text-sm truncate">
                    {category.name}
                  </div>
                  {category.description && (
                    <div className="text-xs text-muted-foreground truncate">
                      {category.description}
                    </div>
                  )}
                </div>
                {selectedCategory === category.name && (
                  <ChevronRight className="h-3 w-3 text-muted-foreground" />
                )}
              </Button>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Add Category Button */}
      {!isLoading && activeCategories.length > 0 && (
        <div className="p-4 border-t">
          <Button
            variant="outline"
            className="w-full gap-2"
            onClick={() => setShowCRUD(true)}
          >
            <Plus className="h-4 w-4" />
            Add Category
          </Button>
        </div>
      )}

      {/* Category CRUD Modal */}
      {showCRUD && (
        <CategoryCRUD
          isOpen={showCRUD}
          onClose={() => setShowCRUD(false)}
        />
      )}
    </div>
  );
}