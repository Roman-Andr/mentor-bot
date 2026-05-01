"use client";

import { useState } from "react";
import { useTranslations } from "@/hooks/use-translations";
import { Button } from "@/components/ui/button";
import { PageContent } from "@/components/layout/page-content";
import { UserPlus, Building2 } from "lucide-react";
import { useUsers } from "@/hooks/use-users";
import { useDepartments } from "@/hooks/use-departments";
import { UsersTabSwitcher } from "@/components/features/users/users-tab-switcher";
import { UsersSection } from "@/components/features/users/users-section";
import { DepartmentsSection } from "@/components/features/users/departments-section";

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
      subtitle={t("users.title")}
      actions={
        <div className="flex items-center gap-2">
          <UsersTabSwitcher activeTab={activeTab} onTabChange={setActiveTab} />
          <Button className="gap-2" onClick={handleAddClick}>
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
        />
      )}
    </PageContent>
  );
}
