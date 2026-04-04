# ✅ ФИНАЛЬНЫЙ ЧЕК-ЛИСТ: Vercel Deploy со Stack Auth

## 🎯 Что было сделано:

✅ **Добавлены Stack Auth переменные в `.env`:**
- VITE_STACK_PROJECT_ID 
- VITE_STACK_PUBLISHABLE_KEY
- VITE_API_URL

✅ **Создан `.env.example`** - для документации

✅ **Созданы гайды:**
- VERCEL_DEPLOY_WITH_STACK_AUTH.md
- DEPLOY_GUIDE_VERCEL_RAILWAY.md  
- Procfile для Railway
- vercel.json для Vercel

✅ **Запушено на GitHub** - готово к деплою

✅ **Фронт локально запустился** на http://localhost:5177

---

## 🚀 ЧТО ДЕЛАТЬ ТЕПЕРЬ:

### Шаг 1: Добавить ENV Variables в Vercel (2 минуты)

1. Открыть https://vercel.com/dashboard
2. Выбрать проект `supergov`
3. **Settings** → **Environment Variables**
4. **Добавить эти строки:**

```
VITE_STACK_PROJECT_ID = 6a0925d5-467b-40ef-ad9e-265556e73476
VITE_STACK_PUBLISHABLE_KEY = pck_e11h1wjz9zkb4ngebj7xn4ngebj7xn...
VITE_API_URL = https://supergov-api.railway.app
```

(VITE_API_URL поставь для Production. Для Development можно `http://localhost:8000`)

5. **Deploy** → Выбрать последний deployment → **Redeploy**

### Шаг 2: Дождаться Build (✋ 2-3 минуты)

Смотришь **Deployments** → ждёшь когда статус будет **Ready** (зелёная галочка)

### Шаг 3: Проверить

Открыть https://supergov.vercel.app

**Должно быть:**
- ✅ Страница загрузилась (без красной ошибки про Stack Auth)
- ✅ Кнопка "Log in with Stack" видна
- ✅ Нажимаешь → открывается форма логина Stack Auth

---

## 📝 Видеоинструкция (если сложно):

```
1. https://vercel.com/dashboard 
2. Клик на "supergov"
3. Settings (меню слева внизу)
4. Ищешь "Environment Variables"
5. Добавляешь 3 переменные из таблицы выше
6. Save
7. Deployments вверху
8. Клик на последний (красная иконка если нужно пересобрать)
9. Сверху "Redeploy" (или "Deploying...")
10. Ждёшь зелёную "Ready"
11. Клик на URL вверху → открывается приложение
```

---

## 🆘 Если Что-то Не Работает:

### ❌ "Stack Auth not configured"

**Проверить:**
1. Переменные добавлены в Vercel Settings?
2. Нажал ли Redeploy?
3. Deployment статус "Ready"?

**Решение:**
- Vercel → Deployments → последний
- Смотри **Logs** (внизу) - там ошибка будет

### ❌ 502 Bad Gateway

**Означает:** Backend (Railway) не запущен

**Решение:**
- Проверь Railway dashboard
- Status должен быть "Running/Healthy"
- SUPABASE_URL и SUPABASE_SERVICE_KEY установлены в Railway?

### ❌ Логин не работает

**Проверить:**
1. VITE_STACK_PROJECT_ID правильный?
2. VITE_STACK_PUBLISHABLE_KEY правильный?
3. Network tab в Developer Tools (F12) - ошибка какая?

---

## 🎊 После Успешного Деплоя:

```
Frontend (Vercel)     Backend (Railway)
      ↓                      ↓
 https://                https://
supergov.              supergov-api.
vercel.app             railway.app
      ↓                      ↓
    Login             Database
   (Stack Auth)       (Supabase)
      └──────────────────┘
           ↓
    Готово к использованию! 🎉
```

---

## 📞 Быстрая Помощь:

**Что делать если видишь ошибку:**

1. **Сделай скриншот ошибки**
2. **Открой https://vercel.com/dashboard → supergov → Deployments**
3. **Клик на deployment → Logs**
4. **Сделай скриншот logs**
5. **Покажи мне оба скриншота** → помогу за 2 минуты! 

---

## 📋 Все файлы готовы к деплою:

✅ `.env` - основные переменные (локальные)
✅ `.env.example` - шаблон для других
✅ `vercel.json` - конфиг Vercel
✅ `Procfile` - конфиг Railway для бэка
✅ `VERCEL_DEPLOY_WITH_STACK_AUTH.md` - подробный гайд
✅ `DEPLOY_GUIDE_VERCEL_RAILWAY.md` - общий гайд
✅ GitHub репозиторий - обновлён и готов

---

**ДАВАЙ! Добавляй переменные в Vercel Settings и пресс Redeploy!** 🚀

Нужна помощь на конкретном шаге? Напиши что видишь на экране! 👍
