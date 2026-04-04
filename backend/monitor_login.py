#!/usr/bin/env python3
"""
Real-time log monitor for login flow debugging
Analyzes server logs and highlights key events
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(f"""
{Colors.BOLD}{Colors.OKBLUE}
╔════════════════════════════════════════════════════════════════╗
║           LOGIN FLOW LOG MONITOR                               ║
║  This script monitors backend logs during login flow           ║
║  Start this BEFORE logging in to capture full flow            ║
╚════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")

print(f"{Colors.WARNING}Instructions:{Colors.ENDC}")
print("1. Start backend server in another terminal:")
print("   cd backend")
print("   python -m uvicorn app.main:app --reload --port 8000")
print()
print("2. Run this script:")
print("   python monitor_login.py")
print()
print("3. In browser, go to http://localhost:5176")
print("4. Try to login")
print("5. Watch this window for login flow events")
print()
print(f"{Colors.OKGREEN}Starting monitor...{Colors.ENDC}\n")

# Keywords to highlight
KEYWORDS = {
    'get_current_user() CALLED': ('🔐', Colors.OKBLUE),
    'Stack user_id from token': ('🔑', Colors.BOLD),
    'Found existing user': ('✅', Colors.OKGREEN),
    'New user detected': ('👤', Colors.OKCYAN),
    'Inserting user to database': ('📝', Colors.OKCYAN),
    'User created successfully': ('✅', Colors.OKGREEN),
    'Failed to create user': ('❌', Colors.FAIL),
    'Missing authorization header': ('❌', Colors.FAIL),
    'Token verification': ('🔐', Colors.OKBLUE),
    'Database error': ('❌', Colors.FAIL),
    'OTP token verified': ('✅', Colors.OKGREEN),
    'Profile not found': ('❌', Colors.FAIL),
    'Profile created successfully': ('✅', Colors.OKGREEN),
}

def parse_log_line(line):
    """Extract timestamp and highlight keywords"""
    for keyword, (emoji, color) in KEYWORDS.items():
        if keyword.lower() in line.lower():
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            return f"{Colors.BOLD}[{timestamp}]{Colors.ENDC} {emoji} {color}{line}{Colors.ENDC}"
    return None

print(f"{Colors.BOLD}Listening for logs...{Colors.ENDC}")
print("(Press Ctrl+C to stop)\n")

# Try to run uvicorn and capture output
proc = None
try:
    # Check if backend directory exists
    backend_dir = Path(__file__).parent
    if not (backend_dir / "app" / "main.py").exists():
        print(f"{Colors.FAIL}Error: Could not find app/main.py{Colors.ENDC}")
        print(f"Run this script from the backend/ directory")
        sys.exit(1)
    
    # Start process with unbuffered output
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
        cwd=str(backend_dir),
    )
    
    print(f"{Colors.OKGREEN}✓ Backend started{Colors.ENDC}\n")
    
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        
        # Remove trailing newline
        line = line.rstrip('\n\r')
        
        # Try to highlight important lines
        highlighted = parse_log_line(line)
        if highlighted:
            print(highlighted)
        elif any(keyword.lower() in line.lower() for keyword in [
            'error', 'exception', 'warning', 'failed', 'traceback',
            'profile', 'user', 'token', 'auth', 'stack'
        ]):
            # Show other important lines in neutral color
            if 'traceback' in line.lower():
                print(f"{Colors.FAIL}{line}{Colors.ENDC}")
            else:
                print(line)

except KeyboardInterrupt:
    print(f"\n\n{Colors.WARNING}Monitor stopped{Colors.ENDC}")
    
except Exception as e:
    print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
    
finally:
    if proc:
        proc.terminate()
        print(f"{Colors.WARNING}Backend process terminated{Colors.ENDC}")

print(f"""
{Colors.BOLD}Analysis Complete{Colors.ENDC}

{Colors.OKGREEN}Key events to look for:{Colors.ENDC}
  ✅ get_current_user() CALLED - Auth check started
  🔑 Stack user_id from token - Token decoded
  ✅ Found existing user - Login successful
  👤 New user detected - Creating new profile
  📝 Inserting user to database - Writing to DB
  ✅ User created successfully - New profile created
  ❌ Failed to create user - Something went wrong

{Colors.OKCYAN}If you see errors:{Colors.ENDC}
  1. Check Supabase connection
  2. Verify STACK_AUTH_JWKS_URL in .env
  3. Ensure users table schema is correct
  4. Check Supabase credentials
""")
