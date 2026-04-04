import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import toast from 'react-hot-toast';
import { requireStack } from '../../lib/stack';
import { clearOtpToken } from '../../lib/apiHeaders';
import { api } from '../../lib/axios';
import { MailCheck } from 'lucide-react';

const registerSchema = z.object({
  iin: z.string().length(12, 'ИИН должен содержать ровно 12 цифр').regex(/^\d+$/, 'Только цифры'),
  name: z.string().min(2, 'Введите полное имя'),
  email: z.string().email('Неверный формат email'),
  phone: z.string().min(10, 'Введите номер телефона'),
  password: z.string().min(6, 'Пароль минимум 6 символов'),
});

type RegisterForm = z.infer<typeof registerSchema>;

export function Register() {
  const [loading, setLoading] = useState(false);
  const [successMode, setSuccessMode] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema)
  });

  const onSubmit = async (data: RegisterForm) => {
    setLoading(true);
    try {
      clearOtpToken();
      const app = requireStack();
      const signUp = await app.signUpWithCredential({
        email: data.email,
        password: data.password,
        noVerificationCallback: true,
      });
      if (signUp.status === 'error') {
        throw signUp.error;
      }

      const user = await app.getUser();
      const stackUserId = user?.id ?? 'mock_id';

      await api.post('/api/auth/register', {
        iin: data.iin,
        email: data.email.trim().toLowerCase(),
        phone: data.phone,
        full_name: data.name,
        stack_user_id: stackUserId,
      });

      setSuccessMode(true);
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? String((err as { response?: { data?: { detail?: unknown } } }).response?.data?.detail ?? '')
          : '';
      toast.error(
        msg || 'Ошибка при регистрации. Возможно, пользователь уже существует.',
      );
    } finally {
      setLoading(false);
    }
  };

  if (successMode) {
    return (
      <div className="text-center py-6 animate-in fade-in zoom-in duration-500">
        <div className="w-20 h-20 bg-emerald-100 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <MailCheck className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-navy mb-2">Проверьте вашу почту</h2>
        <p className="text-slate-500 text-sm mb-6 max-w-sm mx-auto leading-relaxed">
          Мы отправили письмо на <span className="font-semibold">{errors.email ? '' : ''}</span> с инструкциями для подтверждения аккаунта.
        </p>
        <Link to="/login">
          <Button variant="outline" className="w-full">Вернуться ко входу</Button>
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-navy mb-6">Создать аккаунт</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input 
          label="ИИН" 
          placeholder="12 цифр"
          {...register('iin')}
          error={errors.iin?.message}
        />
        <Input 
          label="ФИО" 
          placeholder="Иванов Иван Иванович"
          {...register('name')}
          error={errors.name?.message}
        />
        <Input 
          label="Email" 
          type="email" 
          placeholder="ivan@example.com"
          {...register('email')}
          error={errors.email?.message}
        />
        <Input 
          label="Телефон" 
          type="tel" 
          placeholder="+7 (XXX) XXX-XX-XX"
          {...register('phone')}
          error={errors.phone?.message}
        />
        <Input 
          label="Пароль" 
          type="password" 
          placeholder="••••••••"
          {...register('password')}
          error={errors.password?.message}
        />
        <Button type="submit" className="w-full mt-4" size="lg" disabled={loading}>
          {loading ? 'Создание...' : 'Зарегистрироваться'}
        </Button>
      </form>
      <p className="text-center mt-6 text-sm text-slate-500">
        Уже есть аккаунт? <Link to="/login" className="text-cyan font-semibold hover:underline">Войти</Link>
      </p>
    </div>
  );
}
