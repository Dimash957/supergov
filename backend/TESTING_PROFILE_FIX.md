# ✅ PROFILE FIX - TESTING INSTRUCTIONS

## 🎯 What Was Fixed

**Problem**: Users got error "Профиль не найден в базе" after login
**Solution**: `get_current_user()` now auto-creates profile on first Stack Auth login

---

## 🧪 How to Test

### Step 1: Run Diagnostics
```bash
cd backend
python check_profile_creation.py
```

Should show:
- ✅ Supabase connected
- ✅ Users table accessible
- ✅ auth.py imported
- ✅ Auto-create logic found
- ✅ User created successfully (test)

### Step 2: Start Backend with Logging
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Watch logs for:
```
👤 New user detected: [USER_ID]
📝 Creating user with data: {...}
✅ User created successfully: [ID]
```

### Step 3: Start Frontend
```bash
npm run dev
```

### Step 4: Test Flow

**Option A: Stack Auth Login**
1. Go to http://localhost:5176
2. Click **"Вход через Stack"** (Stack Login)
3. Enter Stack credentials
4. Should log in successfully ✅

**Option B: Direct Registration (if available)**
1. Go to http://localhost:5176/register
2. Fill registration form
3. Should create profile ✅

### Step 5: Verify Profile Created
1. After login, check console for any errors
2. Go to http://localhost:5176/profile
3. Should show your profile data ✅

---

## 🔍 Checking Server Logs

### Watch for Success Messages
```
INFO: ✅ Found existing user: user_123
INFO: ✅ User created successfully: [UUID]
```

### Watch for Errors  
```
ERROR: ❌ Failed to create user: [ERROR_TYPE]: [ERROR_MESSAGE]
```

---

## 🛠 If Still Getting Error

### Check 1: Supabase Connection
```bash
python check_profile_creation.py
```

If Supabase fails:
- Verify `SUPABASE_URL` in `.env`
- Verify `SUPABASE_SERVICE_KEY` in `.env`
- Check Supabase dashboard for API key validity

### Check 2: Database Permissions
- Supabase `users` table must allow inserts
- Service key must have write permission
- Check Supabase Row Level Security (RLS) settings

### Check 3: Stack Auth Token
- Token must include `sub` field (stack_user_id)
- Token must be valid (not expired)
- Check Stack Auth configuration

### Check 3: Database Schema
Verify `users` table has columns:
- `id` (uuid, primary key)
- `stack_user_id` (text)
- `email` (text)
- `full_name` (text)
- `phone` (text)
- `iin` (text)

You can check in Supabase dashboard under Tables → users

---

## 📊 Flow Diagram

```
User Logs In (Stack Auth)
       ↓
Stack returns JWT with stack_user_id
       ↓
get_current_user() called
       ↓
Look up user by stack_user_id
       ↓
     NOT FOUND?
    ╱      ╲
  NO       YES
  ↓         ↓
Return  AUTO-CREATE
user    Profile
 ↓        ↓
 └────┬────┘
      ↓
 ✅ LOGGED IN
```

---

## 📝 Key Changes Made

### File: `app/auth.py`
- Added logging import
- Added profile auto-creation in `get_current_user()`
- When new user detected:
  - Extract email, name from JWT
  - Create profile in database
  - Return user data
- Added detailed logging for debugging

### File: `app/routers/profile_fix.py`
- Simplified `/api/profile/me` to just verify profile
- Updated error handling

---

## ✅ Expected Behavior

| Scenario | Before | After |
|----------|--------|-------|
| New Stack Auth user | ❌ "Профиль не найден" | ✅ Auto-created + logged in |
| Existing user login | ✅ Works | ✅ Works |
| Fill profile data | ❌ Error | ✅ Works |
| Access protected endpoints | ❌ Error | ✅ Works |

---

## 🚀 Production Deployment

Before deploying:
1. Run `python check_profile_creation.py` ✅
2. Test login flow locally ✅
3. Check server logs for errors ✅
4. Verify Supabase permissions ✅
5. Test with real Stack Auth credentials ✅

---

## 💡 Helpful Commands

```bash
# Run full diagnostic
cd backend && python check_profile_creation.py

# Start with verbose logging
cd backend && python -m uvicorn app.main:app --log-level debug --reload --port 8000

# Check backend errors
tail -f backend.log

# Check if Supabase accessible
curl https://your-supabase-url/rest/v1/

# Test user creation manually (from Python)
from app.database import get_db
db = get_db()
result = db.table("users").select("*").execute()
print(result.data)
```

---

## 📞 If Still Having Issues

1. **Check backend logs** - Start server and watch for emoji messages (✅, ❌, 👤, 📝)
2. **Run diagnostics** - `python check_profile_creation.py`
3. **Verify Supabase** - Can you insert rows manually?
4. **Check .env** - Do SUPABASE_* variables exist?
5. **Test Stack Auth locally** - Can you get valid tokens?

---

✅ **All systems should be working now!**
