import { useEntity } from "./use-entity";
import { api } from "@/lib/api";
import type { Department } from "@/types";

export interface DepartmentRow {
  id: number;
  name: string;
  description: string;
  createdAt: string;
}

export interface DepartmentFormData {
  name: string;
  description: string;
}

const DEFAULT_FORM: DepartmentFormData = {
  name: "",
  description: "",
};

function mapDepartment(d: Department): DepartmentRow {
  return {
    id: d.id,
    name: d.name,
    description: d.description || "",
    createdAt: d.created_at ? d.created_at.split("T")[0] : "",
  };
}

function toCreatePayload(form: DepartmentFormData) {
  return {
    name: form.name,
    description: form.description || null,
  };
}

function toUpdatePayload(form: DepartmentFormData) {
  return toCreatePayload(form);
}

function toForm(item: DepartmentRow): DepartmentFormData {
  return {
    name: item.name,
    description: item.description,
  };
}

export function useDepartments() {
  return useEntity<DepartmentRow, DepartmentFormData, ReturnType<typeof toCreatePayload>, ReturnType<typeof toUpdatePayload>>({
    entityName: "Отдел",
    translationNamespace: "departments",
    queryKeyPrefix: "departments",
    listFn: (params) => api.departments.list(params),
    listDataKey: "departments",
    createFn: (data) => api.departments.create(data),
    updateFn: (id, data) => api.departments.update(id, data),
    deleteFn: (id) => api.departments.delete(id),
    defaultForm: DEFAULT_FORM,
    mapItem: (item: unknown) => mapDepartment(item as Department),
    toCreatePayload,
    toUpdatePayload,
    toForm,
    labels: {
      createdKey: "departments.created",
      updatedKey: "departments.updated",
      deletedKey: "departments.deleted",
      createErrorKey: "departments.createError",
      updateErrorKey: "departments.updateError",
      deleteErrorKey: "departments.deleteError",
    },
    searchable: true,
    searchParamName: "search",
    sortable: true,
    pageSize: 20,
  });
}
