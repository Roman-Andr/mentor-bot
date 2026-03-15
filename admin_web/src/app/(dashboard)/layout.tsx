import { AuthCheck } from "@/components/auth-check";
import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthCheck>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 overflow-y-auto bg-gray-50">{children}</div>
      </div>
    </AuthCheck>
  );
}
