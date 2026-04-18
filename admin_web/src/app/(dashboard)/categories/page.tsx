"use client";

import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { PageContent } from "@/components/layout/page-content";
import { Plus, SquarePen, Trash2 } from "lucide-react";
import { useCategories, CategoryRow, CategoryFormData } from "@/hooks/use-categories";
import { useDepartments } from "@/hooks/use-departments";
import { EntityFormDialog } from "@/components/entity/entity-form-dialog";
import { SortableTableHead } from "@/components/ui/sortable-table-head";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTable } from "@/components/ui/data-table";
import { CardHeader, CardTitle } from "@/components/ui/card";
import { SearchInput } from "@/components/ui/search-input";
import { cn } from "@/lib/utils";

// ============================================================================
// Table Columns Definition
// ============================================================================

interface Column {
  key: string;
  title: string;
  width?: string;
  sortable?: boolean;
  render: (item: CategoryRow) => React.ReactNode;
}

function useColumns(
  tCommon: (key: string) => string | undefined,
  tKnowledge: (key: string) => string | undefined
): Column[] {
  return [
    {
      key: "name",
      title: tCommon("name") ?? "Name",
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
      key: "slug",
      title: tKnowledge("slug") ?? "Slug",
      sortable: true,
      render: (item: CategoryRow) => <span className="text-muted-foreground text-sm">{item.slug}</span>,
    },
    {
      key: "parent",
      title: tKnowledge("parentCategory") ?? "Parent Category",
      render: (item: CategoryRow) => item.parent_name || "—",
    },
    {
      key: "department",
      title: tCommon("department") ?? "Department",
      render: (item: CategoryRow) => item.department || "—",
    },
    {
      key: "position",
      title: tCommon("position") ?? "Position",
      render: (item: CategoryRow) => item.position || "—",
    },
    {
      key: "level",
      title: tKnowledge("level") ?? "Level",
      render: (item: CategoryRow) => item.level || "—",
    },
    {
      key: "stats",
      title: tKnowledge("articles") ?? "Articles",
      width: "w-24",
      sortable: true,
      render: (item: CategoryRow) => (
        <div className="flex flex-col gap-1 text-sm">
          <span>{item.articles_count} {tKnowledge("articlesShort") ?? "art."}</span>
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
      title: tCommon("actions") ?? "Actions",
      width: "w-24",
      render: (_item: CategoryRow) => null, // Actions are handled separately
    },
  ];
}

// ============================================================================
// Form Component
// ============================================================================

interface CategoryFormProps {
  formData: CategoryFormData;
  onChange: (data: CategoryFormData) => void;
  categories: CategoryRow[];
  departments: { id: number; name: string }[];
  isEdit?: boolean;
}

function CategoryForm({ formData, onChange, categories, departments, isEdit }: CategoryFormProps) {
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");

  // Filter out the current category and its children to prevent circular references
  const availableParents = isEdit
    ? categories.filter((c) => c.id !== (formData as unknown as { id: number }).id)
    : categories;

  const parentOptions = [
    { value: "0", label: tCommon("notSelected") ?? "Not selected" },
    ...availableParents.map((c) => ({
      value: String(c.id),
      label: c.parent_id ? `— ${c.name}` : c.name,
    })),
  ];

  const departmentOptions = [
    { value: "0", label: tCommon("notSelected") ?? "Not selected" },
    ...departments.map((d) => ({ value: String(d.id), label: d.name })),
  ];

  const handleChange = (field: keyof CategoryFormData, value: string | number) => {
    onChange({ ...formData, [field]: value });
  };

  return (
    <div className="grid gap-4 py-4">
      <div className="grid gap-2">
        <label className="text-sm font-medium">{t("name")} *</label>
        <Input
          placeholder={t("name") ?? "Name"}
          value={formData.name}
          onChange={(e) => handleChange("name", e.target.value)}
        />
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium">{t("slug")}</label>
        <Input
          placeholder={t("slug") ?? "Slug"}
          value={formData.slug}
          onChange={(e) => handleChange("slug", e.target.value)}
          disabled={isEdit}
        />
        {isEdit && (
          <p className="text-muted-foreground text-xs">{t("slugImmutable")}</p>
        )}
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium">{tCommon("description")}</label>
        <Textarea
          placeholder={tCommon("description") ?? "Description"}
          value={formData.description}
          onChange={(e) => handleChange("description", e.target.value)}
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("parentCategory")}</label>
          <Select
            value={formData.parent_id ? String(formData.parent_id) : "0"}
            onChange={(val) => handleChange("parent_id", parseInt(val) || 0)}
            options={parentOptions}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{tCommon("department")}</label>
          <Select
            value={formData.department_id ? String(formData.department_id) : "0"}
            onChange={(val) => handleChange("department_id", parseInt(val) || 0)}
            options={departmentOptions}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("position")}</label>
          <Input
            placeholder={t("position") ?? "Position"}
            value={formData.position}
            onChange={(e) => handleChange("position", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("level")}</label>
          <Input
            placeholder={t("level") ?? "Level"}
            value={formData.level}
            onChange={(e) => handleChange("level", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("order")}</label>
          <Input
            type="number"
            value={formData.order}
            onChange={(e) => handleChange("order", parseInt(e.target.value) || 0)}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("icon")}</label>
          <Input
            placeholder={t("icon") ?? "Icon (e.g. Folder)"}
            value={formData.icon}
            onChange={(e) => handleChange("icon", e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <label className="text-sm font-medium">{t("color")}</label>
          <div className="flex items-center gap-2">
            <Input
              placeholder="#3b82f6"
              value={formData.color}
              onChange={(e) => handleChange("color", e.target.value)}
            />
            {formData.color && (
              <span
                className="inline-block size-9 shrink-0 rounded-md border"
                style={{ backgroundColor: formData.color }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================

export default function CategoriesPage() {
  const t = useTranslations("knowledge");
  const tCommon = useTranslations("common");
  const categories = useCategories();
  const departments = useDepartments();

  const columns = useColumns(tCommon, t);

  // Create dialog
  const createDialog = (
    <EntityFormDialog
      isOpen={categories.isCreateDialogOpen}
      onClose={() => categories.setIsCreateDialogOpen(false)}
      onSubmit={categories.handleSubmit}
      title={t("addCategoryTitle") ?? "Add Category"}
      description={t("createNewCategory") ?? "Create a new category"}
      submitLabel={tCommon("create") ?? "Create"}
      cancelLabel={tCommon("cancel") ?? "Cancel"}
      isSubmitting={categories.isSubmitting}
      isValid={!!categories.formData.name}
      formData={categories.formData}
    >
      <CategoryForm
        formData={categories.formData}
        onChange={categories.setFormData}
        categories={categories.categories}
        departments={departments.items}
      />
    </EntityFormDialog>
  );

  // Edit dialog
  const editDialog = (
    <EntityFormDialog
      isOpen={categories.isEditDialogOpen}
      onClose={() => {
        categories.setIsEditDialogOpen(false);
        categories.setSelectedCategory(null);
      }}
      onSubmit={categories.handleSubmit}
      title={t("editCategoryTitle") ?? "Edit Category"}
      description={t("changeCategory") ?? "Change category details"}
      submitLabel={tCommon("save") ?? "Save"}
      cancelLabel={tCommon("cancel") ?? "Cancel"}
      isSubmitting={categories.isSubmitting}
      isValid={!!categories.formData.name}
      formData={categories.formData}
    >
      <CategoryForm
        formData={categories.formData}
        onChange={categories.setFormData}
        categories={categories.categories}
        departments={departments.items}
        isEdit
      />
    </EntityFormDialog>
  );

  return (
    <PageContent
      title={t("categories") ?? "Categories"}
      subtitle={t("title") ?? "Knowledge Base"}
      actions={
        <Button
          className="gap-2"
          onClick={() => {
            categories.resetForm();
            categories.setIsCreateDialogOpen(true);
          }}
        >
          <Plus className="size-4" />
          {t("addCategory") ?? "Add Category"}
        </Button>
      }
    >
      {createDialog}
      {editDialog}

      <DataTable
        loading={categories.loading}
        empty={categories.categories.length === 0}
        currentPage={categories.currentPage}
        totalPages={categories.totalPages}
        totalCount={categories.totalCount}
        pageSize={categories.pageSize}
        onPageChange={categories.setCurrentPage}
        onPageSizeChange={categories.setPageSize}
        showPageSizeSelector={true}
        header={
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                {t("categories") ?? "Categories"}{" "}
                <span className="text-muted-foreground text-sm font-normal">
                  ({categories.totalCount ?? categories.categories.length})
                </span>
              </CardTitle>
              <div className="flex gap-2">
                <SearchInput
                  value={categories.searchQuery}
                  onChange={categories.setSearchQuery}
                />
                <Button variant="outline" onClick={categories.resetFilters}>
                  {tCommon("reset") ?? "Reset"}
                </Button>
              </div>
            </div>
          </CardHeader>
        }
      >
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <SortableTableHead
                  key={col.key}
                  field={col.key}
                  sortable={col.sortable}
                  sortField={categories.sortField ?? null}
                  sortDirection={categories.sortDirection}
                  onSort={categories.toggleSort}
                  width={col.width}
                >
                  {col.title}
                </SortableTableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {categories.categories.map((category) => (
              <TableRow
                key={category.id}
                className={cn(
                  "cursor-pointer",
                  category.parent_id && "bg-muted/50"
                )}
                onClick={() => categories.openEdit(category)}
              >
                {columns.map((col) => (
                  <TableCell key={col.key}>
                    {col.key === "actions" ? (
                      <div
                        className="flex gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => categories.openEdit(category)}
                        >
                          <SquarePen className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-500"
                          onClick={() => categories.handleDelete(category.id)}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    ) : (
                      col.render(category)
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </DataTable>
    </PageContent>
  );
}
