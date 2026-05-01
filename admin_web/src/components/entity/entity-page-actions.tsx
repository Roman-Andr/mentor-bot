import { Button } from "@/components/ui/button";
import { Trash2, SquarePen } from "lucide-react";

interface EntityPageActionsProps<TItem> {
  item: TItem;
  onEdit: (item: TItem) => void;
  onDelete: (id: number) => void;
}

export function EntityPageActions<TItem>({ item, onEdit, onDelete }: EntityPageActionsProps<TItem>) {
  const id = (item as Record<string, unknown>).id as number;
  return (
    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onEdit(item)}
        title="Edit"
      >
        <SquarePen className="size-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="text-destructive hover:text-destructive"
        onClick={() => onDelete(id)}
        title="Delete"
      >
        <Trash2 className="size-4" />
      </Button>
    </div>
  );
}
