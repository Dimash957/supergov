"""
РАСШИРЕННЫЙ сервис для интеграции с eGov API Казахстана
50+ функций для полной интеграции с государственными сервисами
"""

import httpx
import os
import inspect
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import json
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class ApplicationStatus(str, Enum):
    """Статусы заявления"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentType(str, Enum):
    """Типы документов"""
    PASSPORT = "passport"
    ID_CARD = "id_card"
    DRIVING_LICENSE = "driving_license"
    WORK_PERMIT = "work_permit"
    RESIDENCE_PERMIT = "residence_permit"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CERTIFICATE = "marriage_certificate"
    DIVORCE_CERTIFICATE = "divorce_certificate"


class EGovConnector:
    """
    Расширенный сервис интеграции с eGov API (50+ функций)
    
    Поддерживает:
    - 5 базовых операций
    - 10 операций с услугами
    - 10 операций с заявлениями
    - 10 операций с документами
    - 10 операций с профилем
    - 5 платежей/аналитики
    """

    DEMO_SERVICES: List[Dict[str, Any]] = [
        {
            "id": "PASSPORT",
            "name": "Получение паспорта",
            "description": "Оформление или замена паспорта гражданина",
            "category": "documents",
            "processing_time": "5 рабочих дней",
            "requirements": [
                {"field": "iin", "required": True},
                {"field": "full_name", "required": True},
                {"field": "birth_date", "required": True},
            ],
            "documents": [
                {"name": "Удостоверение личности", "required": True},
                {"name": "Фото 3x4", "required": True},
            ],
            "cost": {"amount": 8000, "currency": "KZT"},
        },
        {
            "id": "ID_CARD",
            "name": "Получение удостоверения личности",
            "description": "Первичное получение или замена удостоверения",
            "category": "documents",
            "processing_time": "3 рабочих дня",
            "requirements": [
                {"field": "iin", "required": True},
                {"field": "address", "required": False},
            ],
            "documents": [
                {"name": "Свидетельство о рождении", "required": False},
            ],
            "cost": {"amount": 0, "currency": "KZT"},
        },
        {
            "id": "BENEFITS",
            "name": "Оформление социальной выплаты",
            "description": "Подача заявления на социальную поддержку",
            "category": "benefits",
            "processing_time": "7 рабочих дней",
            "requirements": [
                {"field": "iin", "required": True},
                {"field": "income_level", "required": True},
            ],
            "documents": [
                {"name": "Справка о доходах", "required": True},
            ],
            "cost": {"amount": 0, "currency": "KZT"},
        },
    ]
    
    def __init__(self):
        self.base_url = os.getenv("EGOV_API_BASE_URL", "https://api.egov.kz/v1")
        self.api_key = os.getenv("EGOV_API_KEY")
        self.company_id = os.getenv("EGOV_COMPANY_ID")
        self.timeout = 30.0
        self._service_cache: Optional[List[Dict]] = None
        self._cache_timestamp = 0
        self._cache_duration = 3600
        self._api_call_count = 0
        self._last_error = None
        self._demo_mode = (
            os.getenv("EGOV_MOCK", "true").strip().lower() == "true"
            or os.getenv("DEMO_MODE", "false").strip().lower() == "true"
            or not self.api_key
        )
        self._api_enabled = bool(self.api_key) and not self._demo_mode
        
        if self._demo_mode:
            logger.warning("eGov connector running in DEMO mode")
        elif not self._api_enabled:
            logger.warning("EGOV_API_KEY is not set")
        else:
            logger.info(f"EGovConnector инициализирован: {self.base_url}")

    def __getattribute__(self, name: str):
        attr = object.__getattribute__(self, name)
        if name.startswith("_"):
            return attr
        if not callable(attr):
            return attr

        # Respect monkeypatches/tests that override instance attributes.
        instance_dict = object.__getattribute__(self, "__dict__")
        if name in instance_dict:
            return attr

        if not object.__getattribute__(self, "_demo_mode"):
            return attr

        method_obj = getattr(type(self), name, None)
        if not method_obj or not inspect.iscoroutinefunction(method_obj):
            return attr

        async def _demo_async_wrapper(*args, **kwargs):
            return object.__getattribute__(self, "_demo_result")(name, *args, **kwargs)

        return _demo_async_wrapper

    def _pick_arg(self, args: tuple, kwargs: dict, idx: int, key: str, default: Any = None) -> Any:
        if key in kwargs:
            return kwargs[key]
        if len(args) > idx:
            return args[idx]
        return default

    def _demo_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        for service in self.DEMO_SERVICES:
            if service.get("id") == service_id:
                return service
        return None

    def _demo_documents(self, user_iin: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": "DOC123",
                "iin": user_iin,
                "type": "passport",
                "number": "P1234567",
                "status": "active",
                "issued_at": "2025-01-15",
            },
            {
                "id": "DOC124",
                "iin": user_iin,
                "type": "id_card",
                "number": "ID7654321",
                "status": "active",
                "issued_at": "2024-09-01",
            },
        ]

    def _demo_result(self, method_name: str, *args, **kwargs):
        now_iso = datetime.now().isoformat()

        if method_name == "healthcheck":
            return True
        if method_name == "get_api_version":
            return "mock-1.0.0"
        if method_name == "get_status":
            return {
                "status": "online",
                "mode": "demo",
                "provider": "local-mock",
                "timestamp": now_iso,
            }
        if method_name == "reset_cache":
            self._service_cache = None
            self._cache_timestamp = 0
            return True

        if method_name == "get_services":
            return list(self.DEMO_SERVICES)
        if method_name == "get_service_by_id":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            return self._demo_service_by_id(service_id)
        if method_name == "search_services":
            query = (self._pick_arg(args, kwargs, 0, "query", "") or "").lower()
            return [
                s for s in self.DEMO_SERVICES
                if query in s.get("id", "").lower()
                or query in s.get("name", "").lower()
                or query in s.get("description", "").lower()
            ]
        if method_name == "get_services_by_category":
            category = (self._pick_arg(args, kwargs, 0, "category", "") or "").lower()
            return [s for s in self.DEMO_SERVICES if s.get("category", "").lower() == category]
        if method_name == "get_service_requirements":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            service = self._demo_service_by_id(service_id)
            return service.get("requirements", []) if service else None
        if method_name == "get_service_documents":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            service = self._demo_service_by_id(service_id)
            return service.get("documents", []) if service else None
        if method_name == "get_service_cost":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            service = self._demo_service_by_id(service_id)
            if not service:
                return None
            return {
                "service_id": service_id,
                **service.get("cost", {"amount": 0, "currency": "KZT"}),
            }
        if method_name == "get_service_processing_time":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            service = self._demo_service_by_id(service_id)
            return service.get("processing_time") if service else None
        if method_name == "get_service_offices":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            return [
                {
                    "id": "OFFICE-1",
                    "name": "Demo ЦОН Астана",
                    "address": "ул. Демо, 10",
                    "service_id": service_id,
                }
            ]
        if method_name == "get_service_faq":
            service_id = self._pick_arg(args, kwargs, 0, "service_id", "PASSPORT")
            return [
                {"q": f"Как подать на {service_id}?", "a": "Заполните форму и нажмите Отправить."},
                {"q": "Сколько это занимает?", "a": "Обычно от 3 до 7 рабочих дней."},
            ]

        if method_name == "submit_application":
            service_type = self._pick_arg(args, kwargs, 0, "service_type", "PASSPORT")
            user_iin = self._pick_arg(args, kwargs, 1, "user_iin", "870412300415")
            user_email = self._pick_arg(args, kwargs, 2, "user_email", "demo@example.com")
            return {
                "reference_number": "REF123",
                "ref_number": "REF123",
                "status": "submitted",
                "service_type": service_type,
                "applicant_iin": user_iin,
                "applicant_email": user_email,
                "submitted_at": now_iso,
            }
        if method_name == "check_application_status":
            ref_number = self._pick_arg(args, kwargs, 0, "egov_ref_number", "REF123")
            return {
                "reference_number": ref_number,
                "status": "processing",
                "updated_at": now_iso,
            }
        if method_name == "get_application_details":
            ref_number = self._pick_arg(args, kwargs, 0, "egov_ref_number", "REF123")
            return {
                "reference_number": ref_number,
                "service_type": "PASSPORT",
                "status": "processing",
                "created_at": now_iso,
            }
        if method_name == "cancel_application":
            return True
        if method_name == "resubmit_application":
            ref_number = self._pick_arg(args, kwargs, 0, "egov_ref_number", "REF123")
            return {
                "reference_number": ref_number,
                "status": "resubmitted",
                "updated_at": now_iso,
            }
        if method_name == "get_application_history":
            user_iin = self._pick_arg(args, kwargs, 0, "user_iin", "870412300415")
            limit = int(self._pick_arg(args, kwargs, 1, "limit", 50) or 50)
            history = [
                {
                    "reference_number": "REF123",
                    "status": "processing",
                    "service_type": "PASSPORT",
                    "iin": user_iin,
                },
                {
                    "reference_number": "REF122",
                    "status": "completed",
                    "service_type": "ID_CARD",
                    "iin": user_iin,
                },
            ]
            return history[:limit]
        if method_name == "get_application_steps":
            return [
                {"step": 1, "name": "created", "status": "done"},
                {"step": 2, "name": "review", "status": "in_progress"},
            ]
        if method_name == "upload_application_document":
            return True
        if method_name == "poll_application_status":
            ref_number = self._pick_arg(args, kwargs, 0, "egov_ref_number", "REF123")
            return {
                "reference_number": ref_number,
                "status": "completed",
                "updated_at": now_iso,
            }
        if method_name == "batch_check_applications":
            refs = self._pick_arg(args, kwargs, 0, "ref_numbers", []) or []
            return [{"reference_number": r, "status": "processing"} for r in refs]

        if method_name == "get_documents":
            user_iin = self._pick_arg(args, kwargs, 0, "user_iin", "870412300415")
            return self._demo_documents(user_iin)
        if method_name == "get_document_by_id":
            document_id = self._pick_arg(args, kwargs, 0, "document_id", "DOC123")
            user_iin = self._pick_arg(args, kwargs, 1, "user_iin", "870412300415")
            docs = self._demo_documents(user_iin)
            return next((d for d in docs if d.get("id") == document_id), None)
        if method_name == "verify_document":
            document_id = self._pick_arg(args, kwargs, 0, "document_id", "DOC123")
            return {"document_id": document_id, "verified": True, "verified_at": now_iso}
        if method_name == "download_document":
            return b"%PDF-1.4 Demo eGov document"
        if method_name == "get_document_status":
            return "active"
        if method_name == "renew_document":
            return True
        if method_name == "get_document_template":
            doc_type = self._pick_arg(args, kwargs, 0, "doc_type", "passport")
            return {
                "doc_type": doc_type,
                "fields": ["iin", "full_name", "birth_date"],
            }
        if method_name == "validate_document_data":
            return (True, "Demo validation passed")
        if method_name == "request_document_copy":
            return True
        if method_name == "get_document_history":
            document_id = self._pick_arg(args, kwargs, 0, "document_id", "DOC123")
            return [
                {"document_id": document_id, "action": "created", "at": "2025-01-10"},
                {"document_id": document_id, "action": "viewed", "at": "2025-02-01"},
            ]

        if method_name == "get_user_profile":
            user_iin = self._pick_arg(args, kwargs, 0, "user_iin", "870412300415")
            return {
                "iin": user_iin,
                "full_name": "Demo User",
                "email": "demo@example.com",
                "phone": "+77000000000",
            }
        if method_name in {"update_user_contact", "verify_user_phone", "verify_user_email"}:
            return True
        if method_name == "get_user_notifications":
            limit = int(self._pick_arg(args, kwargs, 1, "limit", 20) or 20)
            notifications = [
                {"id": "N1", "title": "Заявление принято", "read": False},
                {"id": "N2", "title": "Готово к выдаче", "read": True},
            ]
            return notifications[:limit]
        if method_name == "mark_notification_read":
            return True
        if method_name == "get_user_preferences":
            return {"language": "ru", "notifications": True, "theme": "light"}
        if method_name == "update_user_preferences":
            return True
        if method_name == "get_user_subscriptions":
            return [{"service_id": "PASSPORT", "channel": "email"}]
        if method_name == "subscribe_to_service":
            return True

        if method_name == "get_payment_info":
            application_id = self._pick_arg(args, kwargs, 0, "application_id", "APP123")
            return {
                "application_id": application_id,
                "amount": 10000,
                "currency": "KZT",
                "status": "pending",
            }
        if method_name == "initiate_payment":
            application_id = self._pick_arg(args, kwargs, 0, "application_id", "APP123")
            amount = self._pick_arg(args, kwargs, 1, "amount", 10000)
            currency = self._pick_arg(args, kwargs, 2, "currency", "KZT")
            return {
                "payment_id": "PAY-001",
                "application_id": application_id,
                "amount": amount,
                "currency": currency,
                "status": "initiated",
                "payment_url": "https://demo-pay.supergov.local/pay/PAY-001",
            }
        if method_name == "get_analytics":
            return {
                "total_applications": 124,
                "success_rate": 0.94,
                "avg_processing_days": 4.2,
                "top_services": ["PASSPORT", "ID_CARD", "BENEFITS"],
            }
        if method_name == "get_system_load":
            return {
                "cpu_percent": 22,
                "memory_percent": 48,
                "requests_per_minute": 35,
                "status": "normal",
            }
        if method_name == "report_issue":
            return True

        raise AttributeError(f"No demo handler for method: {method_name}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SuperGov/1.0",
            "X-Request-ID": f"supergov-{datetime.now().timestamp()}"
        }
    
    def _is_cache_valid(self) -> bool:
        """Проверить, не устарел ли кэш"""
        return (datetime.now().timestamp() - self._cache_timestamp) < self._cache_duration
    
    def _log_api_call(self, method: str, endpoint: str, status: int, error: Optional[str] = None):
        """Логировать API вызов"""
        self._api_call_count += 1
        if error:
            self._last_error = error
            logger.error(f"API {method} {endpoint}: {status} - {error}")
        else:
            logger.info(f"API {method} {endpoint}: {status}")
    
    # ====== 1-5: БАЗОВЫЕ ОПЕРАЦИИ ======
    
    async def healthcheck(self) -> bool:
        """1. Проверить доступность eGov API"""
        if not self._api_enabled:
            self._last_error = "EGOV_API_KEY is not set"
            return False

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health", headers=self._get_headers())
                self._log_api_call("GET", "/health", response.status_code)
                return response.status_code == 200
        except Exception as e:
            self._log_api_call("GET", "/health", 500, str(e))
            return False
    
    async def get_api_version(self) -> Optional[str]:
        """2. Получить версию API"""
        if not self._api_enabled:
            return "mock"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/version", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("version")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_status(self) -> Dict[str, Any]:
        """3. Получить полный статус API"""
        if not self._api_enabled:
            return {"status": "offline", "reason": "EGOV_API_KEY is not set"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/status", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return {"status": "offline"}
    
    def get_stats(self) -> Dict[str, Any]:
        """4. Получить статистику использования"""
        return {
            "total_api_calls": self._api_call_count,
            "last_error": self._last_error,
            "cache_valid": self._is_cache_valid(),
            "cached_services": len(self._service_cache) if self._service_cache else 0,
            "mode": "demo" if self._demo_mode else "live",
            "api_enabled": self._api_enabled,
        }
    
    async def reset_cache(self) -> bool:
        """5. Очистить кэш"""
        self._service_cache = None
        self._cache_timestamp = 0
        logger.info("Cache cleared")
        return True
    
    # ====== 6-15: УСЛУГИ ======
    
    async def get_services(self, force_refresh: bool = False) -> List[Dict]:
        """6. Получить список услуг"""
        try:
            if not force_refresh and self._service_cache and self._is_cache_valid():
                return self._service_cache
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/services", headers=self._get_headers())
                if response.status_code == 200:
                    services = response.json().get("services", [])
                    self._service_cache = services
                    self._cache_timestamp = datetime.now().timestamp()
                    return services
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def get_service_by_id(self, service_id: str) -> Optional[Dict]:
        """7. Получить услугу по ID"""
        try:
            services = await self.get_services()
            return next((s for s in services if s.get("id") == service_id), None)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def search_services(self, query: str) -> List[Dict]:
        """8. Поиск услуг"""
        try:
            services = await self.get_services()
            query_lower = query.lower()
            return [s for s in services if query_lower in s.get("name", "").lower() or query_lower in s.get("description", "").lower()]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def get_services_by_category(self, category: str) -> List[Dict]:
        """9. Услуги по категории"""
        try:
            services = await self.get_services()
            return [s for s in services if s.get("category") == category]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def get_service_requirements(self, service_id: str) -> Optional[List[Dict]]:
        """10. Требования для услуги"""
        try:
            service = await self.get_service_by_id(service_id)
            return service.get("requirements", []) if service else None
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_service_documents(self, service_id: str) -> Optional[List[Dict]]:
        """11. Документы для услуги"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/services/{service_id}/documents", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("documents", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_service_cost(self, service_id: str) -> Optional[Dict]:
        """12. Стоимость услуги"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/services/{service_id}/cost", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_service_processing_time(self, service_id: str) -> Optional[str]:
        """13. Время обработки"""
        try:
            service = await self.get_service_by_id(service_id)
            return service.get("processing_time") if service else None
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_service_offices(self, service_id: str) -> Optional[List[Dict]]:
        """14. Офисы услуги"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/services/{service_id}/offices", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("offices", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_service_faq(self, service_id: str) -> Optional[List[Dict]]:
        """15. FAQ услуги"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/services/{service_id}/faq", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("faqs", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    # ====== 16-25: ЗАЯВЛЕНИЯ ======
    
    async def submit_application(self, service_type: str, user_iin: str, user_email: str, data: Dict[str, Any], applicant_name: str = "", applicant_phone: str = "") -> Optional[Dict]:
        """16. Отправить заявление"""
        try:
            payload = {
                "service_type": service_type,
                "applicant_iin": user_iin,
                "applicant_email": user_email,
                "applicant_name": applicant_name,
                "applicant_phone": applicant_phone,
                "application_data": data,
                "company_id": self.company_id,
                "submitted_at": datetime.now().isoformat()
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/applications/submit", json=payload, headers=self._get_headers())
                if response.status_code in [200, 201]:
                    self._log_api_call("POST", "/applications/submit", response.status_code)
                    return response.json()
        except Exception as e:
            self._log_api_call("POST", "/applications/submit", 500, str(e))
        return None
    
    async def check_application_status(self, egov_ref_number: str) -> Optional[Dict]:
        """17. Проверить статус заявления"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/applications/{egov_ref_number}/status", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_application_details(self, egov_ref_number: str) -> Optional[Dict]:
        """18. Детали заявления"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/applications/{egov_ref_number}/details", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def cancel_application(self, egov_ref_number: str, reason: str = "") -> bool:
        """19. Отменить заявление"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/applications/{egov_ref_number}/cancel", json={"reason": reason}, headers=self._get_headers())
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def resubmit_application(self, egov_ref_number: str, data: Dict) -> Optional[Dict]:
        """20. Переотправить заявление"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/applications/{egov_ref_number}/resubmit", json=data, headers=self._get_headers())
                if response.status_code in [200, 201]:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_application_history(self, user_iin: str, limit: int = 50) -> List[Dict]:
        """21. История заявлений"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/applications/history", params={"iin": user_iin, "limit": limit}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("applications", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def get_application_steps(self, egov_ref_number: str) -> Optional[List[Dict]]:
        """22. Этапы заявления"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/applications/{egov_ref_number}/steps", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("steps", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def upload_application_document(self, egov_ref_number: str, file_path: str, doc_type: str) -> bool:
        """23. Загрузить документ"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    response = await client.post(f"{self.base_url}/applications/{egov_ref_number}/upload", files=files, data={'document_type': doc_type}, headers=self._get_headers())
                    return response.status_code == 200
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def poll_application_status(self, egov_ref_number: str, interval: int = 60, max_attempts: int = 10) -> Optional[Dict]:
        """24. Опрашивать статус (polling)"""
        for attempt in range(max_attempts):
            status = await self.check_application_status(egov_ref_number)
            if status and status.get("status") != ApplicationStatus.PENDING.value:
                return status
            if attempt < max_attempts - 1:
                await asyncio.sleep(interval)
        return None
    
    async def batch_check_applications(self, ref_numbers: List[str]) -> List[Dict]:
        """25. Проверить несколько заявлений"""
        tasks = [self.check_application_status(ref) for ref in ref_numbers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict) and r is not None]
    
    # ====== 26-35: ДОКУМЕНТЫ ======
    
    async def get_documents(self, user_iin: str) -> List[Dict]:
        """26. Получить документы"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents", params={"iin": user_iin}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("documents", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def get_document_by_id(self, document_id: str, user_iin: str) -> Optional[Dict]:
        """27. Документ по ID"""
        try:
            documents = await self.get_documents(user_iin)
            return next((d for d in documents if d.get("id") == document_id), None)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def verify_document(self, document_id: str, user_iin: str) -> Optional[Dict]:
        """28. Проверить подлинность"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents/{document_id}/verify", params={"iin": user_iin}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def download_document(self, document_id: str, user_iin: str) -> Optional[bytes]:
        """29. Скачать документ"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents/{document_id}/download", params={"iin": user_iin}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_document_status(self, document_id: str) -> Optional[str]:
        """30. Статус документа"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents/{document_id}/status", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("status")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def renew_document(self, document_id: str, user_iin: str) -> bool:
        """31. Продлить документ"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/documents/{document_id}/renew", json={"iin": user_iin}, headers=self._get_headers())
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def get_document_template(self, doc_type: str) -> Optional[Dict]:
        """32. Шаблон документа"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents/templates/{doc_type}", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def validate_document_data(self, doc_type: str, data: Dict) -> Tuple[bool, Optional[str]]:
        """33. Валидировать документ"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/documents/validate", json={"document_type": doc_type, "data": data}, headers=self._get_headers())
                if response.status_code == 200:
                    result = response.json()
                    return (result.get("valid", False), result.get("message"))
                return (False, response.text)
        except Exception as e:
            return (False, str(e))
    
    async def request_document_copy(self, document_id: str, user_iin: str, delivery_method: str = "email") -> bool:
        """34. Запросить копию"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/documents/{document_id}/copy", json={"iin": user_iin, "delivery_method": delivery_method}, headers=self._get_headers())
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def get_document_history(self, document_id: str) -> List[Dict]:
        """35. История документа"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/documents/{document_id}/history", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("history", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    # ====== 36-45: ПОЛЬЗОВАТЕЛЬ ======
    
    async def get_user_profile(self, user_iin: str) -> Optional[Dict]:
        """36. Профиль пользователя"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_iin}", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def update_user_contact(self, user_iin: str, contact_type: str, value: str) -> bool:
        """37. Обновить контакт"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/contact", json={"contact_type": contact_type, "value": value}, headers=self._get_headers())
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def verify_user_phone(self, user_iin: str, phone: str, otp: str) -> bool:
        """38. Верифицировать телефон"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/verify-phone", json={"phone": phone, "otp": otp}, headers=self._get_headers())
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def verify_user_email(self, user_iin: str, email: str, token: str) -> bool:
        """39. Верифицировать email"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/verify-email", json={"email": email, "token": token}, headers=self._get_headers())
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def get_user_notifications(self, user_iin: str, limit: int = 20) -> List[Dict]:
        """40. Уведомления"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_iin}/notifications", params={"limit": limit}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("notifications", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def mark_notification_read(self, user_iin: str, notification_id: str) -> bool:
        """41. Отметить уведомление"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/notifications/{notification_id}/read", headers=self._get_headers())
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def get_user_preferences(self, user_iin: str) -> Optional[Dict]:
        """42. Предпочтения"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_iin}/preferences", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def update_user_preferences(self, user_iin: str, preferences: Dict) -> bool:
        """43. Обновить предпочтения"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/preferences", json=preferences, headers=self._get_headers())
                return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    async def get_user_subscriptions(self, user_iin: str) -> List[Dict]:
        """44. Подписки"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/users/{user_iin}/subscriptions", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json().get("subscriptions", [])
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return []
    
    async def subscribe_to_service(self, user_iin: str, service_id: str) -> bool:
        """45. Подписаться на услугу"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/users/{user_iin}/subscriptions", json={"service_id": service_id}, headers=self._get_headers())
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False
    
    # ====== 46-50: ПЛАТЕЖИ И АНАЛИТИКА ======
    
    async def get_payment_info(self, application_id: str) -> Optional[Dict]:
        """46. Информация о платежах"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/payments/{application_id}", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def initiate_payment(self, application_id: str, amount: float, currency: str = "KZT") -> Optional[Dict]:
        """47. Начать платёж"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"application_id": application_id, "amount": amount, "currency": currency}
                response = await client.post(f"{self.base_url}/payments/initiate", json=payload, headers=self._get_headers())
                if response.status_code in [200, 201]:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_analytics(self, filter_type: str = "all") -> Optional[Dict]:
        """48. Аналитика"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/analytics", params={"filter": filter_type}, headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def get_system_load(self) -> Optional[Dict]:
        """49. Загруженность системы"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/system/load", headers=self._get_headers())
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return None
    
    async def report_issue(self, issue_title: str, issue_description: str, severity: str = "normal") -> bool:
        """50. Сообщить об ошибке"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "title": issue_title,
                    "description": issue_description,
                    "severity": severity,
                    "reported_at": datetime.now().isoformat()
                }
                response = await client.post(f"{self.base_url}/support/report", json=payload, headers=self._get_headers())
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        return False


# Глобальный экземпляр
egov_connector = EGovConnector()
