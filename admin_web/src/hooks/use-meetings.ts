import { useState, useEffect, useCallback } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { useConfirm } from "@/components/ui/confirm-dialog";
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

export function useMeetings() {
  const confirm = useConfirm();
  const { toast } = useToast();
  const [meetings, setMeetings] = useState<MeetingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingItem | null>(null);
  const [formData, setFormData] = useState<MeetingFormData>({ ...defaultFormData });

  const debouncedSearch = useDebounce(searchQuery);
  const pageSize = 20;

  const resetForm = useCallback(() => {
    setFormData({ ...defaultFormData });
    setSelectedMeeting(null);
  }, []);

  const loadMeetings = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      };
      if (typeFilter !== "ALL") params.meeting_type = typeFilter;

      const response = await api.meetings.list(params);
      if (response.data) {
        let items = response.data.meetings.map(mapMeeting);
        if (debouncedSearch) {
          const q = debouncedSearch.toLowerCase();
          items = items.filter(
            (m) =>
              m.title.toLowerCase().includes(q) ||
              m.description.toLowerCase().includes(q),
          );
        }
        setMeetings(items);
        setTotalCount(response.data.total);
        setTotalPages(response.data.pages || 1);
      }
    } catch (err) {
      console.error("Failed to load meetings:", err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, typeFilter, debouncedSearch]);

  useEffect(() => {
    loadMeetings();
  }, [loadMeetings]);

  const handleCreate = async () => {
    try {
      const response = await api.meetings.create({
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
      if (response.data) {
        setMeetings([mapMeeting(response.data), ...meetings]);
        setTotalCount((c) => c + 1);
        setIsCreateDialogOpen(false);
        resetForm();
        toast("Встреча создана", "success");
      } else {
        toast(response.error || "Ошибка создания", "error");
      }
    } catch (err) {
      console.error("Failed to create meeting:", err);
      toast("Ошибка создания встречи", "error");
    }
  };

  const handleUpdate = async () => {
    if (!selectedMeeting) return;
    try {
      const response = await api.meetings.update(selectedMeeting.id, {
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
      if (response.data) {
        setMeetings(
          meetings.map((m) => (m.id === selectedMeeting.id ? mapMeeting(response.data!) : m)),
        );
        setIsEditDialogOpen(false);
        setSelectedMeeting(null);
        resetForm();
        toast("Встреча обновлена", "success");
      } else {
        toast(response.error || "Ошибка обновления", "error");
      }
    } catch (err) {
      console.error("Failed to update meeting:", err);
      toast("Ошибка обновления встречи", "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirm({ title: "Удаление встречи", description: "Вы уверены, что хотите удалить эту встречу?", variant: "destructive", confirmText: "Удалить" }))) return;
    try {
      await api.meetings.delete(id);
      setMeetings(meetings.filter((m) => m.id !== id));
      setTotalCount((c) => c - 1);
      toast("Встреча удалена", "success");
    } catch (err) {
      console.error("Failed to delete meeting:", err);
      toast("Ошибка удаления встречи", "error");
    }
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
  };
}
