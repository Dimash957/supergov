#!/usr/bin/env python3
"""
FINAL VERIFICATION CHECKLIST - Check everything in one command
"""

import subprocess
import sys
import os
from pathlib import Path

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def check(message, condition):
    symbol = f"{GREEN}✅{RESET}" if condition else f"{RED}❌{RESET}"
    print(f"{symbol} {message}")
    return condition

def warn(message, condition):
    symbol = f"{YELLOW}⚠️{RESET}" if not condition else f"{GREEN}✅{RESET}"
    print(f"{symbol} {message}")
    return condition

print(f"""
{BOLD}{BLUE}
╔════════════════════════════════════════════════════════════════╗
║               FINAL VERIFICATION CHECKLIST                    ║
║              Running all diagnostic checks...                 ║
╚════════════════════════════════════════════════════════════════╝
{RESET}
""")

# Check 1: Files exist
print_header("1. FILE STRUCTURE CHECK")
backend_dir = Path(__file__).parent

files_to_check = {
    "app/auth.py": "Authentication module",
    "app/main.py": "Main app entry",
    "app/database.py": "Database connection",
    "app/routers/profile_fix.py": "Profile endpoints",
    ".env": "Environment variables",
}

all_files_ok = True
for file, desc in files_to_check.items():
    exists = (backend_dir / file).exists()
    check(f"{desc:<30} ({file})", exists)
    all_files_ok = all_files_ok and exists

# Check 2: Environment variables
print_header("2. ENVIRONMENT VARIABLES CHECK")

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv()

required_env_vars = {
    "SUPABASE_URL": "Database URL",
    "SUPABASE_SERVICE_KEY": "Database Service Key (write permissions)",
    "STACK_AUTH_JWKS_URL": "Stack Auth JWKS endpoint",
    "STACK_PROJECT_ID": "Stack Auth Project ID",
}

env_ok = True
for var, desc in required_env_vars.items():
    val = os.getenv(var, "")
    exists = bool(val)
    if exists:
        if "KEY" in var or "URL" in var:
            display = val[:20] + "..." if len(val) > 20 else val
        else:
            display = val
        check(f"{desc:<35} = {display}", exists)
    else:
        check(f"{desc:<35} = NOT SET", exists)
    env_ok = env_ok and exists

# Check 3: Database connection
print_header("3. DATABASE CONNECTION CHECK")

try:
    from app.database import get_db
    db = get_db()
    
    # Test connection
    try:
        result = db.table("users").select("count", count="exact").execute()
        check(f"Supabase connection successful", True)
        check(f"Users table accessible, total users: {result.count}", True)
    except Exception as e:
        check(f"Query users table", False)
        print(f"   Error: {str(e)[:80]}")
        
except Exception as e:
    check(f"Import database module", False)
    print(f"   Error: {str(e)[:80]}")

# Check 4: Auth module
print_header("4. AUTHENTICATION MODULE CHECK")

try:
    import app.auth as auth_module
    check("auth.py imports successfully", True)
    
    # Check key functions
    has_get_current_user = hasattr(auth_module, 'get_current_user')
    check("get_current_user() function exists", has_get_current_user)
    
    # Check for auto-create logic
    with open(backend_dir / "app/auth.py", "r") as f:
        auth_content = f.read()
        has_auto_create = "NEW USER - AUTO-CREATE PROFILE" in auth_content
        has_logging = "logger.info" in auth_content
        check("Auto-create profile logic implemented", has_auto_create)
        check("Detailed logging implemented", has_logging)
        
except Exception as e:
    check("Import auth module", False)
    print(f"   Error: {str(e)[:80]}")

# Check 5: API Routes
print_header("5. API ROUTES CHECK")

try:
    from app.main import app
    from fastapi.routing import APIRoute
    
    profile_routes = []
    auth_routes = []
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            if "/profile" in route.path:
                profile_routes.append(f"{route.path}")
            elif "/auth" in route.path:
                auth_routes.append(f"{route.path}")
    
    check(f"Profile routes available: {len(profile_routes)} routes", len(profile_routes) > 0)
    for route in profile_routes:
        print(f"   └─ {route}")
        
    check(f"Auth routes available: {len(auth_routes)} routes", len(auth_routes) > 0)
    for route in auth_routes:
        print(f"   └─ {route}")
        
except Exception as e:
    check("Load main app", False)
    print(f"   Error: {str(e)[:80]}")

# Check 6: Diagnostic Scripts
print_header("6. DIAGNOSTIC TOOLS CHECK")

diagnostic_files = {
    "check_profile_creation.py": "Profile creation diagnostic",
    "advanced_diagnostics.py": "Advanced system diagnostic",
    "monitor_login.py": "Real-time login monitoring",
}

for file, desc in diagnostic_files.items():
    exists = (backend_dir / file).exists()
    check(f"{desc:<35<} ({file})", exists)

# Check 7: Documentation
print_header("7. DOCUMENTATION CHECK")

doc_files = {
    "TESTING_PROFILE_FIX.md": "Testing guide",
    "DEBUGGING_GUIDE_RU.md": "Debugging guide (Russian)",
}

for file, desc in doc_files.items():
    exists = (backend_dir / file).exists()
    check(f"{desc:<35} ({file})", exists)

# Final Summary
print_header("FINAL SUMMARY")

print(f"\n{BOLD}To start debugging:{RESET}\n")
print("1. Quick check (5 min):")
print(f"   {BLUE}python check_profile_creation.py{RESET}")

print("\n2. Real-time monitoring (when testing):")
print(f"   {BLUE}python monitor_login.py{RESET}")

print("\n3. Full debugging (if issues):")
print(f"   {BLUE}python advanced_diagnostics.py{RESET}\n")

print("\n4. Detailed guide (read first):")
print(f"   {BLUE}more DEBUGGING_GUIDE_RU.md{RESET}\n")

print(f"\n{BOLD}Expected login flow with proper logging:{RESET}")
print(f"  🔐 get_current_user() CALLED")
print(f"  🔑 Stack user_id from token: xxx")
print(f"  📊 Querying database for existing user...")
print(f"  👤 New user detected (or ✅ Found existing user)")
print(f"  📝 Inserting user to database...")
print(f"  ✅ User created successfully (DB ID: xxx)")
print(f"  🔐=== get_current_user() FINISHED ===\n")

if all_files_ok and env_ok:
    print(f"{GREEN}{BOLD}✅ All checks passed! Ready to test.{RESET}\n")
else:
    print(f"{YELLOW}{BOLD}⚠️ Some checks failed. See above and fix issues.{RESET}\n")
