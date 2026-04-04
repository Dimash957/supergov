import { requireStack } from './stack';

const OTP_KEY = 'supergov_otp_token';

export function getOtpToken(): string | null {
  return localStorage.getItem(OTP_KEY);
}

export function setOtpToken(token: string) {
  localStorage.setItem(OTP_KEY, token);
}

export function clearOtpToken() {
  localStorage.removeItem(OTP_KEY);
}

/** Сессия Stack (@stackframe/stack): токен через getAccessToken (актуально), getTokens — запасной вариант. */
type StackSessionUser = {
  getAccessToken?: () => Promise<string | null>;
  getTokens?: () => Promise<{ accessToken: string | null }>;
} | null;

async function tokenFromStackApp(): Promise<string | null> {
  try {
    const app = requireStack();
    if (typeof app.getAccessToken === 'function') {
      return await app.getAccessToken();
    }
  } catch {
    /* Stack не инициализирован вне провайдера */
  }
  return null;
}

export async function buildAuthHeaders(stackUser: StackSessionUser): Promise<Record<string, string>> {
  const headers: Record<string, string> = {};
  const otp = getOtpToken();
  if (otp) {
    headers.Authorization = `Bearer ${otp}`;
    return headers;
  }

  if (stackUser) {
    if (typeof stackUser.getAccessToken === 'function') {
      const access = await stackUser.getAccessToken();
      if (access) {
        headers.Authorization = `Bearer ${access}`;
        return headers;
      }
    }
    if (typeof stackUser.getTokens === 'function') {
      const t = await stackUser.getTokens();
      if (t?.accessToken) {
        headers.Authorization = `Bearer ${t.accessToken}`;
        return headers;
      }
    }
  }

  const fromApp = await tokenFromStackApp();
  if (fromApp) {
    headers.Authorization = `Bearer ${fromApp}`;
  }
  return headers;
}
