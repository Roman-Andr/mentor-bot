"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */
import { useTranslations } from "@/hooks/use-translations";
import { UserFormDialog } from "@/components/features/users/user-form-dialog";
import { UsersTable } from "@/components/features/users/users-table";
import { AssignMentorDialog } from "@/components/features/users/assign-mentor-dialog";

interface UsersSectionProps {
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;
  formData: any;
  setFormData: (data: any) => void;
  handleCreateUser: any;
  handleUpdateUser: any;
  setSelectedUser: any;
  departments: any[];
  users: any[];
  loading: boolean;
  openEditDialog: (user: any) => void;
  handleDeleteUser: (id: number) => Promise<void>;
  openAssignMentorDialog: (user: any) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  roleFilter: string;
  setRoleFilter: (filter: string) => void;
  departmentFilter: string;
  setDepartmentFilter: (filter: string) => void;
  resetFilters: () => void;
  currentPage: number;
  totalPages: number;
  totalUsers: number;
  pageSize: number;
  setCurrentPage: (page: number) => void;
  setPageSize: (size: number) => void;
  sortField?: string | null;
  sortDirection?: "asc" | "desc";
  toggleSort: (field: string) => void;
  assignMentorDialogOpen: boolean;
  setAssignMentorDialogOpen: (open: boolean) => void;
  selectedUserForMentor: any;
  handleAssignMentor: (userId: number, mentorId: number) => Promise<void>;
  handleUnassignMentor: (mentorRelationId: number) => Promise<void>;
  currentMentor: any;
}

export function UsersSection({
  isCreateDialogOpen,
  setIsCreateDialogOpen,
  isEditDialogOpen,
  setIsEditDialogOpen,
  formData,
  setFormData,
  handleCreateUser,
  handleUpdateUser,
  setSelectedUser,
  departments,
  users,
  loading,
  openEditDialog,
  handleDeleteUser,
  openAssignMentorDialog,
  searchQuery,
  setSearchQuery,
  roleFilter,
  setRoleFilter,
  departmentFilter,
  setDepartmentFilter,
  resetFilters,
  currentPage,
  totalPages,
  totalUsers,
  pageSize,
  setCurrentPage,
  setPageSize,
  sortField,
  sortDirection,
  toggleSort,
  assignMentorDialogOpen,
  setAssignMentorDialogOpen,
  selectedUserForMentor,
  handleAssignMentor,
  handleUnassignMentor,
  currentMentor,
}: UsersSectionProps) {
  const t = useTranslations();

  return (
    <>
      <UserFormDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        mode="create"
        formData={formData}
        onFormDataChange={setFormData}
        onSubmit={handleCreateUser}
        onCancel={() => setIsCreateDialogOpen(false)}
        departments={departments}
      />

      <UserFormDialog
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        mode="edit"
        formData={formData}
        onFormDataChange={setFormData}
        onSubmit={handleUpdateUser}
        onCancel={() => {
          setIsEditDialogOpen(false);
          setSelectedUser(null);
        }}
        departments={departments}
      />

      <UsersTable
        users={users}
        loading={loading}
        onEdit={openEditDialog}
        onDelete={handleDeleteUser}
        onAssignMentor={openAssignMentorDialog}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        roleFilter={roleFilter}
        onRoleFilterChange={setRoleFilter}
        departmentFilter={departmentFilter}
        onDepartmentFilterChange={setDepartmentFilter}
        onReset={resetFilters}
        departments={departments}
        currentPage={currentPage}
        totalPages={totalPages}
        totalCount={totalUsers}
        pageSize={pageSize}
        onPageChange={setCurrentPage}
        onPageSizeChange={setPageSize}
        sortField={sortField}
        sortDirection={sortDirection}
        onSort={toggleSort}
      />

      <AssignMentorDialog
        isOpen={assignMentorDialogOpen}
        onOpenChange={setAssignMentorDialogOpen}
        userId={selectedUserForMentor?.id || null}
        userName={selectedUserForMentor?.name || ""}
        onAssign={handleAssignMentor}
        onUnassign={handleUnassignMentor}
        currentMentor={currentMentor}
      />
    </>
  );
}
