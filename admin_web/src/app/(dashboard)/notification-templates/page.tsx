"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { PageContent } from "@/components/layout/page-content";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { DataTable } from "@/components/ui/data-table";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { TableActions, buildEditAction, buildDeleteAction, buildCopyAction } from "@/components/shared";
import { Select } from "@/components/ui/select";
import { useNotificationTemplates, useDeleteNotificationTemplate } from "@/hooks/use-notification-templates";
import { useConfirm } from "@/hooks/use-confirm";
import { useToast } from "@/hooks/use-toast";
import { NotificationTemplateFormDialog } from "@/components/features/notification-templates/notification-template-form-dialog";
import type { NotificationTemplate } from "@/types/notification";

const CHANNEL_OPTIONS = [
  { value: "", label: "All Channels" },
  { value: "email", label: "Email" },
  { value: "telegram", label: "Telegram" },
  { value: "sms", label: "SMS" },
];

const LANGUAGE_OPTIONS = [
  { value: "", label: "All Languages" },
  { value: "en", label: "English" },
  { value: "ru", label: "Russian" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "true", label: "Active" },
  { value: "false", label: "Inactive" },
];

export default function NotificationTemplatesPage() {
  const t = useTranslations("notificationTemplates");
  const tCommon = useTranslations("common");
  const confirm = useConfirm();
  const toast = useToast();

  const [search, setSearch] = useState("");
  const [channel, setChannel] = useState("");
  const [language, setLanguage] = useState("");
  const [isActive, setIsActive] = useState<string>("");
  const [page, setPage] = useState(0);
  const [pageSize] = useState(20);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);

  const { data: templatesData, isLoading } = useNotificationTemplates({
    skip: page * pageSize,
    limit: pageSize,
    name: search || undefined,
    channel: channel || undefined,
    language: language || undefined,
    is_active: isActive ? isActive === "true" : undefined,
  });

  const templates = templatesData?.templates || [];
  const totalCount = templatesData?.total || 0;
  const totalPages = templatesData?.pages || 1;

  const deleteMutation = useDeleteNotificationTemplate();

  const handleDelete = async (template: NotificationTemplate) => {
    const confirmed = await confirm({
      title: tCommon("deleteTitle"),
      message: t("confirmDelete", { name: template.name }),
    });

    if (confirmed) {
      deleteMutation.mutate(template.id, {
        onSuccess: () => {
          toast(tCommon("successfullyDeleted"), "success");
        },
        onError: () => {
          toast(t("deleteError"), "error");
        },
      });
    }
  };

  const handleEdit = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    setDialogOpen(true);
  };

  const handleClone = (template: NotificationTemplate) => {
    // Create a copy of the template with a modified name for creating a new template
    const clonedTemplate: NotificationTemplate = {
      ...template,
      name: `${template.name} (copy)`,
      id: 0, // Will be set by backend on create
      version: 1,
      is_active: true,
      is_default: false,
      created_at: "",
      updated_at: "",
      created_by: null,
    };
    setEditingTemplate(clonedTemplate);
    setDialogOpen(true);
  };

  const handleCreate = () => {
    setEditingTemplate(null);
    setDialogOpen(true);
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    setPage(0);
  };

  const handleFilterChange = () => {
    setPage(0);
  };

  const resetFilters = () => {
    setSearch("");
    setChannel("");
    setLanguage("");
    setIsActive("");
    setPage(0);
  };

  return (
    <>
      <PageContent
        title={t("title")}
        subtitle={t("subtitle")}
        actions={
          <Button onClick={handleCreate}>
            <Plus className="mr-2 size-4" />
            {t("addTemplate")}
          </Button>
        }
      >
        <DataTable
          loading={isLoading}
          empty={!isLoading && totalCount === 0}
          currentPage={page + 1}
          totalPages={totalPages || 1}
          totalCount={totalCount}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p - 1)}
          header={
            <div className="flex flex-wrap gap-4 p-4">
              <div className="flex-1 min-w-[200px]">
                <input
                  type="text"
                  placeholder={t("searchPlaceholder")}
                  value={search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full h-9 px-3 rounded-md border border-input bg-transparent text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>
              <Select
                options={CHANNEL_OPTIONS}
                value={channel}
                onChange={(v) => {
                  setChannel(v);
                  handleFilterChange();
                }}
              />
              <Select
                options={LANGUAGE_OPTIONS}
                value={language}
                onChange={(v) => {
                  setLanguage(v);
                  handleFilterChange();
                }}
              />
              <Select
                options={STATUS_OPTIONS}
                value={isActive}
                onChange={(v) => {
                  setIsActive(v);
                  handleFilterChange();
                }}
              />
              {(search || channel || language || isActive) && (
                <Button variant="outline" onClick={resetFilters}>
                  {tCommon("reset")}
                </Button>
              )}
            </div>
          }
        >
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("name")}</TableHead>
                <TableHead>{t("channel")}</TableHead>
                <TableHead>{t("language")}</TableHead>
                <TableHead>{t("subject")}</TableHead>
                <TableHead>{t("variables")}</TableHead>
                <TableHead>{t("status")}</TableHead>
                <TableHead>{t("version")}</TableHead>
                <TableHead>{tCommon("actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {templates?.map((template) => (
                <TableRow key={template.id}>
                  <TableCell className="font-medium">{template.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{template.channel}</Badge>
                  </TableCell>
                  <TableCell>{template.language}</TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {template.subject || "-"}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {template.variables.length > 0 ? (
                        template.variables.slice(0, 3).map((v) => (
                          <Badge key={v} variant="secondary" className="text-xs">
                            {v}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-muted-foreground text-sm">-</span>
                      )}
                      {template.variables.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{template.variables.length - 3}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={template.is_active ? "default" : "secondary"}>
                      {template.is_active ? t("active") : t("inactive")}
                    </Badge>
                    {template.is_default && (
                      <Badge variant="outline" className="ml-1">
                        {t("default")}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>{template.version}</TableCell>
                  <TableCell>
                    <TableActions
                      actions={[
                        buildEditAction(() => handleEdit(template)),
                        buildCopyAction(() => handleClone(template)),
                        buildDeleteAction(() => handleDelete(template), deleteMutation.isPending),
                      ]}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DataTable>
      </PageContent>
      <NotificationTemplateFormDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        template={editingTemplate}
      />
    </>
  );
}
