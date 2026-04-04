"""
Test OTP sending through the API
"""
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "zhunisbek.dinmukhamed@mail.ru"

async def test_otp_send():
    """Test OTP code sending """
    async with httpx.AsyncClient() as client:
        # First check if user exists by trying to get OTP
        print(f"🧪 Testing OTP Send to: {TEST_EMAIL}")
        print("-" * 60)
        
        payload = {"email": TEST_EMAIL}
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/otp/send",
                json=payload,
                timeout=30.0
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ SUCCESS: {data.get('data', {}).get('message', 'OTP sent')}")
                print(f"   Check your email at: {TEST_EMAIL}")
            elif response.status_code == 404:
                print(f"\n⚠ User not found: {TEST_EMAIL}")
                print("   Register first or check email address")
            else:
                print(f"\n❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Details: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
            print("\nMake sure backend server is running:")
            print("  cd backend && python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_otp_send())
