import { useEffect } from 'react';
import { useUser } from '@stackframe/stack';
import { useStore } from '../store/useStore';
import { getApiBase } from '../lib/apiBase';
import { buildAuthHeaders } from '../lib/apiHeaders';

const API_BASE = getApiBase();

/** Подтягивает профиль из API (Stack JWT или OTP JWT) в Zustand. */
export function UserProfileBootstrap() {
  const stackUser = useUser();
  const setUser = useStore((s) => s.setUser);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const headers = await buildAuthHeaders(stackUser as Parameters<typeof buildAuthHeaders>[0]);
      if (!headers.Authorization) {
        if (stackUser?.displayName) {
          setUser({
            name: stackUser.displayName || 'Пользователь',
            email: stackUser.primaryEmail || '',
            phone: '',
            iin: '',
            stackUserId: stackUser.id,
          });
        }
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/api/auth/me`, { headers });
        if (!res.ok) return;
        const json = (await res.json()) as { data?: Record<string, string> };
        const u = json.data;
        if (cancelled || !u) return;
        setUser({
          name: (u.full_name as string) || (u.email as string) || 'Пользователь',
          email: (u.email as string) || '',
          phone: (u.phone as string) || '',
          iin: (u.iin as string) || '',
          stackUserId: (u.stack_user_id as string) || '',
        });
      } catch {
        /* ignore */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [stackUser, setUser]);

  return null;
}
