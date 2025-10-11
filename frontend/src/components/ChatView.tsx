import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { v4 as uuidv4 } from "uuid";
import { ManipulatePanel } from "./ManipulatePanel";
import { MessageBubble } from "./MessageBubble";    
import { set } from "date-fns";

interface ChatViewProps {
  documentId: number;
  onBack: () => void;
}
type ChatSender = "user" | "ai";

interface ChatMessage {
  sender: ChatSender;
  text: string;
}
export const ChatView = ({ documentId, onBack }: ChatViewProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<string[]>([]);  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    //Add user message
    setMessages((prev) => [...prev, { sender: "user" as const, text: input }]);

  // Helper: add message locally
  const addMessage = (sender: ChatSender, text: string) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  // Fetch chat sessions for this document
  const fetchSessions = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/chat/sessions/${documentId}`
      );
      if (!res.ok) throw new Error("Failed to fetch sessions");
      const data: string[] = await res.json();
      setSessions(data);

      // Auto-select the most recent session
      if (data.length > 0) {
        setSessionId(data[0]);
        fetchHistory(data[0]);
      }
    } catch (err) {
      console.error("Error fetching sessions:", err);
    }
  };

  // Fetch history for a given session
  const fetchHistory = async (session: string) => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/chat/history/${documentId}/${session}`
      );
      if (!res.ok) throw new Error("Failed to fetch history");
      const history: { sender: ChatSender; text: string }[] = await res.json();
      setMessages(history);
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  };


    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: documentId,
          message: input,
          session_id: sessionId,
        }),
      });

      if (!res.ok) throw new Error("Chat request failed");
      const data = await res.json();

      setMessages((prev) => [...prev, { sender: "ai" as const, text: data.response || "No reply" }]);
    
    } catch (err) {
      console.error("Error chatting:", err);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  const handleManipulate = async (operation: string, customPrompt?: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/manipulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: documentId,
          operation,
          custom_prompt: customPrompt || "",
        }),
      });

      if (!res.ok) throw new Error("Manipulation failed");
      const data = await res.json();

      const aiMsg = { sender: "ai" as const, text: data.result || "No result" };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error("Error manipulating content:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex justify-between items-center">
        <CardTitle>Chat with PDF</CardTitle>
        <Button variant="outline" onClick={onBack}>⬅ Back</Button>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-3">
        {messages.map((m, i) => (
          <MessageBubble key={i} sender={m.sender} text={m.text} />
        ))}
        {loading && <p className="text-muted-foreground">AI is typing...</p>}
      </CardContent>
      <div className="p-3 border-t flex gap-2">
        <Input
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <Button onClick={sendMessage} disabled={loading}>Send</Button>
      </div>

      {/* Manipulation panel below chat */}
      <ManipulatePanel onManipulate={handleManipulate} />
    </Card>
  );
};
