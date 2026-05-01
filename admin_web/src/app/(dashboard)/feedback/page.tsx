"use client";

import { useTranslations } from "@/hooks/use-translations";
import { DataTable } from "@/components/ui/data-table";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import {
  FeedbackStats,
  FeedbackAnonymityStats,
  FeedbackFilters,
  FeedbackTable,
  FeedbackDetailsDialog,
  FeedbackReplyDialog,
} from "@/components/features/feedback";
import { useFeedback } from "@/hooks/use-feedback";

export default function FeedbackPage() {
  const t = useTranslations();
  const f = useFeedback();

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
          header={
            <CardHeader>
              <div className="flex items-center justify-between gap-4">
                <CardTitle>
                  {t("feedback.title")}{" "}
                  <span className="text-muted-foreground text-base font-normal">({f.totalCount})</span>
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
