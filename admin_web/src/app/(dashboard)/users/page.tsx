"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { PageContent } from "@/components/layout/page-content";
import { UserPlus, Building2, Users } from "lucide-react";
import { useUsers } from "@/hooks/use-users";
import { useDepartments } from "@/hooks/use-departments";
import { UserFormDialog } from "@/components/features/users/user-form-dialog";
import { UserFilters } from "@/components/features/users/user-filters";
import { UsersTable } from "@/components/features/users/users-table";
import { DepartmentsTable } from "@/components/features/users/departments-table";
import { DepartmentFormDialog } from "@/components/features/users/department-form-dialog";
import { cn } from "@/lib/utils";

type Tab = "users" | "departments";

export default function UsersPage() {
  const [activeTab, setActiveTab] = useState<Tab>("users");
  const u = useUsers();
  const d = useDepartments();

  const handleDepartmentSubmit = async () => {
    await d.handleSubmit();
    u.loadDepartments();
  };

  const handleDepartmentDelete = async (id: number) => {
    await d.handleDelete(id);
    u.loadDepartments();
  };

  return (
    <PageContent
      title="Пользователи"
      subtitle="Управление пользователями и отделами"
      actions={
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border">
            <button
              className={cn(
                "flex items-center gap-1.5 rounded-l-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "users"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("users")}
            >
              <Users className="size-4" />
              Пользователи
            </button>
            <button
              className={cn(
                "flex items-center gap-1.5 rounded-r-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "departments"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("departments")}
            >
              <Building2 className="size-4" />
              Отделы
            </button>
          </div>
          <Button
            className="gap-2"
            onClick={() => {
              if (activeTab === "users") {
                u.resetForm();
                u.setIsCreateDialogOpen(true);
              } else {
                d.resetForm();
                d.setIsCreateDialogOpen(true);
              }
            }}
          >
            {activeTab === "users" ? (
              <>
                <UserPlus className="size-4" />
                Добавить пользователя
              </>
            ) : (
              <>
                <Building2 className="size-4" />
                Добавить отдел
              </>
            )}
          </Button>
        </div>
      }
    >
      {activeTab === "users" && (
        <>
          <UserFormDialog
            open={u.isCreateDialogOpen}
            onOpenChange={u.setIsCreateDialogOpen}
            mode="create"
            formData={u.formData}
            onFormDataChange={u.setFormData}
            onSubmit={u.handleCreateUser}
            onCancel={() => u.setIsCreateDialogOpen(false)}
            departments={u.departments}
          />

          <UserFormDialog
            open={u.isEditDialogOpen}
            onOpenChange={u.setIsEditDialogOpen}
            mode="edit"
            formData={u.formData}
            onFormDataChange={u.setFormData}
            onSubmit={u.handleUpdateUser}
            onCancel={() => {
              u.setIsEditDialogOpen(false);
              u.setSelectedUser(null);
            }}
            departments={u.departments}
          />

          <UserFilters
            searchQuery={u.searchQuery}
            onSearchChange={u.setSearchQuery}
            roleFilter={u.roleFilter}
            onRoleFilterChange={u.setRoleFilter}
            departmentFilter={u.departmentFilter}
            onDepartmentFilterChange={u.setDepartmentFilter}
            departments={u.departments}
          />

          <UsersTable
            users={u.users}
            loading={u.loading}
            onEdit={u.openEditDialog}
            onDelete={u.handleDeleteUser}
            currentPage={u.currentPage}
            totalPages={u.totalPages}
            totalCount={u.totalUsers}
            onPageChange={u.setCurrentPage}
          />
        </>
      )}

      {activeTab === "departments" && (
        <>
          <Dialog open={d.isCreateDialogOpen} onOpenChange={d.setIsCreateDialogOpen}>
            <DepartmentFormDialog
              mode="create"
              formData={d.formData}
              onFormDataChange={d.updateFormField}
              onSubmit={handleDepartmentSubmit}
              onCancel={() => {
                d.setIsCreateDialogOpen(false);
                d.resetForm();
              }}
            />
          </Dialog>
          <Dialog open={d.isEditDialogOpen} onOpenChange={d.setIsEditDialogOpen}>
            <DepartmentFormDialog
              mode="edit"
              formData={d.formData}
              onFormDataChange={d.updateFormField}
              onSubmit={handleDepartmentSubmit}
              onCancel={() => {
                d.setIsEditDialogOpen(false);
                d.resetForm();
              }}
            />
          </Dialog>

          <DepartmentsTable
            departments={d.departments}
            loading={d.loading}
            searchQuery={d.searchQuery}
            onSearchChange={d.setSearchQuery}
            currentPage={d.currentPage}
            totalPages={d.totalPages}
            totalCount={d.totalCount}
            onPageChange={d.setCurrentPage}
            onEdit={d.openEdit}
            onDelete={handleDepartmentDelete}
          />
        </>
      )}
    </PageContent>
  );
}
