/**
 * Базовый URL API.
 * - В dev без VITE_API_URL используется относительный путь `/api` -> Vite proxy на бэкенд.
 * - В production при ошибочно заданном localhost используется same-origin `/api`,
 *   чтобы не ломать сайт на внешнем домене.
 */
export function getApiBase(): string {
  const raw = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
  if (raw) {
    const normalized = raw.replace(/\/$/, '');
    const isLocalApi = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(normalized);
    const isBrowser = typeof window !== 'undefined';
    const isCurrentHostLocal = isBrowser
      ? /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname)
      : false;

    if (!import.meta.env.DEV && isLocalApi && !isCurrentHostLocal) {
      return '';
    }

    return normalized;
  }

  return '';
}
