"use client";

import { useRef } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/ui/tooltip";
import { useConfirm } from "@/shared/hooks/use-confirm";
import { FileText, Upload, ExternalLink, X, AlertCircle } from "lucide-react";
import { cn } from "@/shared/lib/utils";

const ALLOWED_TYPES = ["pdf", "jpg", "jpeg", "png", "docx", "xlsx", "txt", "doc", "xls", "ppt", "pptx"];
const MAX_FILE_SIZE_MB = 10;

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  if (["jpg", "jpeg", "png", "gif", "webp"].includes(ext)) {
    return <FileText className="size-4 text-blue-500 dark:text-blue-400" />;
  }
  if (ext === "pdf") {
    return <FileText className="size-4 text-red-500 dark:text-red-400" />;
  }
  if (["doc", "docx"].includes(ext)) {
    return <FileText className="size-4 text-blue-700 dark:text-blue-500" />;
  }
  if (["xls", "xlsx"].includes(ext)) {
    return <FileText className="size-4 text-green-600 dark:text-green-400" />;
  }
  if (["ppt", "pptx"].includes(ext)) {
    return <FileText className="size-4 text-orange-500 dark:text-orange-400" />;
  }
  return <FileText className="size-4 text-muted-foreground" />;
}

interface MaterialFileManagerProps {
  url: string;
  onUrlChange: (url: string) => void;
  disabled?: boolean;
}

export function MaterialFileManager({ url, onUrlChange, disabled }: MaterialFileManagerProps) {
  const t = useTranslations();
  const confirm = useConfirm();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    if (!ALLOWED_TYPES.includes(ext)) {
      alert(`${t("meetings.invalidFileType") || "Invalid file type"}: ${ALLOWED_TYPES.join(", ")}`);
      return;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      alert(`${t("meetings.fileTooBig") || "File too big"}: ${MAX_FILE_SIZE_MB} MB`);
      return;
    }

    // For now, we'll just use the file name as a placeholder
    // In a real implementation, this would upload the file and get a URL
    onUrlChange(file.name);

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleClear = async () => {
    if (
      !(await confirm({
        title: t("meetings.clearFile") || "Clear file",
        description: t("meetings.clearFileConfirm") || "Are you sure you want to remove this file?",
        variant: "destructive",
        confirmText: t("common.delete") || "Delete",
      }))
    )
      return;
    onUrlChange("");
  };

  const handleOpenUrl = () => {
    if (url) window.open(url, "_blank");
  };

  return (
    <div className="grid gap-3">
      {!url ? (
        <div className="flex flex-col items-center justify-center rounded-md border border-dashed p-6 text-center">
          <FileText className="mb-2 size-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{t("meetings.noFileSelected") || "No file selected"}</p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="mt-2 gap-1"
          >
            <Upload className="size-3" />
            {t("meetings.selectFile") || "Select file"}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept={ALLOWED_TYPES.map((t) => `.${t}`).join(",")}
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        <div className="rounded-md border">
          <div className="flex items-center gap-3 px-3 py-2">
            {getFileIcon(url)}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{url}</p>
              <p className="text-muted-foreground text-xs">{t("meetings.fileUrl") || "File URL"}</p>
            </div>
            <TooltipProvider>
              <div className="flex gap-1">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={handleOpenUrl}
                    >
                      <ExternalLink className="size-3.5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t("common.open") || "Open"}</p>
                  </TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={handleClear}
                      disabled={disabled}
                      className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                    >
                      <X className="size-3.5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t("common.remove") || "Remove"}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </TooltipProvider>
          </div>
        </div>
      )}
    </div>
  );
}
