"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { DataTable } from "@/shared/ui/data-table";
import { PageContent } from "@/shared/layout/page-content";
import { CardHeader, CardTitle } from "@/shared/ui/card";
import { TabSwitcher, type TabItem } from "@/shared/ui/tab-switcher";
import {
  FeedbackStats, FeedbackAnonymityStats, FeedbackFilters,
  FeedbackTable, FeedbackDetailsDialog, FeedbackReplyDialog,
} from "@/widgets/feedback";
import { useFeedback } from "@/shared/hooks/use-feedback";
import { TrendingUp, Star, MessageSquare } from "lucide-react";
import { useSearchParams } from "next/navigation";
import type { FeedbackType } from "@/shared/types";

type Tab = "all" | "pulse" | "experience" | "comment";

export function FeedbackWidget() {
  const t = useTranslations();
  const f = useFeedback();
  const searchParams = useSearchParams();
  const activeTab = (searchParams.get("tab") as Tab) || "all";

  const tabs: TabItem[] = [
    { id: "all", label: t("common.all") || "All" },
    { id: "pulse", label: t("feedback.pulseSurveys"), icon: TrendingUp },
    { id: "experience", label: t("feedback.experienceRatings"), icon: Star },
    { id: "comment", label: t("feedback.comments"), icon: MessageSquare },
  ];

  const handleTabChange = (tab: string) => {
    f.handleTypeFilterChange(tab === "all" ? "all" : tab as FeedbackType);
  };

  return (
    <PageContent title={t("feedback.title")} subtitle={t("feedback.subtitle")}>
      <div className="space-y-6">
        <FeedbackStats />
        <FeedbackAnonymityStats />
        <TabSwitcher tabs={tabs} onTabChange={handleTabChange} />
        <DataTable
          loading={f.loading}
          empty={f.feedbackItems.length === 0}
          emptyMessage={t("common.noData")}
          currentPage={f.currentPage}
          totalPages={f.totalPages}
          totalCount={f.totalCount}
          pageSize={f.pageSize}
          onPageChange={f.setCurrentPage}
          onPageSizeChange={f.setPageSize}
          showPageSizeSelector={true}
          header={
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <CardTitle>
                  {t("feedback.title")}{" "}
                  <span className="text-muted-foreground text-sm font-normal">({f.totalCount})</span>
                </CardTitle>
                <FeedbackFilters
                  typeFilter={f.typeFilter}
                  anonymityFilter={f.anonymityFilter}
                  onTypeFilterChange={f.handleTypeFilterChange}
                  onAnonymityFilterChange={f.handleAnonymityFilterChange}
                  onResetFilters={f.resetFilters}
                />
              </div>
            </CardHeader>
          }
        >
          <FeedbackTable
            items={f.feedbackItems}
            getUserName={(userId) => f.getUserName(userId)}
            onViewDetails={(item) => f.viewDetails(item)}
            onReply={(id) => f.handleReply(id)}
            sortField={f.sortField}
            sortDirection={f.sortDirection}
            onSort={f.toggleSort}
            t={t}
          />
        </DataTable>
      </div>
      <FeedbackDetailsDialog
        item={f.selectedFeedback}
        open={f.selectedFeedback !== null && !f.isReplyModalOpen}
        getUserName={(userId) => f.getUserName(userId)}
        onOpenChange={(open) => { if (!open) f.closeDetails(); }}
      />
      <FeedbackReplyDialog
        item={f.selectedFeedback}
        open={f.isReplyModalOpen}
        submitting={f.replySubmitting}
        onOpenChange={(open) => { if (!open) f.closeReplyModal(); }}
        onSubmit={f.submitReply}
      />
    </PageContent>
  );
}
