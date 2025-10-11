import { Button } from "@/components/ui/button";

interface ActionButtonsProps {
  onChat: () => void;
  onQuiz: () => void;
}

export const ActionButtons = ({ onChat, onQuiz }: ActionButtonsProps) => {
  return (
    <div className="flex gap-4 justify-center">
      <Button onClick={onChat} className="gap-2">💬 Chat with PDF</Button>
      <Button onClick={onQuiz} className="gap-2">📝 Quiz Me</Button>
    </div>
  );
};
