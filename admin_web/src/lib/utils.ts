import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return "-";
  const d = new Date(date);
  return d.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return "-";
  const d = new Date(date);
  return d.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getInitials(firstName: string, lastName?: string): string {
  const first = firstName?.[0]?.toUpperCase() || "";
  const last = lastName?.[0]?.toUpperCase() || "";
  return first + last || first;
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800",
    INACTIVE: "bg-gray-100 text-gray-800",
    DRAFT: "bg-yellow-100 text-yellow-800",
    PUBLISHED: "bg-blue-100 text-blue-800",
    ARCHIVED: "bg-red-100 text-red-800",
    COMPLETED: "bg-green-100 text-green-800",
    PENDING: "bg-yellow-100 text-yellow-800",
    IN_PROGRESS: "bg-blue-100 text-blue-800",
    OVERDUE: "bg-red-100 text-red-800",
  };
  return colors[status?.toUpperCase()] || "bg-gray-100 text-gray-800";
}

export function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    ADMIN: "bg-purple-100 text-purple-800",
    HR: "bg-blue-100 text-blue-800",
    MENTOR: "bg-green-100 text-green-800",
    NEWBIE: "bg-gray-100 text-gray-800",
  };
  return colors[role?.toUpperCase()] || "bg-gray-100 text-gray-800";
}
