"""
Быстрая проверка интеграции eGov
Запустить: python check_egov_integration.py
"""

import sys
import os
from pathlib import Path

def check_files():
    """Проверить что все файлы созданы"""
    print("\n📁 Проверка файлов...")
    
    files = {
        "app/routers/egov.py": "Роутер с 50 эндпоинтами",
        "app/services/egov_connector_extended.py": "Расширенный connector (50+ функций)",
        ".env.egov.example": "Пример конфигурации",
        "test_egov_all_functions.py": "Тестовый скрипт",
        "EGOV_INTEGRATION_README.md": "Документация",
    }
    
    all_ok = True
    for file_path, description in files.items():
        full_path = Path("backend") / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}: {description}")
        else:
            print(f"  ❌ {file_path}: ОТСУТСТВУЕТ")
            all_ok = False
    
    return all_ok


def check_imports():
    """Проверить что импорты работают"""
    print("\n📦 Проверка импортов...")
    
    try:
        sys.path.insert(0, str(Path("backend")))
        from app.services.egov_connector_extended import egov_connector
        print(f"  ✅ egov_connector_extended импортирован")
        print(f"  ✅ API URL: {egov_connector.base_url}")
        
        # Проверить что методы существуют
        methods = [
            'healthcheck', 'get_services', 'submit_application',
            'check_application_status', 'get_documents', 'get_user_profile'
        ]
        
        for method in methods:
            if hasattr(egov_connector, method):
                print(f"    ✅ Метод: {method}()")
            else:
                print(f"    ❌ Метод: {method}() - ОТСУТСТВУЕТ")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {str(e)}")
        return False


def check_main_app():
    """Проверить что роутер добавлен в main.py"""
    print("\n🔗 Проверка интеграции в main.py...")
    
    main_path = Path("backend") / "app" / "main.py"
    if not main_path.exists():
        print(f"  ❌ main.py не найден")
        return False
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    checks = {
        "from app.routers import": "Импорт роутеров",
        "egov,": "eGov в импортах",
        "app.include_router(egov.router)": "eGov роутер подключён",
    }
    
    all_ok = True
    for pattern, description in checks.items():
        if pattern in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}: ОТСУТСТВУЕТ")
            all_ok = False
    
    return all_ok


def print_next_steps():
    """Показать следующие шаги"""
    print("\n" + "="*80)
    print("🚀 СЛЕДУЮЩИЕ ШАГИ")
    print("="*80)
    
    print("""
1️⃣ ОБНОВИТЬ КОНФИГУРАЦИЮ
   cp backend/.env.egov.example backend/.env
   # Отредактировать с реальными значениями от eGov:
   # - EGOV_API_BASE_URL
   # - EGOV_API_KEY
   # - EGOV_COMPANY_ID

2️⃣ ЗАПУСТИТЬ СЕРВЕР
   cd backend
   python -m uvicorn app.main:app --reload --port 8000

3️⃣ ТЕСТИРОВАТЬ (в другом терминале)
   cd backend
   python test_egov_all_functions.py

4️⃣ ПРОВЕРИТЬ ДОСТУПНОСТЬ
   Открыть в браузере: http://localhost:8000/docs
   Перейти на: /api/egov/health
    """)


def main():
    print("\n" + "="*80)
    print("🔍 Проверка интеграции eGov API")
    print("="*80)
    
    results = {
        "✅ Файлы": check_files(),
        "✅ Импорты": check_imports(),
        "✅ Интеграция": check_main_app(),
    }
    
    print("\n" + "="*80)
    print("📊 ИТОГИ")
    print("="*80)
    
    all_passed = True
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ВСЁ ПРЕКРАСНО! Интеграция успешна!")
    else:
        print("\n⚠️ Обнаружены проблемы. Проверьте сообщения выше.")
    
    print_next_steps()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
