import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usersApi, type UserPreferences, type UserPreferencesUpdate } from "@/lib/api/users";
import { queryKeys } from "@/lib/query-keys";

export function usePreferences() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.preferences(),
    queryFn: () => usersApi.getMyPreferences(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const updateMutation = useMutation({
    mutationFn: (data: UserPreferencesUpdate) => usersApi.updateMyPreferences(data),
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.preferences() });

      // Snapshot previous value
      const previousPreferences = queryClient.getQueryData<UserPreferences>(queryKeys.preferences());

      // Optimistically update
      if (previousPreferences) {
        queryClient.setQueryData<UserPreferences>(queryKeys.preferences(), {
          ...previousPreferences,
          ...newData,
        });
      }

      return { previousPreferences };
    },
    onError: (err, newData, context) => {
      // Rollback on error
      if (context?.previousPreferences) {
        queryClient.setQueryData(queryKeys.preferences(), context.previousPreferences);
      }
    },
    onSettled: () => {
      // Refetch after error or success
      queryClient.invalidateQueries({ queryKey: queryKeys.preferences() });
    },
  });

  return {
    preferences: query.data,
    isLoading: query.isLoading,
    error: query.error,
    updatePreferences: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}
