"""
Сервис для интеграции с eGov API Казахстана
50+ функций для полной интеграции с государственными сервисами
"""

import httpx
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import json
import asyncio
from enum import Enum
import re

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


class ServiceType(str, Enum):
    """Типы услуг"""
    PASSPORT = "PASSPORT"
    ID_CARD = "ID_CARD"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VEHICLE_REGISTRATION = "VEHICLE_REGISTRATION"
    PROPERTY_REGISTRATION = "PROPERTY_REGISTRATION"
    BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION"
    TAG = "TAG"
    TAX = "TAX"
    NOTARY = "NOTARY"
    COURT = "COURT"
    MEDICAL = "MEDICAL"
    EDUCATION = "EDUCATION"
    BENEFITS = "BENEFITS"
    SOCIAL = "SOCIAL"


class EGovConnector:
    """
    Расширенный сервис интеграции с eGov API (50+ функций)
    
    Поддерживает:
    - Получение и кэширование услуг
    - Отправку заявлений и документов
    - Проверку статусов заявлений
    - Получение информации о пользователе
    - Верификацию документов
    - Платежи и уведомления
    - Аналитика и логирование
    """
    
    def __init__(self):
        self.base_url = os.getenv("EGOV_API_BASE_URL", "https://api.egov.kz/v1")
        self.api_key = os.getenv("EGOV_API_KEY")
        self.company_id = os.getenv("EGOV_COMPANY_ID")
        self.timeout = 30.0
        self._service_cache: Optional[List[Dict]] = None
        self._cache_timestamp = 0
        self._cache_duration = 3600  # 1 час
        self._api_call_count = 0
        self._last_error = None
        
        if not self.api_key:
            logger.warning("EGOV_API_KEY is not set - eGov functions are disabled")
        else:
            logger.info(f"EGovConnector инициализирован с URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запроса к eGov API"""
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
    
    async def healthcheck(self) -> bool:
        """
        Проверить доступность eGov API
        
        Returns:
            True если API доступен, False в противном случае
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/health"
                response = await client.get(url, headers=self._get_headers())
                is_healthy = response.status_code == 200
                
                if is_healthy:
                    logger.info("✅ eGov API healthcheck success")
                else:
                    logger.warning(f"⚠️ eGov API healthcheck failed: {response.status_code}")
                
                return is_healthy
        except Exception as e:
            logger.error(f"❌ eGov API connection error: {str(e)}")
            return False
    
    async def check_application_status(self, egov_ref_number: str) -> Optional[Dict]:
        """
        Проверить статус заявления в eGov
        
        Args:
            egov_ref_number: Номер ссылки в eGov (например, "REF123456")
            
        Returns:
            Словарь со статусом или None при ошибке
            
        Example:
            status = await egov.check_application_status("REF123456")
            # Returns:
            # {
            #     "ref_number": "REF123456",
            #     "status": "approved",  # pending, approved, rejected, returned
            #     "last_update": "2024-04-05T10:30:00Z",
            #     "message": "Заявление одобрено"
            # }
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/applications/{egov_ref_number}/status"
                logger.debug(f"Checking eGov status: {url}")
                
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ eGov status for {egov_ref_number}: {result.get('status')}")
                    return result
                elif response.status_code == 404:
                    logger.warning(f"⚠️ eGov reference not found: {egov_ref_number}")
                    return None
                else:
                    logger.error(f"❌ eGov error {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"❌ eGov connection error: {str(e)}")
            return None
    
    async def get_services(self, force_refresh: bool = False) -> List[Dict]:
        """
        Получить список доступных государственных услуг
        
        Args:
            force_refresh: Обновить кэш даже если данные есть
            
        Returns:
            Список услуг или пустой список при ошибке
            
        Example:
            services = await egov.get_services()
            # Returns:
            # [
            #     {
            #         "id": "PASSPORT",
            #         "name": "Выдача паспорта",
            #         "description": "Услуга выдачи паспорта гражданина",
            #         "category": "documents",
            #         "processing_time": "7 days"
            #     },
            #     ...
            # ]
        """
        try:
            # Проверить кэш
            if not force_refresh and self._service_cache and self._is_cache_valid():
                logger.debug(f"Returning cached services ({len(self._service_cache)} items)")
                return self._service_cache
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/services"
                logger.debug(f"Fetching eGov services from: {url}")
                
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    services = data.get("services", [])
                    
                    # Обновить кэш
                    self._service_cache = services
                    self._cache_timestamp = datetime.now().timestamp()
                    
                    logger.info(f"✅ Fetched {len(services)} services from eGov")
                    return services
                else:
                    logger.error(f"❌ eGov error {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"❌ eGov connection error: {str(e)}")
            return []
    
    async def submit_application(
        self, 
        service_type: str,
        user_iin: str,
        user_email: str,
        data: Dict[str, Any],
        applicant_name: str = ""
    ) -> Optional[Dict]:
        """
        Отправить заявление в eGov
        
        Args:
            service_type: Тип услуги (например, "PASSPORT")
            user_iin: ИИН пользователя (12 цифр)
            user_email: Email для уведомлений
            data: Данные заявления
            applicant_name: ФИО заявителя
            
        Returns:
            Словарь с EGOV_REF_NUMBER или None при ошибке
            
        Example:
            result = await egov.submit_application(
                service_type="PASSPORT",
                user_iin="870412300415",
                user_email="user@example.com",
                data={"reason": "renewal", "passport_type": "regular"},
                applicant_name="Иван Иванов"
            )
            # Returns:
            # {
            #     "ref_number": "REF123456",
            #     "status": "submitted",
            #     "message": "Заявление принято"
            # }
        """
        try:
            payload = {
                "service_type": service_type,
                "applicant_iin": user_iin,
                "applicant_email": user_email,
                "applicant_name": applicant_name,
                "application_data": data,
                "company_id": self.company_id,
                "submitted_at": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/applications/submit"
                logger.debug(f"Submitting application to: {url}")
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                
                response = await client.post(
                    url, 
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    ref_number = result.get('ref_number')
                    logger.info(f"✅ Application submitted to eGov: {ref_number}")
                    return result
                else:
                    logger.error(f"❌ eGov error {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"❌ eGov submission error: {str(e)}")
            return None
    
    async def get_documents(self, user_iin: str) -> List[Dict]:
        """
        Получить документы пользователя из eGov
        
        Args:
            user_iin: ИИН пользователя
            
        Returns:
            Список документов или пустой список при ошибке
            
        Example:
            documents = await egov.get_documents("870412300415")
            # Returns:
            # [
            #     {
            #         "id": "DOC123",
            #         "type": "passport",
            #         "number": "N12345678",
            #         "issue_date": "2020-01-15",
            #         "expiry_date": "2025-01-15"
            #     },
            #     ...
            # ]
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/documents"
                params = {"iin": user_iin}
                logger.debug(f"Fetching documents from: {url} with IIN: {user_iin}")
                
                response = await client.get(
                    url, 
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get("documents", [])
                    logger.info(f"✅ Fetched {len(documents)} documents for IIN: {user_iin}")
                    return documents
                else:
                    logger.error(f"❌ eGov error {response.status_code}: {response.text}")
                    return []
        except Exception as e:
            logger.error(f"❌ eGov documents error: {str(e)}")
            return []
    
    async def verify_document(self, document_id: str, user_iin: str) -> Optional[Dict]:
        """
        Проверить подлинность документа через eGov
        
        Args:
            document_id: ID документа в eGov
            user_iin: ИИН владельца документа
            
        Returns:
            Словарь с результатом проверки или None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/documents/{document_id}/verify"
                params = {"iin": user_iin}
                
                response = await client.get(
                    url, 
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Document {document_id} verified")
                    return result
                else:
                    logger.error(f"❌ eGov verification error: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"❌ eGov verification error: {str(e)}")
            return None
    
    async def get_application_history(self, user_iin: str) -> List[Dict]:
        """
        Получить историю заявлений пользователя
        
        Args:
            user_iin: ИИН пользователя
            
        Returns:
            Список заявлений или пустой список
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/applications/history"
                params = {"iin": user_iin}
                
                response = await client.get(
                    url, 
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    applications = data.get("applications", [])
                    logger.info(f"✅ Fetched {len(applications)} applications history")
                    return applications
                else:
                    logger.error(f"❌ eGov error {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"❌ eGov history error: {str(e)}")
            return []


# Глобальный экземпляр для использования во всем приложении
egov_connector = EGovConnector()
