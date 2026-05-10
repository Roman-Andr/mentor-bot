"use client";

import { Clock } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface DateTimePickerProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function DateTimePicker({ value, onChange, placeholder, className }: DateTimePickerProps) {
  return (
    <div className={cn("relative", className)}>
      <Clock className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="datetime-local"
        value={value || ""}
        onChange={(event) => onChange(event.target.value)}
        aria-label={placeholder || "Select date and time"}
        className={cn(
          "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 pl-9 text-sm shadow-sm transition-colors",
          "focus-visible:ring-1 focus-visible:ring-ring focus-visible:outline-none",
          !value && "text-muted-foreground",
        )}
      />
    </div>
  );
}
