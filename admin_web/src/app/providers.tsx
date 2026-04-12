"use client";

import { useState } from "react";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { PaginationProvider } from "@/components/providers/pagination-provider";
import { ConfirmProvider } from "@/components/ui/confirm-dialog";
import { ToastProvider } from "@/components/ui/toast";
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
