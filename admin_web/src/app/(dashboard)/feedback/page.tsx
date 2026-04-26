"use client";

import { useTranslations } from "@/hooks/use-translations";
import { DataTable } from "@/components/ui/data-table";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { FeedbackStats, FeedbackAnonymityStats, FeedbackFilters, FeedbackTable } from "@/components/features/feedback";
import { useFeedback } from "@/hooks/use-feedback";

export default function FeedbackPage() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <PageContent title={t("feedback.title")} subtitle={t("feedback.subtitle")}>
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
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between gap-4">
              <CardTitle className="text-xl">
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
        />
      </DataTable>
    </PageContent>
  );
}
