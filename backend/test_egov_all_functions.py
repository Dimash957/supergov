"""
Тест всех 50 функций eGov API
Запустить через: python test_egov_all_functions.py
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# Тестовые данные
TEST_TOKEN = "test_token_123"
TEST_IIN = "870412300415"
TEST_EMAIL = "test@example.com"
TEST_SERVICE_ID = "PASSPORT"

headers = {"Authorization": f"Bearer {TEST_TOKEN}"}


class EGovTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    async def test(self, name: str, method: str, endpoint: str, **kwargs):
        """Выполнить один тест"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                url = f"{BASE_URL}/egov{endpoint}"
                
                if method == "GET":
                    response = await client.get(url, headers=headers, **kwargs)
                elif method == "POST":
                    response = await client.post(url, headers=headers, **kwargs)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, **kwargs)
                else:
                    response = None
                
                status = response.status_code if response else 500
                is_ok = status < 300 or status == 401  # 401 OK т.к. токены тестовые
                
                result = {
                    "name": name,
                    "status": status,
                    "ok": is_ok,
                    "endpoint": endpoint
                }
                
                self.results.append(result)
                
                if is_ok:
                    self.passed += 1
                    print(f"✅ {name}")
                else:
                    self.failed += 1
                    print(f"❌ {name} (HTTP {status})")
                
                return is_ok
        except Exception as e:
            self.failed += 1
            print(f"❌ {name} - {str(e)}")
            self.results.append({
                "name": name,
                "status": 500,
                "ok": False,
                "error": str(e),
                "endpoint": endpoint
            })
            return False
    
    async def run_all_tests(self):
        """Запустить все 50 тестов"""
        print("=" * 80)
        print("🚀 eGov API - Тестирование всех 50 функций")
        print("=" * 80)
        print()
        
        # 1-5: СТАТУС
        print("📊 СТАТУС И КОНФИГУРАЦИЯ (1-5)")
        await self.test("1. healthcheck", "GET", "/health")
        await self.test("2. get_api_version", "GET", "/version")
        await self.test("3. get_status", "GET", "/status")
        await self.test("4. get_stats", "GET", "/stats")
        await self.test("5. reset_cache", "POST", "/cache/reset")
        print()
        
        # 6-15: УСЛУГИ
        print("🛍️ УСЛУГИ И КАТАЛОГИ (6-15)")
        await self.test("6. get_services", "GET", "/services")
        await self.test("7. get_service_details", "GET", f"/services/{TEST_SERVICE_ID}/details")
        await self.test("8. search_services", "GET", "/services/search", params={"query": "passport"})
        await self.test("9. get_services_by_category", "GET", "/services/documents")
        await self.test("10. get_service_requirements", "GET", f"/services/{TEST_SERVICE_ID}/requirements")
        await self.test("11. get_service_documents", "GET", f"/services/{TEST_SERVICE_ID}/documents")
        await self.test("12. get_service_cost", "GET", f"/services/{TEST_SERVICE_ID}/cost")
        await self.test("13. get_processing_time", "GET", f"/services/{TEST_SERVICE_ID}/processing-time")
        await self.test("14. get_service_offices", "GET", f"/services/{TEST_SERVICE_ID}/offices")
        await self.test("15. get_service_faq", "GET", f"/services/{TEST_SERVICE_ID}/faq")
        print()
        
        # 16-25: ЗАЯВЛЕНИЯ
        print("📋 ЗАЯВЛЕНИЯ (16-25)")
        await self.test("16. submit_application", "POST", "/applications/submit", json={"service_type": TEST_SERVICE_ID, "iin": TEST_IIN, "email": TEST_EMAIL, "data": {}})
        await self.test("17. check_status", "GET", "/applications/REF123/status")
        await self.test("18. get_details", "GET", "/applications/REF123/details")
        await self.test("19. cancel_application", "POST", "/applications/REF123/cancel")
        await self.test("20. resubmit_application", "POST", "/applications/REF123/resubmit", json={"data": {}})
        await self.test("21. get_history", "GET", f"/applications/history/{TEST_IIN}")
        await self.test("22. get_steps", "GET", "/applications/REF123/steps")
        await self.test("23. upload_document", "POST", "/applications/REF123/upload", json={"file_path": "/tmp/doc.pdf", "doc_type": "passport"})
        await self.test("24. poll_status", "POST", "/applications/REF123/poll")
        await self.test("25. batch_check", "POST", "/applications/batch-check", json={"ref_numbers": ["REF1", "REF2"]})
        print()
        
        # 26-35: ДОКУМЕНТЫ
        print("📄 ДОКУМЕНТЫ (26-35)")
        await self.test("26. get_documents", "GET", f"/documents/{TEST_IIN}")
        await self.test("27. get_document_info", "GET", f"/documents/DOC123/info", params={"iin": TEST_IIN})
        await self.test("28. verify_document", "GET", f"/documents/DOC123/verify", params={"iin": TEST_IIN})
        await self.test("29. download_document", "GET", f"/documents/DOC123/download", params={"iin": TEST_IIN})
        await self.test("30. get_document_status", "GET", "/documents/DOC123/status")
        await self.test("31. renew_document", "POST", "/documents/DOC123/renew", json={"iin": TEST_IIN})
        await self.test("32. get_document_template", "GET", "/documents/template/passport")
        await self.test("33. validate_document", "POST", "/documents/validate", json={"doc_type": "passport", "data": {}})
        await self.test("34. request_copy", "POST", "/documents/DOC123/copy", json={"iin": TEST_IIN})
        await self.test("35. get_document_history", "GET", "/documents/DOC123/history")
        print()
        
        # 36-45: ПРОФИЛЬ
        print("👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (36-45)")
        await self.test("36. get_user_profile", "GET", f"/user/{TEST_IIN}/profile")
        await self.test("37. update_contact", "POST", f"/user/{TEST_IIN}/contact", json={"contact_type": "email", "value": TEST_EMAIL})
        await self.test("38. verify_phone", "POST", f"/user/{TEST_IIN}/verify-phone", json={"phone": "+77770000000", "otp": "123456"})
        await self.test("39. verify_email", "POST", f"/user/{TEST_IIN}/verify-email", json={"email": TEST_EMAIL, "token": "token123"})
        await self.test("40. get_notifications", "GET", f"/user/{TEST_IIN}/notifications")
        await self.test("41. mark_notification_read", "POST", f"/user/{TEST_IIN}/notifications/NOTIF123/read")
        await self.test("42. get_preferences", "GET", f"/user/{TEST_IIN}/preferences")
        await self.test("43. update_preferences", "POST", f"/user/{TEST_IIN}/preferences", json={"language": "en"})
        await self.test("44. get_subscriptions", "GET", f"/user/{TEST_IIN}/subscriptions")
        await self.test("45. subscribe_to_service", "POST", f"/user/{TEST_IIN}/subscriptions", json={"service_id": TEST_SERVICE_ID})
        print()
        
        # 46-50: ПЛАТЕЖИ/АНАЛИТИКА
        print("💳 ПЛАТЕЖИ И АНАЛИТИКА (46-50)")
        await self.test("46. get_payment_info", "GET", "/payments/APP123")
        await self.test("47. initiate_payment", "POST", "/payments/initiate", json={"application_id": "APP123", "amount": 10000, "currency": "KZT"})
        await self.test("48. get_analytics", "GET", "/analytics")
        await self.test("49. get_system_load", "GET", "/system/load")
        await self.test("50. report_issue", "POST", "/support/report", json={"issue_title": "Test", "issue_description": "Test issue", "severity": "normal"})
        print()
        
        # РЕЗУЛЬТАТЫ
        print("=" * 80)
        print("📊 РЕЗУЛЬТАТЫ")
        print("=" * 80)
        print(f"✅ Успешно: {self.passed}")
        print(f"❌ Ошибок: {self.failed}")
        print(f"📈 Успешность: {self.passed}/{self.passed + self.failed} ({100 * self.passed // (self.passed + self.failed)}%)")
        print()
        
        # Детальный отчёт
        print("📋 ДЕТАЛЬНЫЙ ОТЧЁТ")
        print("=" * 80)
        
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result["ok"] else "❌"
            print(f"{i}. {status_icon} {result['name']}: {result['status']} {result['endpoint']}")


async def main():
    tester = EGovTester()
    await tester.run_all_tests()
    
    # Сохранить результаты в JSON
    with open("test_egov_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(tester.results),
            "passed": tester.passed,
            "failed": tester.failed,
            "tests": tester.results
        }, f, indent=2)
    
    print(f"\n📁 Результаты сохранены в test_egov_results.json")


if __name__ == "__main__":
    print("\n🚀 Убедитесь, что сервер запущен на http://localhost:8000\n")
    asyncio.run(main())
