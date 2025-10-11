import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface RecentUploadsProps {
  onSelect: (docId: number) => void;
}

export const RecentUploads = ({ onSelect }: RecentUploadsProps) => {
  const [documents, setDocuments] = useState<any[]>([]);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/pdf/documents");
        if (!res.ok) throw new Error("Failed to fetch documents");
        const data = await res.json();
        setDocuments(data);
      } catch (err) {
        console.error("Error fetching documents:", err);
      }
    };
    fetchDocs();
  }, []);

  if (documents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Uploads</CardTitle>
        </CardHeader>
        <CardContent>No PDFs uploaded yet.</CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Uploads</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {documents.map((doc) => (
          <div key={doc.id} className="flex justify-between items-center border p-3 rounded-md">
            <div>
              <p className="font-semibold">{doc.original_filename}</p>
              <p className="text-sm text-muted-foreground">
                {doc.page_count ?? "?"} pages • {Math.round(doc.file_size / 1024)} KB
              </p>
            </div>
            <Button size="sm" variant="outline" onClick={() => onSelect(doc.id)}>
              View
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
