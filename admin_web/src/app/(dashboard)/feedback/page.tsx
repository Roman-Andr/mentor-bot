"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { PageContent } from "@/components/layout/page-content";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, MessageSquare, Incognito, User } from "lucide-react";
import { formatDateTime } from "@/lib/utils";
import { useFeedback } from "@/hooks/use-feedback";
import { FEEDBACK_TYPES, ANONYMITY_OPTIONS } from "@/lib/constants";
import type { FeedbackType } from "@/types";

export default function FeedbackPage() {
  const t = useTranslations();
  const f = useFeedback();

  return (
    <PageContent title={t("feedback.title")} subtitle={t("feedback.subtitle")}>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">{t("feedback.pulseSurveys")}</div>
          <div className="text-2xl font-bold mt-1">
            {f.pulseStats?.total_responses || 0}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {t("feedback.avgRating")}: {f.pulseStats?.average_rating?.toFixed(1) || "-"}/10
          </div>
        </div>
        <div className="bg-card border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">{t("feedback.experienceRatings")}</div>
          <div className="text-2xl font-bold mt-1">
            {f.experienceStats?.total_ratings || 0}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {t("feedback.avgRating")}: {f.experienceStats?.average_rating?.toFixed(1) || "-"}/5
          </div>
        </div>
        <div className="bg-card border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">{t("feedback.comments")}</div>
          <div className="text-2xl font-bold mt-1">{f.totalComments}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {f.commentsWithReply} {t("feedback.withReply")}
          </div>
        </div>
      </div>

      {/* Anonymity Stats */}
      <div className="bg-card border rounded-lg p-4 mb-6">
        <h3 className="font-semibold mb-4">{t("feedback.anonymityStats")}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">{t("feedback.pulseSurveysAnon")}</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="text-lg font-semibold">
                {f.pulseAnonymityStats?.anonymous?.count || 0}
              </div>
              <span className="text-xs text-muted-foreground">
                ({f.pulseAnonymityStats?.attributed?.count || 0} {t("feedback.attributed")})
              </span>
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">{t("feedback.experienceRatingsAnon")}</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="text-lg font-semibold">
                {f.experienceAnonymityStats?.anonymous?.count || 0}
              </div>
              <span className="text-xs text-muted-foreground">
                ({f.experienceAnonymityStats?.attributed?.count || 0} {t("feedback.attributed")})
              </span>
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">{t("feedback.commentsAnon")}</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="text-lg font-semibold">
                {f.commentAnonymityStats?.anonymous?.count || 0}
              </div>
              <span className="text-xs text-muted-foreground">
                ({f.commentAnonymityStats?.attributed?.count || 0} {t("feedback.attributed")})
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Table */}
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
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle>
                {t("feedback.title")}{" "}
                <span className="text-muted-foreground text-sm font-normal">({f.totalCount})</span>
              </CardTitle>
              <div className="flex gap-2 flex-wrap">
                <Select
                  value={f.typeFilter}
                  onChange={(value) => f.setTypeFilter(value as FeedbackType | "all")}
                  options={FEEDBACK_TYPES}
                />
                <Select
                  value={f.anonymityFilter}
                  onChange={f.setAnonymityFilter}
                  options={ANONYMITY_OPTIONS}
                />
                <Button variant="outline" onClick={f.resetFilters}>
                  {t("common.clear")}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>{t("feedback.type")}</TableHead>
              <TableHead>{t("feedback.user")}</TableHead>
              <TableHead>{t("feedback.content")}</TableHead>
              <TableHead>{t("feedback.submittedAt")}</TableHead>
              <TableHead>{t("feedback.status")}</TableHead>
              <TableHead className="w-25">{t("common.actions")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {f.feedbackItems.map((item) => (
              <TableRow key={`${item.type}-${item.id}`}>
                <TableCell>{item.id}</TableCell>
                <TableCell>
                  <StatusBadge status={item.type} />
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {item.is_anonymous ? (
                      <>
                        <Incognito className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {t("feedback.anonymous")}
                        </span>
                      </>
                    ) : (
                      <>
                        <User className="w-4 h-4" />
                        <span>{f.getUserName(item.user_id)}</span>
                      </>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {item.type === "pulse" && (
                    <div className="flex items-center gap-1">
                      <span className="font-bold">{item.rating}</span>
                      <span className="text-muted-foreground">/10</span>
                    </div>
                  )}
                  {item.type === "experience" && (
                    <div className="flex items-center gap-1">
                      <span className="font-bold">{item.rating}</span>
                      <span className="text-muted-foreground">/5 ★</span>
                    </div>
                  )}
                  {item.type === "comment" && (
                    <span className="line-clamp-2 max-w-48">{item.comment || "-"}</span>
                  )}
                </TableCell>
                <TableCell>{formatDateTime(item.submitted_at)}</TableCell>
                <TableCell>
                  {item.type === "comment" && item.reply ? (
                    <StatusBadge status="replied" />
                  ) : item.type === "comment" && item.is_anonymous && !item.allow_contact ? (
                    <StatusBadge status="no_reply" />
                  ) : (
                    <StatusBadge status="pending" />
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => f.viewDetails(item)}
                      title={t("feedback.viewDetails")}
                    >
                      <Eye className="size-4" />
                    </Button>
                    {item.type === "comment" && (!item.is_anonymous || item.allow_contact) && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => f.handleReply(item.id)}
                        title={t("feedback.reply")}
                      >
                        <MessageSquare className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
