import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Briefcase, Map as MapIcon, User } from 'lucide-react';
import { cn } from '../../lib/utils';

export function MobileNav() {
  const items = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Главная' },
    { to: '/chat', icon: MessageSquare, label: 'Чат' },
    { to: '/applications', icon: Briefcase, label: 'Заявки' },
    { to: '/map', icon: MapIcon, label: 'Карта' },
    { to: '/profile', icon: User, label: 'Профиль' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-slate-200 pb-safe z-50 shadow-[0_-4px_10px_rgba(0,0,0,0.02)]">
      <ul className="flex items-center justify-around h-16 px-2">
        {items.map((item) => (
          <li key={item.to} className="w-full">
            <NavLink
              to={item.to}
              className={({ isActive }) => cn(
                "flex flex-col items-center justify-center h-full gap-1 text-[10px] font-medium transition-colors",
                isActive ? "text-cyan" : "text-slate-400 hover:text-slate-600"
              )}
            >
              {({ isActive }) => (
                <>
                  <item.icon className={cn("w-5 h-5", isActive ? "text-cyan" : "")} />
                  <span className={isActive ? "font-bold" : ""}>{item.label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
