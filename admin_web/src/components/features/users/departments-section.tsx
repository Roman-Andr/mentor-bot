"use client";
import { Dialog } from "@/components/ui/dialog";
import { DepartmentsTable } from "@/components/features/users/departments-table";
import { DepartmentFormDialog } from "@/components/features/users/department-form-dialog";
import type { DepartmentFormData, DepartmentRow } from "@/hooks/use-departments";

interface DepartmentsSectionProps {
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;
  formData: DepartmentFormData;
  updateFormField: <K extends keyof DepartmentFormData>(field: K, value: DepartmentFormData[K]) => void;
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
        onPageChange={setCurrentPage}
        onPageSizeChange={setPageSize}
        onEdit={openEditDialog}
        onDelete={handleDelete}
      />
    </>
  );
}
