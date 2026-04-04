#!/usr/bin/env python3
"""
Advanced diagnostic: Simulate exact login flow
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🔬 ADVANCED DIAGNOSTIC: Simulating Login Flow")
print("=" * 80)

# Setup
from app.database import get_db
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Part 1: Check database state
print("\n1️⃣ DATABASE STATE")
print("-" * 80)
try:
    db = get_db()
    result = db.table("users").select("count", count="exact").execute()
    print(f"✅ Total users in database: {result.count}")
    
    # Show recent users
    recent = db.table("users").select("id, stack_user_id, email, full_name").order("id", desc=True).limit(3).execute()
    if recent.data:
        print(f"\n📊 Recent users:")
        for user in recent.data:
            print(f"   - {user['email']} ({user['full_name']})")
    else:
        print("   (No users yet)")
        
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Part 2: Simulate JWT payload
print("\n2️⃣ SIMULATING JWT PAYLOAD (Stack Auth)")
print("-" * 80)

import uuid
from datetime import datetime, timezone, timedelta

simulated_stack_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
simulated_payload = {
    "sub": simulated_stack_user_id,
    "email": f"{simulated_stack_user_id}@test.supergov.kz",
    "primary_email": f"{simulated_stack_user_id}@test.supergov.kz",
    "display_name": "Тестовый Пользователь",
    "aud": os.getenv("STACK_PROJECT_ID", "test-aud"),
    "iss": os.getenv("STACK_AUTH_JWKS_URL", "https://test.iss").split("/")[2],
    "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
}

print(f"📝 Simulated Stack Auth payload:")
print(json.dumps(simulated_payload, indent=2, ensure_ascii=False))

# Part 3: Simulate profile creation
print("\n3️⃣ SIMULATING PROFILE AUTO-CREATION")
print("-" * 80)

try:
    stack_user_id = simulated_payload.get("sub")
    
    # Check if exists
    user_res = db.table("users").select("*").eq("stack_user_id", stack_user_id).execute()
    
    if user_res.data:
        print(f"✅ User already exists: {stack_user_id}")
        print(f"   ID: {user_res.data[0]['id']}")
    else:
        print(f"👤 New user detected: {stack_user_id}")
        
        # Extract from JWT
        email = simulated_payload.get("primary_email") or simulated_payload.get("email") or f"{stack_user_id}@supergov.kz"
        full_name = simulated_payload.get("display_name") or stack_user_id
        
        new_user_data = {
            "stack_user_id": stack_user_id,
            "email": email.strip().lower(),
            "full_name": full_name,
            "phone": "",
            "iin": "",
        }
        
        print(f"📝 Creating user with:")
        print(json.dumps(new_user_data, indent=3, ensure_ascii=False))
        
        # Create
        insert_res = db.table("users").insert(new_user_data).execute()
        
        if insert_res.data:
            created_user = insert_res.data[0]
            print(f"\n✅ Profile created successfully!")
            print(f"   ID: {created_user['id']}")
            print(f"   stack_user_id: {created_user['stack_user_id']}")
            print(f"   email: {created_user['email']}")
            print(f"   full_name: {created_user['full_name']}")
            
            # Verify by re-querying
            verify_res = db.table("users").select("*").eq("id", created_user['id']).execute()
            if verify_res.data:
                print(f"\n✅ Verification: Profile can be re-queried")
            else:
                print(f"\n⚠️  Warning: Could not re-query created profile")
                
        else:
            print(f"\n❌ Insert returned empty result")
            print(f"   This might mean the insert failed or returned no data")
            
            # Try to fetch
            retry_res = db.table("users").select("*").eq("stack_user_id", stack_user_id).execute()
            if retry_res.data:
                print(f"   ℹ️  But user can be found on retry!")
                print(f"   This is a quirk of Supabase API responses")
            else:
                print(f"   ❌ Could not find user on retry either")

except Exception as e:
    print(f"❌ Error during creation: {type(e).__name__}")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

# Part 4: Check what endpoints are available
print("\n4️⃣ CHECKING ENDPOINTS")
print("-" * 80)

try:
    from app.routers import profile_fix
    print("✅ profile_fix router imported")
    
    # List endpoints
    if hasattr(profile_fix.router, 'routes'):
        print(f"   Endpoints:")
        for route in profile_fix.router.routes:
            if hasattr(route, 'path'):
                print(f"   - {route.methods if hasattr(route, 'methods') else '?'} {route.path}")
except Exception as e:
    print(f"⚠️  Could not check profile_fix: {e}")

print("\n" + "=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)

print("\n📝 Summary:")
print("  If you see:")
print("  ✅ Profile created successfully - The fix is working!")
print("  ❌ Error during creation - Check Supabase permissions/connection")
print("  ⚠️  Insert returned empty - This might be normal, check your DB directly")

print("\n💡 Next steps:")
print("  1. If all ✅ - Try login again in the app")
print("  2. If ❌ - Check Supabase dashboard for errors")
print("  3. Watch server logs while testing: `python -m uvicorn app.main:app --reload`")

print("=" * 80)
