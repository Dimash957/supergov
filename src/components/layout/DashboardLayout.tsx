import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { MobileNav } from './MobileNav';

export function DashboardLayout() {
  return (
    <div className="flex h-screen bg-[#f8fafc] overflow-hidden w-full">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden w-full">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6 w-full max-w-7xl mx-auto">
          <Outlet />
        </main>
      </div>
      <MobileNav />
    </div>
  );
}
