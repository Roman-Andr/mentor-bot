"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationTemplatesApi } from "@/lib/api/notification-templates";
import { queryKeys } from "@/lib/query-keys";
import type {
  NotificationTemplate,
  NotificationTemplateCreate,
  NotificationTemplateUpdate,
  NotificationTemplateRenderRequest,
  NotificationTemplateRenderResponse,
} from "@/types/notification";

export function useNotificationTemplates(params?: {
  skip?: number;
  limit?: number;
  name?: string;
  channel?: string;
  language?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: queryKeys.notificationTemplates.list(params),
    queryFn: () => notificationTemplatesApi.list(params),
  });
}

export function useNotificationTemplate(id: number) {
  return useQuery({
    queryKey: queryKeys.notificationTemplates.detail(id),
    queryFn: () => notificationTemplatesApi.get(id),
    enabled: !!id,
  });
}

export function useCreateNotificationTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NotificationTemplateCreate) =>
      notificationTemplatesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notificationTemplates.all });
    },
  });
}

export function useUpdateNotificationTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: NotificationTemplateUpdate }) =>
      notificationTemplatesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notificationTemplates.all });
      queryClient.invalidateQueries({
        queryKey: queryKeys.notificationTemplates.detail(variables.id),
      });
    },
  });
}

export function useDeleteNotificationTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => notificationTemplatesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notificationTemplates.all });
    },
  });
}

export function useRenderNotificationTemplate() {
  return useMutation({
    mutationFn: (data: NotificationTemplateRenderRequest) =>
      notificationTemplatesApi.render(data),
  });
}

export function usePreviewNotificationTemplate() {
  return useMutation({
    mutationFn: (data: { body_text?: string | null; body_html?: string | null; subject?: string | null; variables: Record<string, string> }) =>
      notificationTemplatesApi.preview(data),
  });
}
