#!/usr/bin/env python3
"""
QUICK START - Launch everything you need to debug the login issue
"""

import subprocess
import sys
import os
from pathlib import Path

def run_menu():
    while True:
        print("""
╔════════════════════════════════════════════════════════════╗
║          🔧 BACKEND DEBUGGING QUICK START                  ║
╚════════════════════════════════════════════════════════════╝

Choose what to do:

1️⃣  Run Full Verification (verify all components)
2️⃣  Check Profile Creation (simulate auto-create)  
3️⃣  Start Login Monitor (watch logs in real-time)
4️⃣  Run Advanced Diagnostics (deep system check)
5️⃣  Start Backend Server (python -m uvicorn...)
6️⃣  View Documentation

0️⃣  Exit

Command (0-6):""", end=" ", flush=True)

        try:
            choice = input().strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

        backend_dir = Path(__file__).parent

        if choice == "1":
            print("\n🔍 Running full verification...\n")
            subprocess.run([sys.executable, "verify_all.py"], cwd=backend_dir)
            
        elif choice == "2":
            print("\n🧪 Checking profile creation...\n")
            subprocess.run([sys.executable, "check_profile_creation.py"], cwd=backend_dir)
            
        elif choice == "3":
            print("\n📊 Starting login monitor...")
            print("(This will start the backend server)")
            print("(Close with Ctrl+C)\n")
            try:
                subprocess.run([sys.executable, "monitor_login.py"], cwd=backend_dir)
            except KeyboardInterrupt:
                print("\n\n✅ Monitor stopped")
                
        elif choice == "4":
            print("\n🔬 Running advanced diagnostics...\n")
            subprocess.run([sys.executable, "advanced_diagnostics.py"], cwd=backend_dir)
            
        elif choice == "5":
            print("\n🚀 Starting backend server...")
            print("(Backend will run on http://localhost:8000)")
            print("(Close with Ctrl+C)\n")
            try:
                subprocess.run([
                    sys.executable, "-m", "uvicorn",
                    "app.main:app",
                    "--reload",
                    "--port", "8000"
                ], cwd=backend_dir)
            except KeyboardInterrupt:
                print("\n\n✅ Server stopped")
                
        elif choice == "6":
            print("\n📖 Documentation Options:\n")
            print("1. View Tools Reference")
            print("   cat TOOLS_README.md")
            print()
            print("2. View Full Debugging Guide")
            print("   cat DEBUGGING_GUIDE_RU.md")
            print()
            print("3. View Testing Instructions")
            print("   cat TESTING_PROFILE_FIX.md")
            print()
            doc_choice = input("\nCommand (or press Enter to go back): ").strip()
            
            if doc_choice == "1":
                with open(backend_dir / "TOOLS_README.md") as f:
                    print(f.read())
            elif doc_choice == "2":
                with open(backend_dir / "DEBUGGING_GUIDE_RU.md") as f:
                    print(f.read())
            elif doc_choice == "3":
                with open(backend_dir / "TESTING_PROFILE_FIX.md") as f:
                    print(f.read())
                    
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Try again!")

        print("\n" + "="*60)

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
