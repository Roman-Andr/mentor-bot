"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { DepartmentDocumentsTable } from "./department-documents-table";
import { DepartmentDocumentFormDialog } from "./department-document-form-dialog";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useDepartmentDocuments } from "@/hooks/use-department-documents";
import type { DepartmentDocument, DepartmentDocumentUpdate } from "@/types/department-document";

export function DepartmentDocumentsTab() {
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>();
  const [departmentFilter, setDepartmentFilter] = useState<number | undefined>();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<DepartmentDocument | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null);

  const [formData, setFormData] = useState({
    department_id: 0,
    title: "",
    description: "",
    category: "",
    is_public: false,
    file: undefined as File | undefined,
  });

  const {
    documents,
    isLoading,
    createDocument,
    isCreating,
    updateDocument,
    isUpdating,
    deleteDocument,
    isDeleting,
  } = useDepartmentDocuments({ category: categoryFilter, department_id: departmentFilter });

  const handleCreate = () => {
    if (!formData.file) return;

    const data = new FormData();
    data.append("department_id", formData.department_id.toString());
    data.append("title", formData.title);
    data.append("description", formData.description);
    data.append("category", formData.category);
    data.append("is_public", formData.is_public.toString());
    data.append("file", formData.file);

    createDocument(data, {
      onSuccess: () => {
        setIsCreateDialogOpen(false);
        resetForm();
      },
    });
  };

  const handleEdit = (document: DepartmentDocument) => {
    setSelectedDocument(document);
    setFormData({
      department_id: document.department_id,
      title: document.title,
      description: document.description || "",
      category: document.category,
      is_public: document.is_public,
      file: undefined,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!selectedDocument) return;

    const updateData: DepartmentDocumentUpdate = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      is_public: formData.is_public,
    };

    updateDocument(selectedDocument.id, updateData, {
      onSuccess: () => {
        setIsEditDialogOpen(false);
        setSelectedDocument(null);
        resetForm();
      },
    });
  };

  const handleDeleteClick = (id: number) => {
    setDeleteTargetId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteTargetId) {
      deleteDocument(deleteTargetId, {
        onSuccess: () => {
          setDeleteConfirmOpen(false);
          setDeleteTargetId(null);
        },
      });
    }
  };

  const resetForm = () => {
    setFormData({
      department_id: 0,
      title: "",
      description: "",
      category: "",
      is_public: false,
      file: undefined,
    });
  };

  const handleOpenCreateDialog = () => {
    resetForm();
    setIsCreateDialogOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={handleOpenCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Добавить документ
        </Button>
      </div>

      <DepartmentDocumentsTable
        documents={documents}
        loading={isLoading}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        categoryFilter={categoryFilter}
        onCategoryFilterChange={setCategoryFilter}
        departmentFilter={departmentFilter}
        onDepartmentFilterChange={setDepartmentFilter}
        onEdit={handleEdit}
        onDelete={handleDeleteClick}
      />

      {isCreateDialogOpen && (
        <DepartmentDocumentFormDialog
          mode="create"
          formData={formData}
          onFormDataChange={(field, value) => setFormData({ ...formData, [field]: value })}
          onSubmit={handleCreate}
          onCancel={() => setIsCreateDialogOpen(false)}
          isSubmitting={isCreating}
        />
      )}

      {isEditDialogOpen && selectedDocument && (
        <DepartmentDocumentFormDialog
          mode="edit"
          formData={formData}
          onFormDataChange={(field, value) => setFormData({ ...formData, [field]: value })}
          onSubmit={handleUpdate}
          onCancel={() => {
            setIsEditDialogOpen(false);
            setSelectedDocument(null);
            resetForm();
          }}
          isSubmitting={isUpdating}
        />
      )}

      <ConfirmDialog
        open={deleteConfirmOpen}
        onOpenChange={setDeleteConfirmOpen}
        onConfirm={handleDeleteConfirm}
        title="Удалить документ"
        description="Вы уверены, что хотите удалить этот документ? Это действие нельзя отменить."
        confirmLabel="Удалить"
        cancelLabel="Отмена"
        isSubmitting={isDeleting}
      />
    </div>
  );
}
