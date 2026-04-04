import type { LucideIcon } from 'lucide-react';
import {
  Mic,
  Sparkles,
  Scale,
  CalendarClock,
  Star,
  FolderOpen,
  Users,
  BarChart3,
  WifiOff,
  FlaskConical,
  MessageSquare,
  FileInput,
  ListOrdered,
  LayoutDashboard,
  FormInput,
  FileWarning,
  MapPin,
  GitBranch,
} from 'lucide-react';

export type SuperGovService = {
  id: string;
  tier: 'innovation' | 'mvp';
  title: string;
  subtitle: string;
  icon: LucideIcon;
  /** маршрут или deep-link в чат */
  href: string;
  chatPrompt?: string;
};

/** 18 услуг/функций продукта */
export const SUPERGOV_SERVICES: SuperGovService[] = [
  { id: 'voice-agent', tier: 'innovation', title: 'Голосовой агент', subtitle: 'Полное управление голосом. Для пожилых и регионов', icon: Mic, href: '/chat', chatPrompt: 'Расскажи про голосовой агент SuperGov' },
  { id: 'predict-benefits', tier: 'innovation', title: 'Предиктивные льготы', subtitle: 'ИИ находит пособия и субсидии по праву', icon: Sparkles, href: '/benefits', chatPrompt: 'Какие льготы мне доступны? Предиктивный подбор.' },
  { id: 'ai-lawyer', tier: 'innovation', title: 'AI-юрист', subtitle: 'Законы простым языком, ссылки на НПА', icon: Scale, href: '/chat', chatPrompt: 'Объясни мои права при обращении в госорган простым языком' },
  { id: 'smart-queue', tier: 'innovation', title: 'Умная очередь ЦОН', subtitle: 'Запись с прогнозом загрузки', icon: CalendarClock, href: '/chat', chatPrompt: 'Как записаться в ЦОН с умной очередью?' },
  { id: 'agency-rating', tier: 'innovation', title: 'Рейтинг ведомств', subtitle: 'Публичный рейтинг скорости и качества', icon: Star, href: '/rating', chatPrompt: 'Как устроен рейтинг ведомств?' },
  { id: 'digital-vault', tier: 'innovation', title: 'Цифровое хранилище', subtitle: 'Документы в облаке, автоподгрузка в заявках', icon: FolderOpen, href: '/chat', chatPrompt: 'Как работает цифровое хранилище документов?' },
  { id: 'family', tier: 'innovation', title: 'Семейный профиль', subtitle: 'Один аккаунт на семью, доверенности онлайн', icon: Users, href: '/chat', chatPrompt: 'Как настроить семейный профиль?' },
  { id: 'gov-analytics', tier: 'innovation', title: 'Gov-аналитика', subtitle: 'Узкие места, аномалии, тренды для государства', icon: BarChart3, href: '/chat', chatPrompt: 'Что показывает Gov-аналитика?' },
  { id: 'offline', tier: 'innovation', title: 'Офлайн-режим', subtitle: 'Формы без сети, синхронизация при подключении', icon: WifiOff, href: '/chat', chatPrompt: 'Как работает офлайн-режим заполнения форм?' },
  { id: 'sandbox', tier: 'innovation', title: 'Песочница', subtitle: 'Проверка заявки до отправки без риска', icon: FlaskConical, href: '/chat', chatPrompt: 'Как проверить заявку в песочнице до отправки?' },
  { id: 'ai-chat', tier: 'mvp', title: 'AI-помощник', subtitle: 'Чат kk / ru / en, голосовой ввод', icon: MessageSquare, href: '/chat' },
  { id: 'form-gen', tier: 'mvp', title: 'Генерация форм', subtitle: 'До 95% полей из ИИН и профиля', icon: FileInput, href: '/services', chatPrompt: 'Как работает автозаполнение форм из ИИН?' },
  { id: 'guide', tier: 'mvp', title: 'Пошаговый гайд', subtitle: 'План с прогрессом, объяснение шагов', icon: ListOrdered, href: '/services', chatPrompt: 'Дай пошаговый гайд по выбранной услуге' },
  { id: 'status-dash', tier: 'mvp', title: 'Дашборд статусов', subtitle: 'Все заявки, статусы в реальном времени', icon: LayoutDashboard, href: '/applications' },
  { id: 'autofill', tier: 'mvp', title: 'Автозаполнение', subtitle: 'Профиль → поля формы без ручного ввода', icon: FormInput, href: '/services', chatPrompt: 'Как включить автозаполнение из профиля?' },
  { id: 'refusal-ai', tier: 'mvp', title: 'AI-объяснение отказов', subtitle: 'Юридический текст → план исправления', icon: FileWarning, href: '/chat', chatPrompt: 'Объясни отказ в заявке простым языком' },
  { id: 'complaints-map', tier: 'mvp', title: 'Карта жалоб', subtitle: 'Карта и кластеризация по районам', icon: MapPin, href: '/map' },
  { id: 'unified-flow', tier: 'mvp', title: 'Единый поток', subtitle: 'Жизненное событие → услуги параллельно', icon: GitBranch, href: '/chat', chatPrompt: 'Как оформить жизненное событие и все услуги сразу?' },
];
