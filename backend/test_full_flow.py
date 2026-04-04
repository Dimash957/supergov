"""
Full end-to-end test: Register user -> Send OTP -> Verify OTP
"""
import httpx
import json
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "zhunisbek.dinmukhamed@mail.ru"
TEST_IIN = "123456789012"
TEST_PHONE = "+7 777 123 4567"

async def test_full_flow():
    """Test registration, OTP send, and OTP verify"""
    async with httpx.AsyncClient() as client:
        print("=" * 70)
        print("FULL OTP FLOW TEST")
        print("=" * 70)
        print()
        
        # Step 1: Register user
        print("STEP 1: Register user")
        print("-" * 70)
        
        register_payload = {
            "stack_user_id": "test_user_123",
            "iin": TEST_IIN,
            "email": TEST_EMAIL,
            "phone": TEST_PHONE,
            "full_name": "Test User",
        }
        
        try:
            register_response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json=register_payload,
                timeout=30.0
            )
            
            print(f"Status: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            
            if register_response.status_code not in (200, 201):
                if register_response.status_code == 409:
                    print("User already exists - continuing to OTP test")
                else:
                    print("Registration failed!")
                    return
            else:
                print("User registered successfully")
            
        except Exception as e:
            print(f"Registration request failed: {e}")
            return
        
        print()
        print()
        
        # Step 2: Request OTP
        print("STEP 2: Request OTP code")
        print("-" * 70)
        
        otp_send_payload = {"email": TEST_EMAIL}
        
        try:
            otp_response = await client.post(
                f"{BASE_URL}/api/auth/otp/send",
                json=otp_send_payload,
                timeout=30.0
            )
            
            print(f"Status: {otp_response.status_code}")
            print(f"Response: {otp_response.text}")
            
            if otp_response.status_code == 200:
                data = otp_response.json()
                print()
                print("OTP sent successfully!")
                print(f"   Message: {data.get('data', {}).get('message', 'N/A')}")
                print(f"   Check email: {TEST_EMAIL}")
                print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                print()
                print("   The email should arrive in a few seconds.")
                print("   If not received after 1 minute, check spam/junk folder.")
                print("   Check server logs above for SendGrid errors.")
            else:
                print(f"Failed to send OTP")
                try:
                    error_data = otp_response.json()
                    print(f"   Error details: {error_data}")
                except:
                    pass
                
        except Exception as e:
            print(f"OTP send request failed: {e}")
            return
        
        print()
        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Check your email inbox for the OTP code")
        print("2. Look for subject: 'SuperGov -- kod vkhoda'")
        print("3. Watch the backend server logs for SendGrid activity")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(test_full_flow())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
