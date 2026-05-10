"use client";

import { useState } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { DataTable } from "@/shared/ui/data-table";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/shared/ui/table";
import { Badge } from "@/shared/ui/badge";
import {
  TableActions,
  buildEditAction,
  buildDeleteAction,
  buildCopyAction,
} from "@/shared/components";
import { Select } from "@/shared/ui/select";
import { SearchInput } from "@/shared/ui/search-input";
import { CardHeader, CardTitle, Card, CardContent } from "@/shared/ui/card";
import {
  useNotificationTemplates,
  useDeleteNotificationTemplate,
} from "@/shared/hooks/use-notification-templates";
import { useConfirm } from "@/shared/hooks/use-confirm";
import { useToast } from "@/shared/hooks/use-toast";
import type { NotificationTemplate } from "@/shared/types/notification";

interface NotificationTemplatesTabProps {
  onCreate?: () => void;
  onEdit?: (template: NotificationTemplate) => void;
}

function TemplateCard({
  template,
  onEdit,
  onClone,
  onDelete,
}: {
  template: NotificationTemplate;
  onEdit: (t: NotificationTemplate) => void;
  onClone: (t: NotificationTemplate) => void;
  onDelete: (t: NotificationTemplate) => void;
}) {
  const t = useTranslations("notificationTemplates");
  const tCommon = useTranslations("common");

  return (
    <Card>
      <CardContent className="p-4">
        <div className="mb-2 flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-semibold">{template.name}</p>
            {template.subject && (
              <p className="mt-0.5 truncate text-xs text-muted-foreground">{template.subject}</p>
            )}
          </div>
          <div className="flex shrink-0 flex-col items-end gap-1">
            <Badge variant={template.is_active ? "default" : "secondary"}>
              {template.is_active ? t("active") : t("inactive")}
            </Badge>
            {template.is_default && <Badge variant="outline">{t("default")}</Badge>}
          </div>
        </div>

        <div className="mb-3 flex flex-wrap gap-1.5 text-xs">
          <Badge variant="outline">{template.channel}</Badge>
          <span className="text-muted-foreground">{template.language}</span>
          <span className="text-muted-foreground">
            {t("version")} {template.version}
          </span>
          {template.variables.length > 0 && (
            <span className="text-muted-foreground">
              {template.variables.length} {t("variables")}
            </span>
          )}
        </div>

        <div className="flex items-center justify-end border-t pt-2">
          <TableActions
            actions={[
              buildEditAction(() => onEdit(template), tCommon("edit")),
              buildCopyAction(() => onClone(template), tCommon("copy")),
              buildDeleteAction(() => onDelete(template), tCommon("delete")),
            ]}
          />
        </div>
      </CardContent>
    </Card>
  );
}

export function NotificationTemplatesTab({ onCreate, onEdit }: NotificationTemplatesTabProps) {
  const t = useTranslations("notificationTemplates");
  const tCommon = useTranslations("common");

  const CHANNEL_OPTIONS = [
    { value: "", label: t("allChannels") },
    { value: "email", label: "Email" },
    { value: "telegram", label: "Telegram" },
    { value: "sms", label: "SMS" },
  ];

  const LANGUAGE_OPTIONS = [
    { value: "", label: t("allLanguages") },
    { value: "en", label: "English" },
    { value: "ru", label: "Russian" },
  ];

  const STATUS_OPTIONS = [
    { value: "", label: t("allStatuses") },
    { value: "true", label: t("active") },
    { value: "false", label: t("inactive") },
  ];
  const confirm = useConfirm();
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [channel, setChannel] = useState("");
  const [language, setLanguage] = useState("");
  const [isActive, setIsActive] = useState<string>("");
  const [page, setPage] = useState(0);
  const [pageSize] = useState(20);

  const { data: templatesData, isLoading } = useNotificationTemplates({
    skip: page * pageSize,
    limit: pageSize,
    name: search || undefined,
    channel: channel || undefined,
    language: language || undefined,
    is_active: isActive ? isActive === "true" : undefined,
  });

  const templates =
    templatesData?.success && templatesData.data ? templatesData.data.templates || [] : [];
  const totalCount =
    templatesData?.success && templatesData.data ? templatesData.data.total || 0 : 0;
  const totalPages =
    templatesData?.success && templatesData.data ? templatesData.data.pages || 1 : 1;

  const deleteMutation = useDeleteNotificationTemplate();

  const handleDelete = async (template: NotificationTemplate) => {
    const confirmed = await confirm({
      title: tCommon("deleteTitle"),
      description: t("confirmDelete", { name: template.name }),
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

  const handleClone = (template: NotificationTemplate) => {
    const clonedTemplate: NotificationTemplate = {
      ...template,
      name: `${template.name} (copy)`,
      id: 0,
      version: 1,
      is_active: true,
      is_default: false,
      created_at: "",
      updated_at: "",
      created_by: null,
    };
    if (onEdit) {
      onEdit(clonedTemplate);
    }
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

  const hasFilter = !!(search || channel || language || isActive);

  const mobileView = (
    <div className="space-y-3 p-4">
      {templates.map((template: NotificationTemplate) => (
        <TemplateCard
          key={template.id}
          template={template}
          onEdit={(tpl) => onEdit?.(tpl)}
          onClone={handleClone}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );

  return (
    <>
      <DataTable
        loading={isLoading}
        empty={!isLoading && totalCount === 0}
        currentPage={page + 1}
        totalPages={totalPages || 1}
        totalCount={totalCount}
        pageSize={pageSize}
        onPageChange={(p) => setPage(p - 1)}
        mobileView={mobileView}
        header={
          <CardHeader>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
                {t("title")}{" "}
                <span className="text-sm font-normal text-muted-foreground">({totalCount})</span>
              </CardTitle>
              <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center">
                <SearchInput
                  placeholder={t("searchPlaceholder")}
                  value={search}
                  onChange={handleSearch}
                  className="w-full sm:w-64"
                />
                <Select
                  options={CHANNEL_OPTIONS}
                  value={channel}
                  onChange={(v) => {
                    setChannel(v);
                    handleFilterChange();
                  }}
                  className="w-full sm:w-auto"
                />
                <Select
                  options={LANGUAGE_OPTIONS}
                  value={language}
                  onChange={(v) => {
                    setLanguage(v);
                    handleFilterChange();
                  }}
                  className="w-full sm:w-auto"
                />
                <Select
                  options={STATUS_OPTIONS}
                  value={isActive}
                  onChange={(v) => {
                    setIsActive(v);
                    handleFilterChange();
                  }}
                  className="w-full sm:w-auto"
                />
                {hasFilter && (
                  <Button variant="outline" onClick={resetFilters} className="w-full sm:w-auto">
                    {tCommon("reset")}
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
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
            {templates?.map((template: NotificationTemplate) => (
              <TableRow key={template.id}>
                <TableCell className="font-medium">{template.name}</TableCell>
                <TableCell>
                  <Badge variant="outline">{template.channel}</Badge>
                </TableCell>
                <TableCell>{template.language}</TableCell>
                <TableCell className="max-w-[200px] truncate">{template.subject || "-"}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {template.variables.length > 0 ? (
                      template.variables.slice(0, 3).map((v: string) => (
                        <Badge key={v} variant="secondary" className="text-xs">
                          {v}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
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
                      buildEditAction(() => onEdit?.(template), tCommon("edit")),
                      buildCopyAction(() => handleClone(template), tCommon("copy")),
                      buildDeleteAction(
                        () => handleDelete(template),
                        tCommon("delete"),
                        deleteMutation.isPending,
                      ),
                    ]}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </>
  );
}
