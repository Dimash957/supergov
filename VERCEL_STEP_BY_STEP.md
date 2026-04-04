# 🎯 VERCEL DEPLOY: Финальная Инструкция

## Текущий Статус:

✅ Stack Auth переменные добавлены в `.env`  
✅ Все файлы конфигурации готовы  
✅ GitHub репозиторий обновлён  
✅ Фронт локально работает  

**Осталось:** Добавить ENV переменные в Vercel = 3 минуты ⏱️

---

## 🔧 Этап 1: Vercel Settings (3 минуты)

### Открыть Dashboard:
```
https://vercel.com/dashboard
```

**Должен выглядеть так:**
```
┌─────────────────────────────────────┐
│  Your Projects                      │
├─────────────────────────────────────┤
│ [supergov]  ...  [Settings] [Redeploy]
└─────────────────────────────────────┘
```

### Клик на Settings:
```
→ Settings (в группе кнопок рядом с supergov)
```

**Должна открыться страница:**
```
┌──────────────────────────────────────┐
│ Settings                             │
├──────────────────────────────────────┤
│ ☐ General                            │
│ ☐ Deployments                        │
│ ☑ Environment Variables              │
│ ☐ Domains                            │
│ ☐ Git                                │
└──────────────────────────────────────┘
```

### Нажать "Environment Variables":
```
→ Должна быть уже выбрана
→ Если нет - кликнуть на неё
```

---

## 📝 Этап 2: Добавить Переменные

### В форме "Add New Variable" добавить одну за одной:

#### Переменная 1:
```
Name:  VITE_STACK_PROJECT_ID
Value: 6a0925d5-467b-40ef-ad9e-265556e73476
Environment: All environments (or Production)
→ [Save]
```

#### Переменная 2:
```
Name:  VITE_STACK_PUBLISHABLE_KEY
Value: pck_e11h1wjz9zkb4ngebj7xn4ngebj7xn...
       (копировать точное значение из своего Stack Auth)
Environment: All environments (or Production)
→ [Save]
```

#### Переменная 3:
```
Name:  VITE_API_URL
Value: https://supergov-api.railway.app

(или для Development: http://localhost:8000)

Environment: Production (для продакшена)
→ [Save]
```

### Результат должен быть:
```
┌────────────────────────────────────────┐
│ Environment Variables                  │
├────────────────────────────────────────┤
│ ✅ VITE_STACK_PROJECT_ID               │
│    = 6a0925d5-467b-40ef-ad9e-265556...│
│    [Edit] [Delete]                     │
│                                        │
│ ✅ VITE_STACK_PUBLISHABLE_KEY          │
│    = pck_e11h1wjz9zkb4ngebj7xn4n...   │
│    [Edit] [Delete]                     │
│                                        │
│ ✅ VITE_API_URL                        │
│    = https://supergov-api.railway.app  │
│    [Edit] [Delete]                     │
└────────────────────────────────────────┘
```

---

## 🔄 Этап 3: Пересобрать (Redeploy)

### Перейти на Deployments:
```
Vercel Dashboard → supergov → Deployments (вверху)
```

**Должно выглядеть:**
```
┌──────────────────────────────────────┐
│ Deployments                          │
├──────────────────────────────────────┤
│ 1. 🔴 d757b4b... (latest)            │
│    Apr 5, 2026 10:30 AM              │
│    Vercel: Ready to Redeploy         │
│                                      │
│ 2. 🟢 ed49537...                     │
│    Apr 4, 2026 5:00 PM               │
│    Ready                             │
└──────────────────────────────────────┘
```

### Нажать на последний (самый верхний) deployment

### В открывшейся странице нажать [Redeploy] (вверху справа)

### Дождаться (может быть долго):
```
Building...     (4-5 минут)
Deploying...    (1-2 минут)
Ready ✅        (готово!)
```

---

## ✅ Этап 4: Проверка

### Открыть приложение:
```
https://supergov.vercel.app
```

### Что должно быть видно:
```
┌─────────────────────────────────┐
│   SuperGov                      │
│   [Your Profile]  [Log in]      │
├─────────────────────────────────┤
│ eGov Functions                  │
│ Documents                       │
│ Benefits                        │
│ ...                             │
└─────────────────────────────────┘
```

### Проверки:
- [ ] Нет красной ошибки про Stack Auth
- [ ] Нет ошибок в консоли (F12 → Console)
- [ ] Кнопка "Log in" видна
- [ ] Можно нажать Login

### Конечная проверка:
1. Нажать **"Log in"** (если есть Stack Auth button)
2. Должна открыться Stack Auth форма
3. ✅ Готово!

---

## 🚨 Если Что-то Не Работает:

### Проблема: Deployments не начинается

**Решение:**
1. Refresh страницу (F5)
2. Попробуй Redeploy ещё раз
3. Если всё равно - check GitHub Actions

### Проблема: Build Fail ❌

**Смотри Logs:**
1. Deployments → клик на красный deployment
2. Scrolled вниз - Find "Logs"
3. Там будет ошибка типа:
   ```
   Error: VITE_STACK_PUBLISHABLE_KEY is not defined
   ```

**Решение:** Переменные не добавились
- Вернись на Settings → Environment Variables
- Проверь что все 3 переменные есть
- Нажми [Redeploy] снова

### Проблема: Deployment Ready но приложение показывает ошибку

**Смотри Console (F12):**
```javascript
// Might show:
// TypeError: stack is undefined
// CORS error: Access to XMLHttpRequest...
// 502 Bad Gateway
```

**Решение различается:**
- `stack is undefined` → VITE_STACK_PROJECT_ID или VITE_STACK_PUBLISHABLE_KEY неправильны
- `502 Bad Gateway` → Railway backend не запущен
- `CORS error` → Backend CORS настройки нужны

---

## 📱 Если Всё Работает:

```
┌─────────────────────────────┐
│  DEPLOYMENT: ✅ SUCCESS!    │
├─────────────────────────────┤
│                             │
│  Frontend: ✅ Vercel        │
│  Backend:  🚂 Railway       │
│  Database: 🗄️ Supabase      │
│  Auth:     🔐 Stack Auth    │
│                             │
│  Link: https://             │
│        supergov.vercel.app  │
│                             │
│  Готово к использованию! 🎉 │
└─────────────────────────────┘
```

---

## 💬 Нужна Помощь?

**Отправь скриншот:**
1. Страницы Settings → Environment Variables
2. Страницы Deployments с ошибкой/статусом
3. Developer Console (F12) если ошибка в приложении

**Я помогу за 2 минуты!** 👍

---

## ⏱️ Примерное время выполнения:

```
Добавить 3 переменные        = 2 минуты
Нажать Redeploy              = 30 секунд
Build & Deploy               = 5-7 минут
Проверка                     = 1 минута
─────────────────────────────
Всего:                      ~8-10 минут ✅
```

**Начнём? Открыл Vercel Dashboard?** 🚀
