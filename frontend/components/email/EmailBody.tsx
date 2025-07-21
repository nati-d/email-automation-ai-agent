"use client"

import { Mail } from "lucide-react"
import type React from "react"
import { useRef, useEffect, useState } from "react"

interface EmailBodyProps {
  htmlBody?: string
  body?: string
}

export const EmailBody: React.FC<EmailBodyProps> = ({ htmlBody, body }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [iframeHeight, setIframeHeight] = useState<number | string>("auto") // State to store iframe height

  useEffect(() => {
    if (iframeRef.current && htmlBody) {
      const iframe = iframeRef.current
      const doc = iframe.contentDocument

      if (doc) {
        // Clear previous content and write new HTML
        doc.open()
        doc.write(htmlBody)
        doc.close()

        // Function to adjust iframe height
        const adjustIframeHeight = () => {
          try {
            // Get the scroll height of the content within the iframe
            // Using documentElement.scrollHeight is generally more reliable
            const contentHeight = iframe.contentWindow?.document.documentElement.scrollHeight
            if (contentHeight) {
              setIframeHeight(contentHeight)
            }
          } catch (e) {
            console.error("Error measuring iframe content height:", e)
            // Fallback to a default height if there's an error (e.g., cross-origin issues, though unlikely here)
            setIframeHeight(400)
          }
        }

        // Attach load event listener to the iframe
        // This ensures the content (including images, scripts) is fully loaded and rendered before measuring
        iframe.onload = adjustIframeHeight

        // Also try to adjust height immediately in case the content is simple
        // and renders before the load event fires, or if it's cached.
        // The onload event will provide the final, accurate height.
        adjustIframeHeight()
      }
    } else if (!htmlBody) {
      // Reset height if htmlBody is removed or not provided
      setIframeHeight("auto")
    }
  }, [htmlBody]) // Re-run effect when htmlBody changes

  if (htmlBody) {
    return (
      <div className="bg-card rounded-lg p-6 w-full">
        <iframe
          ref={iframeRef}
          title="Email Content"
          // Set height dynamically, maintaining a minHeight for initial load or empty content
          style={{ width: "100%", height: iframeHeight, minHeight: 400, border: "none", background: "white" }}
          sandbox="allow-same-origin" // Allows content to be treated as same origin for script execution and DOM access
        />
      </div>
    )
  }

  return (
    <div className="bg-card rounded-lg p-6 w-full">
      <div className="prose prose-sm max-w-none">
        {body ? (
          <div
            className="email-content whitespace-pre-wrap"
            style={{
              fontSize: "14px",
              lineHeight: "1.6",
              color: "var(--foreground)",
            }}
          >
            {body}
          </div>
        ) : (
          <div className="text-center py-12">
            <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No content available</p>
          </div>
        )}
      </div>
    </div>
  )
}
