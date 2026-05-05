"use client";

import { useState } from "react";
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
  FileText,
  Link2,
  FileIcon,
  Image,
  Video,
  Plus,
  Trash2,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/shared/lib/utils";

const MATERIAL_TYPE_ICONS: Record<string, React.ReactNode> = {
  PDF: <FileText className="size-4 text-red-500" />,
  LINK: <Link2 className="size-4 text-blue-500" />,
  DOC: <FileIcon className="size-4 text-blue-700" />,
  IMAGE: <Image className="size-4 text-emerald-500" />,
  VIDEO: <Video className="size-4 text-purple-500" />,
};

const MATERIAL_TYPE_OPTIONS = [
  { value: "LINK", label: "Link" },
  { value: "PDF", label: "PDF" },
  { value: "DOC", label: "Document" },
  { value: "IMAGE", label: "Image" },
  { value: "VIDEO", label: "Video" },
];

interface AddMaterialDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  meetingId: number;
}

function AddMaterialDialog({ open, onOpenChange, meetingId }: AddMaterialDialogProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const qc = useQueryClient();
  const [form, setForm] = useState({ title: "", url: "", type: "LINK", description: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await meetingsApi.addMaterial(meetingId, {
        title: form.title,
        url: form.url,
        type: form.type,
        description: form.description || null,
      });
      toast(t("meetings.materialAdded") || "Material added", "success");
      qc.invalidateQueries({ queryKey: ["meeting-materials", meetingId] });
      setForm({ title: "", url: "", type: "LINK", description: "" });
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
      title={t("meetings.addMaterial") || "Add material"}
      isSubmitting={loading}
      onSubmit={handleSubmit}
      onCancel={() => onOpenChange(false)}
    >
      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("common.name")}</Label>
          <Input
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            placeholder={t("meetings.materialTitle") || "Material title"}
            required
            autoFocus
          />
        </div>
        <div className="space-y-1.5">
          <Label>URL</Label>
          <Input
            value={form.url}
            onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))}
            placeholder="https://..."
            required
            type="url"
          />
        </div>
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
              className="group flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm"
            >
              {MATERIAL_TYPE_ICONS[m.type] ?? <FileIcon className="size-4 text-muted-foreground" />}
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{m.title}</p>
                {m.description && (
                  <p className="text-muted-foreground truncate text-xs">{m.description}</p>
                )}
              </div>
              <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                <a
                  href={m.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground rounded p-1 hover:text-foreground"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="size-3.5" />
                </a>
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

      <AddMaterialDialog open={addOpen} onOpenChange={setAddOpen} meetingId={meetingId} />

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
