import { Button } from "@/components/ui/button";

interface ManipulatePanelProps {
  onManipulate: (operation: string, customPrompt?: string) => void;
}

export const ManipulatePanel = ({ onManipulate }: ManipulatePanelProps) => {
  return (
    <div className="p-3 border-t flex gap-2">
      <Button size="sm" variant="outline" onClick={() => onManipulate("summarize")}>
        Summarize
      </Button>
      <Button size="sm" variant="outline" onClick={() => onManipulate("translate")}>
        Translate
      </Button>
      <Button size="sm" variant="outline" onClick={() => onManipulate("simplify")}>
        Simplify
      </Button>
    </div>
  );
};
