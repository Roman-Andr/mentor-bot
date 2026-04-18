import { cn } from "@/lib/utils";

export interface ServiceOption {
  id: string;
  name: string;
  url: string;
  description: string;
}

export const services: ServiceOption[] = [
  {
    id: "auth",
    name: "Auth Service",
    url: "http://auth_service:8001/openapi.json",
    description: "Authentication & users",
  },
  {
    id: "checklists",
    name: "Checklists Service",
    url: "http://checklists_service:8002/openapi.json",
    description: "Tasks & templates",
  },
  {
    id: "knowledge",
    name: "Knowledge Service",
    url: "http://knowledge_service:8003/openapi.json",
    description: "Articles & search",
  },
  {
    id: "notification",
    name: "Notification Service",
    url: "http://notification_service:8004/openapi.json",
    description: "Emails & Telegram",
  },
  {
    id: "escalation",
    name: "Escalation Service",
    url: "http://escalation_service:8005/openapi.json",
    description: "Issue escalation",
  },
  {
    id: "meeting",
    name: "Meeting Service",
    url: "http://meeting_service:8006/openapi.json",
    description: "Calendar & scheduling",
  },
  {
    id: "feedback",
    name: "Feedback Service",
    url: "http://feedback_service:8007/openapi.json",
    description: "Surveys & ratings",
  },
];

interface ServiceSelectorProps {
  selected: string;
  onSelect: (service: ServiceOption) => void;
}

export function ServiceSelector({ selected, onSelect }: ServiceSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-4 lg:grid-cols-7">
      {services.map((service) => (
        <button
          key={service.id}
          onClick={() => onSelect(service)}
          className={cn(
            "rounded-lg border p-3 text-left transition-colors",
            selected === service.id
              ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950/30"
              : "border-slate-200 hover:border-blue-300 dark:border-slate-700 dark:hover:border-blue-700"
          )}
        >
          <div className="font-medium text-sm">{service.name}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {service.description}
          </div>
        </button>
      ))}
    </div>
  );
}
