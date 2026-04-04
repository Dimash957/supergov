import { useState } from 'react';
import { Search, Bell, LogOut } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStackApp } from '@stackframe/stack';
import { useStore } from '../../store/useStore';
import { clearOtpToken } from '../../lib/apiHeaders';

export function TopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const stackApp = useStackApp();
  const [search, setSearch] = useState('');
  const [loggingOut, setLoggingOut] = useState(false);
  const { language, setLanguage, user, setUser } = useStore();

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      clearOtpToken();
      setUser(null);
      try {
        await stackApp.signOut();
      } catch {
        /* нет сессии Stack — только OTP */
      }
      navigate('/login', { replace: true });
    } finally {
      setLoggingOut(false);
    }
  };

  const getPageTitle = () => {
    const map: Record<string, string> = {
      '/dashboard': 'Главная',
      '/chat': 'AI Ассистент',
      '/services': 'Услуги',
      '/applications': 'Мои заявки',
      '/map': 'Карта проблем',
      '/rating': 'Рейтинг ведомств',
      '/profile': 'Профиль',
    };
    return map[location.pathname] || 'SuperGov';
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/chat?q=${encodeURIComponent(search)}`);
    }
  };

  return (
    <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
      <h2 className="text-xl font-semibold text-navy hidden md:block">{getPageTitle()}</h2>
      
      {/* Mobile Title */}
      <h2 className="text-lg font-bold text-navy md:hidden flex items-center">
        <span className="text-cyan">super</span>gov
      </h2>

      <div className="flex items-center gap-4 ml-auto">
        {user?.name && (
          <span className="hidden lg:inline text-sm text-slate-600 max-w-[140px] truncate" title={user.name}>
            {user.name}
          </span>
        )}
        <form onSubmit={handleSearch} className="hidden md:flex relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Задать вопрос AI..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 w-64 bg-slate-100 border-none rounded-full text-sm focus:ring-2 focus:ring-cyan outline-none transition-all focus:bg-white focus:w-80 shadow-sm focus:shadow-md"
          />
        </form>

        <button className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
        </button>

        <div className="flex items-center bg-slate-100 rounded-full p-1 border border-slate-200 shadow-inner hidden md:flex">
          {['kz', 'ru', 'en'].map((lang) => (
            <button
              key={lang}
              onClick={() => setLanguage(lang as 'kz' | 'ru' | 'en')}
              className={`px-3 py-1 text-[10px] font-bold rounded-full transition-colors uppercase tracking-wider ${
                language === lang ? 'bg-white text-navy shadow-sm' : 'text-slate-500 hover:text-navy'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => void handleLogout()}
          disabled={loggingOut}
          className="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 hover:text-navy disabled:opacity-60"
          title="Выйти"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">{loggingOut ? 'Выход…' : 'Выйти'}</span>
        </button>
      </div>
    </header>
  );
}
