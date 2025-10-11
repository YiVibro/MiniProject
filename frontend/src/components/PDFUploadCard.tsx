
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, X, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Label } from "./ui/label";

interface PDFUploadCardProps {
  onUploadComplete: () => void;
}

export const PDFUploadCard = ({ onUploadComplete }: PDFUploadCardProps) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setIsUploading(true);
    try{
      const formData = new FormData();
      formData.append("file", uploadedFile);

      const response = await fetch("http://127.0.0.1:8000/api/pdf/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const text = await response.text();
      console.log("Raw response:",text);

      if(!response.ok){
        throw new Error("Upload failed");
      }
      const result = JSON.parse(text);
      console.log("Upload success:",result);
      onUploadComplete();
    }
    catch(error){
      console.error("Error uploading file:",error);
    }finally{
      setIsUploading(false);
    }
    
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Upload PDF & Generate Quiz
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
          <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm text-muted-foreground mb-2">
            Upload a PDF to generate a quiz
          </p>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            className="hidden"
            id="pdf-upload"
          />
          <Button variant="outline" asChild>
            <label htmlFor="pdf-upload" className="cursor-pointer">
              Choose PDF
            </label>
          </Button>
        </div>

        {uploadedFile && (
          <div className="space-y-2">
            <Label>Uploaded File:</Label>
            <div className="flex items-center justify-between">
              <Badge variant="secondary" className="gap-1">
                {uploadedFile.name}
                <X
                  className="w-3 h-3 cursor-pointer"
                  onClick={removeFile}
                />
              </Badge>
              <Button onClick={handleUpload} disabled={isUploading}>
                {isUploading ? "Uploading..." : "Upload"}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
