"use client";

import { useState, useRef, useEffect } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const PRESET_COLORS = [
  "#6366f1", // Indigo
  "#8b5cf6", // Violet
  "#ec4899", // Pink
  "#f43f5e", // Rose
  "#ef4444", // Red
  "#f97316", // Orange
  "#eab308", // Yellow
  "#22c55e", // Green
  "#14b8a6", // Teal
  "#06b6d4", // Cyan
  "#3b82f6", // Blue
  "#6366f1", // Indigo
  "#64748b", // Slate
];

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 99, g: 102, b: 241 };
}

function rgbToHex(r: number, g: number, b: number): string {
  return "#" + [r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function rgbToHsv(r: number, g: number, b: number): { h: number; s: number; v: number } {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const d = max - min;
  let h = 0;
  const s = max === 0 ? 0 : d / max;
  const v = max;

  if (d !== 0) {
    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return { h: h * 360, s, v };
}

function hsvToRgb(h: number, s: number, v: number): { r: number; g: number; b: number } {
  const c = v * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = v - c;

  let r = 0,
    g = 0,
    b = 0;

  if (h >= 0 && h < 60) {
    r = c;
    g = x;
    b = 0;
  } else if (h >= 60 && h < 120) {
    r = x;
    g = c;
    b = 0;
  } else if (h >= 120 && h < 180) {
    r = 0;
    g = c;
    b = x;
  } else if (h >= 180 && h < 240) {
    r = 0;
    g = x;
    b = c;
  } else if (h >= 240 && h < 300) {
    r = x;
    g = 0;
    b = c;
  } else if (h >= 300 && h < 360) {
    r = c;
    g = 0;
    b = x;
  }

  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((b + m) * 255),
  };
}

interface ColorPickerProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function ColorPicker({ value, onChange, className }: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const svCanvasRef = useRef<HTMLCanvasElement>(null);
  const hueCanvasRef = useRef<HTMLCanvasElement>(null);
  const t = useTranslations();

  const rgb = hexToRgb(value || "#6366f1");
  const hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);

  const handleSvClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = svCanvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const y = Math.max(0, Math.min(e.clientY - rect.top, rect.height));

    const s = x / rect.width;
    const v = 1 - y / rect.height;

    const newRgb = hsvToRgb(hsv.h, s, v);
    onChange(rgbToHex(newRgb.r, newRgb.g, newRgb.b));
  };

  const handleHueClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = hueCanvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const y = Math.max(0, Math.min(e.clientY - rect.top, rect.height));
    const h = (y / rect.height) * 360;

    const newRgb = hsvToRgb(h, hsv.s, hsv.v);
    onChange(rgbToHex(newRgb.r, newRgb.g, newRgb.b));
  };

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen) {
      const svCanvas = svCanvasRef.current;
      const hueCanvas = hueCanvasRef.current;
      if (!svCanvas || !hueCanvas) return;

      const svCtx = svCanvas.getContext("2d");
      const hueCtx = hueCanvas.getContext("2d");
      if (!svCtx || !hueCtx) return;

      // Draw SV canvas
      const svWidth = svCanvas.width;
      const svHeight = svCanvas.height;

      // Create gradient for hue
      const hueGradient = svCtx.createLinearGradient(0, 0, svWidth, 0);
      hueGradient.addColorStop(0, `hsl(${hsv.h}, 100%, 50%)`);
      hueGradient.addColorStop(1, "white");

      svCtx.fillStyle = hueGradient;
      svCtx.fillRect(0, 0, svWidth, svHeight);

      // Create gradient for value
      const valueGradient = svCtx.createLinearGradient(0, 0, 0, svHeight);
      valueGradient.addColorStop(0, "transparent");
      valueGradient.addColorStop(1, "black");

      svCtx.fillStyle = valueGradient;
      svCtx.fillRect(0, 0, svWidth, svHeight);

      // Draw hue canvas
      const hueHeight = hueCanvas.height;
      const hueGradient2 = hueCtx.createLinearGradient(0, 0, 0, hueHeight);
      const colors = [
        "#ff0000", "#ffff00", "#00ff00", "#00ffff", "#0000ff", "#ff00ff", "#ff0000",
      ];
      colors.forEach((color, i) => {
        hueGradient2.addColorStop(i / (colors.length - 1), color);
      });

      hueCtx.fillStyle = hueGradient2;
      hueCtx.fillRect(0, 0, hueCanvas.width, hueHeight);

      // Draw selection indicator on SV canvas
      const svX = hsv.s * svWidth;
      const svY = (1 - hsv.v) * svHeight;

      svCtx.beginPath();
      svCtx.arc(svX, svY, 6, 0, 2 * Math.PI);
      svCtx.strokeStyle = "white";
      svCtx.lineWidth = 2;
      svCtx.stroke();
      svCtx.beginPath();
      svCtx.arc(svX, svY, 5, 0, 2 * Math.PI);
      svCtx.strokeStyle = "black";
      svCtx.lineWidth = 1;
      svCtx.stroke();

      // Draw selection indicator on hue canvas
      const hueY = (hsv.h / 360) * hueHeight;
      hueCtx.fillStyle = "white";
      hueCtx.fillRect(0, hueY - 2, hueCanvas.width, 4);
    }
  }, [isOpen, hsv]);

  return (
    <div className={cn("relative", className)} ref={containerRef}>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="border-input bg-background hover:bg-accent focus-visible:ring-ring flex h-9 w-12 items-center justify-center rounded-md border transition-colors focus-visible:ring-1 focus-visible:outline-none"
        >
          <div
            className="size-5 rounded-sm border"
            style={{ backgroundColor: value || "#6366f1" }}
          />
        </button>
        <input
          type="text"
          value={value || "#6366f1"}
          onChange={(e) => onChange(e.target.value)}
          className="border-input focus-visible:ring-ring flex h-9 w-full rounded-md border bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:ring-1 focus-visible:outline-none"
          placeholder="#6366f1"
        />
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="border-input bg-background hover:bg-accent focus-visible:ring-ring flex h-9 items-center justify-center rounded-md border px-2 transition-colors focus-visible:ring-1 focus-visible:outline-none"
        >
          <ChevronDown className="size-4" />
        </button>
      </div>

      {isOpen && (
        <div className="bg-popover text-popover-foreground absolute bottom-full z-50 mb-2 w-72 rounded-md border shadow-md">
          <div className="p-4">
            <div className="mb-4">
              <label className="text-muted-foreground mb-2 block text-xs font-medium">
                {t("common.customColor") || "Custom color"}
              </label>

              <div className="flex gap-2">
                <div className="relative">
                  <canvas
                    ref={svCanvasRef}
                    width={200}
                    height={200}
                    onMouseDown={handleSvClick}
                    onMouseMove={(e) => e.buttons === 1 && handleSvClick(e)}
                    className="border-input cursor-crosshair rounded-md border"
                  />
                </div>
                <div className="relative">
                  <canvas
                    ref={hueCanvasRef}
                    width={24}
                    height={200}
                    onMouseDown={handleHueClick}
                    onMouseMove={(e) => e.buttons === 1 && handleHueClick(e)}
                    className="border-input cursor-crosshair rounded-md border"
                  />
                </div>
              </div>

              <div
                className="border-input mt-3 h-8 w-full rounded-md border"
                style={{ backgroundColor: value || "#6366f1" }}
              />
            </div>

            <div>
              <label className="text-muted-foreground mb-2 block text-xs font-medium">
                {t("common.presetColors") || "Preset colors"}
              </label>
              <div className="grid grid-cols-7 gap-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => {
                      onChange(color);
                    }}
                    className="hover:border-ring focus-visible:ring-ring relative flex size-8 items-center justify-center rounded-md border transition-colors focus-visible:ring-1 focus-visible:outline-none"
                    style={{ backgroundColor: color }}
                  >
                    {value === color && (
                      <Check className="size-4 text-white" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
