import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { queryKeys, getEntityListKey } from "@/lib/query-keys";
import type { ListParams } from "../use-queries";
import type { UseEntityOptions } from "./types";

export function useEntityQuery<TItem>(
  options: Pick<UseEntityOptions<TItem, unknown, unknown, unknown>, "queryKeyPrefix" | "listFn" | "listDataKey" | "mapItem">,
  queryParams: ListParams,
) {
  const { queryKeyPrefix, listFn, listDataKey = "items", mapItem } = options;

  const listQueryKey = useMemo(
    () => {
      const keyConfig = queryKeys[queryKeyPrefix];
      if ("list" in keyConfig && typeof keyConfig.list === "function") {
        return keyConfig.list(queryParams);
      }
      return [queryKeyPrefix, "list", queryParams];
    },
    [queryKeyPrefix, queryParams],
  );

  const { data: listData, isLoading: loading } = useQuery({
    queryKey: listQueryKey,
    queryFn: () => listFn(queryParams),
    select: (result) => {
      if (!result.success || !result.data) return undefined;

      // Handle case when API returns an array directly
      if (Array.isArray(result.data)) {
        return {
          items: result.data.map(mapItem),
          total: result.data.length,
          pages: 1,
        };
      }

      // Extract items using the specified key or default
      const data = result.data as Record<string, unknown>;
      const rawItems = (data[listDataKey] ?? data.items ?? []) as unknown[];

      return {
        items: rawItems.map(mapItem),
        total: (data.total as number | undefined) ?? 0,
        pages: (data.pages as number | undefined) ?? 1,
      };
    },
  });

  const items = listData?.items ?? [];
  const totalCount = listData?.total ?? 0;
  const totalPages = listData?.pages ?? 1;

  return { items, loading, totalCount, totalPages, listQueryKey };
}
