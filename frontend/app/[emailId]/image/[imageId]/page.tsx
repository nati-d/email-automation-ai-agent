"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useEmail } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download } from "lucide-react";

export default function ImageViewPage() {
  const params = useParams();
  const router = useRouter();
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  
  const { data: email } = useEmail(params.emailId as string);
  
  useEffect(() => {
    if (email?.attachments) {
      const attachment = email.attachments.find(
        (att: any) => att.id === params.imageId
      );
      if (attachment?.url) {
        setImageUrl(attachment.url);
      }
    }
  }, [email, params.imageId]);

  const handleBack = () => {
    router.back();
  };

  const handleDownload = () => {
    if (imageUrl) {
      window.open(imageUrl, "_blank");
    }
  };

  return (
    <div className="fixed inset-0 bg-background flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <Button variant="ghost" onClick={handleBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <Button variant="outline" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>

      {/* Image Container */}
      <div className="flex-1 overflow-auto flex items-center justify-center p-4">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Email attachment"
            className="max-w-full max-h-full object-contain"
          />
        ) : (
          <div className="text-muted-foreground">Image not found</div>
        )}
      </div>
    </div>
  );
} 