import { Card, CardContent, CardHeader } from "@/shared/ui/card";
import { cn } from "@/shared/lib/utils";

interface SkeletonBlockProps {
  className?: string;
}

export function SkeletonBlock({ className }: SkeletonBlockProps) {
  return <div className={cn("animate-pulse rounded bg-muted", className)} />;
}

export function PageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-2">
          <SkeletonBlock className="h-8 w-48" />
          <SkeletonBlock className="h-4 w-72" />
        </div>
        <SkeletonBlock className="h-10 w-32" />
      </div>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <SkeletonBlock className="h-6 w-40" />
            <div className="flex gap-2">
              <SkeletonBlock className="h-10 w-48" />
              <SkeletonBlock className="h-10 w-28" />
              <SkeletonBlock className="h-10 w-24" />
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <SkeletonBlock key={index} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

export function DashboardPageSkeleton() {
  return (
    <div className="space-y-4 p-4 sm:space-y-6 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <div className="space-y-2">
            <SkeletonBlock className="h-8 w-48" />
            <SkeletonBlock className="h-4 w-72 max-w-full" />
          </div>
          <SkeletonBlock className="size-9 rounded-md" />
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <SkeletonBlock className="h-9 w-full sm:w-44" />
          <SkeletonBlock className="h-9 w-full sm:w-32" />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardContent className="space-y-4 p-6">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1 space-y-2">
                  <SkeletonBlock className="h-4 w-28 max-w-full" />
                  <SkeletonBlock className="h-9 w-16" />
                  <SkeletonBlock className="h-3 w-36 max-w-full" />
                </div>
                <SkeletonBlock className="ml-3 size-10 shrink-0 rounded-xl" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <SkeletonBlock className="h-6 w-44" />
            <SkeletonBlock className="h-8 w-20" />
          </CardHeader>
          <CardContent className="space-y-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-center gap-4">
                <div className="min-w-0 flex-1 space-y-2">
                  <div className="flex items-center justify-between gap-4">
                    <SkeletonBlock className="h-4 w-32" />
                    <SkeletonBlock className="h-3 w-8" />
                  </div>
                  <SkeletonBlock className="h-2 w-full rounded-full" />
                </div>
                <SkeletonBlock className="h-3 w-20 shrink-0" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <SkeletonBlock className="h-6 w-40" />
            <SkeletonBlock className="h-8 w-20" />
          </CardHeader>
          <CardContent className="space-y-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-start gap-3">
                <SkeletonBlock className="mt-2 size-2 rounded-full" />
                <div className="min-w-0 flex-1 space-y-2">
                  <SkeletonBlock className="h-4 w-40 max-w-full" />
                  <SkeletonBlock className="h-3 w-28 max-w-full" />
                </div>
                <SkeletonBlock className="h-3 w-12 shrink-0" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <SkeletonBlock className="h-6 w-36" />
            <SkeletonBlock className="h-8 w-20" />
          </CardHeader>
          <CardContent className="space-y-3">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2">
                  <SkeletonBlock className="size-3 shrink-0 rounded-full" />
                  <SkeletonBlock className="h-4 w-24" />
                </div>
                <SkeletonBlock className="h-4 w-6 shrink-0" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <SkeletonBlock className="h-5 w-32" />
            <SkeletonBlock className="h-8 w-20" />
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-4">
              <SkeletonBlock className="size-24 rounded-full" />
              <SkeletonBlock className="mt-3 h-4 w-36" />
            </div>
            <div className="mt-2 space-y-2 border-t pt-3">
              <div className="flex justify-between">
                <SkeletonBlock className="h-3 w-16" />
                <SkeletonBlock className="h-3 w-6" />
              </div>
              <div className="flex justify-between">
                <SkeletonBlock className="h-3 w-20" />
                <SkeletonBlock className="h-3 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <SkeletonBlock className="h-5 w-28" />
            <SkeletonBlock className="h-8 w-20" />
          </CardHeader>
          <CardContent className="space-y-2">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="space-y-2 rounded-lg border px-3 py-2">
                <div className="flex items-start justify-between gap-2">
                  <SkeletonBlock className="h-4 w-36 max-w-full" />
                  <SkeletonBlock className="h-3 w-16 shrink-0" />
                </div>
                <SkeletonBlock className="h-3 w-44 max-w-full" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center justify-end gap-1.5">
        <SkeletonBlock className="size-3" />
        <SkeletonBlock className="h-3 w-28" />
      </div>
    </div>
  );
}

export function AnalyticsPageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardContent className="space-y-4 p-6">
              <SkeletonBlock className="h-4 w-28" />
              <SkeletonBlock className="h-8 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardHeader>
              <SkeletonBlock className="h-6 w-40" />
            </CardHeader>
            <CardContent>
              <SkeletonBlock className="h-64 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function DetailPageSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-4">
        <SkeletonBlock className="h-10 w-10" />
        <div className="space-y-2">
          <SkeletonBlock className="h-8 w-56" />
          <SkeletonBlock className="h-4 w-72" />
        </div>
      </div>
      <Card>
        <CardHeader>
          <SkeletonBlock className="h-6 w-44" />
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <SkeletonBlock key={index} className="h-10 w-full" />
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <SkeletonBlock className="h-6 w-36" />
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <SkeletonBlock key={index} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

export function AppShellSkeleton() {
  return (
    <div className="flex h-screen">
      <div className="w-64 border-r bg-card p-4">
        <SkeletonBlock className="mb-8 h-8 w-36" />
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, index) => (
            <SkeletonBlock key={index} className="h-10 w-full" />
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-hidden bg-background">
        <PageSkeleton />
      </div>
    </div>
  );
}
