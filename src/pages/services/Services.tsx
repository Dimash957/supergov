import { useMemo, useState } from 'react';
import { Card, CardContent } from '../../components/ui/Card';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, MessageCircle } from 'lucide-react';
import { SUPERGOV_SERVICES } from '../../data/superGovServices';

export function Services() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'Все' | 'Новое' | 'MVP'>('Все');

  const filtered = useMemo(() => {
    if (filter === 'Все') return SUPERGOV_SERVICES;
    if (filter === 'Новое') return SUPERGOV_SERVICES.filter((s) => s.tier === 'innovation');
    return SUPERGOV_SERVICES.filter((s) => s.tier === 'mvp');
  }, [filter]);

  const openService = (s: (typeof SUPERGOV_SERVICES)[0]) => {
    if (s.chatPrompt && s.href === '/chat') {
      navigate(`/chat?q=${encodeURIComponent(s.chatPrompt)}`);
      return;
    }
    if (s.chatPrompt && s.href !== '/chat') {
      navigate(`${s.href}?from=services`);
      return;
    }
    navigate(s.href);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">18 функций SuperGov</h1>
        <p className="text-slate-500 mt-1 text-sm">
          Инновации и MVP-ядро: услуги, AI, карта, банк, документы — всё из одного каталога.
        </p>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
        {(['Все', 'Новое', 'MVP'] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setFilter(t)}
            className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-colors tracking-wide ${
              filter === t
                ? 'bg-navy text-white shadow-md shadow-navy/20'
                : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((s) => (
          <Card
            key={s.id}
            className="hover:border-cyan hover:shadow-lg transition-all duration-300 group cursor-pointer border-slate-200/60"
            onClick={() => openService(s)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between gap-2 mb-3">
                <span
                  className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full ${
                    s.tier === 'innovation' ? 'bg-emerald-100 text-emerald-800' : 'bg-cyan/15 text-navy'
                  }`}
                >
                  {s.tier === 'innovation' ? 'Новое' : 'MVP'}
                </span>
                {s.chatPrompt && <MessageCircle className="w-4 h-4 text-cyan shrink-0" />}
              </div>
              <div className="w-12 h-12 rounded-2xl bg-cyan/10 text-cyan flex items-center justify-center mb-4 group-hover:bg-cyan group-hover:text-white transition-colors duration-300">
                <s.icon className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-navy mb-1.5">{s.title}</h3>
              <p className="text-xs text-slate-500 line-clamp-3 leading-relaxed min-h-[3rem]">{s.subtitle}</p>
              <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                  {s.href === '/services' ? 'Каталог' : s.href.replace('/', '')}
                </span>
                <div className="flex items-center text-cyan text-sm font-semibold opacity-0 group-hover:opacity-100 transition-all duration-300 -translate-x-2 group-hover:translate-x-0">
                  Открыть <ArrowRight className="w-4 h-4 ml-1" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
