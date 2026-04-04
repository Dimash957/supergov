import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card, CardContent } from '../../components/ui/Card';
import { CheckCircle2, UploadCloud, ChevronRight, Check } from 'lucide-react';
import toast from 'react-hot-toast';

export function ApplicationWizard() {
  const { serviceType } = useParams();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleNext = () => {
    if (step < 5) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    toast.success('Заявка успешно подана!');
    navigate('/tracker');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-navy">Оформление услуги</h1>
        <p className="text-slate-500 mt-1 text-sm font-medium">Следуйте инструкциям для заполнения заявки.</p>
      </div>

      <div className="flex justify-between items-center relative mb-12">
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1.5 bg-slate-100 -z-10 rounded-full overflow-hidden">
           <div className="h-full bg-cyan transition-all duration-500" style={{ width: `${((step - 1) / 4) * 100}%` }}></div>
        </div>
        {[1, 2, 3, 4, 5].map((s) => (
          <div key={s} className={`w-10 h-10 rounded-full border-[3px] flex items-center justify-center font-bold text-sm bg-white transition-colors duration-300 ${step >= s ? 'border-cyan text-cyan' : 'border-slate-200 text-slate-400'} ${step > s ? 'bg-cyan text-white border-cyan' : ''}`}>
            {step > s ? <Check className="w-5 h-5" /> : s}
          </div>
        ))}
      </div>

      <Card className="min-h-[350px] shadow-sm border-slate-200/60">
        <CardContent className="p-8">
          {step === 1 && (
            <div className="space-y-5 animate-in fade-in slide-in-from-right-4 duration-500">
              <h2 className="font-bold text-navy text-lg">Шаг 1: Основные данные</h2>
              <div className="p-4 bg-[aliceblue] border border-blue-100 rounded-xl flex items-start gap-3">
                 <CheckCircle2 className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
                 <p className="text-sm text-blue-800 leading-relaxed font-medium">Данные автоматически заполнены из вашего цифрового профиля.</p>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <Input label="ИИН" value="950412300456" disabled className="bg-slate-50 text-slate-500" />
                <Input label="ФИО" value="Иванов Иван Иванович" disabled className="bg-slate-50 text-slate-500" />
              </div>
              <Input label="Адрес регистрации" value="г. Астана, пр. Мангилик Ел, д. 23" disabled className="bg-slate-50 text-slate-500" />
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5 animate-in fade-in slide-in-from-right-4 duration-500">
              <h2 className="font-bold text-navy text-lg">Шаг 2: Детали заявки</h2>
              <Input label="Название организации" placeholder="Например: SuperCompany" />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-slate-700">Вид деятельности (ОКЭД)</label>
                <select className="flex h-12 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan transition-shadow">
                  <option>Выберите вид деятельности...</option>
                  <option>Разработка программного обеспечения (62.01.1)</option>
                  <option>Розничная торговля (47.19.1)</option>
                </select>
              </div>
            </div>
          )}

          {/* Steps 3,4,5... */}
          {/* Using concise implementation for brevity */}
          {step === 3 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
              <h2 className="font-bold text-navy text-lg mb-4">Шаг 3: Документы</h2>
              <div className="border-2 border-dashed border-slate-200 rounded-2xl p-10 flex flex-col items-center justify-center text-center hover:border-cyan hover:bg-cyan/5 transition-colors cursor-pointer group">
                <UploadCloud className="w-12 h-12 text-slate-300 group-hover:text-cyan mb-3 transition-colors" />
                <p className="font-semibold text-slate-700">Перетащите файлы сюда</p>
                <p className="text-xs text-slate-400 mt-1.5">или нажмите чтобы выбрать (PDF, JPG до 5 МБ)</p>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
              <h2 className="font-bold text-navy text-lg mb-4">Шаг 4: Проверка данных</h2>
              <div className="space-y-0 border border-slate-100 rounded-2xl bg-slate-50 overflow-hidden">
                <div className="flex justify-between border-b border-slate-200 p-4">
                  <span className="text-sm text-slate-500">Услуга</span>
                  <span className="text-sm font-semibold text-right">Открытие ИП</span>
                </div>
                <div className="flex justify-between border-b border-slate-200 p-4">
                  <span className="text-sm text-slate-500">Госпошлина</span>
                  <span className="text-sm font-bold text-emerald-600">0 ₸ (Бесплатно)</span>
                </div>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 text-center py-8">
              <div className="w-24 h-24 mx-auto bg-gradient-to-tr from-navy to-blue-800 text-white rounded-full flex items-center justify-center font-bold shadow-xl shadow-navy/20 mb-6 border-4 border-white">
                <span className="text-sm tracking-widest">EDS</span>
              </div>
              <h2 className="font-bold text-navy text-2xl">Подписание ЭЦП</h2>
              <p className="text-sm text-slate-500 max-w-sm mx-auto leading-relaxed">Нажмите кнопку ниже для старта процесса подписания через NCALayer или eGov Mobile.</p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={handleBack} disabled={step === 1 || loading} className="w-32">Назад</Button>
        {step < 5 ? (
          <Button onClick={handleNext} className="w-40">Далее <ChevronRight className="w-4 h-4 ml-1" /></Button>
        ) : (
          <Button onClick={handleSubmit} disabled={loading} className="w-auto px-8 bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/20">
            {loading ? 'Обработка...' : 'Подписать и отправить'}
          </Button>
        )}
      </div>
    </div>
  );
}
