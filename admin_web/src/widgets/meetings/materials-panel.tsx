"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useToast } from "@/shared/hooks/use-toast";
import { meetingsApi, type MeetingMaterial } from "@/shared/lib/api/meetings";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Select } from "@/shared/ui/select";
import { FormDialog } from "@/shared/ui/form-dialog";
import { ConfirmDialog } from "@/shared/ui/confirm-dialog";
import {
  File,
  FileText,
  Link2,
  Plus,
  Trash2,
  ExternalLink,
  Edit3,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { MaterialFileManager } from "./material-file-manager";

const MATERIAL_TYPE_ICONS: Record<string, React.ReactNode> = {
  FILE: <File className="size-4 text-blue-500" />,
  NOTE: <FileText className="size-4 text-emerald-500" />,
  URL: <Link2 className="size-4 text-purple-500" />,
};

const MATERIAL_TYPE_OPTIONS = [
  { value: "FILE", label: "File" },
  { value: "NOTE", label: "Note" },
  { value: "URL", label: "URL" },
];

interface AddMaterialDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  meetingId: number;
  editingMaterial?: MeetingMaterial | null;
}

function AddMaterialDialog({ open, onOpenChange, meetingId, editingMaterial }: AddMaterialDialogProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const qc = useQueryClient();
  const [form, setForm] = useState({ title: "", url: "", type: "URL", description: "", content: "" });
  const [errors, setErrors] = useState<{ title?: string; url?: string; content?: string }>({});
  const [loading, setLoading] = useState(false);

  // Reset form when dialog opens/closes or editing material changes
  useEffect(() => {
    if (editingMaterial) {
      setForm({
        title: editingMaterial.title,
        url: editingMaterial.url || "",
        type: editingMaterial.type,
        description: editingMaterial.description || "",
        content: editingMaterial.content || "",
      });
    } else if (!open) {
      setForm({ title: "", url: "", type: "URL", description: "", content: "" });
    }
  }, [open, editingMaterial]);

  const validateUrl = (url: string): string | undefined => {
    if (!url.trim()) {
      return t("meetings.urlRequired") || "URL is required";
    }
    try {
      new URL(url);
    } catch {
      return t("meetings.invalidUrl") || "URL must be valid (e.g., https://example.com)";
    }
    return undefined;
  };

  const validateContent = (content: string): string | undefined => {
    if (form.type === "NOTE" && !content.trim()) {
      return t("meetings.contentRequired") || "Content is required for notes";
    }
    return undefined;
  };

  const handleSubmit = async () => {
    const newErrors: { title?: string; url?: string; content?: string } = {};
    if (!form.title.trim()) {
      newErrors.title = t("meetings.materialTitleRequired") || "Title is required";
    }
    
    if (form.type === "URL") {
      const urlError = validateUrl(form.url);
      if (urlError) {
        newErrors.url = urlError;
      }
    }
    
    if (form.type === "FILE" && !form.url.trim()) {
      newErrors.url = t("meetings.fileRequired") || "File is required";
    }
    
    if (form.type === "NOTE") {
      const contentError = validateContent(form.content);
      if (contentError) {
        newErrors.content = contentError;
      }
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setLoading(true);
    try {
      if (editingMaterial) {
        await meetingsApi.updateMaterial(editingMaterial.id, {
          title: form.title,
          url: (form.type === "URL" || form.type === "FILE") ? form.url : null,
          content: form.type === "NOTE" ? form.content : null,
          type: form.type,
          description: form.description || null,
        });
        toast(t("meetings.materialUpdated") || "Material updated", "success");
      } else {
        await meetingsApi.addMaterial(meetingId, {
          title: form.title,
          url: (form.type === "URL" || form.type === "FILE") ? form.url : null,
          content: form.type === "NOTE" ? form.content : null,
          type: form.type,
          description: form.description || null,
        });
        toast(t("meetings.materialAdded") || "Material added", "success");
      }
      qc.invalidateQueries({ queryKey: ["meeting-materials", meetingId] });
      setForm({ title: "", url: "", type: "URL", description: "", content: "" });
      onOpenChange(false);
    } catch {
      toast(t("common.error") || "Error", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={editingMaterial ? (t("meetings.editMaterial") || "Edit material") : (t("meetings.addMaterial") || "Add material")}
      isSubmitting={loading}
      canSubmit={Object.keys(errors).length === 0}
      onSubmit={handleSubmit}
      onCancel={() => onOpenChange(false)}
    >
      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("common.name")}</Label>
          <Input
            value={form.title}
            onChange={(e) => {
              setForm((f) => ({ ...f, title: e.target.value }));
              if (errors.title) setErrors((e) => ({ ...e, title: undefined }));
            }}
            placeholder={t("meetings.materialTitle") || "Material title"}
            required
            autoFocus
            className={errors.title ? "border-red-500" : ""}
          />
          {errors.title && <p className="text-red-500 text-xs">{errors.title}</p>}
        </div>
        {form.type === "FILE" && (
          <div className="space-y-1.5">
            <Label>{t("meetings.file") || "File"}</Label>
            <MaterialFileManager url={form.url} onUrlChange={(url) => setForm((f) => ({ ...f, url }))} disabled={loading} />
          </div>
        )}
        {form.type === "URL" && (
          <div className="space-y-1.5">
            <Label>URL</Label>
            <Input
              value={form.url}
              onChange={(e) => {
                setForm((f) => ({ ...f, url: e.target.value }));
                if (errors.url) setErrors((e) => ({ ...e, url: undefined }));
              }}
              onBlur={() => {
                const error = validateUrl(form.url);
                setErrors((e) => ({ ...e, url: error }));
              }}
              placeholder="https://..."
              required
              type="url"
              className={errors.url ? "border-red-500" : ""}
            />
            {errors.url && <p className="text-red-500 text-xs">{errors.url}</p>}
          </div>
        )}
        {form.type === "NOTE" && (
          <div className="space-y-1.5">
            <Label>{t("meetings.content") || "Content"}</Label>
            <textarea
              value={form.content}
              onChange={(e) => {
                setForm((f) => ({ ...f, content: e.target.value }));
                if (errors.content) setErrors((e) => ({ ...e, content: undefined }));
              }}
              onBlur={() => {
                const error = validateContent(form.content);
                setErrors((e) => ({ ...e, content: error }));
              }}
              placeholder={t("meetings.noteContent") || "Enter note content..."}
              required
              className={cn(
                "flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
                errors.content ? "border-red-500" : ""
              )}
            />
            {errors.content && <p className="text-red-500 text-xs">{errors.content}</p>}
          </div>
        )}
        <div className="space-y-1.5">
          <Label>{t("meetings.materialType") || "Type"}</Label>
          <Select
            value={form.type}
            onChange={(v) => setForm((f) => ({ ...f, type: v }))}
            options={MATERIAL_TYPE_OPTIONS}
          />
        </div>
        <div className="space-y-1.5">
          <Label>{t("common.description") || "Description"}</Label>
          <Input
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            placeholder={t("common.optional") || "Optional"}
          />
        </div>
      </div>
    </FormDialog>
  );
}

interface MaterialsPanelProps {
  meetingId: number;
  className?: string;
}

export function MaterialsPanel({ meetingId, className }: MaterialsPanelProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const qc = useQueryClient();
  const [addOpen, setAddOpen] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState<MeetingMaterial | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["meeting-materials", meetingId],
    queryFn: () => meetingsApi.getMaterials(meetingId),
    staleTime: 30000,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => meetingsApi.deleteMaterial(id),
    onSuccess: () => {
      toast(t("meetings.materialDeleted") || "Material deleted", "success");
      qc.invalidateQueries({ queryKey: ["meeting-materials", meetingId] });
    },
    onError: () => {
      toast(t("common.error") || "Error", "error");
    },
  });

  const materials: MeetingMaterial[] = data?.success ? (data.data as MeetingMaterial[]) ?? [] : [];

  const handleEdit = (material: MeetingMaterial) => {
    setEditingMaterial(material);
    setAddOpen(true);
  };

  const handleCloseDialog = () => {
    setAddOpen(false);
    setEditingMaterial(null);
  };

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">{t("meetings.materials") || "Materials"}</p>
        <Button size="sm" variant="outline" className="gap-1.5 h-7 text-xs" onClick={() => setAddOpen(true)}>
          <Plus className="size-3" />
          {t("meetings.addMaterial") || "Add"}
        </Button>
      </div>

      {isLoading ? (
        <div className="text-muted-foreground text-xs">{t("common.loading")}</div>
      ) : materials.length === 0 ? (
        <div className="text-muted-foreground rounded-lg border border-dashed p-4 text-center text-xs">
          {t("meetings.noMaterials") || "No materials yet"}
        </div>
      ) : (
        <div className="space-y-1.5">
          {materials.map((m) => (
            <div
              key={m.id}
              className="group flex items-start gap-2 rounded-lg border bg-card px-3 py-2 text-sm"
            >
              {MATERIAL_TYPE_ICONS[m.type] ?? <File className="size-4 text-muted-foreground" />}
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{m.title}</p>
                {m.description && (
                  <p className="text-muted-foreground truncate text-xs">{m.description}</p>
                )}
                {m.type === "NOTE" && m.content && (
                  <p className="text-muted-foreground mt-1 line-clamp-2 text-xs">{m.content}</p>
                )}
                {(m.type === "URL" || m.type === "FILE") && m.url && (
                  <p className="text-muted-foreground mt-1 truncate text-xs">{m.url}</p>
                )}
              </div>
              <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  onClick={() => handleEdit(m)}
                  className="rounded p-1 text-muted-foreground hover:text-foreground"
                  title={t("meetings.editMaterial") || "Edit material"}
                >
                  <Edit3 className="size-3.5" />
                </button>
                {(m.type === "URL" || m.type === "FILE") && m.url && (
                  <a
                    href={m.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground rounded p-1 hover:text-foreground"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="size-3.5" />
                  </a>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeletingId(m.id);
                  }}
                  className="rounded p-1 text-red-400 hover:text-red-600"
                >
                  <Trash2 className="size-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <AddMaterialDialog open={addOpen} onOpenChange={handleCloseDialog} meetingId={meetingId} editingMaterial={editingMaterial} />

      <ConfirmDialog
        open={deletingId !== null}
        onOpenChange={(open) => !open && setDeletingId(null)}
        onConfirm={() => {
          if (deletingId !== null) {
            deleteMutation.mutate(deletingId);
            setDeletingId(null);
          }
        }}
        title={t("meetings.deleteMaterial") || "Delete material"}
        description={t("meetings.deleteMaterialConfirm") || "Are you sure you want to delete this material?"}
      />
    </div>
  );
}
