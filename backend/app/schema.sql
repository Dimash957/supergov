-- Supabase Schema for SuperGov

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  stack_user_id text UNIQUE NOT NULL,
  iin text UNIQUE NOT NULL,
  email text UNIQUE NOT NULL,
  phone text,
  full_name text,
  address text,
  birth_date date,
  has_eds boolean DEFAULT false,
  eds_expires_at timestamptz,
  subscription_tier text DEFAULT 'free',
  language text DEFAULT 'ru',
  notification_telegram boolean DEFAULT true,
  notification_email boolean DEFAULT true,
  notification_sms boolean DEFAULT false,
  telegram_chat_id text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS applications (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  service_type text NOT NULL,
  egov_application_id text,
  status text DEFAULT 'submitted',
  status_label text,
  form_data jsonb DEFAULT '{}',
  agency text,
  predicted_completion_date date,
  citizen_rating integer,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_steps (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id uuid REFERENCES applications(id),
  step_number integer,
  title text,
  status text DEFAULT 'pending',
  completed_at timestamptz
);

CREATE TABLE IF NOT EXISTS complaints (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  category text,
  description text,
  lat double precision,
  lng double precision,
  status text DEFAULT 'new',
  agency_assigned text,
  votes integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  doc_type text,
  file_name text,
  storage_path text,
  ocr_text text,
  extracted_fields jsonb DEFAULT '{}',
  expires_at date,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS benefits (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text,
  description text,
  amount_min integer,
  amount_max integer,
  frequency text,
  criteria jsonb,
  agency text,
  service_type text
);

CREATE TABLE IF NOT EXISTS user_benefits (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  benefit_id uuid REFERENCES benefits(id),
  is_eligible boolean,
  explanation text,
  discovered_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  title text,
  body text,
  type text,
  is_read boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agencies (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name text,
  code text UNIQUE,
  avg_processing_days numeric,
  approval_rate numeric,
  avg_citizen_rating numeric,
  composite_score numeric,
  score_trend numeric
);
