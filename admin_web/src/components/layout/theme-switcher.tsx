"use client";

import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ThemeSwitcherProps {
  collapsed?: boolean;
}

export function ThemeSwitcher({ collapsed }: ThemeSwitcherProps) {
  const { theme, setTheme } = useTheme();

  const options = [
    { value: "light", icon: Sun },
    { value: "dark", icon: Moon },
    { value: "system", icon: Monitor },
  ] as const;

  if (collapsed) {
    const next = theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
    const CurrentIcon = theme === "light" ? Sun : theme === "dark" ? Moon : Monitor;
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={() => setTheme(next)}
              className="flex w-full items-center justify-center rounded-lg px-3 py-2.5 text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
            >
              <CurrentIcon className="size-5 shrink-0" />
            </button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{theme}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <div className="flex items-center gap-1 rounded-lg px-3 py-2.5">
        {options.map(({ value, icon: Icon }) => (
          <Tooltip key={value}>
            <TooltipTrigger asChild>
              <button
                onClick={() => setTheme(value)}
                className={cn(
                  "rounded p-1.5 transition-colors",
                  theme === value
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white",
                )}
              >
                <Icon className="size-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{value}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </TooltipProvider>
  );
}
