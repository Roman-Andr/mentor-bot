"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { DataTable } from "@/shared/ui/data-table";
import { PageContent } from "@/shared/layout/page-content";
import { CardHeader, CardTitle } from "@/shared/ui/card";
import {
  FeedbackStats,
  FeedbackAnonymityStats,
  FeedbackFilters,
  FeedbackTable,
  FeedbackDetailsDialog,
  FeedbackReplyDialog,
} from "@/widgets/feedback";
import { useFeedback } from "@/shared/hooks/use-feedback";

export function FeedbackWidget() {
  const t = useTranslations();
  const f = useFeedback();

  const feedbackTable = FeedbackTable({
    items: f.feedbackItems,
    getUserName: (userId) => f.getUserName(userId),
    onViewDetails: (item) => f.viewDetails(item),
    onReply: (id) => f.handleReply(id),
    onDelete: (item) => f.handleDelete(item),
    sortField: f.sortField,
    sortDirection: f.sortDirection,
    onSort: f.toggleSort,
    t: t,
  });

  return (
    <PageContent title={t("feedback.title")} subtitle={t("feedback.subtitle")}>
      <div className="space-y-6">
        <FeedbackStats />
        <FeedbackAnonymityStats />
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
          mobileView={feedbackTable.mobileView}
          header={
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <CardTitle className="inline-flex items-baseline gap-1 whitespace-nowrap">
                  {t("feedback.title")}{" "}
                  <span className="text-sm font-normal text-muted-foreground">
                    ({f.totalCount})
                  </span>
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
          {feedbackTable.table}
        </DataTable>
      </div>
      <FeedbackDetailsDialog
        item={f.selectedFeedback}
        open={f.selectedFeedback !== null && !f.isReplyModalOpen}
        getUserName={(userId) => f.getUserName(userId)}
        onOpenChange={(open) => {
          if (!open) f.closeDetails();
        }}
      />
      <FeedbackReplyDialog
        item={f.selectedFeedback}
        open={f.isReplyModalOpen}
        submitting={f.replySubmitting}
        onOpenChange={(open) => {
          if (!open) f.closeReplyModal();
        }}
        onSubmit={f.submitReply}
      />
    </PageContent>
  );
}
