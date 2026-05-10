"use client";

/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useRef, useEffect, useCallback } from "react";
import { useTranslations } from "@/shared/hooks/use-translations";
import { Search, ChevronDown, X } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { useDebounce } from "@/shared/hooks/use-debounce";
import { UserAvatar } from "@/shared/ui/user-avatar";

export interface SelectOption {
  value: string;
  label: string;
  description?: string;
  id?: number; // For avatar generation
  telegram_id?: number | null;
  email?: string | null;
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
  selectedOption?: SelectOption;
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
    <div ref={containerRef} className={cn("relative", isOpen && "z-10", className)}>
      <button
        type="button"
        title={selectedOption ? selectedOption.label : placeholderText}
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
              className="size-3.5 text-muted-foreground hover:text-foreground/80"
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
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md">
          <div className="flex items-center border-b px-2">
            <Search className="size-4 shrink-0 text-muted-foreground" />
            <input
              ref={inputRef}
              className="flex h-9 w-full bg-transparent px-2 py-1 text-sm outline-none placeholder:text-muted-foreground"
              placeholder={searchPlaceholderText}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="max-h-50 overflow-y-auto p-1">
            {filtered.length === 0 ? (
              <div className="px-2 py-3 text-center text-sm text-muted-foreground">
                {t("common.noResults")}
              </div>
            ) : (
              filtered.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  title={option.label}
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
                    <span className="w-full truncate text-left text-xs text-muted-foreground">
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
  selectedOption,
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
    <div ref={containerRef} className={cn("relative", isOpen && "z-10", className)}>
      <button
        type="button"
        title={value ? displayLabel : placeholderText}
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex h-9 w-full cursor-pointer items-center justify-between rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors",
          "focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none",
          "disabled:cursor-not-allowed disabled:opacity-50",
          !value && "text-muted-foreground",
        )}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          {selectedOption?.id && (
            <UserAvatar name={selectedOption.label} id={selectedOption.id} size="sm" />
          )}
          <span className="truncate">{value ? displayLabel : placeholderText}</span>
        </div>
        <div className="flex items-center gap-1">
          {value && !disabled && (
            <X
              className="size-3.5 text-muted-foreground hover:text-foreground/80"
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
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md">
          <div className="flex items-center border-b px-2">
            <Search className="size-4 shrink-0 text-muted-foreground" />
            <input
              ref={inputRef}
              className="flex h-9 w-full bg-transparent px-2 py-1 text-sm outline-none placeholder:text-muted-foreground"
              placeholder={searchPlaceholderText}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="max-h-50 overflow-y-auto p-1">
            {loading ? (
              <div className="px-2 py-3 text-center text-sm text-muted-foreground">
                {t("common.loading")}
              </div>
            ) : search.length < minSearchLength ? (
              <div className="px-2 py-3 text-center text-sm text-muted-foreground">
                {t("common.minSearchChars", { count: minSearchLength })}
              </div>
            ) : options.length === 0 ? (
              <div className="px-2 py-3 text-center text-sm text-muted-foreground">
                {t("common.noResults")}
              </div>
            ) : (
              options.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  title={option.label}
                  className={cn(
                    "flex w-full cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground",
                    option.value === value && "bg-accent text-accent-foreground",
                  )}
                  onClick={() => {
                    onChange(option.value);
                    onOptionSelect?.(option);
                    setIsOpen(false);
                    setSearch("");
                  }}
                >
                  {option.id && <UserAvatar name={option.label} id={option.id} size="sm" />}
                  <div className="flex flex-col items-start overflow-hidden">
                    <span className="truncate text-left">{option.label}</span>
                    {option.description && (
                      <span className="truncate text-left text-xs text-muted-foreground">
                        {option.description}
                      </span>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
