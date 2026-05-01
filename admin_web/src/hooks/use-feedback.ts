import { useState, useMemo, useCallback, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { useTranslations } from "@/hooks/use-translations";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { feedbackApi } from "@/lib/api/feedback";
import type {
  FeedbackItem,
  PulseStats,
  ExperienceStats,
  AnonymityStats,
  FeedbackType,
  Comment,
} from "@/types/feedback";

export function useFeedback() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const t = useTranslations();

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  // Sorting
  const [sortField, setSortField] = useState<string>("submitted_at");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  // Filters
  const [typeFilter, setTypeFilter] = useState<FeedbackType | "all">("all");
  const [anonymityFilter, setAnonymityFilter] = useState<"all" | "anonymous" | "attributed">("all");

  const handleTypeFilterChange = useCallback((value: FeedbackType | "all") => {
    setTypeFilter(value);
    setCurrentPage(1);
  }, []);

  const handleAnonymityFilterChange = useCallback((value: "all" | "anonymous" | "attributed") => {
    setAnonymityFilter(value);
    setCurrentPage(1);
  }, []);

  const toggleSort = useCallback((field: string) => {
    setSortField((current) => {
      if (current === field) {
        setSortDirection((dir) => dir === "asc" ? "desc" : "asc");
      } else {
        setSortDirection("desc");
      }
      return field;
    });
    setCurrentPage(1);
  }, []);

  // Refetch queries when type filter changes
  useEffect(() => {
    if (typeFilter !== "all") {
      // Invalidate queries to ensure fresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.feedback.all });
    }
  }, [typeFilter, queryClient]);

  // Modal state
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);
  const [isReplyModalOpen, setIsReplyModalOpen] = useState(false);
  const [replyingToId, setReplyingToId] = useState<number | null>(null);

  // Calculate skip based on page
  const skip = useMemo(() => (currentPage - 1) * pageSize, [currentPage, pageSize]);

  // Fetch pulse surveys (always fetch, filter on client)
  const {
    data: pulseData,
    isLoading: isPulseLoading,
    refetch: refetchPulse,
  } = useQuery({
    queryKey: queryKeys.feedback.pulse({ skip, limit: pageSize, sort_by: sortField, sort_order: sortDirection }),
    queryFn: () =>
      feedbackApi.getPulseSurveys({
        skip,
        limit: pageSize,
        from_date: undefined,
        to_date: undefined,
        sort_by: sortField,
        sort_order: sortDirection,
      }),
    staleTime: 60 * 1000,
  });

  // Fetch experience ratings (always fetch, filter on client)
  const {
    data: experienceData,
    isLoading: isExperienceLoading,
    refetch: refetchExperience,
  } = useQuery({
    queryKey: queryKeys.feedback.experience({ skip, limit: pageSize, sort_by: sortField, sort_order: sortDirection }),
    queryFn: () =>
      feedbackApi.getExperienceRatings({
        skip,
        limit: pageSize,
        from_date: undefined,
        to_date: undefined,
        sort_by: sortField,
        sort_order: sortDirection,
      }),
    staleTime: 60 * 1000,
  });

  // Fetch comments (always fetch, filter on client)
  const {
    data: commentsData,
    isLoading: isCommentsLoading,
    refetch: refetchComments,
  } = useQuery({
    queryKey: queryKeys.feedback.comments({ skip, limit: pageSize, sort_by: sortField, sort_order: sortDirection }),
    queryFn: () =>
      feedbackApi.getComments({
        skip,
        limit: pageSize,
        from_date: undefined,
        to_date: undefined,
        sort_by: sortField,
        sort_order: sortDirection,
      }),
    staleTime: 60 * 1000,
  });

  // Fetch stats
  const { data: pulseStats } = useQuery({
    queryKey: queryKeys.feedback.pulseStats(),
    queryFn: () => feedbackApi.getPulseStats(),
    staleTime: 5 * 60 * 1000,
  });

  const { data: experienceStats } = useQuery({
    queryKey: queryKeys.feedback.experienceStats(),
    queryFn: () => feedbackApi.getExperienceStats(),
    staleTime: 5 * 60 * 1000,
  });

  // Fetch anonymity stats (only pulse exists in backend)
  const { data: pulseAnonymityStats } = useQuery({
    queryKey: queryKeys.feedback.pulseAnonymityStats(),
    queryFn: () => feedbackApi.getPulseAnonymityStats(),
    staleTime: 5 * 60 * 1000,
  });

  // Fetch users for name lookup
  const { data: usersData } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => api.users.list({ limit: 1000 }),
    select: (result) => {
      const map = new Map<number, string>();
      if (result.success && result.data) {
        for (const u of result.data.users) {
          map.set(u.id, `${u.first_name ?? ""} ${u.last_name ?? ""}`.trim() || String(u.id));
        }
      }
      return map;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Reply mutation
  const replyMutation = useMutation({
    mutationFn: async ({ commentId, reply }: { commentId: number; reply: string }) => {
      const result = await feedbackApi.replyToComment(commentId, reply);
      if (!result.success) {
        throw new Error(result.error?.message || "Failed to reply");
      }
      return result.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.feedback.all });
      setIsReplyModalOpen(false);
      setReplyingToId(null);
      setSelectedFeedback(null);
      toast(t("feedback.replySent"), "success");
    },
    onError: (error) => {
      toast(error instanceof Error ? error.message : t("feedback.replyError"), "error");
    },
  });

  // Combine all feedback items
  const feedbackItems = useMemo<FeedbackItem[]>(() => {
    const items: FeedbackItem[] = [];

    if (pulseData?.success && pulseData.data?.items) {
      for (const item of pulseData.data.items) {
        items.push({
          ...item,
          type: "pulse" as FeedbackType,
          department_id: null,
          allow_contact: false,
          contact_email: null,
          reply: null,
        } as FeedbackItem);
      }
    }

    if (experienceData?.success && experienceData.data?.items) {
      for (const item of experienceData.data.items) {
        items.push({
          ...item,
          type: "experience" as FeedbackType,
          department_id: null,
          allow_contact: false,
          contact_email: null,
          reply: null,
        } as FeedbackItem);
      }
    }

    if (commentsData?.success && commentsData.data?.items) {
      for (const item of commentsData.data.items) {
        items.push({
          ...item,
          type: "comment" as FeedbackType,
        } as FeedbackItem);
      }
    }

    // Sort by submitted_at descending
    return items.sort(
      (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
    );
  }, [pulseData, experienceData, commentsData]);

  // Apply type and anonymity filters
  const filteredItems = useMemo(() => {
    let items = feedbackItems;

    // Apply type filter
    if (typeFilter !== "all") {
      items = items.filter((item) => item.type === typeFilter);
    }

    // Apply anonymity filter
    if (anonymityFilter !== "all") {
      const isAnonymous = anonymityFilter === "anonymous";
      items = items.filter((item) => item.is_anonymous === isAnonymous);
    }

    return items;
  }, [feedbackItems, typeFilter, anonymityFilter]);

  // Calculate totals based on type filter
  const totalCount = useMemo(() => {
    if (typeFilter === "pulse") return pulseData?.success ? pulseData.data?.total || 0 : 0;
    if (typeFilter === "experience") return experienceData?.success ? experienceData.data?.total || 0 : 0;
    if (typeFilter === "comment") return commentsData?.success ? commentsData.data?.total || 0 : 0;
    // typeFilter === "all" - sum all totals
    return (
      (pulseData?.success ? pulseData.data?.total || 0 : 0) +
      (experienceData?.success ? experienceData.data?.total || 0 : 0) +
      (commentsData?.success ? commentsData.data?.total || 0 : 0)
    );
  }, [pulseData, experienceData, commentsData, typeFilter]);

  const totalPages = useMemo(() => Math.ceil(totalCount / pageSize), [totalCount, pageSize]);

  const totalComments = commentsData?.success ? commentsData.data?.total || 0 : 0;

  const commentsWithReply = useMemo(() => {
    return (
      commentsData?.success && commentsData.data?.items ? commentsData.data.items.filter((c: any) => c.reply).length : 0
    );
  }, [commentsData]);

  // Handlers
  const getUserName = useCallback(
    (id: number | null): string => {
      if (id === null || id === undefined) return "-";
      return usersData?.get(id) ?? String(id);
    },
    [usersData]
  );

  const viewDetails = useCallback((item: FeedbackItem) => {
    setSelectedFeedback(item);
  }, []);

  const handleReply = useCallback((commentId: number) => {
    const item = feedbackItems.find((feedbackItem) => feedbackItem.type === "comment" && feedbackItem.id === commentId);
    setSelectedFeedback(item ?? null);
    setReplyingToId(commentId);
    setIsReplyModalOpen(true);
  }, [feedbackItems]);

  const submitReply = useCallback(
    async (reply: string) => {
      if (replyingToId === null) return;
      await replyMutation.mutateAsync({ commentId: replyingToId, reply });
    },
    [replyingToId, replyMutation]
  );

  const resetFilters = useCallback(() => {
    setTypeFilter("all");
    setAnonymityFilter("all");
    setCurrentPage(1);
  }, []);

  const invalidate = useCallback(() => {
    refetchPulse();
    refetchExperience();
    refetchComments();
  }, [refetchPulse, refetchExperience, refetchComments]);

  return {
    // Data
    feedbackItems: filteredItems,
    loading: isPulseLoading || isExperienceLoading || isCommentsLoading,
    selectedFeedback,
    isReplyModalOpen,
    replyingToId,
    replySubmitting: replyMutation.isPending,

    // Stats
    pulseStats: pulseStats?.success ? pulseStats.data as PulseStats | undefined : undefined,
    experienceStats: experienceStats?.success ? experienceStats.data as ExperienceStats | undefined : undefined,
    pulseAnonymityStats: pulseAnonymityStats?.success ? pulseAnonymityStats.data as AnonymityStats | undefined : undefined,
    totalComments,
    commentsWithReply,

    // Pagination
    currentPage,
    setCurrentPage,
    totalCount,
    totalPages,
    pageSize,
    setPageSize,

    // Sorting
    sortField,
    sortDirection,
    toggleSort,

    // Filters
    typeFilter,
    setTypeFilter,
    handleTypeFilterChange,
    anonymityFilter,
    setAnonymityFilter,
    handleAnonymityFilterChange,

    // Handlers
    getUserName,
    viewDetails,
    handleReply,
    submitReply,
    resetFilters,
    invalidate,
    closeReplyModal: () => {
      setIsReplyModalOpen(false);
      setReplyingToId(null);
      setSelectedFeedback(null);
    },
    closeDetails: () => setSelectedFeedback(null),
  };
}
