import { Card, CardContent } from '../../components/ui/Card';
import { ArrowUpRight, ArrowDownRight, Activity, Star } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, Tooltip } from 'recharts';

export function AgenciesRating() {
  const data = [
    { name: 'МВД Республики Казахстан', score: 98, trend: 'up', val: '+2%' },
    { name: 'Правительство для граждан (ЦОН)', score: 92, trend: 'up', val: '+5%' },
    { name: 'Министерство Здравоохранения', score: 85, trend: 'down', val: '-1%' },
    { name: 'Налоговый комитет РК', score: 76, trend: 'up', val: '+10%' },
  ];

  const chartData = [ { name: 'Jan', uv: 80 }, { name: 'Feb', uv: 85 }, { name: 'Mar', uv: 92 }, { name: 'Apr', uv: 98 } ];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-navy">Рейтинг ведомств</h1>
        <p className="text-slate-500 mt-1 text-sm">Оценка скорости и качества государственных услуг.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {data.map((agency, i) => (
            <Card key={i} className="hover:border-cyan transition-colors cursor-pointer group shadow-sm">
               <CardContent className="p-5 flex items-center justify-between">
                 <div className="flex items-center gap-5">
                   <div className="w-14 h-14 rounded-full bg-slate-50 flex items-center justify-center font-black text-slate-300 text-2xl group-hover:bg-cyan group-hover:text-white transition-all shadow-inner">
                     {i + 1}
                   </div>
                   <div>
                     <h3 className="font-bold text-navy text-lg">{agency.name}</h3>
                     <div className="flex items-center gap-4 mt-2">
                       <span className="text-xs font-semibold text-slate-400">Индекс CSI</span>
                       <div className="w-32 h-2 bg-slate-100 rounded-full overflow-hidden">
                         <div className={`h-full ${agency.score > 90 ? 'bg-emerald-400' : agency.score > 80 ? 'bg-cyan' : 'bg-gold'}`} style={{ width: `${agency.score}%` }}></div>
                       </div>
                     </div>
                   </div>
                 </div>
                 <div className="text-right flex flex-col items-end gap-1">
                   <span className="text-3xl font-black text-navy">{agency.score}</span>
                   <span className={`text-xs font-bold flex items-center bg-slate-50 px-2 py-0.5 rounded-md ${agency.trend === 'up' ? 'text-emerald-500' : 'text-red-500'}`}>
                     {agency.trend === 'up' ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
                     {agency.val}
                   </span>
                 </div>
               </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="sticky top-24">
          <Card className="border-slate-200 shadow-xl shadow-slate-200/20 bg-gradient-to-b from-white to-slate-50/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-cyan/10 flex items-center justify-center">
                  <Activity className="w-5 h-5 text-cyan" />
                </div>
                <div>
                  <h3 className="font-bold text-navy">Динамика МВД РК</h3>
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Последние 4 месяца</p>
                </div>
              </div>
              <div className="h-56 w-full -ml-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <Tooltip 
                      contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)' }} 
                      itemStyle={{ color: '#1A2B6B', fontWeight: 'bold' }}
                    />
                    <Line type="monotone" dataKey="uv" stroke="#00B4D8" strokeWidth={4} dot={{ r: 5, fill: '#fff', strokeWidth: 3, stroke: '#00B4D8' }} activeDot={{ r: 8, fill: '#00B4D8', strokeWidth: 0 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
