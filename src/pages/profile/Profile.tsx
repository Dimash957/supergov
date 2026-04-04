import { useEffect, useState } from 'react';
import { useUser } from '@stackframe/stack';
import toast from 'react-hot-toast';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiBase } from '../../lib/apiBase';
import { buildAuthHeaders } from '../../lib/apiHeaders';
import { useStore } from '../../store/useStore';

const API_BASE = getApiBase();

type Me = {
  full_name?: string;
  email?: string;
  phone?: string;
  iin?: string;
  address?: string;
  birth_date?: string;
  language?: string;
};

export function Profile() {
  const stackUser = useUser();
  const setStoreUser = useStore((s) => s.setUser);
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    address: '',
    birth_date: '',
    language: 'ru',
  });

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
        const res = await fetch(`${API_BASE}/api/auth/me`, { headers });
        if (!res.ok) throw new Error('Не удалось загрузить профиль');
        const json = (await res.json()) as { data: Me };
        const u = json.data;
        setMe(u);
        setForm({
          full_name: u.full_name || stackUser?.displayName || '',
          phone: u.phone || '',
          address: (u as { address?: string }).address || '',
          birth_date: u.birth_date || '',
          language: u.language || 'ru',
        });
      } catch {
        toast.error('Профиль недоступен без авторизации');
      } finally {
        setLoading(false);
      }
    })();
  }, [stackUser]);

  const save = async () => {
    setSaving(true);
    try {
      const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        method: 'PATCH',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: form.full_name || undefined,
          phone: form.phone || undefined,
          address: form.address || undefined,
          birth_date: form.birth_date || undefined,
          language: form.language || undefined,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const json = (await res.json()) as { data: Me };
      setMe(json.data);
      setStoreUser({
        name: form.full_name || json.data?.email || 'Пользователь',
        email: json.data?.email || me?.email || '',
        phone: form.phone || '',
        iin: me?.iin || '',
        stackUserId: '',
      });
      toast.success('Сохранено');
      setSaveSuccess(true);
      window.setTimeout(() => setSaveSuccess(false), 6000);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Ошибка');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="text-slate-500 text-sm p-6">Загрузка профиля…</p>;
  }

  return (
    <div className="max-w-xl space-y-6 p-2 md:p-0">
      <div>
        <h1 className="text-2xl font-bold text-navy">Личные данные</h1>
        <p className="text-slate-500 text-sm mt-1">Имя из регистрации используется в AI-ассистенте и интерфейсе.</p>
      </div>
      {saveSuccess && (
        <div
          className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-900"
          role="status"
        >
          Форма успешно отправлена — данные профиля сохранены.
        </div>
      )}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <Input label="ФИО" value={form.full_name} onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))} />
        <Input label="Email" value={me?.email || ''} disabled className="opacity-70" />
        <Input label="ИИН" value={me?.iin || ''} disabled className="opacity-70" />
        <Input label="Телефон" value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} />
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">Адрес</label>
          <textarea
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm min-h-[72px]"
            value={form.address}
            onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
          />
        </div>
        <Input
          label="Дата рождения"
          type="date"
          value={form.birth_date}
          onChange={(e) => setForm((f) => ({ ...f, birth_date: e.target.value }))}
        />
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">Язык интерфейса</label>
          <select
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            value={form.language}
            onChange={(e) => setForm((f) => ({ ...f, language: e.target.value }))}
          >
            <option value="ru">Русский</option>
            <option value="kz">Қазақша</option>
            <option value="en">English</option>
          </select>
        </div>
        <Button type="button" className="w-full" onClick={() => void save()} disabled={saving}>
          {saving ? 'Сохранение…' : 'Сохранить'}
        </Button>
      </div>
    </div>
  );
}
