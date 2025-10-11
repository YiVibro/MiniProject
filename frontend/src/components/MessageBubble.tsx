interface MessageBubbleProps {
  sender: "user" | "ai";
  text: string;
}

export const MessageBubble = ({ sender, text }: MessageBubbleProps) => {
  const isUser = sender === "user";
  return (
    <div
      className={`p-3 rounded-lg max-w-lg ${
        isUser ? "bg-primary text-white ml-auto" : "bg-muted mr-auto"
      }`}
    >
      {text}
    </div>
  );
};
