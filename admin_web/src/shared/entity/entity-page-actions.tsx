import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import { Trash2, SquarePen } from "lucide-react";

interface EntityPageActionsProps<TItem> {
  item: TItem;
  onEdit: (item: TItem) => void;
  onDelete: (id: number) => void;
  t: (key: string) => string;
}

export function EntityPageActions<TItem>({
  item,
  onEdit,
  onDelete,
  t,
}: EntityPageActionsProps<TItem>) {
  const id = (item as Record<string, unknown>).id as number;
  return (
    <TooltipProvider>
      <div className="flex flex-wrap gap-1 sm:flex-nowrap" onClick={(e) => e.stopPropagation()}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" onClick={() => onEdit(item)}>
              <SquarePen className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{t("common.edit")}</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-destructive hover:text-destructive"
              onClick={() => onDelete(id)}
            >
              <Trash2 className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{t("common.delete")}</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
}
