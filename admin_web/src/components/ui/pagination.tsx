"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalCount?: number;
  pageSize?: number;
  pageSizeOptions?: number[];
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  showPageSizeSelector?: boolean;
  showPageInput?: boolean;
  showingFrom?: number;
  showingTo?: number;
}

const DEFAULT_PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export function Pagination({
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  onPageChange,
  onPageSizeChange,
  showPageSizeSelector = true,
  showPageInput = true,
  showingFrom,
  showingTo,
}: PaginationProps) {
  const t = useTranslations("pagination");
  const [inputPage, setInputPage] = useState("");

  if (totalPages <= 1 && !showPageSizeSelector) return null;

  const handleInputSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      const page = parseInt(inputPage, 10);
      if (!isNaN(page) && page >= 1 && page <= totalPages) {
        onPageChange(page);
        setInputPage("");
      }
    }
  };

  const handleInputBlur = () => {
    const page = parseInt(inputPage, 10);
    if (!isNaN(page) && page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
    setInputPage("");
  };

  const pageSizeOptionsFormatted = pageSizeOptions.map((size) => ({
    value: String(size),
    label: String(size),
  }));

  const from = showingFrom ?? (currentPage - 1) * (pageSize || 20) + 1;
  const to = showingTo ?? Math.min(currentPage * (pageSize || 20), totalCount || 0);

  return (
    <div className="flex flex-col gap-3 border-t px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      {/* Left side: Showing info and Page Size Selector */}
      <div className="flex flex-wrap items-center gap-4">
        {totalCount !== undefined && totalCount > 0 && (
          <span className="text-muted-foreground text-sm">
            {t("showing", { from, to, total: totalCount })}
          </span>
        )}

        {showPageSizeSelector && onPageSizeChange && pageSize && (
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-sm">{t("itemsPerPageLabel")}</span>
            <Select
              value={String(pageSize)}
              onChange={(value) => onPageSizeChange(Number(value))}
              options={pageSizeOptionsFormatted}
              className="w-20"
            />
          </div>
        )}
      </div>

      {/* Right side: Navigation controls */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Back Button */}
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="gap-1"
        >
          <ChevronLeft className="size-4" />
          {t("back")}
        </Button>

        {/* Page Info / Input */}
        <div className="flex items-center gap-2 px-2">
          <span className="text-muted-foreground text-sm">
            {t("page")} {currentPage} {t("of")} {totalPages}
          </span>

          {showPageInput && totalPages > 1 && (
            <div className="flex items-center gap-1">
              <Input
                type="number"
                min={1}
                max={totalPages}
                value={inputPage}
                onChange={(e) => setInputPage(e.target.value)}
                onKeyDown={handleInputSubmit}
                onBlur={handleInputBlur}
                placeholder={t("pageNumberPlaceholder")}
                className="h-8 w-24 text-sm"
              />
            </div>
          )}
        </div>

        {/* Forward Button */}
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="gap-1"
        >
          {t("next")}
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
