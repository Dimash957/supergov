import { Card, CardContent } from '../../components/ui/Card';
import { Gift, Sparkles } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function Benefits() {
  const benefits = [
    { id: 1, name: 'Пособие по уходу за ребенком', amount: '350 000 ₸', tags: ['Семья', 'Дети'], desc: 'Доступно на основе состава вашей семьи по данным ГБД ФЛ.' },
    { id: 2, name: 'Скидка на транспортный налог', amount: '45 000 ₸', tags: ['Авто'], desc: 'Рассчитано на основе вашего автомобиля 2.4L и статуса льготника.' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-8 md:p-10 rounded-[2rem] text-white shadow-xl shadow-emerald-500/20 relative overflow-hidden">
        <Sparkles className="absolute -right-4 top-1/2 -translate-y-1/2 w-64 h-64 text-white/10 rotate-12" />
        <div className="relative z-10 w-full md:w-2/3">
          <span className="bg-white/20 backdrop-blur-md px-3 py-1.5 text-[10px] uppercase font-bold tracking-widest rounded-full mb-4 inline-block">AI Smart Discovery</span>
          <h1 className="text-3xl md:text-4xl font-black mb-3 leading-tight">Найдено 2 льготы</h1>
          <p className="text-emerald-50 text-lg opacity-90 max-w-lg leading-relaxed">Мы проанализировали ваш профиль и нашли государственные выплаты на общую сумму <span className="font-bold underline decoration-white/30 decoration-2 underline-offset-4">395 000 ₸ в год</span>.</p>
        </div>
      </div>
      
      <div className="grid md:grid-cols-2 gap-5 pt-2">
        {benefits.map(b => (
          <Card key={b.id} className="border-emerald-100 hover:border-emerald-300 hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6 md:p-8">
              <div className="flex flex-col h-full gap-6">
                <div className="flex gap-4 items-start">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                    <Gift className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="font-bold text-navy text-xl leading-tight mb-2">{b.name}</h3>
                    <div className="flex gap-2">
                      {b.tags.map(t => (
                        <span key={t} className="text-[10px] px-2 py-1 bg-slate-100 text-slate-500 font-bold uppercase rounded-md tracking-wider">{t}</span>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="mt-auto pt-4 border-t border-slate-100">
                  <p className="text-3xl font-black text-emerald-500 mb-3">{b.amount}<span className="text-sm font-semibold text-slate-400 ml-1">/ год</span></p>
                  <p className="text-sm text-slate-500 mb-6 leading-relaxed">{b.desc}</p>
                  <Button className="w-full bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white transition-colors h-12 text-sm">Оформить в 1 клик</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
