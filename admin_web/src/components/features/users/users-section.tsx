"use client";

import { UserFormDialog } from "@/components/features/users/user-form-dialog";
import { UsersTable } from "@/components/features/users/users-table";
import { AssignMentorDialog } from "@/components/features/users/assign-mentor-dialog";
import type { UserFormData } from "@/hooks/use-users";
import type { UserItem } from "@/hooks/use-users";
import type { Department } from "@/types/department";
import type { UserMentor } from "@/types/user";

interface UsersSectionProps {
  isCreateDialogOpen: boolean;
  setIsCreateDialogOpen: (open: boolean) => void;
  isEditDialogOpen: boolean;
  setIsEditDialogOpen: (open: boolean) => void;
  formData: UserFormData;
  setFormData: (data: UserFormData) => void;
  handleCreateUser: () => void;
  handleUpdateUser: () => void;
  setSelectedUser: (user: UserItem | null) => void;
  selectedUser: UserItem | null;
  departments: Department[];
  users: UserItem[];
  loading: boolean;
  isLoading: boolean;
  openEditDialog: (user: UserItem) => void;
  handleDeleteUser: (id: number) => Promise<void>;
  openAssignMentorDialog: (user: UserItem) => void;
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
  selectedUserForMentor: UserItem | null;
  handleAssignMentor: (userId: number, mentorId: number) => Promise<void>;
  handleUnassignMentor: (mentorRelationId: number) => Promise<void>;
  currentMentor: UserMentor | null;
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
