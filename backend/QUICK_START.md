# 🚀 БЫСТРЫЙ СТАРТ - eGov 50+ функций

## За 5 минут всё готово к работе!

### ✅ ЧТО ЭТО ДАЁТ

- **50+ готовых функций** из коробки
- **50 HTTP эндпоинтов** при запуске
- **Полная интеграция** в приложение
- **Тестирование всех функций** в одной команде
- **Никакой ручной настройки** - всё автоматическое

---

## 🎯 БЫСТРЫЙ СТАРТ (3 шага)

### Шаг 1️⃣: Запустить проверку интеграции

В папке `backend/`:

```bash
# Windows (PowerShell)
.\egov-setup.ps1

# Linux/Mac (bash)
bash egov-setup.sh

# Или прямо Python
python check_egov_integration.py
```

**Результат:** Проверка что всё установлено правильно ✅

---

### Шаг 2️⃣: Запустить сервер (как обычно)

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Вы увидите:**
```
INFO:     Application startup complete
```

**И все 50 функций будут доступны на `/api/egov/*`** 🎉

---

### Шаг 3️⃣: Протестировать всё (в другом терминале)

```bash
cd backend
python test_egov_all_functions.py
```

**Вы увидите:**
```
🚀 eGov API - Тестирование всех 50 функций

📊 СТАТУС И КОНФИГУРАЦИЯ (1-5)
✅ 1. healthcheck
✅ 2. get_api_version
✅ 3. get_status
✅ 4. get_stats
✅ 5. reset_cache

🛍️ УСЛУГИ И КАТАЛОГИ (6-15)
✅ 6. get_services
✅ 7. get_service_details
... и ещё 43 функции

📊 РЕЗУЛЬТАТЫ
✅ Успешно: 50
❌ Ошибок: 0
📈 Успешность: 50/50 (100%)
```

---

## 🌐 ПРОВЕРИТЬ В БРАУЗЕРЕ

Откройте в браузере:

```
http://localhost:8000/docs
```

Увидите **все 50 эндпоинтов** в Swagger UI! 

Прямо там можно тестировать:
- Нажи­майте на эндпоинт
- "Try it out" 
- Отправляйте запрос
- Видите ответ

---

## 📋 ТОП 10 ФУНКЦИЙ ДЛЯ НАЧИНА­ЮЩИХ

```bash
# 1. Проверить статус API
curl http://localhost:8000/api/egov/health

# 2. Получить список услуг
curl http://localhost:8000/api/egov/services

# 3. Поиск услуг
curl "http://localhost:8000/api/egov/services/search?query=passport"

# 4. Получить документы пользователя
curl http://localhost:8000/api/egov/documents/{iin}

# 5. Историю заявлений
curl http://localhost:8000/api/egov/applications/history/{iin}

# 6. Отправить заявление (POST)
curl -X POST http://localhost:8000/api/egov/applications/submit \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "PASSPORT",
    "iin": "870412300415",
    "email": "user@example.com",
    "full_name": "John Doe",
    "data": {"reason": "renewal"}
  }'

# 7. Проверить статус заявления
curl http://localhost:8000/api/egov/applications/{ref}/status

# 8. Профиль пользователя
curl http://localhost:8000/api/egov/user/{iin}/profile

# 9. Уведомления
curl http://localhost:8000/api/egov/user/{iin}/notifications

# 10. Информация о платежах
curl http://localhost:8000/api/egov/payments/{app_id}
```

---

## 🔑 КОНФИГУРАЦИЯ (если нужна)

Если захотите подключить **реального eGov** (не демо):

### 1. Скопировать пример конфига

```bash
cp backend/.env.egov.example backend/.env
```

### 2. Отредактировать в текстовом редакторе:

```env
EGOV_API_BASE_URL=https://api.egov.kz/v1
EGOV_API_KEY=ваш_ключ_здесь
EGOV_COMPANY_ID=ваш_id_компании
```

### 3. Перезапустить сервер

```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Всё!** Сервер автоматически исполь­зует новые значения.

---

## 📚 ДОКУМЕНТАЦИЯ

| Файл | Назначение |
|------|-----------|
| `EGOV_INTEGRATION_README.md` | 📖 Полная документация (все 50 функций) |
| `EGOV_QUICKSTART.md` | ⚡ Краткий гайд (основное) |
| `EGOV_INTEGRATION_STEP_BY_STEP.md` | 📚 Детальное руководство (6 фаз) |
| `app/routers/egov.py` | 🔗 50 HTTP эндпоинтов (готовые) |
| `app/services/egov_connector_extended.py` | 🔧 50+ Python методов |

---

## 🆘 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проверка 1: Запущен ли сервер?

```bash
curl http://localhost:8000/api/egov/health
```

Должен ответить: `{"status":"online"}`

### Проверка 2: Есть ли ошибки?

```bash
# В консоли сервера посмотрите логи
# Может быть ошибка импорта
```

### Проверка 3: Переустановить

```bash
# Удалить кэш Python
rm -rf backend/__pycache__
rm -rf backend/app/__pycache__

# Перезапустить сервер
python -m uvicorn app.main:app --reload --port 8000
```

### Проверка 4: Связка не сработала?

```bash
# Заново запустить проверку
python backend/check_egov_integration.py
```

---

## 🎓 ПРИМЕРЫ КОДА

### Python (FastAPI):

```python
from app.routers.egov import router

# Все 50 функций уже в router
# Они добавлены в main.py автоматически
```

### JavaScript/React:

```javascript
// Получить услуги
const services = await fetch('/api/egov/services')
  .then(r => r.json());

// Отправить заявление
const result = await fetch('/api/egov/applications/submit', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_type: 'PASSPORT',
    iin: '870412300415',
    email: 'user@example.com',
    data: { reason: 'renewal' }
  })
})
```

---

## ✨ ЧТО ВКЛЮЧЕНО

- ✅ 5 функций статуса API
- ✅ 10 функций работы с услугами (каталог)
- ✅ 10 функций работы с заявлениями
- ✅ 10 функций работы с документами
- ✅ 10 функций профиля пользователя
- ✅ 5 функций платежей/аналитики

**Всего: 50 функций × готовы к использованию** 🚀

---

## 🎉 ГОТОВО!

Сервер запущен → Все 50 функций работают → Тесты пройдены ✅

**Начните с одного из Top 10 примеров выше!**

---

Вопросы? Смотрите полную документацию в `EGOV_INTEGRATION_README.md`
