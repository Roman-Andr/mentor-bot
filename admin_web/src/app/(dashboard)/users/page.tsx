"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { PageContent } from "@/components/layout/page-content";
import { UserPlus, Building2, Users } from "lucide-react";
import { useUsers } from "@/hooks/use-users";
import { useDepartments } from "@/hooks/use-departments";
import { UserFormDialog } from "@/components/features/users/user-form-dialog";
import { UsersTable } from "@/components/features/users/users-table";
import { AssignMentorDialog } from "@/components/features/users/assign-mentor-dialog";
import { DepartmentsTable } from "@/components/features/users/departments-table";
import { DepartmentFormDialog } from "@/components/features/users/department-form-dialog";
import { cn } from "@/lib/utils";

type Tab = "users" | "departments";

export default function UsersPage() {
  const t = useTranslations();
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
      title={t("users.title")}
      subtitle={t("users.title")}
      actions={
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border">
            <button
              className={cn(
                "flex cursor-pointer items-center gap-1.5 rounded-l-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "users"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("users")}
            >
              <Users className="size-4" />
              {t("users.title")}
            </button>
            <button
              className={cn(
                "flex cursor-pointer items-center gap-1.5 rounded-r-md px-3 py-1.5 text-sm font-medium transition-colors",
                activeTab === "departments"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab("departments")}
            >
              <Building2 className="size-4" />
              {t("users.department")}
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
                {t("users.addUser")}
              </>
            ) : (
              <>
                <Building2 className="size-4" />
                {t("common.create")}
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

          <UsersTable
            users={u.users}
            loading={u.loading}
            onEdit={u.openEditDialog}
            onDelete={u.handleDeleteUser}
            onAssignMentor={u.openAssignMentorDialog}
            searchQuery={u.searchQuery}
            onSearchChange={u.setSearchQuery}
            roleFilter={u.roleFilter}
            onRoleFilterChange={u.setRoleFilter}
            departmentFilter={u.departmentFilter}
            onDepartmentFilterChange={u.setDepartmentFilter}
            onReset={u.resetFilters}
            departments={u.departments}
            currentPage={u.currentPage}
            totalPages={u.totalPages}
            totalCount={u.totalUsers}
            pageSize={u.pageSize}
            onPageChange={u.setCurrentPage}
            onPageSizeChange={u.setPageSize}
          />

          <AssignMentorDialog
            isOpen={u.assignMentorDialogOpen}
            onOpenChange={u.setAssignMentorDialogOpen}
            userId={u.selectedUserForMentor?.id || null}
            userName={u.selectedUserForMentor?.name || ""}
            onAssign={u.handleAssignMentor}
            onUnassign={u.handleUnassignMentor}
            currentMentor={u.currentMentor}
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
            departments={d.items}
            loading={d.loading}
            searchQuery={d.searchQuery}
            onSearchChange={d.setSearchQuery}
            currentPage={d.currentPage}
            totalPages={d.totalPages}
            totalCount={d.totalCount}
            pageSize={d.pageSize}
            onPageChange={d.setCurrentPage}
            onPageSizeChange={d.setPageSize}
            onEdit={d.openEditDialog}
            onDelete={handleDepartmentDelete}
          />
        </>
      )}
    </PageContent>
  );
}
