import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { departmentDocumentsApi } from "@/lib/api/department-documents";
import type { DepartmentDocument, DepartmentDocumentCreate, DepartmentDocumentUpdate } from "@/types/department-document";

export function useDepartmentDocuments(params?: { department_id?: number; category?: string; is_public?: boolean }) {
  const queryClient = useQueryClient();

  const listQuery = useQuery({
    queryKey: ["department-documents", params],
    queryFn: () => departmentDocumentsApi.list(params),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormData) => departmentDocumentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["department-documents"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: DepartmentDocumentUpdate }) =>
      departmentDocumentsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["department-documents"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => departmentDocumentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["department-documents"] });
    },
  });

  return {
    documents: listQuery.data?.documents || [],
    total: listQuery.data?.total || 0,
    isLoading: listQuery.isLoading,
    error: listQuery.error,
    createDocument: createMutation.mutate,
    isCreating: createMutation.isPending,
    updateDocument: (id: number, data: DepartmentDocumentUpdate) =>
      updateMutation.mutate({ id, data }),
    isUpdating: updateMutation.isPending,
    deleteDocument: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  };
}

export function useDepartmentDocument(id: number) {
  return useQuery({
    queryKey: ["department-document", id],
    queryFn: () => departmentDocumentsApi.get(id),
    enabled: !!id,
  });
}
