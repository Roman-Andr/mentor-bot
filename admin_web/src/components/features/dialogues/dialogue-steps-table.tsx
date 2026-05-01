import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, GripVertical } from "lucide-react";
import { TableActions, buildEditAction, buildDeleteAction } from "@/components/shared";
import { cn } from "@/lib/utils";
import type { DialogueStep } from "@/types";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

const ANSWER_TYPE_LABEL: Record<string, string> = {
  TEXT: "Text",
  CHOICE: "Choice",
  LINK: "Link",
};

interface SortableStepRowProps {
  step: DialogueStep;
  position: number;
  onEdit: (id: number) => void;
  onDelete: (id: number, question: string) => void;
  t: (key: string) => string;
}

function SortableStepRow({ step, position, onEdit, onDelete, t }: SortableStepRowProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: step.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <TableRow ref={setNodeRef} style={style} className={cn(isDragging && "bg-muted")}>
      <TableCell className="w-8 px-2">
        <button
          {...attributes}
          {...listeners}
          className="text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing"
          tabIndex={-1}
        >
          <GripVertical className="size-4" />
        </button>
      </TableCell>
      <TableCell className="w-16 text-center font-mono">{position}</TableCell>
      <TableCell>
        <p className="line-clamp-2">{step.question}</p>
      </TableCell>
      <TableCell className="w-24">
        <span className="bg-muted rounded px-2 py-0.5 text-xs font-medium">
          {ANSWER_TYPE_LABEL[step.answer_type] ?? step.answer_type}
        </span>
      </TableCell>
      <TableCell className="w-32">
        {step.answer_type === "CHOICE" ? (
          <span className="text-muted-foreground text-xs">
            {step.options?.length ?? 0} {t("dialogues.options")}
          </span>
        ) : (
          <p className="text-muted-foreground line-clamp-1 text-xs">
            {step.answer_content || "—"}
          </p>
        )}
      </TableCell>
      <TableCell className="w-16">
        <span
          className={cn(
            "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
            step.is_final
              ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
              : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
          )}
        >
          {step.is_final ? t("common.yes") : t("common.no")}
        </span>
      </TableCell>
      <TableCell className="w-20">
        <TableActions
          actions={[
            buildEditAction(() => onEdit(step.id), t("common.edit")),
            buildDeleteAction(() => onDelete(step.id, step.question), t("common.delete")),
          ]}
        />
      </TableCell>
    </TableRow>
  );
}

interface DialogueStepsTableProps {
  steps: DialogueStep[];
  onEdit: (id: number) => void;
  onDelete: (id: number, question: string) => void;
  onAddStep: () => void;
  onDragOver: (event: DragOverEvent) => void;
  onDragEnd: (event: DragEndEvent) => void;
  t: (key: string) => string;
}

export function DialogueStepsTable({
  steps,
  onEdit,
  onDelete,
  onAddStep,
  onDragOver,
  onDragEnd,
  t,
}: DialogueStepsTableProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            {t("dialogues.steps")}{" "}
            <span className="text-muted-foreground text-sm font-normal">({steps.length})</span>
          </CardTitle>
          <Button size="sm" onClick={onAddStep} className="gap-1">
            <Plus className="size-4" />
            {t("dialogues.addStep")}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {steps.length === 0 ? (
          <div className="flex h-32 items-center justify-center">
            <p className="text-muted-foreground text-sm">{t("dialogues.noSteps")}</p>
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragOver={onDragOver}
            onDragEnd={onDragEnd}
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8" />
                  <TableHead className="w-16">{t("dialogues.stepNumber")}</TableHead>
                  <TableHead>{t("dialogues.question")}</TableHead>
                  <TableHead className="w-24">{t("dialogues.answerType")}</TableHead>
                  <TableHead className="w-32">{t("dialogues.answerContent")}</TableHead>
                  <TableHead className="w-16">{t("dialogues.isFinal")}</TableHead>
                  <TableHead className="w-20">{t("common.actions")}</TableHead>
                </TableRow>
              </TableHeader>
              <SortableContext items={steps.map((s) => s.id)} strategy={verticalListSortingStrategy}>
                <TableBody>
                  {steps.map((step, index) => (
                    <SortableStepRow
                      key={step.id}
                      step={step}
                      position={index + 1}
                      onEdit={onEdit}
                      onDelete={onDelete}
                      t={t}
                    />
                  ))}
                </TableBody>
              </SortableContext>
            </Table>
          </DndContext>
        )}
      </CardContent>
    </Card>
  );
}
