import { StackClientApp } from "@stackframe/stack";

const publishableClientKey = (
  import.meta.env.VITE_STACK_PUBLISHABLE_KEY ||
  import.meta.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY ||
  ""
).trim();

const projectId = (
  import.meta.env.VITE_STACK_PROJECT_ID ||
  import.meta.env.NEXT_PUBLIC_STACK_PROJECT_ID ||
  ""
).trim();

let stackInitError: string | null = null;
let _stack: StackClientApp | null = null;

if (!projectId || !publishableClientKey) {
  stackInitError =
    "В gogo/.env нужны UUID проекта и publishable key: VITE_STACK_PROJECT_ID + VITE_STACK_PUBLISHABLE_KEY, либо как в backend: STACK_PROJECT_ID + STACK_PUBLISHABLE_CLIENT_KEY / NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY. Перезапустите npm run dev.";
} else {
  try {
    _stack = new StackClientApp({
      projectId,
      publishableClientKey,
      tokenStore: "cookie",
      // Без этого в @stackframe/stack для браузера остаётся redirectMethod "nextjs".
      redirectMethod: "window",
    });
  } catch (e) {
    stackInitError =
      e instanceof Error ? e.message : String(e);
  }
}

export { stackInitError };
export const stack = _stack;

/** Для страниц внутри StackProvider — stack всегда задан. */
export function requireStack(): StackClientApp {
  if (!_stack) {
    throw new Error(stackInitError || "Stack не инициализирован");
  }
  return _stack;
}
