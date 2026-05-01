"use client";

/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useRef, useEffect, useCallback } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Search, ChevronDown, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDebounce } from "@/hooks/use-debounce";

export interface SelectOption {
  value: string;
  label: string;
  description?: string;
}

interface SearchableSelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  disabled?: boolean;
  className?: string;
}

interface AsyncSearchableSelectProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => Promise<SelectOption[]>;
  onOptionSelect?: (option: SelectOption) => void;
  selectedLabel?: string;
  placeholder?: string;
  searchPlaceholder?: string;
  disabled?: boolean;
  className?: string;
  debounceMs?: number;
  minSearchLength?: number;
}

/** A searchable dropdown select with filter-as-you-type. */
export function SearchableSelect({
  options,
  value,
  onChange,
  placeholder,
  searchPlaceholder,
  disabled = false,
  className,
}: SearchableSelectProps) {
  const t = useTranslations();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const placeholderText = placeholder ?? t("common.selectPlaceholder");
  const searchPlaceholderText = searchPlaceholder ?? t("common.searchPlaceholder");

  const selectedOption = options.find((o) => o.value === value);

  const filtered = search
    ? options.filter(
        (o) =>
          o.label.toLowerCase().includes(search.toLowerCase()) ||
          o.description?.toLowerCase().includes(search.toLowerCase()),
      )
    : options;

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [isOpen]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex h-9 w-full cursor-pointer items-center justify-between rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors",
          "focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none",
          "disabled:cursor-not-allowed disabled:opacity-50",
          !selectedOption && "text-muted-foreground",
        )}
      >
        <span className="truncate">{selectedOption ? selectedOption.label : placeholderText}</span>
        <div className="flex items-center gap-1">
          {selectedOption && !disabled && (
            <X
              className="text-muted-foreground hover:text-foreground/80 size-3.5"
              onClick={(e) => {
                e.stopPropagation();
                onChange("");
              }}
            />
          )}
          <ChevronDown className="size-4 opacity-50" />
        </div>
      </button>

      {isOpen && (
        <div className="bg-popover text-popover-foreground absolute z-50 mt-1 w-full rounded-md border shadow-md">
          <div className="flex items-center border-b px-2">
            <Search className="text-muted-foreground size-4 shrink-0" />
            <input
              ref={inputRef}
              className="placeholder:text-muted-foreground flex h-9 w-full bg-transparent px-2 py-1 text-sm outline-none"
              placeholder={searchPlaceholderText}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
            <div className="max-h-50 overflow-y-auto p-1">
            {filtered.length === 0 ? (
              <div className="text-muted-foreground px-2 py-3 text-center text-sm">
                {t("common.noResults")}
              </div>
            ) : (
              filtered.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={cn(
                    "flex w-full cursor-pointer flex-col items-start rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground",
                    option.value === value && "bg-accent text-accent-foreground",
                  )}
                  onClick={() => {
                    onChange(option.value);
                    setIsOpen(false);
                    setSearch("");
                  }}
                >
                  <span className="w-full truncate text-left">{option.label}</span>
                  {option.description && (
                    <span className="text-muted-foreground w-full truncate text-left text-xs">
                      {option.description}
                    </span>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/** A searchable dropdown select with server-side search (async). */
export function AsyncSearchableSelect({
  value,
  onChange,
  onSearch,
  onOptionSelect,
  selectedLabel,
  placeholder,
  searchPlaceholder,
  disabled = false,
  className,
  debounceMs = 300,
  minSearchLength = 1,
}: AsyncSearchableSelectProps) {
  const t = useTranslations();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [options, setOptions] = useState<SelectOption[]>([]);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const placeholderText = placeholder ?? t("common.selectPlaceholder");
  const searchPlaceholderText = searchPlaceholder ?? t("common.searchPlaceholder");

  const debouncedSearch = useDebounce(search, debounceMs);

  const fetchOptions = useCallback(
    async (query: string) => {
      if (query.length < minSearchLength) {
        setOptions([]);
        return;
      }
      setLoading(true);
      try {
        const results = await onSearch(query);
        setOptions(results);
      } catch {
        setOptions([]);
      } finally {
        setLoading(false);
      }
    },
    [onSearch, minSearchLength],
  );

  useEffect(() => {
    if (debouncedSearch.length >= minSearchLength) {
      fetchOptions(debouncedSearch);
    } else {
      setOptions([]);
    }
  }, [debouncedSearch, minSearchLength, fetchOptions]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [isOpen]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const displayLabel = selectedLabel || (value ? value : "");

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex h-9 w-full cursor-pointer items-center justify-between rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors",
          "focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none",
          "disabled:cursor-not-allowed disabled:opacity-50",
          !value && "text-muted-foreground",
        )}
      >
        <span className="truncate">{value ? displayLabel : placeholderText}</span>
        <div className="flex items-center gap-1">
          {value && !disabled && (
            <X
              className="text-muted-foreground hover:text-foreground/80 size-3.5"
              onClick={(e) => {
                e.stopPropagation();
                onChange("");
              }}
            />
          )}
          <ChevronDown className="size-4 opacity-50" />
        </div>
      </button>

      {isOpen && (
        <div className="bg-popover text-popover-foreground absolute z-50 mt-1 w-full rounded-md border shadow-md">
          <div className="flex items-center border-b px-2">
            <Search className="text-muted-foreground size-4 shrink-0" />
            <input
              ref={inputRef}
              className="placeholder:text-muted-foreground flex h-9 w-full bg-transparent px-2 py-1 text-sm outline-none"
              placeholder={searchPlaceholderText}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="max-h-50 overflow-y-auto p-1">
            {loading ? (
              <div className="text-muted-foreground px-2 py-3 text-center text-sm">{t("common.loading")}</div>
            ) : search.length < minSearchLength ? (
              <div className="text-muted-foreground px-2 py-3 text-center text-sm">
                {t("common.minSearchChars", { count: minSearchLength })}
              </div>
            ) : options.length === 0 ? (
              <div className="text-muted-foreground px-2 py-3 text-center text-sm">
                {t("common.noResults")}
              </div>
            ) : (
              options.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={cn(
                    "flex w-full cursor-pointer flex-col items-start rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground",
                    option.value === value && "bg-accent text-accent-foreground",
                  )}
                  onClick={() => {
                    onChange(option.value);
                    onOptionSelect?.(option);
                    setIsOpen(false);
                    setSearch("");
                  }}
                >
                  <span className="w-full truncate text-left">{option.label}</span>
                  {option.description && (
                    <span className="text-muted-foreground w-full truncate text-left text-xs">
                      {option.description}
                    </span>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
