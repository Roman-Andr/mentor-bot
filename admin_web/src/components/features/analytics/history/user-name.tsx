"use client";

import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { api } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

interface UserNameProps {
  userId: number | null;
}

export function UserName({ userId }: UserNameProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.users.detail(userId ?? 0),
    queryFn: () => api.users.get(userId ?? 0),
    enabled: userId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });

  if (!userId) {
    return <span className="text-muted-foreground">—</span>;
  }

  if (isLoading) {
    return <Skeleton className="h-4 w-24 inline-block" />;
  }

  if (error || !data?.success || !data?.data) {
    return <span className="text-muted-foreground">User #{userId}</span>;
  }

  const user = data.data;
  const displayName = user.first_name || user.last_name
    ? `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim()
    : user.email || `User #${user.id}`;
  return <span>{displayName}</span>;
}
