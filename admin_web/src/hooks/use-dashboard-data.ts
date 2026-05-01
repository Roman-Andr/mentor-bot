/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { api } from "@/lib/api";
import type { OnboardingProgress } from "@/types";
import { useAuth } from "@/hooks/use-auth";
import { logger } from "@/lib/logger";

interface Activity {
  user: string;
  action: string;
  task: string;
  time: string;
}

interface EscalationCounts {
  hr: number;
  mentor: number;
  inProgress: number;
}

interface DashboardStats {
  total_users: number;
  active_newbies: number;
  completed_onboarding: number;
  pending_tasks: number;
  overdue_tasks: number;
  average_completion_days: number;
}

interface UseDashboardDataResult {
  stats: DashboardStats;
  progress: OnboardingProgress[];
  activity: Activity[];
  departments: Record<string, number>;
  escalations: EscalationCounts;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useDashboardData(): UseDashboardDataResult {
  const t = useTranslations("dashboard");
  const { isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    total_users: 0,
    active_newbies: 0,
    completed_onboarding: 0,
    pending_tasks: 0,
    overdue_tasks: 0,
    average_completion_days: 0,
  });
  const [progress, setProgress] = useState<OnboardingProgress[]>([]);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [departments, setDepartments] = useState<Record<string, number>>({});
  const [escalations, setEscalations] = useState<EscalationCounts>({
    hr: 0,
    mentor: 0,
    inProgress: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (authLoading) return;
    setLoading(true);
    setError(null);
    try {
      const [checklistResult, usersResult, escalationResult, departmentsResult] = await Promise.all(
        [
          api.analytics.checklistStats(),
          api.users.list({ limit: 1 }),
          api.escalations.list({ limit: 100 }),
          api.departments.list({ limit: 500 }),
        ],
      );

      const deptMap = new Map<number, string>();
      if (departmentsResult.success && departmentsResult.data?.departments) {
        for (const dept of departmentsResult.data.departments) {
          deptMap.set(dept.id, dept.name);
        }
      }

      if (checklistResult.success && checklistResult.data) {
        const cs = checklistResult.data;
        setStats({
          total_users: (usersResult.success && usersResult.data?.total) || 0,
          active_newbies: cs.in_progress || 0,
          completed_onboarding: cs.completed || 0,
          pending_tasks: cs.not_started || 0,
          overdue_tasks: cs.overdue || 0,
          average_completion_days: Math.round(cs.avg_completion_days) || 0,
        });
        const deptBreakdown: Record<string, number> = {};
        for (const [deptId, count] of Object.entries(cs.by_department || {})) {
          const name = deptMap.get(Number(deptId)) || deptId;
          deptBreakdown[name] = (deptBreakdown[name] || 0) + count;
        }
        setDepartments(deptBreakdown);
      }

      // Process escalation data
      if (escalationResult.success && escalationResult.data?.requests) {
        const items = escalationResult.data.requests;
        const counts: EscalationCounts = {
          hr: items.filter((e) => e.type === "HR").length,
          mentor: items.filter((e) => e.type === "MENTOR").length,
          inProgress: items.filter((e) => e.status === "IN_PROGRESS").length,
        };
        setEscalations(counts);
      }

      const onboardingResult = await api.analytics.onboardingProgress();
      const allUsersResult = await api.users.list({ limit: 500 });
      const usersMap = new Map<number, string>();
      if (allUsersResult.success && allUsersResult.data?.users) {
        for (const user of allUsersResult.data.users) {
          usersMap.set(user.id, `${user.first_name}${user.last_name ? ` ${user.last_name}` : ""}`);
        }
      }
      if (onboardingResult.success && onboardingResult.data) {
        const data = onboardingResult.data;
        const checklists = data.checklists || [];
        setProgress(
          checklists
            .slice(0, 5)
            .map(
              (c: {
                user_id: number;
                employee_id?: string;
                department?: string;
                start_date: string;
                progress_percentage: number;
                days_remaining?: number;
                status: string;
              }) => ({
                user_id: c.user_id,
                user_name: usersMap.get(c.user_id) || c.employee_id || `User ${c.user_id}`,
                department: c.department || "Unknown",
                start_date: c.start_date,
                completion_percentage: c.progress_percentage,
                days_remaining: c.days_remaining || 0,
                status: c.status,
              }),
            ),
        );
      }

      // Set initial activity with system message
      setActivity([
        {
          user: t("system"),
          action: t("loadedData"),
          task: t("dashboardUpdated"),
          time: t("now"),
        },
      ]);
    } catch (err) {
      setError(t("errorLoading"));
      logger.error("Failed to load dashboard data", { error: err });
    } finally {
      setLoading(false);
    }
  }, [authLoading, t]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    stats,
    progress,
    activity,
    departments,
    escalations,
    loading: loading || authLoading,
    error,
    refetch: fetchData,
  };
}
