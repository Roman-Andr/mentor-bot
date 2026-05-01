import type { CategoryRow } from "@/hooks/use-categories";

interface Column {
  key: string;
  title: string;
  width?: string;
  sortable?: boolean;
  render: (item: CategoryRow) => React.ReactNode;
}

export function useCategoriesColumns(
  tCommon: (key: string) => string | undefined,
  tKnowledge: (key: string) => string | undefined
): Column[] {
  return [
    {
      key: "name",
      title: tCommon("common.name") ?? "Name",
      sortable: true,
      render: (item: CategoryRow) => (
        <div>
          <div className="flex items-center gap-2">
            {item.color && (
              <span
                className="inline-block size-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
            )}
            <span className="font-medium">{item.name}</span>
          </div>
          {item.description && (
            <p className="text-muted-foreground text-sm">{item.description}</p>
          )}
        </div>
      ),
    },
    {
      key: "department",
      title: tCommon("common.department") ?? "Department",
      sortable: true,
      render: (item: CategoryRow) => item.department || "—",
    },
    {
      key: "position",
      title: tCommon("common.position") ?? "Position",
      sortable: true,
      render: (item: CategoryRow) => item.position || "—",
    },
    {
      key: "level",
      title: tKnowledge("level") ?? "Level",
      sortable: true,
      render: (item: CategoryRow) => item.level || "—",
    },
    {
      key: "articlesCount",
      title: tKnowledge("articles") ?? "Articles",
      width: "w-24",
      sortable: true,
      render: (item: CategoryRow) => (
        <div className="flex flex-col gap-1 text-sm">
          <span>{item.articles_count}</span>
          {item.children_count > 0 && (
            <span className="text-muted-foreground text-xs">{item.children_count} {tKnowledge("subcategories") ?? "subcat."}</span>
          )}
        </div>
      ),
    },
    {
      key: "order",
      title: tKnowledge("order") ?? "Order",
      width: "w-20",
      sortable: true,
      render: (item: CategoryRow) => item.order,
    },
    {
      key: "actions",
      title: tCommon("common.actions") ?? "Actions",
      width: "w-24",
      render: (_item: CategoryRow) => null,
    },
  ];
}
