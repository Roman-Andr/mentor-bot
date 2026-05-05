import { AuthCheck } from "@/shared/layout/auth-check";
import { Sidebar } from "@/shared/layout/sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthCheck>
      <div className="flex h-screen">
        <Sidebar />
        <div className="bg-background flex-1 overflow-y-auto">{children}</div>
      </div>
    </AuthCheck>
  );
}
