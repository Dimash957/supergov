import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import toast from 'react-hot-toast';
import { useUser } from '@stackframe/stack';
import { requireStack } from '../../lib/stack';
import { getApiBase } from '../../lib/apiBase';
import { clearOtpToken, getOtpToken, setOtpToken } from '../../lib/apiHeaders';

const API_BASE = getApiBase();

export function Login() {
  const user = useUser();
  const [mode, setMode] = useState<'password' | 'otp'>('password');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      clearOtpToken();
      const result = await requireStack().signInWithCredential({ email, password });
      if (result.status === 'error') {
        toast.error('Ошибка входа. Проверьте email и пароль.');
        return;
      }
      toast.success('Успешный вход!');
      navigate('/dashboard');
    } catch {
      toast.error('Ошибка входа.');
    } finally {
      setLoading(false);
    }
  };

  const sendOtp = async () => {
    if (!email.trim()) {
      toast.error('Введите email');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/otp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || res.statusText);
      }
      setOtpSent(true);
      toast.success('Код отправлен на почту');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Не удалось отправить код');
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (_e: React.FormEvent) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/otp/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), code: code.trim() }),
      });
      if (!res.ok) throw new Error(await res.text());
      const json = (await res.json()) as {
        data?: { access_token?: string; accessToken?: string };
        access_token?: string;
      };
      const tok =
        json.data?.access_token ??
        json.data?.accessToken ??
        json.access_token;
      if (!tok) throw new Error('Нет токена');
      setOtpToken(tok);
      toast.success('Вход по коду выполнен');
      navigate('/dashboard');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Неверный код');
    } finally {
      setLoading(false);
    }
  };

  if (user || getOtpToken()) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-navy mb-2">Вход в систему</h2>
      <div className="flex gap-2 mb-6">
        <button
          type="button"
          onClick={() => {
            setMode('password');
            setOtpSent(false);
          }}
          className={`flex-1 py-2 rounded-xl text-xs font-bold transition-colors ${
            mode === 'password' ? 'bg-navy text-white' : 'bg-slate-100 text-slate-600'
          }`}
        >
          Пароль
        </button>
        <button
          type="button"
          onClick={() => setMode('otp')}
          className={`flex-1 py-2 rounded-xl text-xs font-bold transition-colors ${
            mode === 'otp' ? 'bg-navy text-white' : 'bg-slate-100 text-slate-600'
          }`}
        >
          Код на email
        </button>
      </div>

      {mode === 'password' ? (
        <form onSubmit={handleLogin} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="ivanov@example.com" />
          <Input label="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
          <Button type="submit" className="w-full mt-2" size="lg" disabled={loading}>
            {loading ? 'Загрузка...' : 'Войти'}
          </Button>
        </form>
      ) : (
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (otpSent) void verifyOtp(e);
            else void sendOtp();
          }}
        >
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="ivanov@example.com" disabled={otpSent} />
          {otpSent && (
            <Input label="Код из письма" value={code} onChange={(e) => setCode(e.target.value)} required placeholder="000000" maxLength={6} />
          )}
          <Button type="submit" className="w-full mt-2" size="lg" disabled={loading}>
            {loading ? '...' : otpSent ? 'Войти с кодом' : 'Отправить код'}
          </Button>
          {otpSent && (
            <button type="button" className="w-full text-xs text-cyan font-semibold" onClick={() => { setOtpSent(false); setCode(''); }}>
              Изменить email
            </button>
          )}
        </form>
      )}

      <p className="text-center mt-6 text-sm text-slate-500">
        Нет аккаунта?{' '}
        <Link to="/register" className="text-cyan font-semibold hover:underline">
          Создать аккаунт
        </Link>
      </p>
    </div>
  );
}
