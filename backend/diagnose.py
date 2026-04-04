#!/usr/bin/env python3
"""
PROFILE ERROR QUICK DIAGNOSIS
Emergency helper - run this if you see "Профиль не найден" error
"""

import sys
import os
from pathlib import Path
from datetime import datetime

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_stage(num, title):
    print(f"\n{BOLD}{BLUE}─────────────────────────────────────────{RESET}")
    print(f"{BOLD}{BLUE}STAGE {num}: {title}{RESET}")
    print(f"{BOLD}{BLUE}─────────────────────────────────────────{RESET}\n")

print(f"""
{BOLD}{RED}
╔════════════════════════════════════════════════════╗
║  🆘 PROFILE NOT FOUND - QUICK DIAGNOSIS           ║
║  If you see "Профиль не найден" error             ║
╚════════════════════════════════════════════════════╝
{RESET}
""")

print(f"{YELLOW}Looking for root cause...{RESET}\n")

# Stage 1: Check .env
print_stage(1, "Environment Variables")

backend_dir = Path(__file__).parent
env_file = backend_dir.parent / ".env"

missing_vars = []
if not env_file.exists():
    print(f"{RED}❌ .env file not found at {env_file}{RESET}")
    print(f"   → Create .env file in project root with Supabase credentials")
    missing_vars.append(".env file")
else:
    print(f"{GREEN}✅ .env file exists{RESET}")
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Check critical vars
    critical = {
        "SUPABASE_URL": "Database URL",
        "SUPABASE_SERVICE_KEY": "Database key",
        "STACK_AUTH_JWKS_URL": "Auth JWKS",
        "STACK_PROJECT_ID": "Auth Project ID",
    }
    
    for var, desc in critical.items():
        val = os.getenv(var)
        if not val:
            print(f"{RED}❌ {desc} ({var}) not set{RESET}")
            missing_vars.append(var)
        else:
            print(f"{GREEN}✅ {desc}{RESET}")

# Stage 2: Check database connection
print_stage(2, "Database Connection")

try:
    from app.database import get_db
    db = get_db()
    
    # Try to query
    try:
        result = db.table("users").select("count", count="exact").execute()
        print(f"{GREEN}✅ Database connected successfully{RESET}")
        print(f"   → Found {result.count} users in database")
    except Exception as q_err:
        print(f"{RED}❌ Cannot query users table{RESET}")
        print(f"   → Error: {str(q_err)[:80]}")
        print(f"   → Make sure 'users' table exists in Supabase")
        
except Exception as db_err:
    print(f"{RED}❌ Cannot connect to database{RESET}")
    print(f"   → Error: {str(db_err)[:80]}")
    print(f"   → Check SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")

# Stage 3: Check auth configuration
print_stage(3, "Authentication Setup")

from jose import jwt

jwks_url = os.getenv("STACK_AUTH_JWKS_URL")
if not jwks_url:
    print(f"{YELLOW}⚠️  STACK_AUTH_JWKS_URL not configured{RESET}")
    print(f"   → Using mock authentication")
else:
    print(f"{GREEN}✅ Stack Auth configured{RESET}")
    
    project_id = os.getenv("STACK_PROJECT_ID")
    if project_id:
        print(f"   → Project ID: {project_id}")
    else:
        print(f"{YELLOW}⚠️  STACK_PROJECT_ID not set (but JWKS URL is){RESET}")

# Stage 4: Check application code
print_stage(4, "Application Code")

auth_file = backend_dir / "app" / "auth.py"
if not auth_file.exists():
    print(f"{RED}❌ auth.py not found{RESET}")
else:
    with open(auth_file) as f:
        auth_content = f.read()
    
    checks = {
        "Auto-create logic": "NEW USER - AUTO-CREATE PROFILE" in auth_content,
        "Logging enabled": "logger.info" in auth_content,
        "get_current_user defined": "def get_current_user" in auth_content,
    }
    
    for check_name, result in checks.items():
        symbol = f"{GREEN}✅{RESET}" if result else f"{RED}❌{RESET}"
        print(f"{symbol} {check_name}")

# Stage 5: Check logs directory
print_stage(5, "Recent Server Logs")

print("To see detailed logs during login:")
print(f"  {BLUE}python monitor_login.py{RESET}")
print()
print("This will show each step of auth process with 🔐, 👤, ✅, ❌ indicators")

# Summary
print_stage(6, "Diagnosis Summary")

if missing_vars:
    print(f"{RED}{BOLD}FOUND PROBLEMS:{RESET}\n")
    for var in missing_vars:
        print(f"  ❌ {var}")
    
    print(f"\n{YELLOW}QUICK FIX:{RESET}")
    print("1. Update your .env file with all required variables")
    print("2. Restart your backend server")
    print("3. Try logging in again")
else:
    print(f"{GREEN}{BOLD}✅ ALL CHECKS PASSED!{RESET}\n")
    print("Configuration looks correct.")
    print()
    print(f"{YELLOW}Next steps:{RESET}")
    print("1. Start backend:")
    print(f"   {BLUE}python -m uvicorn app.main:app --reload --port 8000{RESET}")
    print()
    print("2. Monitor logs (in new terminal):")
    print(f"   {BLUE}python monitor_login.py{RESET}")
    print()
    print("3. Try login in browser")
    print()
    print(f"{YELLOW}Watch for these in logs:{RESET}")
    print("  🔐 get_current_user() CALLED")
    print("  👤 New user detected: xxx")
    print("  ✅ User created successfully")

print(f"\n{BLUE}For more help:{RESET}")
print(f"  {BLUE}cat TOOLS_README.md{RESET}          (Quick reference)")
print(f"  {BLUE}cat DEBUGGING_GUIDE_RU.md{RESET}   (Full debugging guide)")
print(f"  {BLUE}python start.py{RESET}              (Interactive menu)")

print(f"\n{BOLD}Diagnosis complete!{RESET}\n")
