# 🔧 Backend Diagnostics & Debugging Suite

## 🎯 Purpose

This suite of tools helps debug and verify the "Профиль не найден" (Profile Not Found) error fix that was implemented in `app/auth.py`.

**Root cause fixed:** Auto-profile creation for new Stack Auth users

---

## 🚀 START HERE

### Option 1: Interactive Menu (Recommended)
```bash
python start.py
```
Choose from 6 different tools with an easy menu.

### Option 2: Quick Diagnosis
```bash
python diagnose.py
```
Emergency helper - tells you what's wrong in 30 seconds.

### Option 3: Just Read (30 seconds)
👉 **Open:** [QUICK_START_RU.md](QUICK_START_RU.md) - 3 action items to get started

---

## 📦 Available Tools

| Tool | Command | Best For |
|------|---------|----------|
| **start.py** | `python start.py` | Interactive menu - choose what to do |
| **diagnose.py** | `python diagnose.py` | Quick diagnosis of "Profile not found" |
| **verify_all.py** | `python verify_all.py` | Complete system verification |
| **monitor_login.py** | `python monitor_login.py` | Watch login flow in real-time |
| **check_profile_creation.py** | `python check_profile_creation.py` | Test profile auto-creation |
| **advanced_diagnostics.py** | `python advanced_diagnostics.py` | Deep system analysis |

---

## 📚 Documentation

| Document | Contains |
|----------|----------|
| **QUICK_START_RU.md** | 3-minute quick start (Russian) |
| **TOOLS_README.md** | Tool reference & troubleshooting |
| **FINAL_SUMMARY.md** | Complete fix explanation & setup |
| **DEBUGGING_GUIDE_RU.md** | Comprehensive debugging guide (Russian) |
| **TESTING_PROFILE_FIX.md** | Testing instructions |

---

## 🔄 Recommended Workflow

### First Time:
1. Read [QUICK_START_RU.md](QUICK_START_RU.md) (3 min)
2. Run `python verify_all.py` to check everything
3. Run `python diagnose.py` if there are issues

### When Testing Login:
1. Run `python monitor_login.py` (watch real-time logs)
2. Open browser: http://localhost:5176
3. Try login
4. Watch the logs in terminal

### If Errors:
1. Run `python diagnose.py` (quick diagnosis)
2. Read [DEBUGGING_GUIDE_RU.md](DEBUGGING_GUIDE_RU.md) (full guide)
3. Run `python advanced_diagnostics.py` (deep analysis)

---

## ✅ Success Indicators

You'll know the fix is working when:
- ✅ `python verify_all.py` shows all green ✅
- ✅ `python monitor_login.py` shows `✅ User created successfully`
- ✅ Browser shows profile without errors
- ✅ Supabase shows new user in `users` table

---

## 🔍 What Was Fixed

### The Problem:
New Stack Auth users couldn't log in because their profiles weren't automatically created.

### The Solution:
Modified `app/auth.py` to auto-create profiles for new users:
- Detects new Stack Auth users
- Extracts email & name from JWT token
- Creates profile in Supabase
- Returns created profile

### Enhanced With:
- **Detailed logging** - See every step with emoji indicators
- **Retry logic** - Handle edge cases gracefully
- **Diagnostic tools** - 6 tools to verify & debug
- **Complete docs** - Guides in Russian & English

---

## 🛠️ Tool Descriptions

### `start.py` - Interactive Menu
```bash
python start.py
```
User-friendly menu to:
- 1. Run full verification
- 2. Test profile creation
- 3. Monitor login in real-time
- 4. Run advanced diagnostics
- 5. Start backend server
- 6. View documentation

**Best for:** Everyone, especially first-time users

---

### `diagnose.py` - Emergency Helper
```bash
python diagnose.py
```
Quickly identifies what's wrong:
- Checks .env file
- Tests database connection
- Verifies auth configuration
- Shows exact next steps

**Best for:** When you see "Профиль не найден" error

---

### `verify_all.py` - Complete Verification
```bash
python verify_all.py
```
Validates entire system:
- File structure ✅
- Environment variables ✅
- Database connection ✅
- Auth module ✅
- API routes ✅

**Best for:** Initial setup & verification

---

### `monitor_login.py` - Real-Time Monitor
```bash
python monitor_login.py
```
Starts backend and monitors logs:
- Auto-starts server
- Highlights key events
- Shows emoji indicators
- Color-coded output

**Best for:** Watching login process step-by-step

**Setup:**
```
Terminal 1: python monitor_login.py
Terminal 2: http://localhost:5176 (try login)
Watch Terminal 1 for live logs
```

---

### `check_profile_creation.py` - Profile Test
```bash
python check_profile_creation.py
```
Tests the auto-create process:
- Supabase connection ✅
- Users table access ✅
- Create test user ✅
- Query created user ✅
- Cleanup ✅

**Best for:** Verifying profile creation works

---

### `advanced_diagnostics.py` - Deep Analysis  
```bash
python advanced_diagnostics.py
```
Simulates entire login flow:
- Database state analysis
- JWT payload simulation
- Auto-create process simulation
- Endpoint availability check

**Best for:** Detailed investigation of issues

---

## 📖 Documentation Guide

### For Beginners:
1. Start → [QUICK_START_RU.md](QUICK_START_RU.md)
2. Questions → [TOOLS_README.md](TOOLS_README.md)
3. Issues → [diagnose.py](diagnose.py)

### For Developers:
1. How-To → [FINAL_SUMMARY.md](FINAL_SUMMARY.md)
2. Details → [DEBUGGING_GUIDE_RU.md](DEBUGGING_GUIDE_RU.md)
3. Testing → [TESTING_PROFILE_FIX.md](TESTING_PROFILE_FIX.md)

### For Troubleshooting:
1. Quick check → `python diagnose.py`
2. Full guide → [DEBUGGING_GUIDE_RU.md](DEBUGGING_GUIDE_RU.md)
3. Advanced → `python advanced_diagnostics.py`

---

## 🎯 Common Tasks

### "I see 'Профіль не знайден' error"
```bash
python diagnose.py
```

### "I want to watch login happening"
```bash
# Terminal 1:
python monitor_login.py

# Terminal 2:
# Open http://localhost:5176 and login
```

### "I want to check if everything is set up correctly"
```bash
python verify_all.py
```

### "I want an interactive menu to choose"
```bash
python start.py
```

### "I need deep technical analysis"
```bash
python advanced_diagnostics.py
```

---

## 🔑 Expected Log Output

When everything works, you'll see:

```
🔐=== get_current_user() CALLED ===
🔑 Stack user_id from token: user_abc123
📊 Querying database for existing user...
👤 New user detected: user_abc123. Creating profile...
📝 Inserting user to database...
✅ User created successfully (DB ID: 42)
🔐=== get_current_user() FINISHED ===
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Database connection failed" | Check `SUPABASE_URL` in `.env` |
| "Missing Stack Auth" | Add `STACK_AUTH_JWKS_URL` to `.env` |
| "Insert returned empty" | Normal - system retries & succeeds |
| "Still getting error after fix" | Run `python diagnose.py` |

---

## 📊 File Structure

```
backend/
├── start.py                    ← Start here (menu)
├── diagnose.py                 ← Emergency help
├── verify_all.py              ← Full verification
├── monitor_login.py           ← Live logs
├── check_profile_creation.py  ← Profile test
├── advanced_diagnostics.py    ← Deep analysis
│
├── QUICK_START_RU.md          ← 3-min start
├── TOOLS_README.md            ← Tool reference
├── FINAL_SUMMARY.md           ← Complete guide
├── DEBUGGING_GUIDE_RU.md      ← Full debugging
├── TESTING_PROFILE_FIX.md     ← Testing
│
├── app/
│   ├── auth.py                ← [FIXED] Auto-create logic
│   └── ...
```

---

## ✨ Next Steps

1. **Right now:** `python start.py`
2. **Test login:** `http://localhost:5176`
3. **Watch it work:** See "✅ User created successfully" in logs
4. **Done!** No more profile errors

---

## 📞 Need Help?

1. Run `python diagnose.py` for instant diagnosis
2. Check logs with `python monitor_login.py`
3. Read [DEBUGGING_GUIDE_RU.md](DEBUGGING_GUIDE_RU.md) for detailed guide
4. Run `python verify_all.py` for system check

---

**Everything you need is here. Start with `python start.py`! 🚀**
