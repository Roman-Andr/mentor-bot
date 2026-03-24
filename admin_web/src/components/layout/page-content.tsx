import type { ReactNode } from "react";
import { PageHeader } from "@/components/layout/page-header";

interface PageContentProps {
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function PageContent({ title, subtitle, actions, children }: PageContentProps) {
  return (
    <div className="space-y-6 p-6">
      <PageHeader title={title} subtitle={subtitle} actions={actions} />
      {children}
    </div>
  );
}
