"use client";

import { useAuth } from "@/hooks/use-auth";
import { AppShellSkeleton } from "@/components/ui/page-skeleton";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function AuthCheck({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return <AppShellSkeleton />;
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
