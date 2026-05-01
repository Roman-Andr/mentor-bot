/** Shared constants used across the admin panel. */

// Role values (without labels - labels should come from translations)
export const ROLE_VALUES = ["ADMIN", "HR", "MENTOR", "NEWBIE"] as const;

// Level values (without labels - labels should come from translations)
export const LEVEL_VALUES = ["JUNIOR", "MIDDLE", "SENIOR", "LEAD"] as const;

// Template status values
export const TEMPLATE_STATUS_VALUES = ["ACTIVE", "DRAFT", "ARCHIVED"] as const;

// Article status values
export const ARTICLE_STATUS_VALUES = ["PUBLISHED", "DRAFT"] as const;

// Checklist status values
export const CHECKLIST_STATUS_VALUES = ["PENDING", "IN_PROGRESS", "COMPLETED", "BLOCKED", "CANCELLED"] as const;

// Escalation status values
export const ESCALATION_STATUS_VALUES = ["PENDING", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"] as const;

// Escalation type values
export const ESCALATION_TYPE_VALUES = ["HR", "MENTOR"] as const;

// Invitation status values
export const INVITATION_STATUS_VALUES = ["PENDING", "USED", "EXPIRED"] as const;

// Meeting type values
export const MEETING_TYPE_VALUES = ["HR", "SECURITY", "TEAM", "MANAGER", "OTHER"] as const;

// Feedback type values
export const FEEDBACK_TYPE_VALUES = ["pulse", "experience", "comment"] as const;

// Anonymity values
export const ANONYMITY_VALUES = ["anonymous", "attributed"] as const;

// Document category values
export const DOCUMENT_CATEGORY_VALUES = ["regulations", "templates", "resources", "policies"] as const;

// Task category values
export const TASK_CATEGORY_VALUES = ["DOCUMENTATION", "INTRODUCTION", "TECHNICAL", "TRAINING", "MEETING", "PAPERWORK", "SECURITY", "HR", "OTHER"] as const;

export const DEPARTMENT_COLORS: Record<string, string> = {
  Разработка: "bg-blue-500 dark:bg-blue-600",
  Дизайн: "bg-purple-500 dark:bg-purple-600",
  QA: "bg-green-500 dark:bg-green-600",
  Маркетинг: "bg-orange-500 dark:bg-orange-600",
  HR: "bg-pink-500 dark:bg-pink-600",
};

// Helper functions to generate translated options
export const getRoleOptions = (t: (key: string) => string, withAll = false) => {
  const roles = ROLE_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...roles];
  }
  return roles;
};

export const getLevelOptions = (t: (key: string) => string, withEmpty = false) => {
  const levels = LEVEL_VALUES.map((value) => ({
    value,
    label: t(`common.${value.toLowerCase()}`),
  }));
  if (withEmpty) {
    return [{ value: "", label: t("common.notSpecified") }, ...levels];
  }
  return levels;
};

export const getTemplateStatusOptions = (t: (key: string) => string, withAll = false) => {
  const statuses = TEMPLATE_STATUS_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...statuses];
  }
  return statuses;
};

export const getArticleStatusOptions = (t: (key: string) => string, withAll = false) => {
  const statuses = ARTICLE_STATUS_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...statuses];
  }
  return statuses;
};

export const getChecklistStatusOptions = (t: (key: string) => string, withAll = false) => {
  const statuses = CHECKLIST_STATUS_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...statuses];
  }
  return statuses;
};

export const getEscalationStatusOptions = (t: (key: string) => string, withAll = false) => {
  const statuses = ESCALATION_STATUS_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...statuses];
  }
  return statuses;
};

export const getEscalationTypeOptions = (t: (key: string) => string, withAll = false) => {
  const types = ESCALATION_TYPE_VALUES.map((value) => ({
    value,
    label: t(`common.${value.toLowerCase()}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...types];
  }
  return types;
};

export const getInvitationStatusOptions = (t: (key: string) => string, withAll = false) => {
  const statuses = INVITATION_STATUS_VALUES.map((value) => ({
    value,
    label: t(`statuses.${value}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...statuses];
  }
  return statuses;
};

export const getMeetingTypeOptions = (t: (key: string) => string, withAll = false) => {
  const types = MEETING_TYPE_VALUES.map((value) => ({
    value,
    label: t(`meetings.${value.toLowerCase()}`),
  }));
  if (withAll) {
    return [{ value: "ALL", label: t("common.all") }, ...types];
  }
  return types;
};

export const getFeedbackTypeOptions = (t: (key: string) => string, withAll = false) => {
  const types = FEEDBACK_TYPE_VALUES.map((value) => ({
    value,
    label: t(`feedback.${value}`),
  }));
  if (withAll) {
    return [{ value: "all", label: t("common.all") }, ...types];
  }
  return types;
};

export const getAnonymityOptions = (t: (key: string) => string, withAll = false) => {
  const options = ANONYMITY_VALUES.map((value) => ({
    value,
    label: t(`feedback.${value}`),
  }));
  if (withAll) {
    return [{ value: "all", label: t("common.all") }, ...options];
  }
  return options;
};

export const getDocumentCategoryOptions = (t: (key: string) => string) => {
  return DOCUMENT_CATEGORY_VALUES.map((value) => ({
    value,
    label: t(`departmentDocuments.${value}`),
  }));
};

export const getTaskCategoryOptions = (t: (key: string) => string) => {
  return TASK_CATEGORY_VALUES.map((value) => ({
    value,
    label: t(`taskCategories.${value}`),
  }));
};

// Backwards compatibility - deprecated, use helper functions above
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
] as const;

export const INVITATION_STATUSES = [
  { value: "ALL", label: "Все статусы" },
  { value: "PENDING", label: "Ожидает" },
  { value: "USED", label: "Принято" },
  { value: "EXPIRED", label: "Истёк" },
] as const;

export const MEETING_TYPES = [
  { value: "ALL", label: "Все типы" },
  { value: "HR", label: "HR" },
  { value: "SECURITY", label: "Безопасность" },
  { value: "TEAM", label: "Команда" },
  { value: "MANAGER", label: "Руководитель" },
  { value: "OTHER", label: "Другое" },
] as const;

export const FEEDBACK_TYPES = [
  { value: "all", label: "Все типы" },
  { value: "pulse", label: "Пульс-опросы" },
  { value: "experience", label: "Оценка опыта" },
  { value: "comment", label: "Комментарии" },
] as const;

export const ANONYMITY_OPTIONS = [
  { value: "all", label: "Все" },
  { value: "anonymous", label: "Анонимные" },
  { value: "attributed", label: "Именные" },
] as const;

export const DOCUMENT_CATEGORIES = [
  { value: "regulations", label: "Регламенты" },
  { value: "templates", label: "Шаблоны" },
  { value: "resources", label: "Полезные ресурсы" },
  { value: "policies", label: "Корпоративные политики" },
] as const;
