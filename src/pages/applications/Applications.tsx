import { Card, CardContent } from '../../components/ui/Card';
import { Clock, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Applications() {
  const navigate = useNavigate();
  
  const apps = [
    { id: '182-391-233', name: 'Открытие ИП онлайн', date: '12 апреля 2026', status: 'В обработке', progress: 40, color: 'text-blue-500', bg: 'bg-blue-100', icon: Clock },
    { id: '182-391-230', name: 'Выдача паспорта гражданина РК', date: '10 апреля 2026', status: 'Готово к выдаче', progress: 80, color: 'text-emerald-500', bg: 'bg-emerald-100', icon: CheckCircle2 },
    { id: '182-391-225', name: 'Пособие по рождению', date: '01 апреля 2026', status: 'Исполнено', progress: 100, color: 'text-emerald-500', bg: 'bg-emerald-100', icon: CheckCircle2 },
  ];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-navy">Мои заявки</h1>
        <p className="text-slate-500 mt-1 text-sm font-medium">История оказания государственных услуг.</p>
      </div>

      <div className="grid gap-4">
        {apps.map(app => (
          <Card key={app.id} className="hover:border-cyan transition-colors cursor-pointer group shadow-sm border-slate-200/60" onClick={() => navigate('/tracker')}>
            <CardContent className="p-6">
               <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                 <div className="flex items-start md:items-center gap-5">
                   <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-inner ${app.bg} ${app.color}`}>
                     <app.icon className="w-7 h-7" />
                   </div>
                   <div>
                     <h3 className="font-bold text-navy text-lg leading-tight mb-1 group-hover:text-cyan transition-colors">{app.name}</h3>
                     <p className="text-xs text-slate-500 font-semibold tracking-wide">ЗАЯВКА № {app.id} • {app.date}</p>
                   </div>
                 </div>
                 
                 <div className="flex flex-col md:items-end w-full md:w-auto">
                   <span className={`inline-block px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-widest mb-3 ${app.progress >= 80 ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                     {app.status}
                   </span>
                   <div className="flex items-center gap-4 w-full md:w-56">
                     <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden shadow-inner">
                       <div className={`h-full rounded-full transition-all duration-1000 ${app.progress >= 80 ? 'bg-emerald-500' : 'bg-cyan'}`} style={{ width: `${app.progress}%` }}></div>
                     </div>
                     <span className="text-xs font-bold text-slate-400 w-8">{app.progress}%</span>
                   </div>
                 </div>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
