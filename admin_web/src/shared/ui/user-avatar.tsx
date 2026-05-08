import { cn } from "@/shared/lib/utils";

const AVATAR_COLORS = [
  "bg-blue-500", "bg-teal-500", "bg-violet-500", "bg-amber-500",
  "bg-rose-500", "bg-cyan-500", "bg-emerald-500", "bg-indigo-500",
];

interface UserAvatarProps {
  name: string;
  id: number;
  size?: "sm" | "md";
}

export function UserAvatar({ name, id, size = "md" }: UserAvatarProps) {
  const initials = name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
  const color = AVATAR_COLORS[id % AVATAR_COLORS.length];
  return (
    <div
      className={cn(
        "shrink-0 flex items-center justify-center rounded-full font-bold text-white",
        size === "sm" ? "size-6 text-[10px]" : "size-8 text-xs",
        color,
      )}
    >
      {initials || "?"}
    </div>
  );
}
