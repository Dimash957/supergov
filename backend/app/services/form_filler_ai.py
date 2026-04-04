"""
AI сервис для заполнения форм подачи в ЦОН (Центр облуживания населения)
Пользователь загружает файлы, облако анализирует и заполняет форму
"""

from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FormFillerAI:
    """
    Система автоматического заполнения форм для подачи в ЦОН
    Анализирует загруженные документы и заполняет поля формы
    """
    
    def __init__(self):
        self.extracted_data = {}
        self.confidence_scores = {}
    
    # ====== ИЗВЛЕЧЕНИЕ ДАННЫХ ======
    
    def extract_from_passport(self, text: str) -> Dict[str, Any]:
        """Извлечь данные из паспорта"""
        data = {}
        
        # ИИН (12 цифр)
        iin_match = re.search(r'\d{12}', text)
        if iin_match:
            data['iin'] = iin_match.group()
        
        # ФИО
        fio_pattern = r'([А-Я][а-яё]+)\s+([А-Я][а-яё]+)\s+([А-Я][а-яё]+)'
        fio_match = re.search(fio_pattern, text)
        if fio_match:
            data['last_name'] = fio_match.group(1)
            data['first_name'] = fio_match.group(2)
            data['middle_name'] = fio_match.group(3)
            data['full_name'] = f"{fio_match.group(1)} {fio_match.group(2)} {fio_match.group(3)}"
        
        # Дата рождения (ДД.MM.ГГГГ или ДД-MM-ГГГГ)
        birth_pattern = r'(\d{2})[.\-](\d{2})[.\-](\d{4})'
        birth_match = re.search(birth_pattern, text)
        if birth_match:
            data['birth_date'] = f"{birth_match.group(3)}-{birth_match.group(2)}-{birth_match.group(1)}"
        
        # Пол
        if re.search(r'мужской|М\b', text, re.IGNORECASE):
            data['gender'] = 'male'
        elif re.search(r'женский|Ж\b', text, re.IGNORECASE):
            data['gender'] = 'female'
        
        # Национальность
        nationality_match = re.search(r'национальност[ь|и]: ([А-Яа-яё]+)', text, re.IGNORECASE)
        if nationality_match:
            data['nationality'] = nationality_match.group(1)
        
        # Адрес
        address_pattern = r'адрес[^:]*:\s*([^,\n]+(?:,[^,\n]+){0,2})'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            data['address'] = address_match.group(1).strip()
        
        self.extracted_data = data
        return data
    
    def extract_from_id_card(self, text: str) -> Dict[str, Any]:
        """Извлечь данные из удостоверения личности"""
        return self.extract_from_passport(text)  # Похожие поля
    
    def extract_from_document(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Извлечь данные из любого документа"""
        extractors = {
            'passport': self.extract_from_passport,
            'id_card': self.extract_from_id_card,
            'birth_certificate': self.extract_from_birth_certificate,
            'marriage_certificate': self.extract_from_marriage_certificate,
        }
        
        extractor = extractors.get(doc_type, self.extract_from_passport)
        return extractor(text)
    
    def extract_from_birth_certificate(self, text: str) -> Dict[str, Any]:
        """Извлечь данные из свидетельства о рождении"""
        data = {}
        
        # ФИО ребенка
        fio_pattern = r'([А-Я][а-яё]+)\s+([А-Я][а-яё]+)\s+([А-Я][а-яё]+)'
        fio_match = re.search(fio_pattern, text)
        if fio_match:
            data['last_name'] = fio_match.group(1)
            data['first_name'] = fio_match.group(2)
            data['middle_name'] = fio_match.group(3)
            data['full_name'] = f"{fio_match.group(1)} {fio_match.group(2)} {fio_match.group(3)}"
        
        # Дата рождения
        birth_pattern = r'(\d{2})[.\-](\d{2})[.\-](\d{4})'
        birth_match = re.search(birth_pattern, text)
        if birth_match:
            data['birth_date'] = f"{birth_match.group(3)}-{birth_match.group(2)}-{birth_match.group(1)}"
        
        # Родители
        parent_pattern = r'(?:мать|отец)[^:]*:\s*([А-Яа-яё\s]+)'
        for match in re.finditer(parent_pattern, text, re.IGNORECASE):
            if 'мать' in match.group(0).lower():
                data['mother_name'] = match.group(1).strip()
            else:
                data['father_name'] = match.group(1).strip()
        
        return data
    
    def extract_from_marriage_certificate(self, text: str) -> Dict[str, Any]:
        """Извлечь данные из свидетельства о браке"""
        data = {}
        
        # Жених и невеста
        spouse_pattern = r'(?:жени[х|ом]|невест[а|ы])[^:]*:\s*([А-Яа-яё\s]+)'
        for match in re.finditer(spouse_pattern, text, re.IGNORECASE):
            # Просто сохраняем всех супругов
            if not 'spouse' in data:
                data['spouse'] = []
            data['spouse'].append(match.group(1).strip())
        
        # Дата брака
        marriage_pattern = r'дат[а|и] брак[а|и][^:]*:\s*(\d{2})[.\-](\d{2})[.\-](\d{4})'
        marriage_match = re.search(marriage_pattern, text, re.IGNORECASE)
        if marriage_match:
            data['marriage_date'] = f"{marriage_match.group(3)}-{marriage_match.group(2)}-{marriage_match.group(1)}"
        
        return data
    
    # ====== ЗАПОЛНЕНИЕ ФОРМ ======
    
    def fill_passport_application_form(self, extracted_data: Dict) -> Dict[str, Any]:
        """Заполнить форму подачи паспорта в ЦОН"""
        return {
            "service_type": "PASSPORT",
            "form_type": "passport_issuance",
            "fields": {
                "full_name": extracted_data.get("full_name", ""),
                "last_name": extracted_data.get("last_name", ""),
                "first_name": extracted_data.get("first_name", ""),
                "middle_name": extracted_data.get("middle_name", ""),
                "iin": extracted_data.get("iin", ""),
                "birth_date": extracted_data.get("birth_date", ""),
                "gender": extracted_data.get("gender", ""),
                "nationality": extracted_data.get("nationality", "kazakhstan"),
                "address": extracted_data.get("address", ""),
                "purpose": "personal_identification",
                "passport_type": "regular",
                "estimated_processing_time": "7 days",
                "fee": 0,  # Первичный паспорт бесплатно
            },
            "documents_attached": ["passport_photo", "birth_certificate", "iin_document"],
            "submitted_at": datetime.now().isoformat(),
            "status": "draft"
        }
    
    def fill_id_card_application_form(self, extracted_data: Dict) -> Dict[str, Any]:
        """Заполнить форму подачи удостоверения личности"""
        return {
            "service_type": "ID_CARD",
            "form_type": "id_card_issuance",
            "fields": {
                "full_name": extracted_data.get("full_name", ""),
                "iin": extracted_data.get("iin", ""),
                "birth_date": extracted_data.get("birth_date", ""),
                "gender": extracted_data.get("gender", ""),
                "nationality": extracted_data.get("nationality", "kazakhstan"),
                "address": extracted_data.get("address", ""),
                "id_card_type": "national",
                "purpose": "domestic_travel",
                "estimated_processing_time": "5 days",
                "fee": 5000,  # В тенге
            },
            "documents_attached": ["id_photo", "birth_certificate", "passport_copy"],
            "submitted_at": datetime.now().isoformat(),
            "status": "draft"
        }
    
    def fill_driving_license_application(self, extracted_data: Dict) -> Dict[str, Any]:
        """Заполнить форму подачи водительского удостоверения"""
        return {
            "service_type": "DRIVING_LICENSE",
            "form_type": "driving_license_issuance",
            "fields": {
                "full_name": extracted_data.get("full_name", ""),
                "iin": extracted_data.get("iin", ""),
                "birth_date": extracted_data.get("birth_date", ""),
                "gender": extracted_data.get("gender", ""),
                "address": extracted_data.get("address", ""),
                "license_category": "B",  # Легковые автомобили
                "estimated_processing_time": "3 days",
                "fee": 3000,  # В тенге
                "exam_date": None,  # Назначается после подачи
            },
            "documents_attached": ["medical_certificate", "passport_copy", "eyesight_test"],
            "submitted_at": datetime.now().isoformat(),
            "status": "draft"
        }
    
    def fill_benefits_application(self, extracted_data: Dict) -> Dict[str, Any]:
        """Заполнить форму подачи благоустройства/пособия"""
        return {
            "service_type": "BENEFITS",
            "form_type": "social_benefits_application",
            "fields": {
                "full_name": extracted_data.get("full_name", ""),
                "iin": extracted_data.get("iin", ""),
                "birth_date": extracted_data.get("birth_date", ""),
                "address": extracted_data.get("address", ""),
                "benefit_type": "child_allowance",  # Пример
                "family_income": None,  # Требуется дополнитель пальные документы
                "household_size": None,
                "employment_status": "unemployed",
                "estimated_processing_time": "14 days",
            },
            "documents_attached": ["passport_copy", "birth_certificates", "income_certificates"],
            "submitted_at": datetime.now().isoformat(),
            "status": "draft"
        }
    
    def auto_fill_form(self, service_type: str, extracted_data: Dict) -> Dict[str, Any]:
        """Автоматически заполнить форму в зависимости от типа услуги"""
        fillers = {
            "PASSPORT": self.fill_passport_application_form,
            "ID_CARD": self.fill_id_card_application_form,
            "DRIVING_LICENSE": self.fill_driving_license_application,
            "BENEFITS": self.fill_benefits_application,
        }
        
        filler = fillers.get(service_type)
        if filler:
            return filler(extracted_data)
        
        # Стандартная форма
        return {
            "service_type": service_type,
            "extracted_data": extracted_data,
            "status": "draft",
            "submitted_at": datetime.now().isoformat()
        }
    
    # ====== ВАЛИДАЦИЯ ======
    
    def validate_extracted_data(self, data: Dict) -> Dict[str, Any]:
        """Валидировать извлеченные данные"""
        issues = []
        confidence = 100
        
        # Проверить ИИН
        if 'iin' not in data:
            issues.append("ИИН не найден в документе")
            confidence -= 20
        elif not re.match(r'^\d{12}$', data['iin']):
            issues.append("ИИН имеет неправильный формат")
            confidence -= 15
        
        # Проверить ФИО
        if 'full_name' not in data:
            issues.append("ФИО не найдено в документе")
            confidence -= 20
        
        # Проверить дату рождения
        if 'birth_date' not in data:
            issues.append("Дата рождения не найдена")
            confidence -= 10
        
        # Проверить адрес
        if 'address' not in data:
            issues.append("Адрес не найден (опционально)")
            confidence -= 5
        
        return {
            "valid": confidence > 60,
            "confidence": max(0, confidence),
            "issues": issues,
            "data": data
        }


# Глобальный экземпляр
form_filler_ai = FormFillerAI()
