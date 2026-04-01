import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/components/ui/toast";
import { api, type Meeting } from "@/lib/api";

export interface MeetingItem {
  id: number;
  title: string;
  description: string;
  type: string;
  departmentId: number | null;
  department: string;
  position: string;
  level: string;
  deadlineDays: number;
  isMandatory: boolean;
  order: number;
  createdAt: string;
}

export interface MeetingFormData {
  title: string;
  description: string;
  type: string;
  department_id: number;
  position: string;
  level: string;
  deadline_days: number;
  is_mandatory: boolean;
  order: number;
}

function mapMeeting(m: Meeting): MeetingItem {
  return {
    id: m.id,
    title: m.title,
    description: m.description || "",
    type: m.type,
    departmentId: m.department_id,
    department: m.department?.name || "",
    position: m.position || "",
    level: m.level || "",
    deadlineDays: m.deadline_days,
    isMandatory: m.is_mandatory,
    order: m.order,
    createdAt: m.created_at,
  };
}

const defaultFormData: MeetingFormData = {
  title: "",
  description: "",
  type: "HR",
  department_id: 0,
  position: "",
  level: "",
  deadline_days: 7,
  is_mandatory: true,
  order: 0,
};

const MEETINGS_KEY = ["meetings"] as const;

export function useMeetings() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingItem | null>(null);
  const [formData, setFormData] = useState<MeetingFormData>({ ...defaultFormData });

  const pageSize = 20;

  const queryParams = {
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
    ...(typeFilter !== "ALL" && { meeting_type: typeFilter }),
  };

  const { data: meetingsData, isLoading: loading } = useQuery({
    queryKey: [...MEETINGS_KEY, queryParams],
    queryFn: () => api.meetings.list(queryParams),
    select: (result) =>
      result.data
        ? {
            meetings: result.data.meetings.map(mapMeeting),
            total: result.data.total,
            pages: result.data.pages,
          }
        : undefined,
  });

  const createMutation = useMutation({
    mutationFn: (data: Parameters<typeof api.meetings.create>[0]) => api.meetings.create(data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: MEETINGS_KEY });
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Встреча создана", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка создания встречи", "error"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof api.meetings.update>[1] }) =>
      api.meetings.update(id, data),
    onSuccess: (result) => {
      if (result.data) {
        queryClient.invalidateQueries({ queryKey: MEETINGS_KEY });
        setIsEditDialogOpen(false);
        setSelectedMeeting(null);
        resetForm();
        toast("Встреча обновлена", "success");
      } else if (result.error) {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка обновления встречи", "error"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.meetings.delete(id),
    onSuccess: (result) => {
      if (!result.error) {
        queryClient.invalidateQueries({ queryKey: MEETINGS_KEY });
        toast("Встреча удалена", "success");
      } else {
        toast(result.error, "error");
      }
    },
    onError: () => toast("Ошибка удаления встречи", "error"),
  });

  const handleCreate = () => {
    createMutation.mutate({
      title: formData.title,
      description: formData.description || null,
      type: formData.type,
      department_id: formData.department_id || null,
      position: formData.position || null,
      level: formData.level || null,
      deadline_days: formData.deadline_days,
      is_mandatory: formData.is_mandatory,
      order: formData.order,
    });
  };

  const handleUpdate = () => {
    if (!selectedMeeting) return;
    updateMutation.mutate({
      id: selectedMeeting.id,
      data: {
        title: formData.title,
        description: formData.description || null,
        type: formData.type,
        department_id: formData.department_id || null,
        position: formData.position || null,
        level: formData.level || null,
        deadline_days: formData.deadline_days,
        is_mandatory: formData.is_mandatory,
        order: formData.order,
      },
    });
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const openEditDialog = (meeting: MeetingItem) => {
    setSelectedMeeting(meeting);
    setFormData({
      title: meeting.title,
      description: meeting.description,
      type: meeting.type,
      department_id: meeting.departmentId || 0,
      position: meeting.position,
      level: meeting.level,
      deadline_days: meeting.deadlineDays,
      is_mandatory: meeting.isMandatory,
      order: meeting.order,
    });
    setIsEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData(defaultFormData);
    setSelectedMeeting(null);
  };

  const meetings = meetingsData?.meetings || [];
  const totalCount = meetingsData?.total || 0;
  const totalPages = meetingsData?.pages || 1;

  return {
    meetings,
    loading,
    searchQuery,
    setSearchQuery,
    typeFilter,
    setTypeFilter,
    currentPage,
    setCurrentPage,
    totalPages,
    totalCount,
    isCreateDialogOpen,
    setIsCreateDialogOpen,
    isEditDialogOpen,
    setIsEditDialogOpen,
    selectedMeeting,
    setSelectedMeeting,
    formData,
    setFormData,
    handleCreate,
    handleUpdate,
    handleDelete,
    openEditDialog,
    resetForm,
    resetFilters: () => {
      setSearchQuery("");
      setTypeFilter("ALL");
      setCurrentPage(1);
    },
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
