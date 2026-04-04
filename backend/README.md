# SuperGov Backend Setup

## 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Tesseract OCR (installed globally or via Docker)

## 2. Environment Setup
Rename `.env.example` to `.env` and fill in your keys:
- Anthropic API Key
- Supabase credentials
- Stack Auth JWKS URL & Project ID
- Redis URL

## 3. Launching

**Using Docker (Recommended):**
```bash
docker-compose up -d --build
```
This starts Redis and Celery (Worker + Beat).

**Starting FastAPI:**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Supabase Setup
Run the `app/schema.sql` file in your Supabase SQL Editor to generate all tables.

## 5. API Documentation
Swagger is automatically available at `http://localhost:8000/docs`.
