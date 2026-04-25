import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useTranslations } from "@/hooks/use-translations";

interface DialogueEditHeaderProps {
  title: string;
  onBack: () => void;
}

export function DialogueEditHeader({ title, onBack }: DialogueEditHeaderProps) {
  const t = useTranslations();

  return (
    <div className="flex items-center gap-3">
      <Button variant="ghost" size="icon" onClick={onBack}>
        <ArrowLeft className="size-5" />
      </Button>
      <div>
        <h1 className="text-2xl font-bold">{t("dialogues.editDialogueTitle")}</h1>
        <p className="text-muted-foreground text-sm">{title}</p>
      </div>
    </div>
  );
}
