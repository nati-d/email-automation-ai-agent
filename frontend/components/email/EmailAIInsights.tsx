"use client";
import { Separator } from "@/components/ui/separator";
import { Tag } from "lucide-react";
import React from "react";

interface EmailAIInsightsProps {
  sentiment?: string;
  mainConcept?: string;
  keyTopics?: string[];
  summary?: string;
}

export const EmailAIInsights: React.FC<EmailAIInsightsProps> = ({ sentiment, mainConcept, keyTopics, summary }) => {
  if (!sentiment && !mainConcept && (!keyTopics || keyTopics.length === 0) && !summary) return null;
  return (
    <>
      <Separator />
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Tag className="h-4 w-4" />
          AI Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sentiment && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Sentiment:</span>
              <span
                className="w-3 h-3 rounded-full"
                style={{
                  background:
                    sentiment === 'positive'
                      ? '#22c55e'
                      : sentiment === 'negative'
                      ? '#ef4444'
                      : sentiment === 'neutral'
                      ? '#facc15'
                      : 'var(--muted-foreground)',
                }}
              />
              <span className="text-sm font-medium capitalize">{sentiment}</span>
            </div>
          )}
          {mainConcept && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Main Concept:</span>
              <span className="px-2 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary">
                {mainConcept}
              </span>
            </div>
          )}
        </div>
        {keyTopics && keyTopics.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Key Topics:</span>
            <div className="flex flex-wrap gap-1">
              {keyTopics.slice(0, 5).map((topic) => (
                <span key={topic} className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                  #{topic}
                </span>
              ))}
            </div>
          </div>
        )}
        {summary && (
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-sm text-muted-foreground mb-1 font-medium">Summary:</p>
            <p className="text-sm text-foreground">{summary}</p>
          </div>
        )}
      </div>
    </>
  );
} 