"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "@/shared/hooks/use-translations";
import { useToast } from "@/shared/hooks/use-toast";
import { tagsApi, type Tag } from "@/shared/lib/api/tags";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { SearchInput } from "@/shared/ui/search-input";
import { ConfirmDialog } from "@/shared/ui/confirm-dialog";
import { FormDialog } from "@/shared/ui/form-dialog";
import { Hash, Plus, Pencil, Trash2 } from "lucide-react";

interface TagFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tag: Tag | null;
  onSaved: () => void;
}

function TagFormDialog({ open, onOpenChange, tag, onSaved }: TagFormDialogProps) {
  const t = useTranslations();
  const { toast } = useToast();
  const qc = useQueryClient();
  const [name, setName] = useState(tag?.name ?? "");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const trimmedName = name.trim();
      if (!trimmedName) {
        return;
      }

      const result = tag
        ? await tagsApi.update(tag.id, { name: trimmedName })
        : await tagsApi.create({ name: trimmedName });

      if (!result.success) {
        toast(result.error.message || t("common.error") || "Error", "error");
        return;
      }

      toast(
        tag
          ? t("knowledge.tagUpdated") || "Tag updated"
          : t("knowledge.tagCreated") || "Tag created",
        "success",
      );
      qc.invalidateQueries({ queryKey: ["tags"] });
      onSaved();
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
      title={tag ? t("knowledge.editTag") || "Edit tag" : t("knowledge.addTag") || "Add tag"}
      isSubmitting={loading}
      canSubmit={!!name.trim()}
      onSubmit={handleSubmit}
      onCancel={() => onOpenChange(false)}
    >
      <div className="space-y-3">
        <div className="space-y-1.5">
          <Label>{t("common.name")}</Label>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("knowledge.tagName") || "Tag name"}
            required
            autoFocus
          />
        </div>
      </div>
    </FormDialog>
  );
}

export function TagsSection() {
  const t = useTranslations();
  const { toast } = useToast();
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["tags", { search }],
    queryFn: () => tagsApi.list({ search: search || undefined, limit: 100 }),
    staleTime: 30000,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => tagsApi.delete(id),
    onSuccess: () => {
      toast(t("knowledge.tagDeleted") || "Tag deleted", "success");
      qc.invalidateQueries({ queryKey: ["tags"] });
    },
    onError: () => {
      toast(t("common.error") || "Error", "error");
    },
  });

  const tags = data?.success ? data.data : [];

  const openCreate = () => {
    setEditingTag(null);
    setDialogOpen(true);
  };

  const openEdit = (tag: Tag) => {
    setEditingTag(tag);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <SearchInput value={search} onChange={setSearch} placeholder={t("common.search")} />
          <span className="text-sm text-muted-foreground">
            {tags.length} {t("knowledge.tags") || "tags"}
          </span>
        </div>
        <Button className="gap-2" onClick={openCreate}>
          <Plus className="size-4" />
          {t("knowledge.addTag") || "Add tag"}
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="py-8 text-center">
            <div className="text-sm text-muted-foreground">{t("common.loading")}</div>
          </CardContent>
        </Card>
      ) : tags.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Hash className="mx-auto mb-3 size-10 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">{t("common.noData")}</p>
            <Button className="mt-4 gap-2" variant="outline" onClick={openCreate}>
              <Plus className="size-4" />
              {t("knowledge.addTag") || "Add first tag"}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">{t("knowledge.tags") || "Tags"}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag: Tag) => (
                <div
                  key={tag.id}
                  className="group flex items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-sm transition-all hover:border-gray-400"
                >
                  <Hash className="size-3.5 text-muted-foreground" />
                  <span className="font-medium">{tag.name}</span>
                  {tag.article_count !== undefined && (
                    <span className="ml-1 text-xs text-muted-foreground">
                      ({tag.article_count})
                    </span>
                  )}
                  <div className="ml-1 flex items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                      onClick={() => openEdit(tag)}
                      className="rounded p-0.5 text-muted-foreground hover:text-primary"
                    >
                      <Pencil className="size-3" />
                    </button>
                    <button
                      onClick={() => setDeletingId(tag.id)}
                      className="rounded p-0.5 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="size-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <TagFormDialog
        key={`${dialogOpen ? "open" : "closed"}-${editingTag?.id ?? "create"}`}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        tag={editingTag}
        onSaved={() => setEditingTag(null)}
      />

      <ConfirmDialog
        open={deletingId !== null}
        onOpenChange={(open) => !open && setDeletingId(null)}
        onConfirm={() => {
          if (deletingId !== null) {
            deleteMutation.mutate(deletingId);
            setDeletingId(null);
          }
        }}
        title={t("knowledge.deleteTag") || "Delete tag"}
        description={t("knowledge.deleteTagConfirm") || "Are you sure you want to delete this tag?"}
      />
    </div>
  );
}
