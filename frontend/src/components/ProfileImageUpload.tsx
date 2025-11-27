import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Upload, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface ProfileImageUploadProps {
    currentAvatarUrl: string | null;
    userName: string;
    onUpload: (file: File) => Promise<{ success: boolean; url?: string; error?: string }>;
}

export const ProfileImageUpload = ({ currentAvatarUrl, userName, onUpload }: ProfileImageUploadProps) => {
    const { toast } = useToast();
    const [uploading, setUploading] = useState(false);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
        if (!allowedTypes.includes(file.type)) {
            toast({
                title: "Invalid file type",
                description: "Please upload a JPEG, PNG, WebP, or GIF image.",
                variant: "destructive",
            });
            return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            toast({
                title: "File too large",
                description: "Maximum file size is 5MB.",
                variant: "destructive",
            });
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onloadend = () => {
            setPreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);

        // Upload
        setUploading(true);
        try {
            const result = await onUpload(file);
            if (result.success) {
                toast({
                    title: "Success",
                    description: "Profile image updated successfully!",
                });
                setPreviewUrl(null);
            } else {
                toast({
                    title: "Upload failed",
                    description: result.error || "Failed to upload image",
                    variant: "destructive",
                });
                setPreviewUrl(null);
            }
        } catch (error) {
            toast({
                title: "Upload failed",
                description: "An unexpected error occurred",
                variant: "destructive",
            });
            setPreviewUrl(null);
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    };

    const avatarUrl = previewUrl || currentAvatarUrl;
    const initials = userName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase();

    return (
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-6">
            <Avatar className="w-20 h-20">
                <AvatarImage src={avatarUrl || undefined} />
                <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <div className="flex flex-col gap-2">
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    onChange={handleFileSelect}
                    className="hidden"
                />
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="gap-2"
                >
                    {uploading ? (
                        <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Uploading...
                        </>
                    ) : (
                        <>
                            <Upload className="w-4 h-4" />
                            Change Photo
                        </>
                    )}
                </Button>
                <p className="text-xs text-muted-foreground">
                    Max 5MB • JPEG, PNG, WebP, or GIF
                </p>
            </div>
        </div>
    );
};
