# 🔧 ПОЛНЫЙ ГАЙД ПО ОТЛАДКЕ ОШИБКИ "Профиль не найден"

## Обзор

Вы получили ошибку "Профиль не найден в базе" при логине. Это происходит когда:
1. Новый пользователь Stack Auth входит
2. Профиль не существует в базе данных
3. Система не смогла создать профиль автоматически

**Что было исправлено:**
- Добавлена функция **auto-create** в `get_current_user()` 
- Теперь при первом входе новый пользователь автоматически получает профиль
- Добавлено детальное логирование для отладки

---

## 🧪 Быстрая Проверка (5 минут)

### Шаг 1: Проверить конфигурацию

```bash
cd backend
python check_profile_creation.py
```

**Должен вывести:**
```
✅ Supabase connection successful
✅ users table accessible
✅ Can insert test user
✅ Can query inserted user
✅ Cleanup successful
```

**Если ошибка:**
- ❌ Connection failed → Проверите `SUPABASE_URL` и `SUPABASE_SERVICE_KEY` в `.env`
- ❌ Table not found → Убедитесь что таблица `users` создана в Supabase


### Шаг 2: Запустить мониторинг логов

Откройте **2 терминала**:

**Терминал 1 - Мониторинг:**
```bash
cd backend
python monitor_login.py
```

**Терминал 2 - Запуск сервера:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Шаг 3: Тестовый логин

В браузере:
1. Откройте http://localhost:5176
2. Нажмите "Log in with Stack"
3. Войдите с тестовым аккаунтом

**В Терминале 1 должны появиться логи:**
```
[14:32:15.123] 🔐 get_current_user() CALLED
[14:32:15.250] 🔑 Stack user_id from token: user_abc123...
[14:32:15.300] 📊 Querying database for existing user...
[14:32:15.320] 👤 New user detected: user_abc123...
[14:32:15.330] 📝 Inserting user to database...
[14:32:15.450] ✅ User created successfully (DB ID: 42)
[14:32:15.460] 🔐=== get_current_user() FINISHED ===
```

---

## 🔍 Детальная Отладка (если есть ошибки)

### Проблема: `❌ Database connection failed`

**Решение:**
1. Откройте `.env` файл в корне проекта
2. Проверьте переменные:
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGc...
   ```
3. Убедитесь что нет лишних пробелов
4. Перезагрузите сервер

**Проверить вручную:**
```bash
cd backend
python
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('SUPABASE_URL'))
print(os.getenv('SUPABASE_SERVICE_KEY')[:20] + "...")
```

Должны вывести URL и ключ (без None).

---

### Проблема: `❌ Insert returned empty`

**Означает:** Insert успешный, но API вернул пустой результат

**Решение:** Это нормально! Система делает retry:
```
⚠️  Insert returned empty, retrying query...
✅ Found created user on retry (DB ID: 123)
```

Если retry не сработал → может быть проблема с правами доступа на таблице `users`.

**Проверить права в Supabase:**
1. Откройте SQL Editor в Supabase
2. Выполните:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```
3. Должна быть таблица `users`
4. Проверьте что сервис-роль может писать:
   ```sql
   INSERT INTO users (stack_user_id, email, full_name, phone, iin)
   VALUES ('test_' || random()::text, 'test@example.com', 'Test', '', '')
   RETURNING id;
   ```

---

### Проблема: `❌ Missing Stack Auth configuration`

**Означает:** `STACK_AUTH_JWKS_URL` не установлен

**Решение:**
1. Откройте `.env`
2. Добавьте:
   ```
   STACK_AUTH_JWKS_URL=https://api.stack-auth.com/api/v1/projects/YOUR_PROJECT_ID/jwks
   STACK_PROJECT_ID=YOUR_PROJECT_ID
   ```
3. Получите `YOUR_PROJECT_ID` из Stack Auth панели
4. Перезагрузите сервер

---

### Проблема: `👤 New user detected` но потом `❌ Failed to create user`

**Смотрите в логах:**
```
❌ Failed to create user: IntegrityError
   Error: duplicate key value violates unique constraint...
```

**Решение:**
- Возможно `stack_user_id` уже существует
- Проверьте в Supabase:
  ```sql
  SELECT id, stack_user_id, email FROM users 
  WHERE stack_user_id = 'user_abc123';
  ```
- Если найдется → удалите и повторите логин

---

## 📊 Прямая Проверка Базы

Откройте Supabase Dashboard:

1. **Таблица users:**
   ```sql
   SELECT * FROM users ORDER BY id DESC LIMIT 5;
   ```

2. **При логине должен создаться новый ряд с:**
   - `stack_user_id` неполный guid
   - `email` из JWT токена
   - `full_name` из JWT токена

3. **Проверить последнюю операцию:**
   ```sql
   SELECT id, stack_user_id, email, full_name, created_at 
   FROM users 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```

---

## 🧩 Что Происходит При Логине

```
┌─────────────────────────────────────────┐
│  Пользователь нажал "Log in with Stack" │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Stack Auth выдал JWT token             │
│  (содержит sub, email, display_name)    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  get_current_user() проверяет token     │
│  🔐=== CALLED ===                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Ищет stack_user_id в базе              │
│  📊 Querying database...                │
└────────┬──────────────────────┬─────────┘
         │                      │
    ┌────▼────┐            ┌────▼────┐
    │ Найдена  │            │ Не      │
    │ старая   │            │ найдена │
    └────┬─────┘            └────┬────┘
         │                       │
         ▼                       ▼
    ┌─────────┐         ┌──────────────┐
    │ ✅      │         │ 👤 NEW USER  │
    │ Return  │         │ Auto-create  │
    │ user    │         └──────┬───────┘
    └─────────┘                │
                              ▼
                      ┌──────────────────┐
                      │ 📝 Extract email │
                      │    & name from   │
                      │    JWT token     │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ Insert to users  │
                      │ table            │
                      └────────┬─────────┘
                               │
                        ┌──────┴───────┐
                        │               │
                    ┌───▼────┐   ┌─────▼──┐
                    │ Data    │   │ Empty  │
                    │ returned│   │result? │
                    └────┬────┘   └────┬───┘
                         │             │
                    ┌────▼──┐   ┌──────▼──┐
                    │ ✅    │   │ Retry   │
                    │Return │   │ query   │
                    │user   │   └────┬────┘
                    └───────┘        │
                                ┌───▼───┐
                                │ ✅ or │
                                │ ❌    │
                                └───────┘
         │
         └──────────────────────┬────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ 🔐=== FINISHED ===      │
                    │ Возвращаем пользователя│
                    └─────────────────────────┘
```

---

## ✅ Проверки Успеха

Если все работает:

1. **Backend логи показывают:**
   ```
   🔐=== get_current_user() CALLED ===
   👤 New user detected: ...
   📝 Inserting user to database...
   ✅ User created successfully
   ```

2. **В Supabase появился новый юзер:**
   - Можете видеть в таблице `users`
   - `stack_user_id` совпадает

3. **Фронтенд не показывает ошибку:**
   - Нет красного баннера "Профиль не найден"
   - Можете видеть username в профиле

4. **Защищенные endpoints работают:**
   - `/api/profile/me` возвращает профиль
   - `/api/egov/functions` возвращает функции
   - Все работает без ошибок

---

## 🆘 Если Ничего Не Помогает

1. **Соберите информацию:**
   ```bash
   python advanced_diagnostics.py > diagnostics.txt 2>&1
   ```

2. **Проверьте Supabase статус:**
   - Откройте https://status.supabase.com
   - Убедитесь что сервис работает

3. **Перезагрузите все:**
   ```bash
   # Stop backend (Ctrl+C)
   # Clear browser cache (Ctrl+Shift+Del)
   # Restart backend
   python -m uvicorn app.main:app --reload --port 8000
   # Try login again
   ```

4. **Проверьте переменные окружения:**
   ```bash
   cat .env | grep -E "SUPABASE|STACK"
   ```
   Убедитесь что все значения скопированы полностью (без переносов)

---

## 📝 Логируемые События

### Каждое событие при логине:

| Эмодзи | Событие | Решение если есть |
|-------|--------|------------------|
| 🔐 | get_current_user() called | Нормально, показывает что auth проверяется |
| 🔑 | Токен декодирован | Нормально, Stack прислал токен |
| 📊 | Запрос к БД | Нормально, ищем пользователя |
| ✅ | User found / created | ✅ ВСЕ ХОРОШО |
| 👤 | New user detected | Нормально для первого входа |
| 📝 | Создание user | Нормально, пишем в БД |
| ⚠️ | Insert empty response | Нормально, есть retry |
| ❌ | Ошибка | ПРОБЛЕМА - см выше решения |

---

## 🚀 Следующие Шаги

После успешного входа:

1. ✅ Проверите что видите профиль
2. ✅ Пройдитесь по всем функциям приложения
3. ✅ Загрузите документ и проверьте AI extraction
4. ✅ Все работает? Отлично!

Если есть другие ошибки → создавайте новые issues с логами из `monitor_login.py`.
