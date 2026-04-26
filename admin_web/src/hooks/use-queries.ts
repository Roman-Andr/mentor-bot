import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { useTranslations } from "@/hooks/use-translations";

export interface ListParams {
  skip?: number;
  limit?: number;
  search?: string;
  [key: string]: unknown;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  pages: number;
  [key: string]: unknown;
}

export interface UseListQueryOptions<TItem, TParams extends ListParams> {
  queryKey: readonly (string | unknown)[];
  queryFn: (params: TParams) => Promise<{ data?: ListResponse<TItem>; error?: string }>;
  pageSize?: number;
  enabled?: boolean;
}

export function useListQuery<TItem, TParams extends ListParams = ListParams>({
  queryKey,
  queryFn,
  enabled = true,
}: UseListQueryOptions<TItem, TParams>) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey,
    queryFn: () => queryFn(queryKey[1] as TParams),
    enabled,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey });

  return {
    ...query,
    invalidate,
  };
}

export interface UseInfiniteListOptions<TItem, TParams extends ListParams> {
  queryKey: readonly (string | unknown)[];
  queryFn: (params: TParams) => Promise<{ data?: ListResponse<TItem>; error?: string }>;
  pageSize?: number;
  enabled?: boolean;
}

export function useInfiniteListQuery<TItem, TParams extends ListParams = ListParams>({
  queryKey,
  queryFn,
  pageSize = 20,
  enabled = true,
}: UseInfiniteListOptions<TItem, TParams>) {
  const queryClient = useQueryClient();

  const query = useInfiniteQuery({
    queryKey,
    queryFn: ({ pageParam = 0 }) => {
      const baseParams = queryKey[1] as TParams;
      return queryFn({ ...baseParams, skip: pageParam, limit: pageSize });
    },
    getNextPageParam: (lastPage, allPages) => {
      if (!lastPage?.data) return undefined;
      const { total } = lastPage.data;
      const loadedCount = allPages.reduce((sum, page) => sum + (page.data?.items?.length || 0), 0);
      return loadedCount < total ? loadedCount : undefined;
    },
    initialPageParam: 0,
    enabled,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey });

  return {
    ...query,
    invalidate,
  };
}

export interface UseMutationOptions<TData, TError = string> {
  onSuccess?: (data: TData) => void;
  onError?: (error: TError) => void;
  successMessage?: string;
  errorMessage?: string;
}

export function useMutate<TData, TError = string>(
  mutationFn: (variables: unknown) => Promise<{ data?: TData; error?: TError }>,
  options?: {
    onSuccess?: (data: TData) => void;
    onError?: (error: TError) => void;
    successMessage?: string;
    errorMessage?: string;
  },
) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const mutation = useMutation({
    mutationFn,
    onSuccess: (result) => {
      if (result.data) {
        options?.onSuccess?.(result.data);
        if (options?.successMessage) {
          toast(options.successMessage, "success");
        }
      } else if (result.error) {
        options?.onError?.(result.error);
        toast(String(result.error), "error");
      }
    },
    onError: (error: TError) => {
      options?.onError?.(error);
      toast(options?.errorMessage || String(error), "error");
    },
  });

  const invalidate = () => queryClient.invalidateQueries();

  return {
    ...mutation,
    invalidate,
  };
}

export function useCreate<TData, TVariables>(
  mutationFn: (data: TVariables) => Promise<{ data?: TData; error?: string }>,
  queryKeyToInvalidate?: readonly unknown[],
) {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const t = useTranslations("common");

  const mutation = useMutation({
    mutationFn,
    onSuccess: (result) => {
      if (result.data) {
        if (queryKeyToInvalidate) {
          queryClient.invalidateQueries({ queryKey: queryKeyToInvalidate });
        }
        toast(t("successfullyCreated"), "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: (error: string) => {
      toast(error, "error");
    },
  });

  return mutation;
}

export function useUpdate<TData, TVariables>(
  mutationFn: (data: TVariables) => Promise<{ data?: TData; error?: string }>,
  queryKeyToInvalidate?: readonly unknown[],
) {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const t = useTranslations("common");

  const mutation = useMutation({
    mutationFn,
    onSuccess: (result) => {
      if (result.data) {
        if (queryKeyToInvalidate) {
          queryClient.invalidateQueries({ queryKey: queryKeyToInvalidate });
        }
        toast(t("successfullyUpdated"), "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: (error: string) => {
      toast(error, "error");
    },
  });

  return mutation;
}

export function useDelete(
  mutationFn: (id: number) => Promise<{ data?: unknown; error?: string }>,
  queryKeyToInvalidate?: readonly unknown[],
) {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const t = useTranslations("common");

  const mutation = useMutation({
    mutationFn,
    onSuccess: (result) => {
      if (!result.error) {
        if (queryKeyToInvalidate) {
          queryClient.invalidateQueries({ queryKey: queryKeyToInvalidate });
        }
        toast(t("successfullyDeleted"), "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: (error: string) => {
      toast(error, "error");
    },
  });

  return mutation;
}
