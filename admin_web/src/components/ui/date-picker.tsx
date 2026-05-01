"use client";

import { useState } from "react";
import { format, parse, isValid } from "date-fns";
import { ru, enUS } from "date-fns/locale";
import { useLocale } from "next-intl";
import { Calendar, ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function DatePicker({ value, onChange, placeholder, className }: DatePickerProps) {
  const locale = useLocale();
  const dateLocale = locale === "ru" ? ru : enUS;
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(() => {
    if (value) {
      const parsed = parse(value, "yyyy-MM-dd", new Date());
      if (isValid(parsed)) return parsed;
    }
    return new Date();
  });
  const [isYearSelectOpen, setIsYearSelectOpen] = useState(false);

  const selectedDate = value ? parse(value, "yyyy-MM-dd", new Date()) : null;
  const displayValue = selectedDate && isValid(selectedDate) ? format(selectedDate, "dd MMM yyyy", { locale: dateLocale }) : placeholder || "Select date";

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPadding = firstDay.getDay();
    const daysInMonth = lastDay.getDate();
    
    const days = [];
    
    // Padding days from previous month
    for (let i = startPadding - 1; i >= 0; i--) {
      const day = new Date(year, month, -i);
      days.push({ date: day, isPadding: true });
    }
    
    // Days in current month
    for (let i = 1; i <= daysInMonth; i++) {
      const day = new Date(year, month, i);
      days.push({ date: day, isPadding: false });
    }
    
    // Padding days from next month
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      const day = new Date(year, month + 1, i);
      days.push({ date: day, isPadding: true });
    }
    
    return days;
  };

  const handleDateSelect = (date: Date) => {
    const formatted = format(date, "yyyy-MM-dd");
    onChange(formatted);
    setIsOpen(false);
  };

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const handleYearSelect = (year: number) => {
    setCurrentMonth(new Date(year, currentMonth.getMonth(), 1));
    setIsYearSelectOpen(false);
  };

  const currentYear = currentMonth.getFullYear();
  const years = [];
  const startYear = currentYear - 50;
  const endYear = currentYear + 50;
  for (let y = startYear; y <= endYear; y++) {
    years.push(y);
  }

  const days = getDaysInMonth(currentMonth);
  const weekDays = locale === "ru" 
    ? ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"] 
    : ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

  const isSelected = (date: Date) => {
    return selectedDate && isValid(selectedDate) && format(date, "yyyy-MM-dd") === format(selectedDate, "yyyy-MM-dd");
  };

  const isToday = (date: Date) => {
    return format(date, "yyyy-MM-dd") === format(new Date(), "yyyy-MM-dd");
  };

  return (
    <div className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex h-9 w-full cursor-pointer items-center justify-between rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
          !value && "text-muted-foreground",
        )}
      >
        <span className="truncate flex items-center">
          <Calendar className="mr-2 h-4 w-4 text-muted-foreground shrink-0" />
          {displayValue}
        </span>
        <ChevronDown className="h-4 w-4 opacity-50 shrink-0" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="bg-popover text-popover-foreground absolute top-full left-0 z-50 mt-2 w-72 rounded-lg border shadow-md p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={handlePrevMonth}
                className="h-8 w-8"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="font-semibold cursor-pointer hover:bg-accent rounded px-2 py-1 flex items-center gap-1" onClick={() => setIsYearSelectOpen(!isYearSelectOpen)}>
                {format(currentMonth, "MMM yyyy", { locale: dateLocale })}
                {isYearSelectOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={handleNextMonth}
                className="h-8 w-8"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {isYearSelectOpen ? (
              <div className="max-h-60 overflow-y-auto">
                <div className="grid grid-cols-4 gap-1">
                  {years.map((year) => (
                    <button
                      key={year}
                      type="button"
                      onClick={() => handleYearSelect(year)}
                      className={cn(
                        "h-8 rounded-md text-sm font-medium transition-colors",
                        "hover:bg-accent hover:text-accent-foreground",
                        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                        year === currentYear && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground"
                      )}
                    >
                      {year}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {/* Week days */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {weekDays.map((day) => (
                    <div
                      key={day}
                      className="text-center text-xs font-medium text-muted-foreground py-1"
                    >
                      {day}
                    </div>
                  ))}
                </div>

                {/* Calendar days */}
                <div className="grid grid-cols-7 gap-1">
                  {days.map(({ date, isPadding }, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => !isPadding && handleDateSelect(date)}
                      disabled={isPadding}
                      className={cn(
                        "h-8 w-8 rounded-md text-sm font-medium transition-colors",
                        "hover:bg-accent hover:text-accent-foreground",
                        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                        isSelected(date) && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground",
                        isToday(date) && !isSelected(date) && "border border-primary",
                        isPadding && "text-muted-foreground opacity-30 cursor-not-allowed hover:bg-transparent"
                      )}
                    >
                      {format(date, "d")}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
