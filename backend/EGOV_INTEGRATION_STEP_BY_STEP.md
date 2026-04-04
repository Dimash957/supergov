# Пошаговое внедрение интеграции eGov API

## Фаза 1: Подготовка и настройка (30 минут)

### Шаг 1.1: Получить API ключи от eGov
**Требуется:**
- Endpoint URL (например: `https://api.egov.kz/v1/`)
- API ключ для проверки подлинности
- Документация API eGov

**Действие:**
```bash
# Сохранить в .env файл
EGOV_API_BASE_URL=https://api.egov.kz/v1
EGOV_API_KEY=your_api_key_here
EGOV_COMPANY_ID=your_company_id_here
```

### Шаг 1.2: Установить необходимые зависимости
**Действие:**
```bash
pip install httpx python-dotenv pydantic
```

### Шаг 1.3: Обновить requirements.txt
**Действие:**
```bash
cd backend
pip freeze > requirements.txt
```

---

## Фаза 2: Создать EGov Connector сервис (1 час)

### Шаг 2.1: Создать файл `backend/app/services/egov_connector.py`

**Структура:**
```python
# backend/app/services/egov_connector.py
import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EGovConnector:
    """Сервис для интеграции с eGov API"""
    
    def __init__(self):
        self.base_url = os.getenv("EGOV_API_BASE_URL", "https://api.egov.kz/v1")
        self.api_key = os.getenv("EGOV_API_KEY")
        self.company_id = os.getenv("EGOV_COMPANY_ID")
        self.timeout = 30.0
        
        if not self.api_key:
            logger.warning("EGOV_API_KEY не установлен - eGov функции отключены")
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SuperGov/1.0"
        }
    
    async def check_application_status(self, egov_ref_number: str) -> Optional[Dict]:
        """
        Проверить статус заявления в eGov
        
        Args:
            egov_ref_number: Номер ссылки в eGov
            
        Returns:
            Словарь со статусом или None при ошибке
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/applications/{egov_ref_number}/status"
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"eGov error {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"eGov connection error: {str(e)}")
            return None
    
    async def get_services(self) -> List[Dict]:
        """
        Получить список доступных государственных услуг
        
        Returns:
            Список услуг или пустой список при ошибке
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/services"
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("services", [])
                else:
                    logger.error(f"eGov error {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"eGov connection error: {str(e)}")
            return []
    
    async def submit_application(
        self, 
        service_type: str,
        user_iin: str,
        data: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Отправить заявление в eGov
        
        Args:
            service_type: Тип услуги
            user_iin: ИИН пользователя
            data: Данные заявления
            
        Returns:
            Словарь с EGOV_REF_NUMBER или None при ошибке
        """
        try:
            payload = {
                "service_type": service_type,
                "applicant_iin": user_iin,
                "data": data,
                "company_id": self.company_id
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/applications/submit"
                response = await client.post(
                    url, 
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"Application submitted: {result.get('ref_number')}")
                    return result
                else:
                    logger.error(f"eGov error {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"eGov connection error: {str(e)}")
            return None
    
    async def get_documents(self, user_iin: str) -> List[Dict]:
        """
        Получить документы пользователя из eGov
        
        Args:
            user_iin: ИИН пользователя
            
        Returns:
            Список документов или пустой список при ошибке
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/documents"
                params = {"iin": user_iin}
                response = await client.get(
                    url, 
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("documents", [])
                else:
                    logger.error(f"eGov error {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"eGov connection error: {str(e)}")
            return []

# Инициализировать глобальный экземпляр
egov_connector = EGovConnector()
```

### Шаг 2.2: Обновить `backend/app/database.py`

**Действие:** Добавить новую таблицу для хранения связей с eGov:

```python
# Добавить после других таблиц в MockDB

if "egov_references" not in self.tables:
    self.tables["egov_references"] = MockDBTable(
        data=[],
        table_name="egov_references",
        id_field="id"
    )
```

**В Supabase:** Выполнить SQL:
```sql
-- Таблица для хранения ссылок на eGov заявления
CREATE TABLE IF NOT EXISTS egov_references (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    application_id BIGINT REFERENCES applications(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    egov_ref_number VARCHAR(255) UNIQUE,
    service_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked_at TIMESTAMP WITH TIME ZONE,
    response_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_egov_ref_number ON egov_references(egov_ref_number);
CREATE INDEX idx_user_id_egov ON egov_references(user_id);
```

---

## Фаза 3: Интегрировать с маршрутизаторами (1.5 часа)

### Шаг 3.1: Обновить `backend/app/routers/applications.py`

**Действие:** Добавить интеграцию с eGov:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy import text
from ..auth import get_current_user
from ..database import get_database
from ..services.egov_connector import egov_connector
import logging

logger = logging.getLogger(__name__)

# ... существующий код ...

@router.post("/api/applications/submit-to-egov")
async def submit_to_egov(
    application_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Отправить заявление в eGov
    
    Процесс:
    1. Получить заявление из БД
    2. Подготовить данные для eGov
    3. Отправить через EGovConnector
    4. Сохранить EGOV_REF_NUMBER в БД
    """
    try:
        # Получить заявление
        app = db.query("applications").filter(
            id=application_id,
            user_id=current_user["id"]
        ).first()
        
        if not app:
            raise HTTPException(status_code=404, detail="Заявление не найдено")
        
        # Подготовить данные для eGov
        egov_data = {
            "full_name": current_user.get("full_name"),
            "iin": current_user.get("iin"),
            "phone": current_user.get("phone"),
            "email": current_user.get("email"),
            "application_details": app.get("details", {})
        }
        
        # Отправить в eGov
        result = await egov_connector.submit_application(
            service_type=app.get("service_type"),
            user_iin=current_user.get("iin"),
            data=egov_data
        )
        
        if result and "ref_number" in result:
            # Сохранить ссылку на eGov
            db.insert("egov_references", {
                "application_id": application_id,
                "user_id": current_user["id"],
                "egov_ref_number": result["ref_number"],
                "service_type": app.get("service_type"),
                "status": "submitted"
            })
            
            return {
                "success": True,
                "egov_ref_number": result["ref_number"],
                "message": "Заявление отправлено в eGov"
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка отправки в eGov")
    
    except Exception as e:
        logger.error(f"Error submitting to eGov: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/applications/egov-status/{egov_ref_number}")
async def check_egov_status(
    egov_ref_number: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Проверить статус заявления в eGov
    """
    try:
        # Проверить права доступа
        ref = db.query("egov_references").filter(
            egov_ref_number=egov_ref_number,
            user_id=current_user["id"]
        ).first()
        
        if not ref:
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получить статус из eGov
        status = await egov_connector.check_application_status(egov_ref_number)
        
        if status:
            # Обновить в БД
            db.update("egov_references", {
                "status": status.get("status"),
                "response_data": status,
                "last_checked_at": "NOW()"
            }).where(egov_ref_number=egov_ref_number)
            
            return {
                "egov_ref_number": egov_ref_number,
                "status": status.get("status"),
                "details": status.get("details"),
                "checked_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка проверки статуса")
    
    except Exception as e:
        logger.error(f"Error checking eGov status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/applications/egov-services")
async def get_egov_services(
    current_user = Depends(get_current_user)
):
    """
    Получить список доступных услуг из eGov
    """
    try:
        services = await egov_connector.get_services()
        return {
            "services": services,
            "count": len(services),
            "cached_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching eGov services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Шаг 3.2: Обновить `backend/app/routers/documents.py`

**Действие:** Добавить получение документов из eGov:

```python
@router.get("/api/documents/from-egov")
async def get_egov_documents(
    current_user = Depends(get_current_user)
):
    """
    Получить документы пользователя из eGov
    """
    try:
        documents = await egov_connector.get_documents(current_user.get("iin"))
        return {
            "documents": documents,
            "count": len(documents),
            "source": "egov",
            "fetched_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching eGov documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Фаза 4: Обновить фронтенд (1 час)

### Шаг 4.1: Создать сервис для работы с eGov

**Действие:** Создать `src/lib/egov.ts`:

```typescript
// src/lib/egov.ts
import { apiBase } from './apiBase';

export const egov = {
  // Получить услуги
  async getServices() {
    const response = await apiBase.get('/applications/egov-services');
    return response.data.services;
  },

  // Отправить заявление в eGov
  async submitToEGov(applicationId: number) {
    const response = await apiBase.post('/applications/submit-to-egov', {
      application_id: applicationId,
    });
    return response.data;
  },

  // Проверить статус в eGov
  async checkStatus(egov_ref_number: string) {
    const response = await apiBase.get(
      `/applications/egov-status/${egov_ref_number}`
    );
    return response.data;
  },

  // Получить документы из eGov
  async getDocuments() {
    const response = await apiBase.get('/documents/from-egov');
    return response.data.documents;
  },
};
```

### Шаг 4.2: Обновить компонент `src/pages/applications/Applications.tsx`

**Действие:** Добавить кнопку "Отправить в eGov":

```typescript
import { egov } from '../../lib/egov';

// В компоненте
const handleSubmitToEGov = async (applicationId: number) => {
  try {
    const result = await egov.submitToEGov(applicationId);
    alert(`Заявление отправлено в eGov: ${result.egov_ref_number}`);
    // Сохранить ref_number для отслеживания
    setEgovRefNumber(result.egov_ref_number);
  } catch (error) {
    alert('Ошибка отправки в eGov');
  }
};

const handleCheckStatus = async (refNumber: string) => {
  const status = await egov.checkStatus(refNumber);
  alert(`Статус: ${status.status}`);
};

// В JSX
<button onClick={() => handleSubmitToEGov(app.id)}>
  Отправить в eGov
</button>
```

---

## Фаза 5: Тестирование (1.5 часа)

### Шаг 5.1: Тестировать эндпоинты локально

**Действие:** Создать `backend/test_egov_integration.py`:

```python
import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

async def test_egov_integration():
    """Тестировать eGov интеграцию"""
    
    async with httpx.AsyncClient() as client:
        # 1. Зарегистрировать пользователя
        print("1️⃣ Регистрация...")
        reg_resp = await client.post(f"{BASE_URL}/auth/register", json={
            "stack_user_id": "test_egov",
            "iin": "870412300415",
            "email": "test@example.com",
            "phone": "+77771234567",
            "full_name": "Test User"
        })
        print(f"   Status: {reg_resp.status_code}")
        
        # 2. Отправить OTP
        print("2️⃣ Отправка OTP...")
        otp_resp = await client.post(f"{BASE_URL}/auth/otp/send", json={
            "email": "test@example.com"
        })
        print(f"   Status: {otp_resp.status_code}")
        
        # Используем тестовый токен
        token = "test_token_123"
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Получить услуги из eGov
        print("3️⃣ Получение услуг из eGov...")
        services_resp = await client.get(
            f"{BASE_URL}/applications/egov-services",
            headers=headers
        )
        print(f"   Status: {services_resp.status_code}")
        if services_resp.status_code == 200:
            data = services_resp.json()
            print(f"   Услуг: {data['count']}")
        
        # 4. Создать заявление
        print("4️⃣ Создание заявления...")
        app_resp = await client.post(
            f"{BASE_URL}/applications",
            json={
                "service_type": "passport",
                "details": {"reason": "renewal"}
            },
            headers=headers
        )
        print(f"   Status: {app_resp.status_code}")
        if app_resp.status_code == 200:
            app = app_resp.json()
            app_id = app.get("id")
            
            # 5. Отправить в eGov
            print("5️⃣ Отправка заявления в eGov...")
            submit_resp = await client.post(
                f"{BASE_URL}/applications/submit-to-egov",
                json={"application_id": app_id},
                headers=headers
            )
            print(f"   Status: {submit_resp.status_code}")
            if submit_resp.status_code == 200:
                submit_data = submit_resp.json()
                ref_number = submit_data.get("egov_ref_number")
                print(f"   EGOV REF: {ref_number}")
                
                # 6. Проверить статус
                print("6️⃣ Проверка статуса в eGov...")
                status_resp = await client.get(
                    f"{BASE_URL}/applications/egov-status/{ref_number}",
                    headers=headers
                )
                print(f"   Status: {status_resp.status_code}")
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    print(f"   eGov статус: {status_data.get('status')}")

if __name__ == "__main__":
    asyncio.run(test_egov_integration())
```

**Действие:** Запустить тест:
```bash
cd backend
python test_egov_integration.py
```

### Шаг 5.2: Проверить в браузере

**Действие:**
1. Открыть приложение на `http://localhost:5176`
2. Зарегистрироваться
3. Создать новое заявление
4. Нажать "Отправить в eGov"
5. Проверить EGOV_REF_NUMBER в консоли браузера

---

## Фаза 6: Дополнительные интеграции (2 часа)

### Шаг 6.1: Автоматическая сверка статусов (Celery задача)

**Действие:** Обновить `backend/app/tasks/status_poller.py`:

```python
from celery import shared_task
from ..database import get_database
from ..services.egov_connector import egov_connector
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_egov_statuses():
    """Периодически проверять статусы заявлений в eGov"""
    db = get_database()
    
    # Получить все активные заявления
    pending_refs = db.query("egov_references").filter(
        status="pending"
    ).all()
    
    for ref in pending_refs:
        try:
            status = egov_connector.check_application_status(ref["egov_ref_number"])
            if status:
                db.update("egov_references", {
                    "status": status.get("status"),
                    "response_data": status
                }).where(id=ref["id"])
                
                logger.info(f"Updated status for {ref['egov_ref_number']}: {status['status']}")
        except Exception as e:
            logger.error(f"Error checking status for {ref['egov_ref_number']}: {str(e)}")

# Запустить каждый час
from celery.schedules import crontab
app.conf.beat_schedule = {
    'check-egov-statuses': {
        'task': 'app.tasks.status_poller.check_egov_statuses',
        'schedule': crontab(minute=0),  # Каждый час
    },
}
```

### Шаг 6.2: Уведомления через Telegram/Email

**Действие:** Обновить `backend/app/services/notifications.py`:

```python
async def notify_egov_status_change(user_email: str, ref_number: str, new_status: str):
    """Уведомить пользователя об изменении статуса в eGov"""
    
    subject = f"Обновление статуса заявления: {ref_number}"
    html_content = f"""
    <h2>Ваше заявление обновлено</h2>
    <p>Номер ссылки: <strong>{ref_number}</strong></p>
    <p>Новый статус: <strong>{new_status}</strong></p>
    <p><a href="http://localhost:5176/applications">Посмотреть заявление</a></p>
    """
    
    await send_email(user_email, subject, html_content)
```

---

## Чек-лист внедрения

### ☐ Подготовка
- [ ] Получить eGov API credentials
- [ ] Обновить .env файл
- [ ] Установить зависимости

### ☐ Бэкенд
- [ ] Создать `egov_connector.py`
- [ ] Обновить `database.py` (новая таблица)
- [ ] Обновить `applications.py` (3 новых эндпоинта)
- [ ] Обновить `documents.py` (получение из eGov)
- [ ] Добавить SQL для таблицы `egov_references` в Supabase

### ☐ Фронтенд
- [ ] Создать `src/lib/egov.ts`
- [ ] Обновить `Applications.tsx`
- [ ] Добавить кнопки отправки в eGov
- [ ] Добавить отображение статуса

### ☐ Тестирование
- [ ] Локальное тестирование (test_egov_integration.py)
- [ ] Ручное тестирование в браузере
- [ ] Проверить отправку заявлений
- [ ] Проверить проверку статусов

### ☐ Дополнительно
- [ ] Настроить Celery для проверки статусов
- [ ] Добавить уведомления
- [ ] Документировать в README

---

## Примеры API запросов

```bash
# Получить услуги
curl -X GET "http://localhost:8000/api/applications/egov-services" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Отправить заявление в eGov
curl -X POST "http://localhost:8000/api/applications/submit-to-egov" \
 -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"application_id": 1}'

# Проверить статус
curl -X GET "http://localhost:8000/api/applications/egov-status/REF123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить документы из eGov
curl -X GET "http://localhost:8000/api/documents/from-egov" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Возможные ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| 401 Unauthorized | Неверный API ключ | Проверить `EGOV_API_KEY` в .env |
| 404 Not Found | Неверный endpoint | Проверить документацию eGov API |
| 500 Server Error | eGov недоступен | Проверить `EGOV_API_BASE_URL` |
| Timeout | Медленное соединение | Увеличить timeout в config |

---

## Контакты поддержки eGov

- 📧 Email: api-support@egov.kz
- 📞 Phone: +7 (7) 172 74-80-80
- 📖 Docs: https://api.egov.kz/docs
