"use client";

import { Upload } from "lucide-react";

interface DepartmentDocumentUploadZoneProps {
  onFileSelect: (file: File) => void;
  maxSize?: number; // in bytes
}

export function DepartmentDocumentUploadZone({
  onFileSelect,
  maxSize = 10 * 1024 * 1024, // 10MB
}: DepartmentDocumentUploadZoneProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > maxSize) {
        alert(`Файл слишком большой. Максимальный размер: ${maxSize / 1024 / 1024} МБ`);
        return;
      }
      onFileSelect(file);
    }
  };

  return (
    <div className="border-muted-foreground/25 hover:border-muted-foreground/50 flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors">
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg,.gif"
        onChange={handleFileChange}
      />
      <label
        htmlFor="file-upload"
        className="flex cursor-pointer flex-col items-center"
      >
        <Upload className="text-muted-foreground mb-4 h-10 w-10" />
        <p className="text-sm font-medium">Нажмите для выбора файла</p>
        <p className="text-muted-foreground mt-2 text-xs">
          PDF, DOCX, XLSX, изображения (макс. {maxSize / 1024 / 1024} МБ)
        </p>
      </label>
    </div>
  );
}
