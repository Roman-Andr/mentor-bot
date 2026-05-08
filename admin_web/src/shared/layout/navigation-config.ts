import {
  LayoutDashboard,
  Users,
  FileText,
  ClipboardCheck,
  BookOpen,
  Mail,
  BarChart3,
  Settings,
  LogOut,
  AlertTriangle,
  CalendarCheck,
  MessageSquare,
  MessageCircle,
  type LucideIcon,
} from "lucide-react";

export const ICON_MAP: Record<string, LucideIcon> = {
  LayoutDashboard,
  Users,
  FileText,
  ClipboardCheck,
  BookOpen,
  Mail,
  BarChart3,
  Settings,
  AlertTriangle,
  CalendarCheck,
  MessageSquare,
  MessageCircle,
};

export interface NavItem {
  key: string;
  href: string;
  icon: string;
}

export interface NavGroup {
  labelKey: string;
  items: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  {
    labelKey: "nav.groupPeople",
    items: [
      { key: "dashboard", href: "/", icon: "LayoutDashboard" },
      { key: "users", href: "/users", icon: "Users" },
      { key: "invitations", href: "/invitations", icon: "Mail" },
    ],
  },
  {
    labelKey: "nav.groupOnboarding",
    items: [
      { key: "templates", href: "/templates", icon: "FileText" },
      { key: "checklists", href: "/checklists", icon: "ClipboardCheck" },
      { key: "meetings", href: "/meetings", icon: "CalendarCheck" },
      { key: "dialogues", href: "/dialogues", icon: "MessageSquare" },
    ],
  },
  {
    labelKey: "nav.groupKnowledge",
    items: [
      { key: "knowledgeBase", href: "/knowledge", icon: "BookOpen" },
    ],
  },
  {
    labelKey: "nav.groupInsights",
    items: [
      { key: "feedback", href: "/feedback", icon: "MessageCircle" },
      { key: "escalations", href: "/escalations", icon: "AlertTriangle" },
      { key: "analytics", href: "/analytics", icon: "BarChart3" },
    ],
  },
  {
    labelKey: "nav.groupSystem",
    items: [
      { key: "settings", href: "/settings", icon: "Settings" },
    ],
  },
];
