import { useState, useMemo, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { feedbackApi } from "@/lib/api/feedback";
import type {
  PulseSurvey,
  ExperienceRating,
  Comment,
  FeedbackItem,
  PulseStats,
  ExperienceStats,
  AnonymityStats,
  FeedbackType,
} from "@/types";

interface FeedbackFilters {
  search?: string;
  type?: FeedbackType | "all";
  anonymity?: "all" | "anonymous" | "attributed";
  from_date?: string;
  to_date?: string;
}

export function useFeedback() {
  const queryClient = useQueryClient();

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  // Search and filters
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<FeedbackType | "all">("all");
  const [anonymityFilter, setAnonymityFilter] = useState<"all" | "anonymous" | "attributed">("all");

  // Modal state
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null);
  const [isReplyModalOpen, setIsReplyModalOpen] = useState(false);
  const [replyingToId, setReplyingToId] = useState<number | null>(null);

  // Calculate skip based on page
  const skip = useMemo(() => (currentPage - 1) * pageSize, [currentPage, pageSize]);

  // Fetch pulse surveys
  const {
    data: pulseData,
    isLoading: isPulseLoading,
    refetch: refetchPulse,
  } = useQuery({
    queryKey: queryKeys.feedback.pulse({ skip, limit: pageSize }),
    queryFn: () =>
      feedbackApi.getPulseSurveys({
        skip,
        limit: pageSize,
        from_date: undefined,
        to_date: undefined,
      }),
    staleTime: 60 * 1000,
  });

  // Fetch experience ratings
  const {
    data: experienceData,
    isLoading: isExperienceLoading,
    refetch: refetchExperience,
  } = useQuery({
    queryKey: queryKeys.feedback.experience({ skip, limit: pageSize }),
    queryFn: () =>
      feedbackApi.getExperienceRatings({
        skip,
        limit: pageSize,
        from_date: undefined,
        to_date: undefined,
      }),
    staleTime: 60 * 1000,
  });

  // Fetch comments
  const {
    data: commentsData,
    isLoading: isCommentsLoading,
    refetch: refetchComments,
  } = useQuery({
    queryKey: queryKeys.feedback.comments({ skip, limit: pageSize }),
    queryFn: () =>
      feedbackApi.getComments({
        skip,
        limit: pageSize,
        search: searchQuery || undefined,
        from_date: undefined,
        to_date: undefined,
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

  // Fetch anonymity stats
  const { data: pulseAnonymityStats } = useQuery({
    queryKey: queryKeys.feedback.pulseAnonymityStats(),
    queryFn: () => feedbackApi.getPulseAnonymityStats(),
    staleTime: 5 * 60 * 1000,
  });

  const { data: experienceAnonymityStats } = useQuery({
    queryKey: queryKeys.feedback.experienceAnonymityStats(),
    queryFn: () => feedbackApi.getExperienceAnonymityStats(),
    staleTime: 5 * 60 * 1000,
  });

  const { data: commentAnonymityStats } = useQuery({
    queryKey: queryKeys.feedback.commentAnonymityStats(),
    queryFn: () => feedbackApi.getCommentAnonymityStats(),
    staleTime: 5 * 60 * 1000,
  });

  // Fetch users for name lookup
  const { data: usersData } = useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => api.users.list({ limit: 1000 }),
    select: (result) => {
      const map = new Map<number, string>();
      if (result.data) {
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
    mutationFn: ({ commentId, reply }: { commentId: number; reply: string }) =>
      feedbackApi.replyToComment(commentId, reply),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.feedback.all });
      setIsReplyModalOpen(false);
      setReplyingToId(null);
    },
  });

  // Combine all feedback items
  const feedbackItems = useMemo<FeedbackItem[]>(() => {
    const items: FeedbackItem[] = [];

    if (pulseData?.data?.items) {
      items.push(
        ...pulseData.data.items.map((item: PulseSurvey) => ({
          ...item,
          type: "pulse" as FeedbackType,
        }))
      );
    }

    if (experienceData?.data?.items) {
      items.push(
        ...experienceData.data.items.map((item: ExperienceRating) => ({
          ...item,
          type: "experience" as FeedbackType,
        }))
      );
    }

    if (commentsData?.data?.items) {
      items.push(
        ...commentsData.data.items.map((item: Comment) => ({
          ...item,
          type: "comment" as FeedbackType,
        }))
      );
    }

    // Sort by submitted_at descending
    return items.sort(
      (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
    );
  }, [pulseData, experienceData, commentsData]);

  // Apply anonymity filter
  const filteredItems = useMemo(() => {
    let items = feedbackItems;

    if (anonymityFilter !== "all") {
      const isAnonymous = anonymityFilter === "anonymous";
      items = items.filter((item) => item.is_anonymous === isAnonymous);
    }

    return items;
  }, [feedbackItems, anonymityFilter]);

  // Calculate totals
  const totalCount = useMemo(() => {
    return (
      (pulseData?.data?.total || 0) +
      (experienceData?.data?.total || 0) +
      (commentsData?.data?.total || 0)
    );
  }, [pulseData, experienceData, commentsData]);

  const totalPages = useMemo(() => Math.ceil(totalCount / pageSize), [totalCount, pageSize]);

  const totalComments = commentsData?.data?.total || 0;

  const commentsWithReply = useMemo(() => {
    return (
      commentsData?.data?.items?.filter((c: Comment) => c.reply)?.length || 0
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
    setReplyingToId(commentId);
    setIsReplyModalOpen(true);
  }, []);

  const submitReply = useCallback(
    async (reply: string) => {
      if (replyingToId === null) return;
      await replyMutation.mutateAsync({ commentId: replyingToId, reply });
    },
    [replyingToId, replyMutation]
  );

  const resetFilters = useCallback(() => {
    setSearchQuery("");
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

    // Stats
    pulseStats: pulseStats?.data as PulseStats | undefined,
    experienceStats: experienceStats?.data as ExperienceStats | undefined,
    pulseAnonymityStats: pulseAnonymityStats?.data as AnonymityStats | undefined,
    experienceAnonymityStats: experienceAnonymityStats?.data as AnonymityStats | undefined,
    commentAnonymityStats: commentAnonymityStats?.data as AnonymityStats | undefined,
    totalComments,
    commentsWithReply,

    // Pagination
    currentPage,
    setCurrentPage,
    totalCount,
    totalPages,
    pageSize,
    setPageSize,

    // Search & Filters
    searchQuery,
    setSearchQuery,
    typeFilter,
    setTypeFilter,
    anonymityFilter,
    setAnonymityFilter,

    // Handlers
    getUserName,
    viewDetails,
    handleReply,
    submitReply,
    resetFilters,
    invalidate,
    closeReplyModal: () => setIsReplyModalOpen(false),
    closeDetails: () => setSelectedFeedback(null),
  };
}
