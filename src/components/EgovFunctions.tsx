/**
 * Компонент для отображения всех 50 eGov функций
 * Заменяет Dashboard hardcoded список функций
 */

import React, { useState, useEffect } from 'react';
import { Input } from './ui/Input';
import { Card } from './ui/Card';
import '../styles/EgovFunctions.css';

interface EgovFunction {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  endpoint: string;
  method: string;
}

// Полный список всех 50 eGov функций
const EGOV_FUNCTIONS: EgovFunction[] = [
  // 1-5: Базовые операции
  {
    id: '1',
    name: 'Здоровье системы',
    description: 'Проверка здоровья и статуса eGov API',
    category: 'Core',
    icon: '⚕️',
    endpoint: '/api/egov/healthcheck',
    method: 'GET'
  },
  {
    id: '2',
    name: 'Версия API',
    description: 'Получить текущую версию API',
    category: 'Core',
    icon: '🔍',
    endpoint: '/api/egov/version',
    method: 'GET'
  },
  {
    id: '3',
    name: 'Статистика',
    description: 'Получить статистику использования API',
    category: 'Core',
    icon: '📊',
    endpoint: '/api/egov/stats',
    method: 'GET'
  },
  {
    id: '4',
    name: 'Кэш',
    description: 'Управление кэшем API',
    category: 'Core',
    icon: '💾',
    endpoint: '/api/egov/cache',
    method: 'GET'
  },
  {
    id: '5',
    name: 'Статус',
    description: 'Текущий статус всех сервисов',
    category: 'Core',
    icon: '🟢',
    endpoint: '/api/egov/status',
    method: 'GET'
  },

  // 6-15: Каталог услуг
  {
    id: '6',
    name: 'Все услуги',
    description: 'Получить полный каталог всех услуг',
    category: 'Services',
    icon: '📋',
    endpoint: '/api/egov/services',
    method: 'GET'
  },
  {
    id: '7',
    name: 'Поиск услуг',
    description: 'Найти услугу по названию или коду',
    category: 'Services',
    icon: '🔎',
    endpoint: '/api/egov/services/search',
    method: 'POST'
  },
  {
    id: '8',
    name: 'Требования услуги',
    description: 'Получить требования для конкретной услуги',
    category: 'Services',
    icon: '📄',
    endpoint: '/api/egov/services/requirements',
    method: 'GET'
  },
  {
    id: '9',
    name: 'Документы услуги',
    description: 'Получить список требуемых документов',
    category: 'Services',
    icon: '📑',
    endpoint: '/api/egov/services/documents',
    method: 'GET'
  },
  {
    id: '10',
    name: 'Стоимость услуги',
    description: 'Получить стоимость услуги',
    category: 'Services',
    icon: '💰',
    endpoint: '/api/egov/services/cost',
    method: 'GET'
  },
  {
    id: '11',
    name: 'Сроки услуги',
    description: 'Получить сроки обработки услуги',
    category: 'Services',
    icon: '⏱️',
    endpoint: '/api/egov/services/deadlines',
    method: 'GET'
  },
  {
    id: '12',
    name: 'Заведомо ложная информация',
    description: 'Проверить достоверность информации',
    category: 'Services',
    icon: '✅',
    endpoint: '/api/egov/services/verify',
    method: 'POST'
  },
  {
    id: '13',
    name: 'Отзывы услуги',
    description: 'Получить отзывы о услуге',
    category: 'Services',
    icon: '⭐',
    endpoint: '/api/egov/services/reviews',
    method: 'GET'
  },
  {
    id: '14',
    name: 'Похожие услуги',
    description: 'Найти похожие услуги',
    category: 'Services',
    icon: '🔗',
    endpoint: '/api/egov/services/related',
    method: 'GET'
  },
  {
    id: '15',
    name: 'Описание услуги',
    description: 'Получить полное описание услуги',
    category: 'Services',
    icon: '📚',
    endpoint: '/api/egov/services/description',
    method: 'GET'
  },

  // 16-25: Заявления
  {
    id: '16',
    name: 'Подать заявление',
    description: 'Подать новое заявление на услугу',
    category: 'Applications',
    icon: '📝',
    endpoint: '/api/egov/applications/submit',
    method: 'POST'
  },
  {
    id: '17',
    name: 'Статус заявления',
    description: 'Проверить статус заявления',
    category: 'Applications',
    icon: '📍',
    endpoint: '/api/egov/applications/status',
    method: 'GET'
  },
  {
    id: '18',
    name: 'Отмена заявления',
    description: 'Отменить поданное заявление',
    category: 'Applications',
    icon: '❌',
    endpoint: '/api/egov/applications/cancel',
    method: 'POST'
  },
  {
    id: '19',
    name: 'История заявлений',
    description: 'Получить историю всех заявлений',
    category: 'Applications',
    icon: '📜',
    endpoint: '/api/egov/applications/history',
    method: 'GET'
  },
  {
    id: '20',
    name: 'Загрузить документ',
    description: 'Загрузить документ к заявлению',
    category: 'Applications',
    icon: '📎',
    endpoint: '/api/egov/applications/upload',
    method: 'POST'
  },
  {
    id: '21',
    name: 'Опрос заявления',
    description: 'Опросить статус в реальном времени',
    category: 'Applications',
    icon: '🔄',
    endpoint: '/api/egov/applications/poll',
    method: 'POST'
  },
  {
    id: '22',
    name: 'Пакетная подача',
    description: 'Подать несколько заявлений одновременно',
    category: 'Applications',
    icon: '📦',
    endpoint: '/api/egov/applications/batch',
    method: 'POST'
  },
  {
    id: '23',
    name: 'Возобновить заявление',
    description: 'Возобновить отклоненное заявление',
    category: 'Applications',
    icon: '🔁',
    endpoint: '/api/egov/applications/resubmit',
    method: 'POST'
  },
  {
    id: '24',
    name: 'Черновики',
    description: 'Получить список черновиков заявлений',
    category: 'Applications',
    icon: '📑',
    endpoint: '/api/egov/applications/drafts',
    method: 'GET'
  },
  {
    id: '25',
    name: 'Комментарии заявления',
    description: 'Получить комментарии к заявлению',
    category: 'Applications',
    icon: '💬',
    endpoint: '/api/egov/applications/comments',
    method: 'GET'
  },

  // 26-35: Документы
  {
    id: '26',
    name: 'Получить документы',
    description: 'Получить список документов пользователя',
    category: 'Documents',
    icon: '📄',
    endpoint: '/api/egov/documents/list',
    method: 'GET'
  },
  {
    id: '27',
    name: 'Верификация документа',
    description: 'Проверить подлинность документа',
    category: 'Documents',
    icon: '✔️',
    endpoint: '/api/egov/documents/verify',
    method: 'POST'
  },
  {
    id: '28',
    name: 'Скачать документ',
    description: 'Скачать электронный документ',
    category: 'Documents',
    icon: '⬇️',
    endpoint: '/api/egov/documents/download',
    method: 'GET'
  },
  {
    id: '29',
    name: 'Возобновить документ',
    description: 'Возобновить действие документа',
    category: 'Documents',
    icon: '🔄',
    endpoint: '/api/egov/documents/renew',
    method: 'POST'
  },
  {
    id: '30',
    name: 'Шаблоны документов',
    description: 'Получить шаблоны документов',
    category: 'Documents',
    icon: '📋',
    endpoint: '/api/egov/documents/templates',
    method: 'GET'
  },
  {
    id: '31',
    name: 'Валидация документа',
    description: 'Проверить корректность документа',
    category: 'Documents',
    icon: '🔍',
    endpoint: '/api/egov/documents/validate',
    method: 'POST'
  },
  {
    id: '32',
    name: 'Копия документа',
    description: 'Создать заверенную копию документа',
    category: 'Documents',
    icon: '©️',
    endpoint: '/api/egov/documents/copy',
    method: 'POST'
  },
  {
    id: '33',
    name: 'История документа',
    description: 'Получить историю изменений документа',
    category: 'Documents',
    icon: '📜',
    endpoint: '/api/egov/documents/history',
    method: 'GET'
  },
  {
    id: '34',
    name: 'Подвижные квартиры',
    description: 'Получить документы для подвижных квартир',
    category: 'Documents',
    icon: '🏠',
    endpoint: '/api/egov/documents/housing',
    method: 'GET'
  },
  {
    id: '35',
    name: 'Архив документов',
    description: 'Получить архивированные документы',
    category: 'Documents',
    icon: '🗃️',
    endpoint: '/api/egov/documents/archive',
    method: 'GET'
  },

  // 36-45: Профиль пользователя
  {
    id: '36',
    name: 'Мой профиль',
    description: 'Получить информацию о профиле',
    category: 'Profile',
    icon: '👤',
    endpoint: '/api/egov/profile',
    method: 'GET'
  },
  {
    id: '37',
    name: 'Контакты',
    description: 'Получить контактную информацию',
    category: 'Profile',
    icon: '📞',
    endpoint: '/api/egov/profile/contacts',
    method: 'GET'
  },
  {
    id: '38',
    name: 'Верификация пользователя',
    description: 'Уровень верификации профиля',
    category: 'Profile',
    icon: '✓',
    endpoint: '/api/egov/profile/verification',
    method: 'GET'
  },
  {
    id: '39',
    name: 'Уведомления',
    description: 'Параметры уведомлений',
    category: 'Profile',
    icon: '🔔',
    endpoint: '/api/egov/profile/notifications',
    method: 'GET'
  },
  {
    id: '40',
    name: 'Предпочтения',
    description: 'Получить предпочтения пользователя',
    category: 'Profile',
    icon: '⚙️',
    endpoint: '/api/egov/profile/preferences',
    method: 'GET'
  },
  {
    id: '41',
    name: 'Подписки',
    description: 'Управление подписками на услуги',
    category: 'Profile',
    icon: '📧',
    endpoint: '/api/egov/profile/subscriptions',
    method: 'GET'
  },
  {
    id: '42',
    name: 'Обновить профиль',
    description: 'Обновить информацию профиля',
    category: 'Profile',
    icon: '✏️',
    endpoint: '/api/egov/profile/update',
    method: 'PUT'
  },
  {
    id: '43',
    name: 'Изменить пароль',
    description: 'Изменить пароль профиля',
    category: 'Profile',
    icon: '🔒',
    endpoint: '/api/egov/profile/password',
    method: 'POST'
  },
  {
    id: '44',
    name: 'Двухфакторная аутентификация',
    description: 'Настройка 2FA',
    category: 'Profile',
    icon: '🔐',
    endpoint: '/api/egov/profile/2fa',
    method: 'POST'
  },
  {
    id: '45',
    name: 'Удалить профиль',
    description: 'Удалить аккаунт (необратимо)',
    category: 'Profile',
    icon: '🗑️',
    endpoint: '/api/egov/profile/delete',
    method: 'DELETE'
  },

  // 46-50: Платежи и аналитика
  {
    id: '46',
    name: 'История платежей',
    description: 'Информация о платежах',
    category: 'Payments',
    icon: '💳',
    endpoint: '/api/egov/payments/history',
    method: 'GET'
  },
  {
    id: '47',
    name: 'Инициировать платеж',
    description: 'Начать процесс платежа',
    category: 'Payments',
    icon: '💵',
    endpoint: '/api/egov/payments/initiate',
    method: 'POST'
  },
  {
    id: '48',
    name: 'Аналитика использования',
    description: 'Статистика использования услуг',
    category: 'Analytics',
    icon: '📈',
    endpoint: '/api/egov/analytics/usage',
    method: 'GET'
  },
  {
    id: '49',
    name: 'Нагрузка системы',
    description: 'Текущая нагрузка eGov системы',
    category: 'Analytics',
    icon: '⚡',
    endpoint: '/api/egov/analytics/load',
    method: 'GET'
  },
  {
    id: '50',
    name: 'Отчет',
    description: 'Получить отчет по использованию',
    category: 'Analytics',
    icon: '📊',
    endpoint: '/api/egov/analytics/report',
    method: 'GET'
  }
];

const EgovFunctions: React.FC = () => {
  const [functions, setFunctions] = useState<EgovFunction[]>(EGOV_FUNCTIONS);
  const [filteredFunctions, setFilteredFunctions] = useState<EgovFunction[]>(EGOV_FUNCTIONS);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Извлечь уникальные категории
  const categories = Array.from(new Set(functions.map(f => f.category)));

  // Фильтровать функции по поисковому запросу и категории
  useEffect(() => {
    let filtered = functions;

    if (searchTerm) {
      filtered = filtered.filter(f => 
        f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.endpoint.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory) {
      filtered = filtered.filter(f => f.category === selectedCategory);
    }

    setFilteredFunctions(filtered);
  }, [searchTerm, selectedCategory, functions]);

  // Выполнить функцию
  const executeFunction = async (func: EgovFunction) => {
    setLoading(true);
    try {
      const response = await fetch(func.endpoint, {
        method: func.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      const data = await response.json();
      console.log(`${func.name} результат:`, data);
      
      // Можно добавить toast уведомление
      alert(`✅ ${func.name} выполнена успешно!\n\nОтвет: ${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      console.error(`Ошибка при выполнении ${func.name}:`, error);
      alert(`❌ Ошибка при выполнении: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="egov-functions-container">
      <div className="egov-header">
        <h1>🏛️ eGov Функции (50+)</h1>
        <p className="egov-subtitle">Полный список всех доступных государственных услуг и функций</p>
      </div>

      {/* Поиск */}
      <div className="egov-search-section">
        <Input
          type="text"
          placeholder="🔎 Поиск функции (название, описание, endpoint)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="egov-search-input"
        />
      </div>

      {/* Фильтры по категориям */}
      <div className="egov-categories">
        <button
          className={`category-btn ${selectedCategory === null ? 'active' : ''}`}
          onClick={() => setSelectedCategory(null)}
        >
          Все ({functions.length})
        </button>
        {categories.map(category => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category)}
          >
            {category} ({functions.filter(f => f.category === category).length})
          </button>
        ))}
      </div>

      {/* Результаты поиска */}
      <div className="egov-stats">
        <p>Найдено {filteredFunctions.length} функций из {functions.length}</p>
      </div>

      {/* Сетка функций */}
      <div className="egov-grid">
        {filteredFunctions.map((func) => (
          <Card key={func.id} className="egov-function-card">
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
                disabled={loading}
              >
                {loading ? '⏳' : '▶️'} Test
              </button>
            </div>
          </Card>
        ))}
      </div>

      {filteredFunctions.length === 0 && (
        <div className="no-results">
          <p>😞 Функции не найдены</p>
          <p>Пожалуйста, попробуйте другой поисковый запрос или категорию</p>
        </div>
      )}
    </div>
  );
};

export default EgovFunctions;
