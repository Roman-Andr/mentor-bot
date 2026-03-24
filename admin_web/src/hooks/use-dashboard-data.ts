import { useState, useEffect, useCallback } from "react";
import { api, type OnboardingProgress, type EscalationRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

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
      const [checklistResult, usersResult, escalationResult] = await Promise.all([
        api.analytics.checklistStats(),
        api.users.list({ limit: 1 }),
        api.escalations.list({ limit: 100 }),
      ]);

      if (checklistResult.data) {
        const cs = checklistResult.data;
        setStats({
          total_users: usersResult.data?.total || 0,
          active_newbies: cs.in_progress || 0,
          completed_onboarding: cs.completed || 0,
          pending_tasks: cs.not_started || 0,
          overdue_tasks: cs.overdue || 0,
          average_completion_days: Math.round(cs.avg_completion_days) || 0,
        });
        setDepartments(cs.by_department || {});
      }

      if (escalationResult.data) {
        const requests = escalationResult.data.requests;
        setEscalations({
          hr: requests.filter((r: EscalationRequest) => r.type === "HR").length,
          mentor: requests.filter((r: EscalationRequest) => r.type === "MENTOR").length,
          inProgress: requests.filter((r: EscalationRequest) => r.status === "IN_PROGRESS")
            .length,
        });
      }

      const onboardingResult = await api.analytics.onboardingProgress();
      if (onboardingResult.data) {
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
                user_name: c.employee_id || `User ${c.user_id}`,
                department: c.department || "Unknown",
                start_date: c.start_date,
                completion_percentage: c.progress_percentage,
                days_remaining: c.days_remaining || 0,
                status: c.status,
              }),
            ),
        );
      }

      setActivity([
        {
          user: "Система",
          action: "Загрузила данные",
          task: "Дашборд обновлён",
          time: "Сейчас",
        },
      ]);
    } catch (err) {
      setError("Ошибка загрузки данных");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [authLoading]);

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
