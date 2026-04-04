# 🚀 Быстрый старт: Интеграция eGov API

## ДЛЯ НАЧАЛА НУЖНО (5 минут)

### 1️⃣ Получить eGov APICredendials

**Что требуется:**
- Свяжитесь с eGov Казахстан
- Запросите:
  - `EGOV_API_BASE_URL` (например: `https://api.egov.kz/v1`)
  - `EGOV_API_KEY` (Bearer token)
  - `EGOV_COMPANY_ID` (ID вашей компании)

**Контакты eGov:**
- Email: api-support@egov.kz
- Phone: +7 (7) 172 74-80-80
- Docs: https://api.egov.kz/docs

---

### 2️⃣ Обновить .env файл

В `backend/.env` добавить (или обновить):

```env
# === eGov Integration ===
EGOV_API_BASE_URL=https://api.egov.kz/v1
EGOV_API_KEY=your_api_key_here_xxxxxxxxxxxxxxxx
EGOV_COMPANY_ID=your_company_id_here
```

---

### 3️⃣ Выполнить SQL миграцию

1. Открыть [Supabase Console](https://supabase.com/)
2. Выбрать свой проект
3. Перейти в **SQL Editor**
4. Создать новый query
5. Скопировать содержимое `backend/migrations_egov_schema.sql`
6. Нажать **Run**

✅ Готово! Таблицы созданы.

---

## ОСНОВНЫЕ ФАЙЛЫ

| Файл | Назначение |
|------|-----------|
| `EGOV_INTEGRATION_STEP_BY_STEP.md` | **📖 Главное руководство** - полное описание всех фаз |
| `app/services/egov_connector.py` | **🔌 Connector** - готовый класс для работы с API |
| `migrations_egov_schema.sql` | **🗄️ Schema** - SQL для создания таблиц |

---

## ФАЗЫ ВНЕДРЕНИЯ

### Фаза 1: Базовая интеграция (✅ это вы тут)
**Что делаем:**
- [x] Получить credentials
- [x] Обновить .env
- [x] Выполнить миграцию

**Как проверить:**
```bash
cd backend
python -c "from app.services.egov_connector import egov_connector; import asyncio; print(asyncio.run(egov_connector.healthcheck()))"
```

### Фаза 2: Интеграция эндпоинтов (1-2 часа)

**Следующие шаги:**

1. **Обновить `backend/app/routers/applications.py`**
   - Добавить `/api/applications/submit-to-egov`
   - Добавить `/api/applications/egov-status/{ref}`
   - Добавить `/api/applications/egov-services`
   - (Код готов в `EGOV_INTEGRATION_STEP_BY_STEP.md` - Фаза 3.1)

2. **Обновить `backend/app/routers/documents.py`**
   - Добавить `/api/documents/from-egov`
   - (Код готов в `EGOV_INTEGRATION_STEP_BY_STEP.md` - Фаза 3.2)

3. **Протестировать эндпоинты**
   ```bash
   cd backend
   python -c "
   import httpx
   import asyncio
   
   async def test():
       # Проверить подключение
       from app.services.egov_connector import egov_connector
       health = await egov_connector.healthcheck()
       print(f'eGov реален: {health}')
       
       # Получить услуги
       services = await egov_connector.get_services()
       print(f'Услуг загружено: {len(services)}')
   
   asyncio.run(test())
   "
   ```

### Фаза 3: Фронтенд (1 час)

1. Создать `src/lib/egov.ts` (Фаза 4.1 в guide)
2. Обновить `src/pages/applications/Applications.tsx` (Фаза 4.2)
3. Добавить кнопки отправки и проверки статусов

### Фаза 4: Тестирование (1-2 часа)

Запустить тесты из `EGOV_INTEGRATION_STEP_BY_STEP.md` - Фаза 5

---

## БЫСТРАЯ ПРОВЕРКА

После добавления эндпоинтов, протестировать через curl:

```bash
# 1. Получить услуги
curl -X GET "http://localhost:8000/api/applications/egov-services" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Отправить заявление
curl -X POST "http://localhost:8000/api/applications/submit-to-egov" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"application_id": 1}'

# 3. Проверить статус
curl -X GET "http://localhost:8000/api/applications/egov-status/REF123456" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 ЧЕК-ЛИСТ БЫСТРОГО СТАРТА

- [ ] Получил eGov API credentials
- [ ] Обновил .env файл
- [ ] Выполнил SQL миграцию в Supabase
- [ ] Проверил healthcheck (`python -c ...`)
- [ ] Прочитал полное руководство `EGOV_INTEGRATION_STEP_BY_STEP.md`
- [ ] Добавил эндпоинты в `applications.py`
- [ ] Добавил эндпоинты в `documents.py`
- [ ] Протестировал через curl
- [ ] Обновил фронтенд (`src/lib/egov.ts`)
- [ ] Протестировал в браузере

---

## ❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ

**Q: Что если eGov API недоступен?**
A: Используйте мок-данные для тестирования. В `EGOV_INTEGRATION_STEP_BY_STEP.md` есть примеры.

**Q: Как отладить запросы к eGov?**
A: В `egov_connector.py` включены логи. Проверьте консоль сервера.

**Q: Как обновлять статусы автоматически?**
A: Используйте Celery (Фаза 6 в guide). Задача `check_egov_statuses()` может работать каждый час.

**Q: Что если заявление отклонено?**
A: Пользователь может увидеть причину в поле `response_data` в таблице `egov_references`.

---

## 🎯 РЕЗУЛЬТАТ

После завершения всех фаз система будет:

✅ Интегрирована с eGov API  
✅ Отправляет заявления в государственные системы  
✅ Проверяет статусы автоматически  
✅ Получает документы прямо из eGov  
✅ Хранит всю исторю в базе  
✅ Уведомляет пользователей об обновлениях  

---

**Начните с Фазы 1! После завершения - откройте `EGOV_INTEGRATION_STEP_BY_STEP.md` для полного руководства 📖**
