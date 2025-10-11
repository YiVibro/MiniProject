import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface PDFContentProps {
  documentId: number;
}

export const PDFContent = ({ documentId }: PDFContentProps) => {
  const [content, setContent] = useState<any>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/pdf/documents/${documentId}/content`);
        if (!res.ok) throw new Error("Failed to fetch document content");
        const data = await res.json();
        setContent(data);
      } catch (err) {
        console.error("Error loading PDF content:", err);
      }
    };

    fetchContent();
  }, [documentId]);

  if (!content) return <p>Loading PDF content...</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{content.filename}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {content.summary && (
          <div>
            <h3 className="font-semibold">Summary</h3>
            <p className="text-sm text-muted-foreground">{content.summary}</p>
          </div>
        )}
        <div>
          <h3 className="font-semibold">Full Content</h3>
          <p className="text-sm whitespace-pre-wrap">{content.content}</p>
        </div>
      </CardContent>
    </Card>
  );
};
