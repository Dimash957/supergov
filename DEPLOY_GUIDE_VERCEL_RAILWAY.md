# 🚀 DEPLOY GUIDE: Vercel (Frontend) + Railway (Backend)

## 📋 Что мы деплоим:
- **Frontend (React/Vite)** → Vercel 
- **Backend (Python/FastAPI)** → Railway.app
- **Database** → Supabase (уже используется)

---

## 🎯 FRONTEND: Deploy на Vercel (5 минут)

### Шаг 1: Создаём аккаунт на Vercel
1. Открыть https://vercel.com
2. Нажать "Sign Up"
3. "Continue with GitHub" → выбрать свой аккаунт `Dimash957`
4. Разрешить Vercel доступ к репозиториям

### Шаг 2: Импортируем проект
1. После авторизации нажать "Add New" → "Project"
2. Нажать "Import Git Repository"
3. Найти и выбрать `Dimash957/supergov`
4. Нажать "Import"

### Шаг 3: Настройка деплоя
Vercel автоматически определит:
- ✅ Framework: Vite
- ✅ Build Command: npm run build
- ✅ Output Directory: dist

**Все должно быть заполнено правильно!** Просто нажимаешь "Deploy"

### Шаг 4: Добавляем Environment Variables
После деплоя (или до):

1. В Vercel: Settings → Environment Variables
2. Добавить переменную:
   - Name: `VITE_API_URL`
   - Value: `https://supergov-api.railway.app` (обновим когда окончателен Railway URL)

3. Сохранить и пересобрать (Deployments → Redeploy)

### Результат:
- ✅ Фронт доступен по типу: `https://supergov.vercel.app`
- ✅ Автоматический деплой при push в GitHub main branch

---

## 🚂 BACKEND: Deploy на Railway (5 минут)

### Шаг 1: Создаём аккаунт на Railway
1. Открыть https://railway.app
2. Нажать "Start Project"
3. "Log in with GitHub" → выбрать `Dimash957`
4. Разрешить доступ

### Шаг 2: Создаём новый проект
1. После входа нажать "New Project"
2. (или + в левом меню)
3. Выбрать "Deploy from GitHub repo"
4. Найти `Dimash957/supergov`
5. Нажать "Deploy"

### Шаг 3: Настройка переменных окружения

⚠️ **ВАЖНО:** Нужно добавить все переменные из `.env`

В Railway:
1. Нажать на проект → Variables
2. Добавить каждую переменную:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...  (Service Role Key)
STACK_AUTH_JWKS_URL=https://api.stack-auth.com/api/v1/projects/YOUR_ID/jwks
STACK_PROJECT_ID=your_stack_project_id
SUPERGOV_JWT_SECRET=your_jwt_secret_key_here
```

3. Сохранить (обычно автоматический деплой начинается)

### Шаг 4: Получаем URL для бэка

После деплоя в Railway:
1. Нажать на проект
2. Найти "Domains" секцию
3. Скопировать URL типа `https://supergov-api.railway.app`

### Шаг 5: Обновляем фронт-ендовский URL

1. В Vercel Settings → Environment Variables
2. Обновить `VITE_API_URL=https://supergov-api.railway.app` (реальный Railway URL)
3. Сохранить и Redeploy

---

## ✅ Проверка После Деплоя

### Frontend:
```
1. Открыть https://supergov.vercel.app
2. Должна загрузиться страница
3. Проверить нет ли ошибок в консоли (F12)
```

### Backend:
```
1. Открыть https://supergov-api.railway.app/docs
2. Должна открыться Swagger документация
3. Проверить есть ли /health endpoint
```

### Логины:
```
1. На фронте нажать "Log in"
2. Написать email
3. Получить OTP код
4. Ввести код и войти
```

---

## 🐛 Если Что-то Не Работает

### Frontend не грузится
- Проверить в Vercel: Deployments → Recent
- Посмотреть Build Logs (нажать на deployment)
- Обычно проблема в npm dependencies

### Backend не запускается
- В Railway: Logs → посмотреть ошибки
- Проверить что все ENV переменные добавлены
- Может быть проблема с SUPABASE_SERVICE_KEY

### Frontend не может достучаться до backend
- Проверить что `VITE_API_URL` правильный
- Проверить что Backend API работает (открыть /docs)
- Проверить CORS настройки в `app/main.py`

---

## 📊 Конечная Архитектура

```
┌─────────────────────┐
│  GitHub Repository  │
│  (supergov)         │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────────┐ ┌────────────────┐
│   Vercel    │ │   Railway      │
│  (Frontend) │ │ (Backend API)  │
│ Vite/React  │ │  FastAPI/Py    │
└──────┬──────┘ └────────┬───────┘
       │                 │
       │                 │
       └────────┬────────┘
                │
                ▼
        ┌──────────────────┐
        │  Supabase        │
        │  PostgreSQL      │
        │  (Database)      │
        └──────────────────┘
```

---

## 🎉 После Успешного Деплоя

1. ✅ Фронт работает на Vercel
2. ✅ Бэк работает на Railway
3. ✅ Логины работают
4. ✅ 50 eGov функций доступны
5. ✅ Загрузка документов работает
6. ✅ Всё автоматически обновляется при push в GitHub

---

## 📝 Хронология Деплоя

1. **Сейчас:** Код в GitHub ✅ (мы уже запушили)
2. **Следующее:** Deploy Vercel (5 мин)
3. **Потом:** Deploy Railway (5 мин)
4. **Проверка:** Оба работают (5 мин)
5. **Готово!** Приложение в Production! 🎉

---

## 💰 Стоимость/Бесплатно

### Vercel
- ✅ Бесплатный tier хорош для production
- ~$0-20/месяц в зависимости от трафика

### Railway
- ✅ $5/месяц credits (обычно достаточно)
- $10+ если нужны большие ресурсы

### Supabase (уже используется)
- ✅ Free tier: 1 database, 500MB
- Обычно хватает для MVP

**Итого:** ~$15-25/месяц для небольшого production приложения

---

**Готов к деплою? Начнём с Vercel! 🚀**
