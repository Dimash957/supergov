import { NavLink } from 'react-router-dom';
import { useStore } from '../../store/useStore';
import { cn } from '../../lib/utils';
import { LayoutDashboard, MessageSquare, Briefcase, Map as MapIcon, Star, User, Building2, FileUp } from 'lucide-react';

export function Sidebar() {
  const { user } = useStore();
  
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Главная' },
    { to: '/chat', icon: MessageSquare, label: 'AI Чат' },
    { to: '/services', icon: Briefcase, label: 'Услуги', badge: 18 },
    { to: '/applications', icon: Briefcase, label: 'Заявки' },
    { to: '/egov', icon: Building2, label: 'eGov (50+)', badge: 50 },
    { to: '/documents', icon: FileUp, label: 'AI Документы' },
    { to: '/map', icon: MapIcon, label: 'Карта' },
    { to: '/rating', icon: Star, label: 'Рейтинг' },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 h-screen border-r border-slate-200 bg-white sticky top-0 shrink-0">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-navy flex items-center">
          <span className="text-cyan">super</span>gov
        </h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium transition-colors",
              isActive ? "bg-cyan/10 text-cyan font-semibold" : "text-slate-600 hover:bg-slate-50 hover:text-navy"
            )}
          >
            <item.icon className={cn("w-5 h-5", item.to === '/chat' && "text-cyan")} />
            <span>{item.label}</span>
            {item.badge && (
              <span className="ml-auto bg-navy text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto border-t border-slate-100">
        <NavLink
          to="/profile"
          className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-cyan/20 flex items-center justify-center text-cyan font-bold shrink-0">
            {user?.name?.charAt(0) || <User className="w-5 h-5" />}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-navy truncate">{user?.name || "Профиль"}</p>
            {user?.iin && <p className="text-xs text-slate-500 truncate">IIN: ****{user.iin.slice(-4)}</p>}
          </div>
        </NavLink>
      </div>
    </aside>
  );
}
