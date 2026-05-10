"use client";
import { Dialog } from "@/shared/ui/dialog";
import { DepartmentsTable } from "@/widgets/users/departments-table";
import { DepartmentFormDialog } from "@/widgets/users/department-form-dialog";
import type { DepartmentFormData, DepartmentRow } from "@/shared/hooks/use-departments";
import type { SortDirection } from "@/shared/hooks/use-sorting";

interface DepartmentsSectionProps {
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;
  formData: DepartmentFormData;
  updateFormField: <K extends keyof DepartmentFormData>(
    field: K,
    value: DepartmentFormData[K],
  ) => void;
  handleSubmit: () => void;
  resetForm: () => void;
  items: DepartmentRow[];
  loading: boolean;
  isLoading: boolean;
  setSelectedItem: (item: DepartmentRow | null) => void;
  selectedItem: DepartmentRow | null;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize: number;
  setCurrentPage: (page: number) => void;
  setPageSize: (size: number) => void;
  openEditDialog: (item: DepartmentRow) => void;
  handleDelete: (id: number) => Promise<void>;
  sortField?: string | null;
  sortDirection?: SortDirection;
  onSort?: (field: string) => void;
}

export function DepartmentsSection({
  isCreateDialogOpen,
  setIsCreateDialogOpen,
  isEditDialogOpen,
  setIsEditDialogOpen,
  formData,
  updateFormField,
  handleSubmit,
  resetForm,
  items,
  loading,
  searchQuery,
  setSearchQuery,
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  sortField,
  sortDirection,
  onSort,
  setCurrentPage,
  setPageSize,
  openEditDialog,
  handleDelete,
}: DepartmentsSectionProps) {
  return (
    <>
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DepartmentFormDialog
          mode="create"
          formData={formData}
          onFormDataChange={updateFormField}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsCreateDialogOpen(false);
            resetForm();
          }}
        />
      </Dialog>
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DepartmentFormDialog
          mode="edit"
          formData={formData}
          onFormDataChange={updateFormField}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsEditDialogOpen(false);
            resetForm();
          }}
        />
      </Dialog>

      <DepartmentsTable
        departments={items}
        loading={loading}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        currentPage={currentPage}
        totalPages={totalPages}
        totalCount={totalCount}
        pageSize={pageSize}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={onSort}
        onPageChange={setCurrentPage}
        onPageSizeChange={setPageSize}
        onEdit={openEditDialog}
        onDelete={handleDelete}
      />
    </>
  );
}
