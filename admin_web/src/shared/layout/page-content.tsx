import type { ReactNode } from "react";
import { PageHeader } from "@/shared/layout/page-header";

interface PageContentProps {
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function PageContent({ title, subtitle, actions, children }: PageContentProps) {
  return (
    <div className="min-w-0 space-y-4 p-4 sm:space-y-6 sm:p-6">
      <PageHeader title={title} subtitle={subtitle} actions={actions} />
      {children}
    </div>
  );
}
