import { Outlet } from 'react-router-dom';
import { SidebarProvider } from '@/components/ui/sidebar';
import { AppSidebar } from '../components/AppSidebar';

export default function DashboardLayout() {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <AppSidebar />
        <main className="flex-1 p-6 bg-slate-950 overflow-auto">
          <Outlet />
        </main>
      </div>
    </SidebarProvider>
  );
}