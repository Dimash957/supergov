"""
Full test: Register -> OTP -> Verify -> Create Complaint
"""
import httpx
import asyncio
import time

async def test():
    async with httpx.AsyncClient() as client:
        email = f'test-{int(time.time())}@example.com'
        
        # 1. Register
        print("1. Registering...")
        resp = await client.post(
            'http://localhost:8000/api/auth/register',
            json={
                'stack_user_id': 'user-' + str(int(time.time())),
                'iin': '123456789012',
                'email': email,
                'phone': '+7 777 777 7777',
                'full_name': 'Test User'
            }
        )
        print(f"   Status: {resp.status_code}")
        
        # 2. Send OTP
        print("\n2. Sending OTP...")
        resp = await client.post(
            'http://localhost:8000/api/auth/otp/send',
            json={'email': email}
        )
        print(f"   Status: {resp.status_code}")
        
        # 3. Verify OTP (use test code from logs: 947022)
        print("\n3. Verifying OTP with code 947022...")
        resp = await client.post(
            'http://localhost:8000/api/auth/otp/verify',
            json={'email': email, 'code': '947022'}
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"   Response: {resp.text}")
            return
        
        data = resp.json()
        token = data['data'].get('access_token') or data['data'].get('accessToken')
        print(f"   Token: {token[:50]}...")
        
        # 4. Create complaint with token
        print("\n4. Creating complaint...")
        resp = await client.post(
            'http://localhost:8000/api/complaints/',
            json={
                'category': 'Тестовая жалоба',
                'description': 'Тестовое описание проблемы',
                'lat': 51.1099,
                'lng': 71.4691
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text}")

asyncio.run(test())
