#!/usr/bin/env python3
"""
Диагностика: Проверка что происходит при логине с Stack Auth
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🔍 DIAGNOSTIC: Checking Profile Auto-Creation")
print("=" * 70)

# 1. Check Supabase connection
print("\n1️⃣ Checking Supabase...")
try:
    from app.database import get_db
    db = get_db()
    print("   ✅ Supabase connected")
    
    # Check users table
    result = db.table("users").select("count", count="exact").execute()
    print(f"   ✅ Users table accessible ({result.count} users)")
    
except Exception as e:
    print(f"   ❌ Supabase ERROR: {e}")
    print(f"   💡 Check: SUPABASE_URL, SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

# 2. Check auth module
print("\n2️⃣ Checking auth.py...")
try:
    from app.auth import get_current_user
    print("   ✅ auth.py imported")
except Exception as e:
    print(f"   ❌ auth.py ERROR: {e}")
    sys.exit(1)

# 3. Check if auto-create logic exists
print("\n3️⃣ Checking auto-create logic in auth.py...")
try:
    with open("app/auth.py", "r", encoding="utf-8") as f:
        auth_code = f.read()
        if "AUTO-CREATE PROFILE" in auth_code or "auto-create" in auth_code.lower():
            print("   ✅ Auto-create logic found")
        else:
            print("   ⚠️  Auto-create logic might be missing")
            
        if "db.table(\"users\").insert" in auth_code:
            print("   ✅ Insert logic found")
        else:
            print("   ❌ Insert logic NOT found")
except Exception as e:
    print(f"   ⚠️  Could not check: {e}")

# 4. Simulate user creation
print("\n4️⃣ Testing manual user creation...")
try:
    import uuid
    test_user_id = str(uuid.uuid4())
    
    test_data = {
        "stack_user_id": f"test_{test_user_id}",
        "email": "test@supergov.kz",
        "full_name": "Test User",
        "phone": "",
        "iin": "",
    }
    
    result = db.table("users").insert(test_data).execute()
    
    if result.data:
        print(f"   ✅ User created successfully: {result.data[0]['id']}")
        
        # Clean up
        created_id = result.data[0]['id']
        db.table("users").delete().eq("id", created_id).execute()
        print("   ✅ Test user cleaned up")
    else:
        print(f"   ❌ Insert returned empty result")
        
except Exception as e:
    print(f"   ❌ Manual creation failed: {e}")

print("\n" + "=" * 70)
print("✅ DIAGNOSTICS COMPLETE")
print("=" * 70)
print("\n📝 Summary:")
print("   If all checks pass but you still get errors:")
print("   1. Make sure Stack Auth is configured")
print("   2. Check that tokens are valid")
print("   3. Verify SUPABASE_SERVICE_KEY has write permission")
print("\n💡 Next steps:")
print("   1. Start server: python -m uvicorn app.main:app --reload --port 8000")
print("   2. Try login at http://localhost:5176")
print("   3. Check server logs for detailed errors")
print("=" * 70)
