"use client";

import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { departmentDocumentsApi } from "@/lib/api/department-documents";

interface DepartmentDocumentDownloadButtonProps {
  documentId: number;
  fileName: string;
}

export function DepartmentDocumentDownloadButton({ documentId, fileName }: DepartmentDocumentDownloadButtonProps) {
  const handleDownload = () => {
    const url = departmentDocumentsApi.downloadUrl(documentId);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Button variant="ghost" size="sm" onClick={handleDownload}>
      <Download className="mr-2 h-4 w-4" />
      Скачать
    </Button>
  );
}
