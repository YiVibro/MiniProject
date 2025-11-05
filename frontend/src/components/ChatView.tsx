import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ManipulatePanel } from "./ManipulatePanel";
import { MessageBubble } from "./MessageBubble";    
import { agentService } from "../lib/agentService";
import { useAuth } from "../store/AuthContext";

interface ChatViewProps {
  documentId?: number;
  onBack: () => void;
  sessionId?: string;
  courseName?: string;
}
type ChatSender = "user" | "ai";

interface ChatMessage {
  sender: ChatSender;
  text: string;
}
export const ChatView = ({ documentId, onBack, sessionId: propSessionId, courseName }: ChatViewProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(propSessionId || null);
  const [sessions, setSessions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [isLearningSession, setIsLearningSession] = useState(!!propSessionId);
  const { user } = useAuth();

  const sendMessage = async () => {
    if (!input.trim()) return;

    //Add user message
    setMessages((prev) => [...prev, { sender: "user" as const, text: input }]);

    setLoading(true);
    try {
      if (isLearningSession && sessionId) {
        // Handle learning session interaction
        const response = await agentService.processUserInteraction(
          sessionId,
          "chat_message",
          { message: input, user_id: user?.id }
        );
        
        setMessages((prev) => [...prev, { 
          sender: "ai" as const, 
          text: response.response || response.message || "I'm here to help you learn!" 
        }]);
      } else if (documentId) {
        // Handle PDF chat
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
      }
    } catch (err) {
      console.error("Error sending message:", err);
      setMessages((prev) => [...prev, { 
        sender: "ai" as const, 
        text: "Sorry, I encountered an error. Please try again." 
      }]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

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

  // Initialize learning session
  useEffect(() => {
    if (isLearningSession && sessionId && courseName) {
      // Add welcome message for learning session
      setMessages([{
        sender: "ai",
        text: `Welcome to your ${courseName} learning session! I'm your AI tutor. How can I help you learn today?`
      }]);
    }
  }, [isLearningSession, sessionId, courseName]);

  // Cleanup function for learning session
  const endLearningSession = async () => {
    if (isLearningSession && sessionId) {
      try {
        await agentService.endLearningSession(sessionId);
        console.log("Learning session ended successfully");
      } catch (error) {
        console.error("Error ending learning session:", error);
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isLearningSession && sessionId) {
        endLearningSession();
      }
    };
  }, [isLearningSession, sessionId]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex justify-between items-center">
        <CardTitle>
          {isLearningSession ? `Learning Session: ${courseName}` : "Chat with PDF"}
        </CardTitle>
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

      {/* Manipulation panel below chat - only show for PDF chat */}
      {!isLearningSession && documentId && (
        <ManipulatePanel onManipulate={handleManipulate} />
      )}
    </Card>
  );
};
