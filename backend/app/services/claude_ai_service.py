"""
Интеграция Claude API для текстовых операций
"""

import os
import logging
from typing import Dict, Any
import anthropic

logger = logging.getLogger(__name__)

class ClaudeAIService:
    """
    Сервис для работы с Claude API
    Используется для анализа текста, обработки документов, заполнения форм
    """
    
    def __init__(self):
        api_key = (os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or "").strip()
        if not api_key:
            logger.warning("CLAUDE_API_KEY/ANTHROPIC_API_KEY not set. Claude API features will be disabled.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def is_available(self) -> bool:
        """Проверить доступность Claude API"""
        return self.client is not None
    
    def extract_data_from_ocr(self, ocr_text: str, doc_type: str) -> Dict[str, Any]:
        """
        Извлечь структурированные данные из OCR текста используя Claude
        """
        if not self.is_available():
            logger.warning("Claude API not available, returning empty data")
            return {}
        
        try:
            prompt = f"""
Анализируй следующий OCR текст из документа типа "{doc_type}" и извлеки структурированные данные.

OCR Текст:
{ocr_text}

Ответь JSON объектом с следующими полями (если найдены в документе):
- full_name: полное имя
- first_name: имя
- last_name: фамилия
- middle_name: отчество
- iin: ИИН (12-значный идентификационный номер)
- birth_date: дата рождения (формат YYYY-MM-DD)
- gender: пол (male/female)
- nationality: национальность
- address: адрес проживания
- passport_number:  номер паспорта (если есть)
- issued_date: дата выдачи
- expiry_date: дата истечения

Верни только JSON, без доп. текста.
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Парсить JSON ответ
            response_text = message.content[0].text
            import json
            data = json.loads(response_text)
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data with Claude: {str(e)}")
            return {}
    
    def analyze_form_requirements(self, service_description: str) -> Dict[str, Any]:
        """
        Анализировать требования к заполнению формы услуги
        """
        if not self.is_available():
            return {}
        
        try:
            prompt = f"""
На основе описания государственной услуги, определи требуемые для заполнения поля и документы.

Описание услуги:
{service_description}

Ответь JSON объектом:
{{
  "required_fields": ["список", "обязательных", "полей"],
  "optional_fields": ["список", "опциональных", "полей"],
  "required_documents": ["список", "требуемых", "документов"],
  "processing_time": "примерное время обработки",
  "fees": "стоимость услуги или "бесплатно"",
  "notes": "важные примечания"
}}
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            import json
            data = json.loads(response_text)
            return data
            
        except Exception as e:
            logger.error(f"Error analyzing form: {str(e)}")
            return {}
    
    def validate_form_data(self, form_data: Dict[str, Any], service_type: str) -> Dict[str, Any]:
        """
        Валидировать полноту и корректность данных формы
        """
        if not self.is_available():
            return {"valid": True, "issues": [], "score": 100}
        
        try:
            prompt = f"""
Проверь полноту и корректность данных для заполнения формы услуги "{service_type}".

Данные:
{str(form_data)}

Ответь JSON объектом:
{{
  "valid": true/false,
  "score": 0-100,
  "issues": ["список проблем"],
  "suggestions": ["список рекомендаций"],
  "missing_fields": ["список недостающих полей"]
}}
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            import json
            data = json.loads(response_text)
            return data
            
        except Exception as e:
            logger.error(f"Error validating form: {str(e)}")
            return {"valid": True, "issues": [], "score": 100}
    
    def generate_form_help(self, field_name: str, service_type: str) -> str:
        """
        Сгенерировать справку для заполнения поля формы
        """
        if not self.is_available():
            return ""
        
        try:
            prompt = f"""
Дай краткую справку (1-2 предложения) о том, как заполнить поле "{field_name}" 
при подаче заявления на услугу "{service_type}".
"""
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=256,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating help: {str(e)}")
            return ""

# Глобальный экземпляр
claude_service = ClaudeAIService()
