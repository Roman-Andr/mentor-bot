/** Shared constants used across the admin panel. */

export const ROLES = [
  { value: "ADMIN", label: "Администратор" },
  { value: "HR", label: "HR" },
  { value: "MENTOR", label: "Наставник" },
  { value: "NEWBIE", label: "Новичок" },
] as const;

export const ROLES_WITH_ALL = [{ value: "ALL", label: "Все роли" }, ...ROLES];

export const LEVELS = [
  { value: "JUNIOR", label: "Junior" },
  { value: "MIDDLE", label: "Middle" },
  { value: "SENIOR", label: "Senior" },
  { value: "LEAD", label: "Lead" },
] as const;

export const LEVELS_WITH_EMPTY = [{ value: "", label: "Не указан" }, ...LEVELS];

export const TEMPLATE_STATUSES = [
  { value: "ALL", label: "Все статусы" },
  { value: "ACTIVE", label: "Активен" },
  { value: "DRAFT", label: "Черновик" },
  { value: "ARCHIVED", label: "Архив" },
] as const;

export const ARTICLE_STATUSES = [
  { value: "ALL", label: "Все статусы" },
  { value: "PUBLISHED", label: "Опубликовано" },
  { value: "DRAFT", label: "Черновик" },
] as const;

export const TASK_CATEGORY_MAP: Record<string, string> = {
  DOCUMENTATION: "Документы",
  INTRODUCTION: "Знакомство с командой",
  TECHNICAL: "Техническая настройка",
  TRAINING: "Обучение",
  MEETING: "Встречи",
  PAPERWORK: "Бумажная работа",
  SECURITY: "Безопасность",
  HR: "HR",
  OTHER: "Прочее",
};

export const TASK_CATEGORIES = Object.entries(TASK_CATEGORY_MAP).map(([value, label]) => ({
  value,
  label,
}));

export const CHECKLIST_STATUSES = [
  { value: "ALL", label: "Все статусы" },
  { value: "PENDING", label: "Ожидает" },
  { value: "IN_PROGRESS", label: "В работе" },
  { value: "COMPLETED", label: "Завершён" },
  { value: "BLOCKED", label: "Заблокирован" },
  { value: "CANCELLED", label: "Отменён" },
] as const;

export const DEPARTMENT_COLORS: Record<string, string> = {
  Разработка: "bg-blue-500",
  Дизайн: "bg-purple-500",
  QA: "bg-green-500",
  Маркетинг: "bg-orange-500",
  HR: "bg-pink-500",
};

export const ESCALATION_STATUSES = [
  { value: "ALL", label: "Все статусы" },
  { value: "PENDING", label: "Ожидает" },
  { value: "ASSIGNED", label: "Назначен" },
  { value: "IN_PROGRESS", label: "В работе" },
  { value: "RESOLVED", label: "Решён" },
  { value: "CLOSED", label: "Закрыт" },
] as const;

export const ESCALATION_TYPES = [
  { value: "ALL", label: "Все типы" },
  { value: "HR", label: "HR" },
  { value: "MENTOR", label: "Наставник" },
  { value: "IT", label: "IT" },
  { value: "GENERAL", label: "Общий" },
] as const;

export const MEETING_TYPES = [
  { value: "ALL", label: "Все типы" },
  { value: "HR", label: "HR" },
  { value: "SECURITY", label: "Безопасность" },
  { value: "TEAM", label: "Команда" },
  { value: "MANAGER", label: "Руководитель" },
  { value: "OTHER", label: "Другое" },
] as const;
