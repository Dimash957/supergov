/**
 * Базовый URL API. В dev без VITE_API_URL используется относительный путь `/api` → Vite proxy на бэкенд.
 */
export function getApiBase(): string {
  const raw = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
  if (raw) return raw.replace(/\/$/, '');
  if (import.meta.env.DEV) return '';
  return 'http://127.0.0.1:8000';
}
