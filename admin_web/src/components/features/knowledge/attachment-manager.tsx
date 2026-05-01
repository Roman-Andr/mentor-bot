"use client";

import { useState, useRef } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { useConfirm } from "@/hooks/use-confirm";
import { attachmentsApi } from "@/lib/api";
import type { Attachment, FileUploadError } from "@/types";
import { FileText, Trash2, Upload, Download, Loader2, X, AlertCircle } from "lucide-react";

const ALLOWED_TYPES = ["pdf", "jpg", "jpeg", "png", "docx", "xlsx", "txt"];
const MAX_FILE_SIZE_MB = 10;

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileIcon(mimeType: string | null) {
  if (!mimeType) return <FileText className="text-muted-foreground size-4" />;
  if (mimeType.startsWith("image/")) return <FileText className="size-4 text-blue-500 dark:text-blue-400" />;
  if (mimeType === "application/pdf") return <FileText className="size-4 text-red-500 dark:text-red-400" />;
  return <FileText className="text-muted-foreground size-4" />;
}

function getFileExt(name: string): string {
  return name.split(".").pop()?.toLowerCase() || "";
}

interface AttachmentManagerProps {
  articleId: number | null;
  attachments: Attachment[];
  onAttachmentsChange: (attachments: Attachment[]) => void;
  pendingFiles?: File[];
  onPendingFilesChange?: (files: File[]) => void;
}

export function AttachmentManager({
  articleId,
  attachments,
  onAttachmentsChange,
  pendingFiles = [],
  onPendingFilesChange,
}: AttachmentManagerProps) {
  const t = useTranslations();
  const confirm = useConfirm();
  const [uploading, setUploading] = useState(false);
  const [uploadErrors, setUploadErrors] = useState<FileUploadError[]>([]);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const ext = getFileExt(file.name);
    if (!ALLOWED_TYPES.includes(ext)) {
      return `${t("knowledge.invalidFileType")}: ${ALLOWED_TYPES.join(", ")}`;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `${t("knowledge.fileTooBig")}: ${MAX_FILE_SIZE_MB} MB`;
    }
    return null;
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploadErrors([]);

    if (articleId) {
      const filesToUpload: File[] = [];
      const clientErrors: FileUploadError[] = [];

      for (const file of Array.from(files)) {
        const error = validateFile(file);
        if (error) {
          clientErrors.push({ filename: file.name, error });
          continue;
        }
        filesToUpload.push(file);
      }

      setUploadErrors(clientErrors);

      if (filesToUpload.length > 0) {
        setUploading(true);
        const response = await attachmentsApi.uploadMultiple(articleId, filesToUpload);

        if (response.success && response.data) {
          const { attachments: newAttachments, errors: serverErrors } = response.data;
          const allErrors = [...clientErrors, ...serverErrors];
          setUploadErrors(allErrors);

          if (newAttachments.length > 0) {
            onAttachmentsChange([...attachments, ...newAttachments]);
          }
        } else {
          setUploadErrors([...clientErrors, { filename: null, error: !response.success && response.error ? response.error.message : t("common.error") }]);
        }
        setUploading(false);
      }
    } else if (onPendingFilesChange) {
      const newFiles: File[] = [];
      const clientErrors: FileUploadError[] = [];

      for (const file of Array.from(files)) {
        const error = validateFile(file);
        if (error) {
          clientErrors.push({ filename: file.name, error });
          continue;
        }
        newFiles.push(file);
      }

      setUploadErrors(clientErrors);

      if (newFiles.length > 0) {
        onPendingFilesChange([...pendingFiles, ...newFiles]);
      }
    }

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDelete = async (attachmentId: number) => {
    if (
      !(await confirm({
        title: t("knowledge.deleteFile"),
        description: t("knowledge.deleteFileConfirm"),
        variant: "destructive",
        confirmText: t("common.delete"),
      }))
    )
      return;
    setDeletingId(attachmentId);
    const response = await attachmentsApi.delete(attachmentId);
    if (response.success) {
      onAttachmentsChange(attachments.filter((a) => a.id !== attachmentId));
    }
    setDeletingId(null);
  };

  const handleRemovePending = (index: number) => {
    if (!onPendingFilesChange) return;
    onPendingFilesChange(pendingFiles.filter((_, i) => i !== index));
  };

  const handleDownload = (attachment: Attachment) => {
    if (!articleId) return;
    const url = attachmentsApi.getDownloadUrl(articleId, attachment.name);
    window.open(url, "_blank");
  };

  const canAddFiles = articleId || onPendingFilesChange;

  return (
    <div className="grid gap-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">{t("knowledge.files")}</label>
        {canAddFiles && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="gap-1"
          >
            {uploading ? (
              <Loader2 className="size-3 animate-spin" />
            ) : (
              <Upload className="size-3" />
            )}
            {uploading ? t("common.loading") : t("knowledge.uploadFile")}
          </Button>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_TYPES.map((t) => `.${t}`).join(",")}
          onChange={handleFileSelect}
          className="hidden"
          multiple
        />
      </div>

      {uploadErrors.length > 0 && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 dark:border-red-900/50 dark:bg-red-950/50">
          <div className="mb-2 flex items-center gap-2">
            <AlertCircle className="size-4 text-red-600 dark:text-red-400" />
            <span className="text-sm font-medium text-red-800 dark:text-red-400">
              {uploadErrors.length === 1
                ? t("knowledge.uploadError")
                : t("knowledge.uploadErrors", { count: uploadErrors.length })}
            </span>
          </div>
          <ul className="space-y-1">
            {uploadErrors.map((err, idx) => (
              <li key={idx} className="text-xs text-red-700 dark:text-red-400">
                {err.filename ? `${err.filename}: ` : ""}
                {err.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {attachments.length > 0 && (
        <div className="divide-y rounded-md border">
          {attachments.map((att) => (
            <div key={att.id} className="flex items-center gap-3 px-3 py-2">
              {getFileIcon(att.mime_type)}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{att.name}</p>
                <p className="text-muted-foreground text-xs">
                  {formatFileSize(att.file_size)}
                  {att.description && ` — ${att.description}`}
                </p>
              </div>
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDownload(att)}
                  title={t("common.download")}
                >
                  <Download className="size-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(att.id)}
                  disabled={deletingId === att.id}
                  className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                  title={t("common.delete")}
                >
                  <Trash2 className="size-3.5" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {pendingFiles.length > 0 && (
        <div className="divide-y rounded-md border border-dashed">
          {pendingFiles.map((file, index) => (
            <div key={`${file.name}-${index}`} className="flex items-center gap-3 px-3 py-2">
              {getFileIcon(file.type || null)}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{file.name}</p>
                <p className="text-muted-foreground text-xs">
                  {formatFileSize(file.size)} — {t("knowledge.willUploadAfterSave")}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => handleRemovePending(index)}
                className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                title={t("knowledge.remove")}
              >
                <X className="size-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {attachments.length === 0 && pendingFiles.length === 0 && (
        <p className="text-muted-foreground text-xs">{t("knowledge.noAttachments")}</p>
      )}
    </div>
  );
}