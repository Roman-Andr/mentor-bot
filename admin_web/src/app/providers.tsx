"use client";

import { useState } from "react";
import { AuthProvider } from "@/shared/lib/auth-context";
import { ThemeProvider } from "@/shared/providers/theme-provider";
import { PaginationProvider } from "@/shared/providers/pagination-provider";
import { ConfirmProvider } from "@/shared/ui/confirm-dialog";
import { ToastProvider } from "@/shared/ui/toast";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5,
        retry: 1,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

function getQueryClient() {
  if (typeof window === "undefined") {
    return makeQueryClient();
  }
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient();
  }
  return browserQueryClient;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => getQueryClient());

  return (
    <ThemeProvider>
      <PaginationProvider>
        <AuthProvider>
          <ToastProvider>
            <ConfirmProvider>
              <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
            </ConfirmProvider>
          </ToastProvider>
        </AuthProvider>
      </PaginationProvider>
    </ThemeProvider>
  );
}
