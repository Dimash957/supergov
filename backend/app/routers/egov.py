"""
Роутер для eGov API интеграции
Все 50+ функций в одном месте
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import logging

from ..auth import get_current_user
from ..database import get_database
from ..services.egov_connector_extended import egov_connector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/egov", tags=["eGov Integration"])


# ============================================================================
# СТАТУС И КОНФИГУРАЦИЯ
# ============================================================================

@router.get("/health")
async def egov_health() -> dict:
    """1. Проверить доступность eGov API"""
    is_online = await egov_connector.healthcheck()
    return {
        "status": "online" if is_online else "offline",
        "timestamp": datetime.now().isoformat(),
        "api_url": egov_connector.base_url
    }


@router.get("/version")
async def egov_version() -> dict:
    """2. Получить версию API"""
    version = await egov_connector.get_api_version()
    return {"version": version or "unknown"}


@router.get("/status")
async def egov_status() -> dict:
    """3. Полный статус API"""
    status = await egov_connector.get_status()
    return status


@router.get("/stats")
async def egov_stats() -> dict:
    """4. Статистика использования"""
    stats = egov_connector.get_stats()
    return stats


@router.post("/cache/reset")
async def reset_cache() -> dict:
    """5. Очистить кэш"""
    await egov_connector.reset_cache()
    return {"message": "Cache cleared"}


# ============================================================================
# УСЛУГИ (КАТАЛОГ)
# ============================================================================

@router.get("/services")
async def get_services(force_refresh: bool = False) -> dict:
    """6. Получить список услуг"""
    services = await egov_connector.get_services(force_refresh=force_refresh)
    return {"services": services, "count": len(services)}


@router.get("/services/search")
async def search_services(query: str = Query(..., min_length=1)) -> dict:
    """8. Поиск услуг"""
    results = await egov_connector.search_services(query)
    return {"results": results, "count": len(results)}


@router.get("/services/{category}")
async def get_services_by_category(category: str) -> dict:
    """9. Услуги по категории"""
    services = await egov_connector.get_services_by_category(category)
    return {"category": category, "services": services, "count": len(services)}


@router.get("/services/{service_id}/details")
async def get_service_details(service_id: str) -> dict:
    """7. Детали услуги"""
    service = await egov_connector.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.get("/services/{service_id}/requirements")
async def get_service_requirements(service_id: str) -> dict:
    """10. Требования для услуги"""
    requirements = await egov_connector.get_service_requirements(service_id)
    if requirements is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service_id": service_id, "requirements": requirements}


@router.get("/services/{service_id}/documents")
async def get_service_documents(service_id: str) -> dict:
    """11. Документы для услуги"""
    documents = await egov_connector.get_service_documents(service_id)
    if documents is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service_id": service_id, "documents": documents}


@router.get("/services/{service_id}/cost")
async def get_service_cost(service_id: str) -> dict:
    """12. Стоимость услуги"""
    cost = await egov_connector.get_service_cost(service_id)
    if cost is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return cost


@router.get("/services/{service_id}/processing-time")
async def get_processing_time(service_id: str) -> dict:
    """13. Время обработки"""
    time = await egov_connector.get_service_processing_time(service_id)
    return {"service_id": service_id, "processing_time": time}


@router.get("/services/{service_id}/offices")
async def get_service_offices(service_id: str) -> dict:
    """14. Офисы услуги"""
    offices = await egov_connector.get_service_offices(service_id)
    if offices is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service_id": service_id, "offices": offices}


@router.get("/services/{service_id}/faq")
async def get_service_faq(service_id: str) -> dict:
    """15. FAQ услуги"""
    faq = await egov_connector.get_service_faq(service_id)
    if faq is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service_id": service_id, "faq": faq}


# ============================================================================
# ЗАЯВЛЕНИЯ
# ============================================================================

@router.post("/applications/submit")
async def submit_application(
    service_type: str,
    iin: str,
    email: str,
    data: dict,
    phone: str = "",
    full_name: str = "",
    current_user = Depends(get_current_user)
) -> dict:
    """16. Отправить заявление в eGov"""
    try:
        result = await egov_connector.submit_application(
            service_type=service_type,
            user_iin=iin,
            user_email=email,
            data=data,
            applicant_phone=phone,
            applicant_name=full_name
        )
        if result:
            return {"success": True, "data": result}
        raise HTTPException(status_code=500, detail="Failed to submit application")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/{ref_number}/status")
async def check_status(
    ref_number: str,
    current_user = Depends(get_current_user)
) -> dict:
    """17. Проверить статус заявления"""
    status = await egov_connector.check_application_status(ref_number)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")
    return status


@router.get("/applications/{ref_number}/details")
async def get_details(
    ref_number: str,
    current_user = Depends(get_current_user)
) -> dict:
    """18. Детали заявления"""
    details = await egov_connector.get_application_details(ref_number)
    if not details:
        raise HTTPException(status_code=404, detail="Application not found")
    return details


@router.post("/applications/{ref_number}/cancel")
async def cancel_application(
    ref_number: str,
    reason: str = "",
    current_user = Depends(get_current_user)
) -> dict:
    """19. Отменить заявление"""
    result = await egov_connector.cancel_application(ref_number, reason)
    if result:
        return {"success": True, "message": "Application cancelled"}
    raise HTTPException(status_code=500, detail="Failed to cancel application")


@router.post("/applications/{ref_number}/resubmit")
async def resubmit_application(
    ref_number: str,
    data: dict,
    current_user = Depends(get_current_user)
) -> dict:
    """20. Переотправить заявление"""
    result = await egov_connector.resubmit_application(ref_number, data)
    if result:
        return {"success": True, "data": result}
    raise HTTPException(status_code=500, detail="Failed to resubmit application")


@router.get("/applications/history/{iin}")
async def get_history(
    iin: str,
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
) -> dict:
    """21. История заявлений"""
    applications = await egov_connector.get_application_history(iin, limit)
    return {"applications": applications, "count": len(applications)}


@router.get("/applications/{ref_number}/steps")
async def get_steps(
    ref_number: str,
    current_user = Depends(get_current_user)
) -> dict:
    """22. Этапы заявления"""
    steps = await egov_connector.get_application_steps(ref_number)
    if steps is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"ref_number": ref_number, "steps": steps}


@router.post("/applications/{ref_number}/upload")
async def upload_document(
    ref_number: str,
    file_path: str,
    doc_type: str,
    current_user = Depends(get_current_user)
) -> dict:
    """23. Загрузить документ"""
    result = await egov_connector.upload_application_document(ref_number, file_path, doc_type)
    if result:
        return {"success": True, "message": "Document uploaded"}
    raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/applications/{ref_number}/poll")
async def poll_status(
    ref_number: str,
    interval: int = Query(60, ge=1, le=300),
    max_attempts: int = Query(10, ge=1, le=60),
    current_user = Depends(get_current_user)
) -> dict:
    """24. Опрашивать статус (polling)"""
    result = await egov_connector.poll_application_status(ref_number, interval, max_attempts)
    if result:
        return result
    raise HTTPException(status_code=408, detail="Polling timeout")


@router.post("/applications/batch-check")
async def batch_check(
    ref_numbers: List[str],
    current_user = Depends(get_current_user)
) -> dict:
    """25. Проверить несколько заявлений"""
    results = await egov_connector.batch_check_applications(ref_numbers)
    return {"results": results, "count": len(results)}


# ============================================================================
# ДОКУМЕНТЫ
# ============================================================================

@router.get("/documents/{iin}")
async def get_documents(
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """26. Получить документы"""
    documents = await egov_connector.get_documents(iin)
    return {"documents": documents, "count": len(documents)}


@router.get("/documents/{document_id}/info")
async def get_document_info(
    document_id: str,
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """27. Документ по ID"""
    doc = await egov_connector.get_document_by_id(document_id, iin)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/{document_id}/verify")
async def verify_document(
    document_id: str,
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """28. Проверить подлинность"""
    result = await egov_connector.verify_document(document_id, iin)
    if not result:
        raise HTTPException(status_code=500, detail="Verification failed")
    return result


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    iin: str,
    current_user = Depends(get_current_user)
):
    """29. Скачать документ"""
    content = await egov_connector.download_document(document_id, iin)
    if not content:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "size": len(content)}


@router.get("/documents/{document_id}/status")
async def get_document_status(
    document_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    """30. Статус документа"""
    status = await egov_connector.get_document_status(document_id)
    if not status:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "status": status}


@router.post("/documents/{document_id}/renew")
async def renew_document(
    document_id: str,
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """31. Продлить документ"""
    result = await egov_connector.renew_document(document_id, iin)
    if result:
        return {"success": True, "message": "Document renewal initiated"}
    raise HTTPException(status_code=500, detail="Failed to renew document")


@router.get("/documents/template/{doc_type}")
async def get_document_template(doc_type: str) -> dict:
    """32. Шаблон документа"""
    template = await egov_connector.get_document_template(doc_type)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/documents/validate")
async def validate_document(
    doc_type: str,
    data: dict,
    current_user = Depends(get_current_user)
) -> dict:
    """33. Валидировать документ"""
    valid, message = await egov_connector.validate_document_data(doc_type, data)
    return {"valid": valid, "message": message}


@router.post("/documents/{document_id}/copy")
async def request_copy(
    document_id: str,
    iin: str,
    delivery_method: str = "email",
    current_user = Depends(get_current_user)
) -> dict:
    """34. Запросить копию"""
    result = await egov_connector.request_document_copy(document_id, iin, delivery_method)
    if result:
        return {"success": True, "message": "Copy request submitted"}
    raise HTTPException(status_code=500, detail="Failed to request copy")


@router.get("/documents/{document_id}/history")
async def get_document_history(
    document_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    """35. История документа"""
    history = await egov_connector.get_document_history(document_id)
    return {"document_id": document_id, "history": history}


# ============================================================================
# ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================================

@router.get("/user/{iin}/profile")
async def get_user_profile(
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """36. Профиль пользователя"""
    profile = await egov_connector.get_user_profile(iin)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/user/{iin}/contact")
async def update_contact(
    iin: str,
    contact_type: str,
    value: str,
    current_user = Depends(get_current_user)
) -> dict:
    """37. Обновить контакт"""
    result = await egov_connector.update_user_contact(iin, contact_type, value)
    if result:
        return {"success": True, "message": "Contact updated"}
    raise HTTPException(status_code=500, detail="Failed to update contact")


@router.post("/user/{iin}/verify-phone")
async def verify_phone(
    iin: str,
    phone: str,
    otp: str,
    current_user = Depends(get_current_user)
) -> dict:
    """38. Верифицировать телефон"""
    result = await egov_connector.verify_user_phone(iin, phone, otp)
    if result:
        return {"success": True, "message": "Phone verified"}
    raise HTTPException(status_code=500, detail="Verification failed")


@router.post("/user/{iin}/verify-email")
async def verify_email(
    iin: str,
    email: str,
    token: str,
    current_user = Depends(get_current_user)
) -> dict:
    """39. Верифицировать email"""
    result = await egov_connector.verify_user_email(iin, email, token)
    if result:
        return {"success": True, "message": "Email verified"}
    raise HTTPException(status_code=500, detail="Verification failed")


@router.get("/user/{iin}/notifications")
async def get_notifications(
    iin: str,
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
) -> dict:
    """40. Уведомления"""
    notifications = await egov_connector.get_user_notifications(iin, limit)
    return {"notifications": notifications, "count": len(notifications)}


@router.post("/user/{iin}/notifications/{notification_id}/read")
async def mark_notification_read(
    iin: str,
    notification_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    """41. Отметить уведомление"""
    result = await egov_connector.mark_notification_read(iin, notification_id)
    if result:
        return {"success": True, "message": "Notification marked as read"}
    raise HTTPException(status_code=500, detail="Failed to mark notification")


@router.get("/user/{iin}/preferences")
async def get_preferences(
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """42. Предпочтения"""
    preferences = await egov_connector.get_user_preferences(iin)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences


@router.post("/user/{iin}/preferences")
async def update_preferences(
    iin: str,
    preferences: dict,
    current_user = Depends(get_current_user)
) -> dict:
    """43. Обновить предпочтения"""
    result = await egov_connector.update_user_preferences(iin, preferences)
    if result:
        return {"success": True, "message": "Preferences updated"}
    raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/user/{iin}/subscriptions")
async def get_subscriptions(
    iin: str,
    current_user = Depends(get_current_user)
) -> dict:
    """44. Подписки"""
    subscriptions = await egov_connector.get_user_subscriptions(iin)
    return {"subscriptions": subscriptions, "count": len(subscriptions)}


@router.post("/user/{iin}/subscriptions")
async def subscribe(
    iin: str,
    service_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    """45. Подписаться на услугу"""
    result = await egov_connector.subscribe_to_service(iin, service_id)
    if result:
        return {"success": True, "message": "Subscribed"}
    raise HTTPException(status_code=500, detail="Failed to subscribe")


# ============================================================================
# ПЛАТЕЖИ И АНАЛИТИКА
# ============================================================================

@router.get("/payments/{application_id}")
async def get_payment_info(
    application_id: str,
    current_user = Depends(get_current_user)
) -> dict:
    """46. Информация о платежах"""
    info = await egov_connector.get_payment_info(application_id)
    if not info:
        raise HTTPException(status_code=404, detail="Payment info not found")
    return info


@router.post("/payments/initiate")
async def initiate_payment(
    application_id: str,
    amount: float,
    currency: str = "KZT",
    current_user = Depends(get_current_user)
) -> dict:
    """47. Начать платёж"""
    result = await egov_connector.initiate_payment(application_id, amount, currency)
    if result:
        return result
    raise HTTPException(status_code=500, detail="Failed to initiate payment")


@router.get("/analytics")
async def get_analytics(
    filter_type: str = "all",
    current_user = Depends(get_current_user)
) -> dict:
    """48. Аналитика"""
    analytics = await egov_connector.get_analytics(filter_type)
    if not analytics:
        raise HTTPException(status_code=500, detail="Failed to get analytics")
    return analytics


@router.get("/system/load")
async def get_system_load() -> dict:
    """49. Загруженность системы"""
    load = await egov_connector.get_system_load()
    if not load:
        raise HTTPException(status_code=500, detail="Failed to get system load")
    return load


@router.post("/support/report")
async def report_issue(
    issue_title: str,
    issue_description: str,
    severity: str = "normal",
    current_user = Depends(get_current_user)
) -> dict:
    """50. Сообщить об ошибке"""
    result = await egov_connector.report_issue(issue_title, issue_description, severity)
    if result:
        return {"success": True, "message": "Issue reported"}
    raise HTTPException(status_code=500, detail="Failed to report issue")
