/**
 * Enhanced eGov functions dashboard
 * - Better UI
 * - Safer API execution
 * - Auto-runs core diagnostics on page load
 */

import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, Clock3, Copy, PlayCircle, Sparkles } from 'lucide-react';
import { Input } from './ui/Input';
import { Card } from './ui/Card';
import { apiClient, formatApiError } from '../lib/apiClient';
import '../styles/EgovFunctions.css';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface EgovFunction {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  method: HttpMethod;
  endpoint: string;
  body?: Record<string, unknown> | string[];
  autoRun?: boolean;
}

interface FunctionResult {
  status: 'idle' | 'loading' | 'success' | 'error';
  durationMs?: number;
  response?: unknown;
  error?: string;
  ranAt?: string;
}

const TEST_IIN = '870412300415';
const TEST_EMAIL = 'test@example.com';
const TEST_REF = 'REF123';
const TEST_DOC = 'DOC123';
const TEST_APP = 'APP123';
const TEST_SERVICE = 'PASSPORT';

const EGOV_FUNCTIONS: EgovFunction[] = [
  { id: '1', name: 'Здоровье системы', description: 'Проверка здоровья API', category: 'Core', icon: '⚕️', method: 'GET', endpoint: '/api/egov/health', autoRun: true },
  { id: '2', name: 'Версия API', description: 'Текущая версия API', category: 'Core', icon: '🔎', method: 'GET', endpoint: '/api/egov/version', autoRun: true },
  { id: '3', name: 'Статистика', description: 'Статистика использования eGov', category: 'Core', icon: '📊', method: 'GET', endpoint: '/api/egov/stats', autoRun: true },
  { id: '4', name: 'Статус сервисов', description: 'Сводный статус eGov', category: 'Core', icon: '🟢', method: 'GET', endpoint: '/api/egov/status' },
  { id: '5', name: 'Сброс кэша', description: 'Очистка кэша сервиса', category: 'Core', icon: '🧹', method: 'POST', endpoint: '/api/egov/cache/reset' },

  { id: '6', name: 'Каталог услуг', description: 'Список всех услуг', category: 'Services', icon: '📚', method: 'GET', endpoint: '/api/egov/services' },
  { id: '7', name: 'Поиск услуг', description: 'Поиск по слову passport', category: 'Services', icon: '🔍', method: 'GET', endpoint: '/api/egov/services/search?query=passport' },
  { id: '8', name: 'Услуги по категории', description: 'Услуги категории documents', category: 'Services', icon: '🗂️', method: 'GET', endpoint: '/api/egov/services/documents' },
  { id: '9', name: 'Детали услуги', description: 'Подробности по услуге PASSPORT', category: 'Services', icon: '📘', method: 'GET', endpoint: '/api/egov/services/PASSPORT/details' },
  { id: '10', name: 'Требования услуги', description: 'Требования к PASSPORT', category: 'Services', icon: '✅', method: 'GET', endpoint: '/api/egov/services/PASSPORT/requirements' },

  { id: '11', name: 'Документы услуги', description: 'Список документов для PASSPORT', category: 'Services', icon: '📄', method: 'GET', endpoint: '/api/egov/services/PASSPORT/documents' },
  { id: '12', name: 'Стоимость услуги', description: 'Стоимость PASSPORT', category: 'Services', icon: '💳', method: 'GET', endpoint: '/api/egov/services/PASSPORT/cost' },
  { id: '13', name: 'Срок обработки', description: 'Срок обработки PASSPORT', category: 'Services', icon: '⏱️', method: 'GET', endpoint: '/api/egov/services/PASSPORT/processing-time' },
  { id: '14', name: 'Офисы услуги', description: 'Офисы обслуживания PASSPORT', category: 'Services', icon: '🏢', method: 'GET', endpoint: '/api/egov/services/PASSPORT/offices' },
  { id: '15', name: 'FAQ услуги', description: 'FAQ по PASSPORT', category: 'Services', icon: '❓', method: 'GET', endpoint: '/api/egov/services/PASSPORT/faq' },

  { id: '16', name: 'Подать заявление', description: 'Создать заявление PASSPORT', category: 'Applications', icon: '📝', method: 'POST', endpoint: `/api/egov/applications/submit?service_type=${TEST_SERVICE}&iin=${TEST_IIN}&email=${TEST_EMAIL}`, body: { data: {} } },
  { id: '17', name: 'Статус заявления', description: 'Проверить статус REF123', category: 'Applications', icon: '📍', method: 'GET', endpoint: `/api/egov/applications/${TEST_REF}/status` },
  { id: '18', name: 'Детали заявления', description: 'Детали REF123', category: 'Applications', icon: '📑', method: 'GET', endpoint: `/api/egov/applications/${TEST_REF}/details` },
  { id: '19', name: 'Отмена заявления', description: 'Отменить REF123', category: 'Applications', icon: '🛑', method: 'POST', endpoint: `/api/egov/applications/${TEST_REF}/cancel?reason=test` },
  { id: '20', name: 'Переотправка', description: 'Переотправить REF123', category: 'Applications', icon: '🔁', method: 'POST', endpoint: `/api/egov/applications/${TEST_REF}/resubmit`, body: { data: {} } },

  { id: '21', name: 'История заявлений', description: 'История по ИИН', category: 'Applications', icon: '🕘', method: 'GET', endpoint: `/api/egov/applications/history/${TEST_IIN}` },
  { id: '22', name: 'Шаги заявления', description: 'Этапы REF123', category: 'Applications', icon: '🧭', method: 'GET', endpoint: `/api/egov/applications/${TEST_REF}/steps` },
  { id: '23', name: 'Загрузить док.', description: 'Загрузка пути документа', category: 'Applications', icon: '📤', method: 'POST', endpoint: `/api/egov/applications/${TEST_REF}/upload?file_path=/tmp/doc.pdf&doc_type=passport` },
  { id: '24', name: 'Poll статуса', description: 'Опрос статуса REF123', category: 'Applications', icon: '🔄', method: 'POST', endpoint: `/api/egov/applications/${TEST_REF}/poll?interval=1&max_attempts=1` },
  { id: '25', name: 'Batch check', description: 'Пакетная проверка', category: 'Applications', icon: '📦', method: 'POST', endpoint: '/api/egov/applications/batch-check', body: ['REF1', 'REF2'] },

  { id: '26', name: 'Мои документы', description: 'Документы по ИИН', category: 'Documents', icon: '🪪', method: 'GET', endpoint: `/api/egov/documents/${TEST_IIN}` },
  { id: '27', name: 'Инфо документа', description: 'Информация DOC123', category: 'Documents', icon: 'ℹ️', method: 'GET', endpoint: `/api/egov/documents/${TEST_DOC}/info?iin=${TEST_IIN}` },
  { id: '28', name: 'Проверка документа', description: 'Верификация DOC123', category: 'Documents', icon: '🛡️', method: 'GET', endpoint: `/api/egov/documents/${TEST_DOC}/verify?iin=${TEST_IIN}` },
  { id: '29', name: 'Скачать документ', description: 'Скачать DOC123', category: 'Documents', icon: '⬇️', method: 'GET', endpoint: `/api/egov/documents/${TEST_DOC}/download?iin=${TEST_IIN}` },
  { id: '30', name: 'Статус документа', description: 'Статус DOC123', category: 'Documents', icon: '🚦', method: 'GET', endpoint: `/api/egov/documents/${TEST_DOC}/status` },

  { id: '31', name: 'Продлить документ', description: 'Продление DOC123', category: 'Documents', icon: '🗓️', method: 'POST', endpoint: `/api/egov/documents/${TEST_DOC}/renew?iin=${TEST_IIN}` },
  { id: '32', name: 'Шаблон документа', description: 'Шаблон passport', category: 'Documents', icon: '📋', method: 'GET', endpoint: '/api/egov/documents/template/passport' },
  { id: '33', name: 'Валидация документа', description: 'Проверка данных документа', category: 'Documents', icon: '🧪', method: 'POST', endpoint: '/api/egov/documents/validate?doc_type=passport', body: { iin: TEST_IIN } },
  { id: '34', name: 'Запрос копии', description: 'Копия DOC123', category: 'Documents', icon: '🖨️', method: 'POST', endpoint: `/api/egov/documents/${TEST_DOC}/copy?iin=${TEST_IIN}&delivery_method=email` },
  { id: '35', name: 'История документа', description: 'История изменений DOC123', category: 'Documents', icon: '📜', method: 'GET', endpoint: `/api/egov/documents/${TEST_DOC}/history` },

  { id: '36', name: 'Профиль по ИИН', description: 'Профиль пользователя', category: 'Profile', icon: '👤', method: 'GET', endpoint: `/api/egov/user/${TEST_IIN}/profile` },
  { id: '37', name: 'Обновить контакт', description: 'Обновить email пользователя', category: 'Profile', icon: '📧', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/contact?contact_type=email&value=${TEST_EMAIL}` },
  { id: '38', name: 'Верификация телефона', description: 'Проверить номер и OTP', category: 'Profile', icon: '📱', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/verify-phone?phone=%2B77770000000&otp=123456` },
  { id: '39', name: 'Верификация email', description: 'Проверить email токеном', category: 'Profile', icon: '✉️', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/verify-email?email=${TEST_EMAIL}&token=token123` },
  { id: '40', name: 'Уведомления', description: 'Уведомления пользователя', category: 'Profile', icon: '🔔', method: 'GET', endpoint: `/api/egov/user/${TEST_IIN}/notifications` },

  { id: '41', name: 'Прочитать уведомление', description: 'Метка read для уведомления', category: 'Profile', icon: '✅', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/notifications/N1/read` },
  { id: '42', name: 'Предпочтения', description: 'Текущие настройки пользователя', category: 'Profile', icon: '⚙️', method: 'GET', endpoint: `/api/egov/user/${TEST_IIN}/preferences` },
  { id: '43', name: 'Обновить настройки', description: 'Обновить preferences', category: 'Profile', icon: '🛠️', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/preferences`, body: { language: 'ru' } },
  { id: '44', name: 'Подписки', description: 'Список подписок', category: 'Profile', icon: '🧾', method: 'GET', endpoint: `/api/egov/user/${TEST_IIN}/subscriptions` },
  { id: '45', name: 'Подписаться', description: 'Подписка на PASSPORT', category: 'Profile', icon: '➕', method: 'POST', endpoint: `/api/egov/user/${TEST_IIN}/subscriptions?service_id=${TEST_SERVICE}` },

  { id: '46', name: 'Платежная инфо', description: 'Информация по APP123', category: 'Payments', icon: '💰', method: 'GET', endpoint: `/api/egov/payments/${TEST_APP}` },
  { id: '47', name: 'Инициировать платеж', description: 'Начать платеж APP123', category: 'Payments', icon: '💸', method: 'POST', endpoint: `/api/egov/payments/initiate?application_id=${TEST_APP}&amount=10000&currency=KZT` },
  { id: '48', name: 'Аналитика', description: 'Сводная аналитика', category: 'Analytics', icon: '📈', method: 'GET', endpoint: '/api/egov/analytics' },
  { id: '49', name: 'Нагрузка системы', description: 'Текущая нагрузка', category: 'Analytics', icon: '📶', method: 'GET', endpoint: '/api/egov/system/load' },
  { id: '50', name: 'Сообщить о проблеме', description: 'Репорт в поддержку', category: 'Support', icon: '🆘', method: 'POST', endpoint: '/api/egov/support/report?issue_title=Test&issue_description=Auto%20report&severity=normal' },
];

const EgovFunctions: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, FunctionResult>>({});
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const categories = useMemo(
    () => Array.from(new Set(EGOV_FUNCTIONS.map((f) => f.category))),
    []
  );

  const filteredFunctions = useMemo(() => {
    return EGOV_FUNCTIONS.filter((f) => {
      const matchesCategory = selectedCategory ? f.category === selectedCategory : true;
      const text = `${f.name} ${f.description} ${f.endpoint}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [searchTerm, selectedCategory]);

  const executeFunction = async (func: EgovFunction) => {
    const startedAt = performance.now();
    setResults((prev) => ({
      ...prev,
      [func.id]: { status: 'loading' },
    }));

    try {
      let response: unknown;
      if (func.method === 'GET') {
        response = await apiClient.get(func.endpoint);
      } else if (func.method === 'POST') {
        response = await apiClient.post(func.endpoint, func.body);
      } else if (func.method === 'PUT') {
        response = await apiClient.put(func.endpoint, func.body);
      } else {
        response = await apiClient.delete(func.endpoint);
      }

      const endedAt = performance.now();
      setResults((prev) => ({
        ...prev,
        [func.id]: {
          status: 'success',
          response,
          durationMs: Math.round(endedAt - startedAt),
          ranAt: new Date().toISOString(),
        },
      }));
    } catch (error) {
      const endedAt = performance.now();
      setResults((prev) => ({
        ...prev,
        [func.id]: {
          status: 'error',
          error: formatApiError(error),
          durationMs: Math.round(endedAt - startedAt),
          ranAt: new Date().toISOString(),
        },
      }));
    }
  };

  useEffect(() => {
    const autoFunctions = EGOV_FUNCTIONS.filter((f) => f.autoRun);
    if (autoFunctions.length === 0) {
      return;
    }

    const runAutoDiagnostics = async () => {
      for (const f of autoFunctions) {
        // Run sequentially to avoid noisy startup bursts.
        // eslint-disable-next-line no-await-in-loop
        await executeFunction(f);
      }
    };

    runAutoDiagnostics();
  }, []);

  const copyResult = async (id: string) => {
    const result = results[id];
    if (!result) {
      return;
    }
    const text = result.status === 'success'
      ? JSON.stringify(result.response, null, 2)
      : result.error || '';

    if (!text) {
      return;
    }

    await navigator.clipboard.writeText(text);
  };

  const successCount = Object.values(results).filter((r) => r.status === 'success').length;
  const errorCount = Object.values(results).filter((r) => r.status === 'error').length;
  const runningCount = Object.values(results).filter((r) => r.status === 'loading').length;

  return (
    <div className="egov-functions-container">
      <section className="hero-panel">
        <div>
          <h1>eGov Operations Center</h1>
          <p>
            При открытии страницы автоматически запускаются базовые проверки API.
            Остальные функции доступны в один клик.
          </p>
        </div>
        <div className="hero-metrics">
          <div className="metric-card">
            <span className="metric-label">Success</span>
            <strong>{successCount}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">Errors</span>
            <strong>{errorCount}</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">Running</span>
            <strong>{runningCount}</strong>
          </div>
        </div>
      </section>

      <section className="toolbar-panel">
        <Input
          type="text"
          placeholder="Поиск по названию, описанию или endpoint..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="egov-search-input"
        />
        <div className="egov-categories">
          <button
            className={`category-btn ${selectedCategory === null ? 'active' : ''}`}
            onClick={() => setSelectedCategory(null)}
          >
            Все ({EGOV_FUNCTIONS.length})
          </button>
          {categories.map((category) => (
            <button
              key={category}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      <section className="egov-grid">
        {filteredFunctions.map((func) => {
          const result = results[func.id] ?? { status: 'idle' as const };
          const isExpanded = expandedId === func.id;

          return (
            <Card key={func.id} className={`egov-function-card ${isExpanded ? 'expanded' : ''}`}>
              <div className="card-header">
                <span className="icon">{func.icon}</span>
                <span className="method-badge">{func.method}</span>
              </div>

              <h3>{func.name}</h3>
              <p className="description">{func.description}</p>

              <div className="endpoint">
                <code>{func.endpoint}</code>
              </div>

              <div className="card-footer">
                <span className="category-tag">{func.category}</span>
                <button
                  className="execute-btn"
                  onClick={() => executeFunction(func)}
                  disabled={result.status === 'loading'}
                >
                  <PlayCircle size={16} />
                  {result.status === 'loading' ? 'Выполнение...' : 'Выполнить'}
                </button>
              </div>

              {result.status !== 'idle' && (
                <div className="result-panel">
                  <div className="result-title-row">
                    {result.status === 'success' && <CheckCircle2 size={16} className="ok" />}
                    {result.status === 'error' && <AlertCircle size={16} className="err" />}
                    {result.status === 'loading' && <Clock3 size={16} className="run" />}
                    <span className="result-title">
                      {result.status === 'success' && 'Успешно'}
                      {result.status === 'error' && 'Ошибка'}
                      {result.status === 'loading' && 'В процессе'}
                    </span>
                    {result.durationMs !== undefined && <span className="latency">{result.durationMs} ms</span>}
                  </div>

                  {result.status === 'error' && (
                    <p className="result-error">{result.error}</p>
                  )}

                  {result.status === 'success' && (
                    <>
                      {isExpanded ? (
                        <pre className="result-json">{JSON.stringify(result.response, null, 2)}</pre>
                      ) : (
                        <pre className="result-json short">{JSON.stringify(result.response, null, 2)}</pre>
                      )}
                      <div className="result-actions">
                        <button className="sub-btn" onClick={() => setExpandedId(isExpanded ? null : func.id)}>
                          <Sparkles size={14} />
                          {isExpanded ? 'Свернуть' : 'Развернуть'}
                        </button>
                        <button className="sub-btn" onClick={() => copyResult(func.id)}>
                          <Copy size={14} />
                          Копировать
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </section>

      {filteredFunctions.length === 0 && (
        <div className="no-results">
          <p>Ничего не найдено по текущему фильтру.</p>
        </div>
      )}
    </div>
  );
};

export default EgovFunctions;
