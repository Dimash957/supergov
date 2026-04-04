import { Card, CardContent } from '../../components/ui/Card';
import { Briefcase, CheckCircle2, Gift, FileText, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useStore } from '../../store/useStore';

export function Dashboard() {
  const navigate = useNavigate();
  const user = useStore((state) => state.user);
  
  const stats = [
    { title: 'Активные заявки', value: '2', icon: Briefcase, color: 'text-blue-500', bg: 'bg-blue-100' },
    { title: 'Завершено', value: '14', icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-100' },
    { title: 'Доступные льготы', value: '3', icon: Gift, color: 'text-yellow-600', bg: 'bg-yellow-100' },
    { title: 'Документы', value: '7', icon: FileText, color: 'text-purple-500', bg: 'bg-purple-100' },
  ];

  const quickServices = [
    { name: 'Открыть ИП', path: '/application/new/ip' },
    { name: 'Пособие на ребёнка', path: '/application/new/child' },
    { name: 'Паспорт', path: '/application/new/passport' },
    { name: 'Недвижимость', path: '/application/new/property' },
    { name: 'Авто и транспорт', path: '/application/new/car' },
    { name: 'Справка о несудимости', path: '/application/new/criminal' },
  ];

  const egov50Function = { name: '🏛️ Все 50+ eGov функций', path: '/egov' };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">Добрый день, {user?.name || 'Пользователь'}!</h1>
        <p className="text-slate-500 mt-1">Здесь сводка ваших государственных услуг и важных уведомлений.</p>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-cyan to-blue-500 rounded-2xl p-6 text-white shadow-lg shadow-cyan/20 flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h3 className="font-bold text-lg mb-1 flex items-center gap-2">
            <span className="bg-white text-cyan text-xs px-2 py-1 rounded-full font-black tracking-wider">AI FOUND</span>
            Найдены доступные льготы
          </h3>
          <p className="text-white/90 text-sm">AI проанализировал ваш профиль и нашел 3 льготы на сумму <span className="font-bold">450,000 ₸/год</span>.</p>
        </div>
        <button 
          onClick={() => navigate('/benefits')}
          className="bg-white text-cyan px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-slate-50 transition-colors shrink-0 shadow-sm"
        >
          Подробнее
        </button>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s, i) => (
          <Card key={i} className="border-none shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex flex-col items-center text-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 ${s.bg} ${s.color}`}>
                <s.icon className="w-6 h-6" />
              </div>
              <p className="text-2xl font-bold text-navy">{s.value}</p>
              <p className="text-xs text-slate-500 font-medium">{s.title}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-6 mt-8">
        <div className="md:col-span-2 space-y-6">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-navy">Популярные услуги</h2>
              <Link to="/services" className="text-sm text-cyan hover:underline font-medium flex items-center">
                Все услуги <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {quickServices.map((service, i) => (
                <button 
                  key={i} 
                  onClick={() => navigate(service.path)}
                  className="bg-white p-4 rounded-xl border border-slate-100 hover:border-cyan hover:shadow-sm text-left transition-all group flex items-center justify-between"
                >
                  <span className="font-medium text-slate-700 group-hover:text-cyan transition-colors text-sm">{service.name}</span>
                  <div className="w-6 h-6 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-cyan/10 transition-colors">
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-cyan" />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* All eGov Functions Button */}
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onClick={() => navigate('/egov')}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all group border-2 border-purple-400/30"
          >
            <div className="text-center">
              <p className="text-sm font-semibold opacity-90 mb-1">РАСШИРЕННО</p>
              <h3 className="text-2xl font-bold mb-1">🏛️ Все 50+ eGov функций</h3>
              <p className="text-sm text-white/80 group-hover:text-white transition-colors">Полный каталог государственных услуг с поиском и тестированием</p>
            </div>
            <div className="flex justify-center mt-3">
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </div>
          </motion.button>
          
          <div>
            <h2 className="text-lg font-bold text-navy mb-4">Активные заявки</h2>
            <Card className="border border-slate-100 overflow-hidden">
              <div className="p-4 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
                <div>
                  <h4 className="font-semibold text-sm">Свидетельство о рождении</h4>
                  <p className="text-xs text-slate-500 mt-1">№ 182-391-233 • Сегодня</p>
                </div>
                <div className="text-right">
                  <span className="inline-block px-2.5 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs font-semibold">В обработке</span>
                </div>
              </div>
              <div className="p-4">
                <div className="w-full bg-slate-100 rounded-full h-1.5 mb-2 overflow-hidden">
                  <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '40%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-slate-500">
                  <span>Проверка документов</span>
                  <span>Ожидается: 12 апреля 2026</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-bold text-navy mb-4">Уведомления</h2>
          <Card className="border border-slate-100 shadow-sm h-[420px] overflow-hidden">
            <CardContent className="p-0 flex flex-col h-full overflow-y-auto">
              <div className="p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">Статус обновлен</p>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">Ваша заявка "Открытие ИП" успешно одобрена.</p>
                    <p className="text-[10px] text-slate-400 mt-2">10 минут назад</p>
                  </div>
                </div>
              </div>
              <div className="p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer bg-blue-50/30">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 relative">
                    <FileText className="w-4 h-4" />
                    <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-400 rounded-full border-2 border-white"></span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">Требуется действие</p>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">Прикрепите копию паспорта для заявки №192.</p>
                    <p className="text-[10px] text-slate-400 mt-2">Вчера</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
