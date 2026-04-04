-- Таблица для хранения ссылок на eGov заявления
-- Копировать в Supabase SQL editor и выполнить

-- Основная таблица для eGov ссылок
CREATE TABLE IF NOT EXISTS egov_references (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    application_id BIGINT REFERENCES applications(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    egov_ref_number VARCHAR(255) UNIQUE NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked_at TIMESTAMP WITH TIME ZONE,
    response_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_egov_ref_number ON egov_references(egov_ref_number);
CREATE INDEX IF NOT EXISTS idx_user_id_egov ON egov_references(user_id);
CREATE INDEX IF NOT EXISTS idx_application_id_egov ON egov_references(application_id);
CREATE INDEX IF NOT EXISTS idx_status_egov ON egov_references(status);
CREATE INDEX IF NOT EXISTS idx_created_at_egov ON egov_references(created_at);

-- Таблица для логирования всех взаимодействий с eGov API
CREATE TABLE IF NOT EXISTS egov_api_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    request_body JSONB,
    response_status INT,
    response_body JSONB,
    error TEXT,
    duration_ms INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индекс для поиска по событиям
CREATE INDEX IF NOT EXISTS idx_egov_logs_created_at ON egov_api_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_egov_logs_endpoint ON egov_api_logs(endpoint);

-- Таблица для кэширования услуг из eGov
CREATE TABLE IF NOT EXISTS egov_services_cache (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    service_id VARCHAR(255) UNIQUE,
    service_name VARCHAR(255),
    category VARCHAR(100),
    description TEXT,
    processing_time VARCHAR(50),
    requirements JSONB,
    raw_data JSONB,
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Индекс для кэша
CREATE INDEX IF NOT EXISTS idx_egov_services_expires ON egov_services_cache(expires_at);

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_egov_references_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER egov_references_update_timestamp
    BEFORE UPDATE ON egov_references
    FOR EACH ROW
    EXECUTE FUNCTION update_egov_references_updated_at();

-- СПРАВКА: Структура таблиц

-- egov_references:
-- - id: автоинкремент
-- - application_id: связь с заявлением
-- - user_id: связь с пользователем
-- - egov_ref_number: номер ссылки в eGov (уникален)
-- - service_type: тип услуги (PASSPORT, BENEFITS и т.д.)
-- - status: pending|submitted|approved|rejected|returned
-- - submitted_at: время отправки заявления
-- - last_checked_at: последняя проверка статуса
-- - response_data: полный ответ от eGov (JSON)
-- - error_message: ошибка если есть
-- - created_at: время создания записи
-- - updated_at: время последнего обновления

-- egov_api_logs:
-- Используется для отладки и анализа взаимодействия с API

-- egov_services_cache:
-- Кэширует услуги из eGov на 24 часа
