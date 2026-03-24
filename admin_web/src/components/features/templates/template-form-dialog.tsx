"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { GripVertical, Trash2 } from "lucide-react";
import { Select } from "@/components/ui/select";
import { type TaskTemplate } from "@/lib/api";
import { TASK_CATEGORY_MAP, TASK_CATEGORIES } from "@/lib/constants";
import type { TemplateFormData } from "@/hooks/use-templates";

interface TemplateFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  formData: TemplateFormData;
  onFormDataChange: (data: TemplateFormData) => void;
  tasks: TaskTemplate[];
  departments?: { id: number; name: string }[];
  onTasksChange: (tasks: TaskTemplate[]) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

/** Dialog for creating or editing a template with task management. */
export function TemplateFormDialog({
  open,
  onOpenChange,
  mode,
  formData,
  onFormDataChange,
  tasks,
  departments = [],
  onTasksChange,
  onSubmit,
  onCancel,
}: TemplateFormDialogProps) {
  const [newTask, setNewTask] = useState({
    name: "",
    description: "",
    category: "DOCUMENTATION",
    deadline_days: 3,
  });

  const addTask = () => {
    if (!newTask.name.trim()) return;
    const task: TaskTemplate = {
      id: 0,
      template_id: 0,
      title: newTask.name,
      description: newTask.description || null,
      instructions: null,
      category: newTask.category,
      order: tasks.length + 1,
      due_days: newTask.deadline_days,
      estimated_minutes: null,
    };
    onTasksChange([...tasks, task]);
    setNewTask({
      name: "",
      description: "",
      category: "DOCUMENTATION",
      deadline_days: 3,
    });
  };

  const removeTask = (index: number) => {
    onTasksChange(tasks.filter((_, i) => i !== index));
  };

  const isCreate = mode === "create";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isCreate ? "Создание шаблона" : "Редактирование шаблона"}</DialogTitle>
          <DialogDescription>
            {isCreate
              ? "Создайте новый шаблон чек-листа для онбординга"
              : "Измените шаблон чек-листа"}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Название *</label>
            <Input
              placeholder={
                isCreate ? "Например: Базовый онбординг разработчика" : "Название шаблона"
              }
              value={formData.name}
              onChange={(e) => onFormDataChange({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Описание</label>
            <Textarea
              placeholder={isCreate ? "Краткое описание шаблона" : "Описание шаблона"}
              value={formData.description}
              onChange={(e) => onFormDataChange({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Отдел</label>
              <Select
                value={formData.department_id}
                onChange={(e) => onFormDataChange({ ...formData, department_id: parseInt(e.target.value) || 0 })}
                placeholder="Выберите отдел"
                options={[
                  { value: "0", label: "Не выбран" },
                  ...departments.map((d) => ({ value: String(d.id), label: d.name })),
                ]}
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">Должность</label>
              <Input
                placeholder={isCreate ? "Например: Developer" : "Должность"}
                value={formData.position}
                onChange={(e) => onFormDataChange({ ...formData, position: e.target.value })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Длительность (дней)</label>
              <Input
                type="number"
                min={1}
                value={formData.duration_days}
                onChange={(e) =>
                  onFormDataChange({
                    ...formData,
                    duration_days: parseInt(e.target.value) || 30,
                  })
                }
              />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">Статус</label>
              <Select
                value={formData.status}
                onChange={(e) => onFormDataChange({ ...formData, status: e.target.value })}
                options={[
                  { value: "DRAFT", label: "Черновик" },
                  { value: "ACTIVE", label: "Активен" },
                  { value: "ARCHIVED", label: "Архив" },
                ]}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={isCreate ? "isDefault" : "isDefaultEdit"}
              checked={formData.is_default}
              onChange={(e) => onFormDataChange({ ...formData, is_default: e.target.checked })}
               className="border-input rounded"
            />
            <label htmlFor={isCreate ? "isDefault" : "isDefaultEdit"} className="text-sm">
              По умолчанию
            </label>
          </div>

          <div className="mt-4 border-t pt-4">
            <h3 className="mb-3 font-medium">Задачи шаблона</h3>
            <div className="mb-4 grid gap-3">
              {tasks.map((task, index) => (
                <div key={index} className="bg-muted flex items-start gap-2 rounded-lg p-3">
                  <GripVertical className="text-muted-foreground mt-1 size-4" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{task.title}</p>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-6"
                        onClick={() => removeTask(index)}
                      >
                        <Trash2 className="size-3" />
                      </Button>
                    </div>
                    <p className="text-muted-foreground text-xs">{task.description}</p>
                    <div className="mt-1 flex gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {TASK_CATEGORY_MAP[task.category] || task.category}
                      </Badge>
                      <span className="text-muted-foreground text-xs">{task.due_days} дн.</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-4 gap-2">
              <Input
                placeholder="Название задачи"
                value={newTask.name}
                onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                className="col-span-2"
              />
              <Select
                value={newTask.category}
                onChange={(e) => setNewTask({ ...newTask, category: e.target.value })}
                options={TASK_CATEGORIES}
              />
              <div className="flex gap-1">
                <Input
                  type="number"
                  min={1}
                  placeholder="Дней"
                  value={newTask.deadline_days}
                  onChange={(e) =>
                    setNewTask({
                      ...newTask,
                      deadline_days: parseInt(e.target.value) || 1,
                    })
                  }
                  className="w-16"
                />
                <Button size="sm" onClick={addTask}>
                  +
                </Button>
              </div>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            Отмена
          </Button>
          <Button onClick={onSubmit} disabled={!formData.name}>
            {isCreate ? "Создать" : "Сохранить"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
