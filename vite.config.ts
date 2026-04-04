import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const root = process.cwd()
  // Пустая строка = все ключи из .env (в т.ч. STACK_* из перенесённого backend/.env).
  const fileEnv = loadEnv(mode, root, '')
  const stackProjectId = (
    fileEnv.VITE_STACK_PROJECT_ID ||
    fileEnv.NEXT_PUBLIC_STACK_PROJECT_ID ||
    fileEnv.STACK_PROJECT_ID ||
    ''
  ).trim()
  const stackPublishable = (
    fileEnv.VITE_STACK_PUBLISHABLE_KEY ||
    fileEnv.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY ||
    fileEnv.STACK_PUBLISHABLE_CLIENT_KEY ||
    fileEnv.NEXT_PUBLIC_STACK_PUBLISHABLE_KEY ||
    ''
  ).trim()
  const supabaseUrl = (
    fileEnv.VITE_SUPABASE_URL ||
    fileEnv.NEXT_PUBLIC_SUPABASE_URL ||
    fileEnv.SUPABASE_URL ||
    ''
  ).trim()
  const supabaseAnon = (
    fileEnv.VITE_SUPABASE_ANON_KEY ||
    fileEnv.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    fileEnv.SUPABASE_ANON_KEY ||
    ''
  ).trim()
  const devApiProxy = (
    fileEnv.VITE_DEV_API_PROXY ||
    fileEnv.VITE_API_URL ||
    'http://127.0.0.1:8000'
  ).trim()

  return {
    // Как в Next.js: NEXT_PUBLIC_* попадает в клиент; плюс стандартный VITE_*.
    envPrefix: ['VITE_', 'NEXT_PUBLIC_'],
    // SDK Stack читает process.env.NEXT_PUBLIC_*; фронт — import.meta.env.VITE_*.
    // Без префикса VITE_ переменные из .env не попадают в бандл — дублируем сюда после merge.
    define: {
      'import.meta.env.VITE_STACK_PROJECT_ID': JSON.stringify(stackProjectId),
      'import.meta.env.VITE_STACK_PUBLISHABLE_KEY': JSON.stringify(stackPublishable),
      'process.env.NEXT_PUBLIC_STACK_PROJECT_ID': JSON.stringify(stackProjectId),
      'process.env.NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY':
        JSON.stringify(stackPublishable),
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(supabaseUrl),
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(supabaseAnon),
      'process.env.NEXT_PUBLIC_SUPABASE_URL': JSON.stringify(supabaseUrl),
      'process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY': JSON.stringify(supabaseAnon),
    },
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target: devApiProxy,
          changeOrigin: true,
        },
      },
    },
  }
})
