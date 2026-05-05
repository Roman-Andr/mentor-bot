"use client";

import { useTranslations } from "@/shared/hooks/use-translations";
import { Button } from "@/shared/ui/button";
import { PageContent } from "@/shared/layout/page-content";
import { UserPlus, Building2, Users } from "lucide-react";
import { useUsers } from "@/shared/hooks/use-users";
import { useDepartments } from "@/shared/hooks/use-departments";
import { TabSwitcher } from "@/shared/ui/tab-switcher";
import { UsersSection } from "@/widgets/users/users-section";
import { DepartmentsSection } from "@/widgets/users/departments-section";
import type { TabItem } from "@/shared/ui/tab-switcher";
import type { UserItem } from "@/shared/hooks/use-users";
import { useSearchParams } from "next/navigation";
import { api } from "@/shared/lib/api";
import { useToast } from "@/shared/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/query-keys";

type Tab = "users" | "departments";

export function UsersWidget() {
  const t = useTranslations();
  const searchParams = useSearchParams();
  const activeTab = (searchParams.get("tab") as Tab) || "users";
  const u = useUsers();
  const d = useDepartments();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const tabs: TabItem[] = [
    { id: "users", label: t("users.title"), icon: Users },
    { id: "departments", label: t("departments.title"), icon: Building2 },
  ];

  const handleDepartmentSubmit = async () => {
    await d.handleSubmit();
    u.loadDepartments();
  };

  const handleDepartmentDelete = async (id: number) => {
    await d.handleDelete(id);
    u.loadDepartments();
  };

  const handleDeactivateUser = async (user: UserItem) => {
    if (user.isActive) {
      const resp = await api.users.deactivate(user.id);
      if (resp.success) {
        toast(t("users.deactivated"), "success");
        await queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
      } else {
        toast(t("users.deactivateError"), "error");
      }
    } else {
      const resp = await api.users.update(user.id, { is_active: true } as any);
      if (resp.success) {
        toast(t("users.activated"), "success");
        await queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
      } else {
        toast(t("users.activateError"), "error");
      }
    }
  };

  const handleAddClick = () => {
    if (activeTab === "users") {
      u.resetForm();
      u.setIsCreateDialogOpen(true);
    } else {
      d.resetForm();
      d.setIsCreateDialogOpen(true);
    }
  };

  return (
    <PageContent
      title={t("users.title")}
      subtitle={t("users.subtitle") || t("users.title")}
      actions={
        <Button className="gap-2" onClick={handleAddClick}>
          {activeTab === "users" ? (
            <><UserPlus className="size-4" />{t("users.addUser")}</>
          ) : (
            <><Building2 className="size-4" />{t("common.create")}</>
          )}
        </Button>
      }
    >
      <div className="space-y-6">
        <TabSwitcher tabs={tabs} />

        {activeTab === "users" && (
          <UsersSection
            isCreateDialogOpen={u.isCreateDialogOpen}
            setIsCreateDialogOpen={u.setIsCreateDialogOpen}
            isEditDialogOpen={u.isEditDialogOpen}
            setIsEditDialogOpen={u.setIsEditDialogOpen}
            formData={u.formData}
            setFormData={u.setFormData}
            handleCreateUser={u.handleCreateUser}
            handleUpdateUser={u.handleUpdateUser}
            setSelectedUser={u.setSelectedUser}
            selectedUser={u.selectedUser}
            departments={u.departments}
            users={u.users}
            loading={u.loading}
            isLoading={u.loading}
            openEditDialog={u.openEditDialog}
            handleDeleteUser={u.handleDeleteUser}
            handleDeactivateUser={handleDeactivateUser}
            openAssignMentorDialog={u.openAssignMentorDialog}
            searchQuery={u.searchQuery}
            setSearchQuery={u.setSearchQuery}
            roleFilter={u.roleFilter}
            setRoleFilter={u.setRoleFilter}
            departmentFilter={u.departmentFilter}
            setDepartmentFilter={u.setDepartmentFilter}
            resetFilters={u.resetFilters}
            currentPage={u.currentPage}
            totalPages={u.totalPages}
            totalUsers={u.totalUsers}
            pageSize={u.pageSize}
            setCurrentPage={u.setCurrentPage}
            setPageSize={u.setPageSize}
            sortField={u.sortField}
            sortDirection={u.sortDirection}
            toggleSort={u.toggleSort}
            assignMentorDialogOpen={u.assignMentorDialogOpen}
            setAssignMentorDialogOpen={u.setAssignMentorDialogOpen}
            selectedUserForMentor={u.selectedUserForMentor}
            handleAssignMentor={(mentorId: number) => u.handleAssignMentor(u.selectedUserForMentor?.id || 0, mentorId)}
            handleUnassignMentor={() => u.handleUnassignMentor(u.currentMentor?.id || 0)}
            currentMentor={u.currentMentor}
          />
        )}

        {activeTab === "departments" && (
          <DepartmentsSection
            isCreateDialogOpen={d.isCreateDialogOpen}
            setIsCreateDialogOpen={d.setIsCreateDialogOpen}
            isEditDialogOpen={d.isEditDialogOpen}
            setIsEditDialogOpen={d.setIsEditDialogOpen}
            formData={d.formData}
            updateFormField={d.updateFormField}
            handleSubmit={handleDepartmentSubmit}
            resetForm={d.resetForm}
            items={d.items}
            loading={d.loading}
            isLoading={d.loading}
            setSelectedItem={d.setSelectedItem}
            selectedItem={d.selectedItem}
            searchQuery={d.searchQuery}
            setSearchQuery={d.setSearchQuery}
            currentPage={d.currentPage}
            totalPages={d.totalPages}
            totalCount={d.totalCount}
            pageSize={d.pageSize}
            setCurrentPage={d.setCurrentPage}
            setPageSize={d.setPageSize}
            openEditDialog={d.openEditDialog}
            handleDelete={handleDepartmentDelete}
            sortField={d.sortField}
            sortDirection={d.sortDirection}
            onSort={d.toggleSort}
          />
        )}
      </div>
    </PageContent>
  );
}
