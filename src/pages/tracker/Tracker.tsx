import { Card, CardContent } from '../../components/ui/Card';
import { Check, Clock, PackageCheck } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function Tracker() {
  const steps = [
    { title: 'Принято в обработку', desc: 'Заявка успешно зарегистрирована.', date: '12 Апр, 10:00', done: true },
    { title: 'Проверка документов', desc: 'Автоматическая сверка с ГБД.', date: '12 Апр, 10:05', done: true },
    { title: 'Проверка ГО', desc: 'Рассмотрение в КГД МФ РК.', date: 'В процессе', done: false, active: true },
    { title: 'Готово к подписи', desc: 'Ожидает вашей подписи.', date: '—', done: false },
    { title: 'Исполнено', desc: 'Услуга оказана успешно.', date: '—', done: false },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">Открытие ИП онлайн</h1>
          <p className="text-slate-500 mt-1 text-sm font-semibold tracking-wide uppercase">ЗАЯВКА № 182-391-233</p>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-700 font-bold text-xs rounded-full">В работе</span>
      </div>

      <Card className="shadow-lg shadow-slate-200/40 border-slate-200/50">
        <CardContent className="p-8 md:p-10">
          <div className="relative border-l-2 border-slate-100 ml-5 md:ml-6 space-y-10">
            {steps.map((s, i) => (
              <div key={i} className="relative pl-8 md:pl-10">
                <div className={`absolute -left-[18px] md:-left-[20px] top-0 w-9 h-9 md:w-10 md:h-10 rounded-full flex items-center justify-center border-[3px] bg-white transition-colors duration-500 ${
                  s.done ? 'border-emerald-500' : s.active ? 'border-cyan shadow-lg shadow-cyan/20' : 'border-slate-200'
                }`}>
                  {s.done ? <Check className="w-5 h-5 text-emerald-500" /> : s.active ? <Clock className="w-5 h-5 text-cyan animate-pulse" /> : <div className="w-2.5 h-2.5 rounded-full bg-slate-200" />}
                </div>
                
                <div>
                  <h3 className={`font-bold text-lg mb-1 ${s.done || s.active ? 'text-navy' : 'text-slate-400'}`}>{s.title}</h3>
                  <p className={`text-sm mb-2 ${s.done || s.active ? 'text-slate-500' : 'text-slate-300'}`}>{s.desc}</p>
                  <span className={`text-[11px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-md ${s.done ? 'bg-emerald-50 text-emerald-600' : s.active ? 'bg-cyan/10 text-cyan' : 'text-slate-300'}`}>
                    {s.date}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="bg-blue-50/50 border border-blue-100 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-white rounded-xl shadow-sm text-blue-500 flex items-center justify-center shrink-0">
             <PackageCheck className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-navy">Ожидаемая дата готовности</h4>
            <p className="text-slate-500 text-sm mt-0.5">12 Апр 2026, до 18:00</p>
          </div>
        </div>
        <Button variant="outline" className="bg-white" disabled>Отозвать заявку</Button>
      </div>
    </div>
  );
}
