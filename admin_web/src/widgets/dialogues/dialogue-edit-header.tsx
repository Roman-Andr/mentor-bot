import { Button } from "@/shared/ui/button";
import { ArrowLeft } from "lucide-react";
import { useTranslations } from "@/shared/hooks/use-translations";

interface DialogueEditHeaderProps {
  title: string;
  onBack: () => void;
}

export function DialogueEditHeader({ title, onBack }: DialogueEditHeaderProps) {
  const t = useTranslations();

  return (
    <div className="flex items-center gap-3">
      <Button variant="ghost" size="icon" onClick={onBack} className="h-10 w-10">
        <ArrowLeft className="size-5" />
      </Button>
      <div className="min-w-0 flex-1">
        <h1 className="text-xl font-bold truncate sm:text-2xl">{t("dialogues.editDialogueTitle")}</h1>
        <p className="text-muted-foreground text-sm truncate">{title}</p>
      </div>
    </div>
  );
}
