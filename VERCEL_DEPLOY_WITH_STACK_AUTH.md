# 🚀 Vercel Deploy: Полная Инструкция со Stack Auth

## 🔴 Если вы видите ошибку про Stack Auth

**Ошибка:**
```
Не настроен Stack Auth
В gogo/.env нужны UUID проекта и publishable key: 
VITE_STACK_PROJECT_ID + VITE_STACK_PUBLISHABLE_KEY
```

**Решение:** Нужно добавить Environment Variables в Vercel!

---

## ✅ Шаг 1: Получить значения Stack Auth

1. Открыть свой **Stack Auth Dashboard**
2. Найти Project → Settings
3. Скопировать:
   - **Project ID** (UUID типа: `6a0925d5-467b-40ef-ad9e-265556e73476`)
   - **Publishable Client Key** (типа: `pck_e11h1wjz9zkb4ngebj7xn...`)

---

## ✅ Шаг 2: Добавить в Vercel Environment Variables

### Вариант А: Через веб интерфейс (Рекомендуется)

1. Открыть https://vercel.com/dashboard
2. Выбрать проект `supergov`
3. Перейти в **Settings** (шестерёнка вверху)
4. Нажать на **Environment Variables** (левое меню)
5. Добавить эти 3 переменные:

| Key | Value | Environments |
|-----|-------|--------------|
| `VITE_STACK_PROJECT_ID` | `6a0925d5-467b-40ef-ad9e-265556e73476` | All |
| `VITE_STACK_PUBLISHABLE_KEY` | `pck_e11h1wjz9zkb4ngebj7xn4ngebj7xn...` | All |
| `VITE_API_URL` | `https://supergov-api.railway.app` | Production |
| `VITE_API_URL` | `http://localhost:8000` | Development |

6. После добавления → **Deployments** → нажать на последний deployment
7. Сверху → **Redeploy** (пересобрать с новыми переменными)

### Вариант Б: Через Vercel CLI

```bash
# Установить Vercel CLI
npm i -g vercel

# Зайти в проект
cd c:\Users\gulzi\OneDrive\Рабочий\ стол\gogo

# Дать переменные
vercel env add VITE_STACK_PROJECT_ID
vercel env add VITE_STACK_PUBLISHABLE_KEY
vercel env add VITE_API_URL

# Пересобрать
vercel redeploy --prod
```

---

## 📋 Все Необходимые Переменные

### Обязательные (для фронта):
```
VITE_STACK_PROJECT_ID=6a0925d5-467b-40ef-ad9e-265556e73476
VITE_STACK_PUBLISHABLE_KEY=pck_e11h1wjz9zkb4ngebj7xn4ngebj7xn...
VITE_API_URL=https://supergov-api.railway.app
```

### Optional (если нужны):
```
VITE_APP_NAME=SuperGov
VITE_APP_VERSION=1.0.0
```

---

## ✅ Проверка После Деплоя

1. Открыть https://supergov.vercel.app
2. Должна загрузиться страница (без красной ошибки)
3. Нажать "Log in with Stack"
4. Должна открыться форма логина
5. ✅ Готово!

---

## 🆘 Если Всё ещё Не Работает

### Ошибка: "Cannot find module @stackframe/stack"
- Решение: Нужна переустановка dependencies
```bash
cd c:\Users\gulzi\OneDrive\Рабочий\ стол\gogo
npm install
npm run build
```

### Ошибка в консоли гого: VITE_STACK_PUBLISHABLE_KEY undefined
- Решение: Переменные не попали в фронт
- Проверь что добавил в Vercel Settings → Environment Variables
- Нажми Redeploy

### Ошибка: 502 Bad Gateway на https://supergov.vercel.app
- Решение: Backend (Railway) не запущен или недоступен
- Проверь Railway dashboard что deploy успешен
- Проверь VITE_API_URL правильный

---

## 🚀 Итоговый Workflow

```
1. Получить Stack Auth credentials ✅
   ↓
2. Добавить в Vercel Settings → Environment Variables ✅
   ↓
3. Нажать Redeploy ✅
   ↓
4. Дождаться Build complete ✅
   ↓
5. Открыть https://supergov.vercel.app ✅
   ↓
6. Тестировать логин ✅
```

---

## 💡 Где Взять Значения?

**VITE_STACK_PROJECT_ID:**
- Открыть https://console.stack-auth.com
- Выбрать свой проект
- Скопировать Project ID

**VITE_STACK_PUBLISHABLE_KEY:**
- Там же на странице Project
- Найти "Publishable Client Key"
- Скопировать ключ

**VITE_API_URL (для продакшена):**
- После деплоя Railway
- Railway dashboard → Project → Domains
- Скопировать URL типа `https://supergov-api.railway.app`

---

**Добавил переменные? Готово! 🎉**

Если ещё есть вопросы - напиши какую точно ошибку видишь!
