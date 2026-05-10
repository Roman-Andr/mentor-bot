"use client";

import { useState } from "react";
import { AuthCheck } from "@/shared/layout/auth-check";
import { Sidebar } from "@/shared/layout/sidebar";
import { MobileHeader } from "@/shared/layout/mobile-header";
import { MobileNavigationDrawer } from "@/shared/layout/mobile-navigation-drawer";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  return (
    <AuthCheck>
      <div className="flex min-h-dvh bg-background">
        {/* Desktop Sidebar - hidden on mobile, visible on lg+ */}
        <div className="sticky top-0 hidden h-dvh lg:block">
          <Sidebar />
        </div>

        {/* Mobile Header - visible on mobile, hidden on lg+ */}
        <div className="flex w-full flex-col lg:hidden">
          <MobileHeader onMenuClick={() => setMobileDrawerOpen(true)} />
          <div className="min-w-0 flex-1 overflow-y-auto">{children}</div>
        </div>

        {/* Desktop Content Area - visible on lg+ */}
        <div className="hidden min-w-0 flex-1 overflow-y-auto bg-background lg:block">
          {children}
        </div>

        {/* Mobile Navigation Drawer */}
        <MobileNavigationDrawer open={mobileDrawerOpen} onOpenChange={setMobileDrawerOpen} />
      </div>
    </AuthCheck>
  );
}
