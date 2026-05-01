"use client";

/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useCreateNotificationTemplate, useUpdateNotificationTemplate, usePreviewNotificationTemplate } from "@/hooks/use-notification-templates";
import { useToast } from "@/hooks/use-toast";
import type { NotificationTemplate, NotificationTemplateCreate, NotificationTemplateUpdate } from "@/types/notification";
import { X, Eye } from "lucide-react";

interface NotificationTemplateFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  template?: NotificationTemplate | null;
}

const CHANNEL_OPTIONS = [
  { value: "email", label: "Email" },
  { value: "telegram", label: "Telegram" },
  { value: "sms", label: "SMS" },
];

const LANGUAGE_OPTIONS = [
  { value: "en", label: "English" },
  { value: "ru", label: "Russian" },
];

export function NotificationTemplateFormDialog({ open, onOpenChange, template }: NotificationTemplateFormDialogProps) {
  const t = useTranslations("notificationTemplates");
  const tCommon = useTranslations("common");
  const { toast } = useToast();
  const createMutation = useCreateNotificationTemplate();
  const updateMutation = useUpdateNotificationTemplate();
  const previewMutation = usePreviewNotificationTemplate();

  const [name, setName] = useState("");
  const [channel, setChannel] = useState<string>("email");
  const [language, setLanguage] = useState("en");
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [bodyText, setBodyText] = useState("");
  const [variables, setVariables] = useState<string[]>([]);
  const [variableInput, setVariableInput] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [previewData, setPreviewData] = useState<{ subject: string | null; body: string } | null>(null);

  const isEdit = !!template && template.id > 0;
  const isClone = !!template && template.id === 0;

  useEffect(() => {
    if (template) {
      setName(template.name);
      setChannel(template.channel);
      setLanguage(template.language);
      setSubject(template.subject || "");
      setBodyHtml(template.body_html || "");
      setBodyText(template.body_text || "");
      setVariables(template.variables || []);
      setIsActive(template.is_active);
    } else {
      resetForm();
    }
  }, [template, open]);

  const resetForm = () => {
    setName("");
    setChannel("email");
    setLanguage("en");
    setSubject("");
    setBodyHtml("");
    setBodyText("");
    setVariables([]);
    setVariableInput("");
    setIsActive(true);
  };

  const handleAddVariable = () => {
    if (variableInput.trim() && !variables.includes(variableInput.trim())) {
      setVariables([...variables, variableInput.trim()]);
      setVariableInput("");
    }
  };

  const handleRemoveVariable = (variable: string) => {
    setVariables(variables.filter((v) => v !== variable));
  };

  const handlePreview = () => {
    if (!bodyText.trim() && !bodyHtml.trim()) {
      toast(t("bodyRequired"), "error");
      return;
    }

    previewMutation.mutate(
      {
        body_text: bodyText.trim() || null,
        body_html: bodyHtml.trim() || null,
        subject: subject.trim() || null,
        variables: variables.reduce((acc, v) => ({ ...acc, [v]: `{${v}}` }), {} as Record<string, string>),
      },
      {
        onSuccess: (data) => {
          if (data.success && data.data) {
            setPreviewData({ subject: data.data.subject, body: data.data.body });
          }
        },
        onError: () => {
          toast(t("previewError"), "error");
        },
      }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast(t("nameRequired"), "error");
      return;
    }

    if (!bodyText.trim() && !bodyHtml.trim()) {
      toast(t("bodyRequired"), "error");
      return;
    }

    const data: NotificationTemplateCreate = {
      name: name.trim(),
      channel,
      language,
      subject: subject.trim() || null,
      body_html: bodyHtml.trim() || null,
      body_text: bodyText.trim() || null,
      variables,
    };

    if (isEdit && template) {
      const updateData: NotificationTemplateUpdate = {
        subject: subject.trim() || null,
        body_html: bodyHtml.trim() || null,
        body_text: bodyText.trim() || null,
        variables,
        is_active: isActive,
      };

      updateMutation.mutate(
        { id: template.id, data: updateData },
        {
          onSuccess: () => {
            toast(tCommon("successfullyUpdated"), "success");
            onOpenChange(false);
          },
          onError: () => {
            toast(t("updateError"), "error");
          },
        }
      );
    } else {
      createMutation.mutate(data, {
        onSuccess: () => {
          toast(tCommon("successfullyCreated"), "success");
          onOpenChange(false);
          resetForm();
        },
        onError: () => {
          toast(t("createError"), "error");
        },
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? t("editTemplate") : isClone ? t("cloneTemplate") : t("createTemplate")}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">{t("name")} *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("namePlaceholder")}
              disabled={isEdit && !isClone}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="channel">{t("channel")} *</Label>
              <Select
                options={CHANNEL_OPTIONS}
                value={channel}
                onChange={(v) => setChannel(v)}
                disabled={isEdit && !isClone}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="language">{t("language")} *</Label>
              <Select
                options={LANGUAGE_OPTIONS}
                value={language}
                onChange={setLanguage}
                disabled={isEdit && !isClone}
              />
            </div>
          </div>

          {channel === "email" && (
            <div className="space-y-2">
              <Label htmlFor="subject">{t("subject")}</Label>
              <Input
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder={t("subjectPlaceholder")}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="bodyText">{t("bodyText")}</Label>
            <Textarea
              id="bodyText"
              value={bodyText}
              onChange={(e) => setBodyText(e.target.value)}
              placeholder={t("bodyTextPlaceholder")}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="bodyHtml">{t("bodyHtml")}</Label>
            <Textarea
              id="bodyHtml"
              value={bodyHtml}
              onChange={(e) => setBodyHtml(e.target.value)}
              placeholder={t("bodyHtmlPlaceholder")}
              rows={6}
            />
          </div>

          <div className="space-y-2">
            <Label>{t("variables")}</Label>
            <div className="flex gap-2">
              <Input
                value={variableInput}
                onChange={(e) => setVariableInput(e.target.value)}
                placeholder={t("variablePlaceholder")}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddVariable();
                  }
                }}
              />
              <Button type="button" onClick={handleAddVariable} variant="outline">
                {t("addVariable")}
              </Button>
            </div>
            {variables.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {variables.map((variable) => (
                  <Badge key={variable} variant="secondary" className="gap-1">
                    {variable}
                    <button
                      type="button"
                      onClick={() => handleRemoveVariable(variable)}
                      className="hover:text-destructive ml-1"
                    >
                      <X className="size-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {isEdit && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="isActive"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className="h-4 w-4"
              />
              <Label htmlFor="isActive" className="cursor-pointer">
                {t("active")}
              </Label>
            </div>
          )}

          {previewData && (
            <div className="space-y-2 rounded-md border p-4">
              <div className="flex items-center justify-between">
                <Label className="font-semibold">{t("previewResult")}</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setPreviewData(null)}
                >
                  <X className="size-4" />
                </Button>
              </div>
              {previewData.subject && (
                <div className="space-y-1">
                  <Label className="text-muted-foreground text-xs">{t("subject")}:</Label>
                  <div className="bg-muted rounded p-2 text-sm">{previewData.subject}</div>
                </div>
              )}
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">{t("body")}:</Label>
                <div className="bg-muted rounded p-2 text-sm whitespace-pre-wrap">{previewData.body}</div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handlePreview}
              disabled={previewMutation.isPending}
            >
              <Eye className="mr-2 size-4" />
              {t("preview")}
            </Button>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {tCommon("cancel")}
            </Button>
            <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
              {createMutation.isPending || updateMutation.isPending
                ? tCommon("saving")
                : isEdit
                ? tCommon("save")
                : tCommon("create")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
