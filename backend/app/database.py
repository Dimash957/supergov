import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

# gogo/.env и backend/.env (часто секреты кладут только в backend)
_env_gogo = Path(__file__).resolve().parents[2] / ".env"
_env_backend = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_gogo)
load_dotenv(_env_backend)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: Supabase credentials не найдены в .env!")
    print("   - SUPABASE_URL:", "OK" if SUPABASE_URL else "missing")
    print("   - SUPABASE_SERVICE_KEY:", "OK" if SUPABASE_SERVICE_KEY else "missing")
else:
    print("OK: Supabase credentials найдены")

# Проверка формата ключа (JWT должен иметь 2 точки: header.payload.signature)
if SUPABASE_SERVICE_KEY and SUPABASE_SERVICE_KEY.count(".") != 2:
    print("WARN: SUPABASE_SERVICE_KEY имеет неправильный формат!")
    print(f"   Найдено {SUPABASE_SERVICE_KEY.count('.')} точек, ожидается 2")
    print("   Проверьте, что все 3 части JWT присутствуют без дублей")

# Use service key for backend admin operations bypass RLS
try:
    supabase: Client = create_client(SUPABASE_URL or "http://localhost", SUPABASE_SERVICE_KEY or "dummy")
except Exception as e:
    print(f"ERROR: Ошибка инициализации Supabase: {e}")
    supabase = None


class MockDBResponse:
    """Mock response object"""
    def __init__(self, data):
        self.data = data


class MockDBTable:
    """Mock table for demo mode when Supabase tables don't exist"""
    
    # Shared storage across all instances
    _storage = {
        "users": [],
        "benefits": [
            {"id": 1, "name": "Пособие на ребенка", "amount_min": 10000, "amount_max": 50000},
            {"id": 2, "name": "Жилищная субсидия", "amount_min": 20000, "amount_max": 100000},
        ],
        "documents": []
    }
    _next_ids = {"users": 100, "documents": 100}
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.select_cols = None
        self.filters = []  # List of (column, value) tuples
        self.limit_count = None
        self.insert_data = None
        self.update_data = None
    
    def select(self, cols: str):
        self.select_cols = cols
        return self
    
    def eq(self, col: str, val):
        self.filters.append((col, val))
        return self
    
    def limit(self, n: int):
        self.limit_count = n
        return self
    
    def insert(self, data):
        self.insert_data = data
        return self

    def update(self, data):
        self.update_data = data
        return self
    
    def execute(self):
        # Handle INSERT
        if self.insert_data:
            # Ensure table exists in storage
            if self.table_name not in self._storage:
                self._storage[self.table_name] = []
            
            table_data = self._storage[self.table_name]
            
            # Generate ID if not provided
            if "id" not in self.insert_data:
                next_id = self._next_ids.get(self.table_name, 100)
                self.insert_data["id"] = str(next_id)
                self._next_ids[self.table_name] = next_id + 1
            
            table_data.append(self.insert_data)
            print(f"[MockDB] INSERT into {self.table_name}: {self.insert_data}")
            print(f"[MockDB] Table now has {len(self._storage[self.table_name])} rows")
            
            return MockDBResponse([self.insert_data])

        # Handle UPDATE
        if self.update_data is not None:
            if self.table_name not in self._storage:
                self._storage[self.table_name] = []

            updated_rows = []
            for idx, row in enumerate(self._storage[self.table_name]):
                row_match = True
                for col, val in self.filters:
                    if row.get(col) != val:
                        row_match = False
                        break
                if row_match:
                    new_row = {**row, **self.update_data}
                    self._storage[self.table_name][idx] = new_row
                    updated_rows.append(new_row)

            print(f"[MockDB] UPDATE {self.table_name} filters={self.filters}: {len(updated_rows)} rows")
            return MockDBResponse(updated_rows)
        
        # Handle SELECT
        if self.table_name not in self._storage:
            self._storage[self.table_name] = []
            
        table_data = list(self._storage[self.table_name])  # Make a copy
        
        # Apply filters
        filters_desc = []
        for col, val in self.filters:
            table_data = [row for row in table_data if row.get(col) == val]
            filters_desc.append(f"{col}={val}")
        
        # Apply limit
        if self.limit_count:
            table_data = table_data[:self.limit_count]
        
        if self.filters:
            print(f"[MockDB] SELECT from {self.table_name} with {filters_desc}: found {len(table_data)} rows")
        
        return MockDBResponse(table_data)


class MockDB:
    """Mock database for when Supabase tables don't exist"""
    def table(self, name: str):
        return MockDBTable(name)


def get_db():
    if supabase is None:
        raise RuntimeError(
            "Supabase not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_KEY in .env"
        )
    
    # Try real DB, fallback to mock if tables don't exist
    try:
        # Test if tables exist by making a simple query
        supabase.table("users").select("id").limit(1).execute()
        return supabase
    except Exception as e:
        if "Could not find the table" in str(e):
            print("WARN: Таблицы Supabase не найдены. Используется демо-режим.")
            print("  INFO: Запустите schema.sql в Supabase SQL Editor для создания таблиц")
            return MockDB()
        raise
