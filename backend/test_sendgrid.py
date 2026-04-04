import os
from pathlib import Path
from dotenv import load_dotenv
import httpx
import json

# Load env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv('SENDGRID_API_KEY')
from_email = os.getenv('SENDGRID_FROM_EMAIL')

print("=" * 60)
print("SendGrid Configuration Test")
print("=" * 60)
print(f"API Key present: {'✓ YES' if api_key else '✗ NO'}")
print(f"From Email: {from_email if from_email else '✗ NOT SET'}")
print()

if not api_key or not from_email:
    print("❌ Missing configuration!")
    exit(1)

# Test SendGrid API
print("Testing SendGrid API connection...")
test_data = {
    "personalizations": [{"to": [{"email": "test@example.com"}]}],
    "from": {"email": from_email},
    "subject": "Test Email from SuperGov",
    "content": [{"type": "text/html", "value": "<strong>Test email</strong>"}]
}

try:
    r = httpx.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=test_data,
        timeout=10
    )
    
    print(f"Response Status Code: {r.status_code}")
    
    if r.text:
        print(f"Response Body: {r.text}")
    
    print()
    if r.status_code in (200, 202):
        print("✓ SUCCESS: SendGrid API is working correctly!")
        print("  Test email would be sent successfully.")
    else:
        print(f"❌ ERROR: SendGrid returned status {r.status_code}")
        
        # Try to parse error
        try:
            error_data = r.json()
            if "errors" in error_data:
                for err in error_data["errors"]:
                    print(f"  Error: {err.get('message', 'Unknown')}")
        except:
            pass
        
        if r.status_code == 403:
            print("  → Likely cause: Sender email not verified in SendGrid")
            print(f"  → Fix: Verify {from_email} in SendGrid Verified Senders")
        elif r.status_code == 401:
            print("  → Likely cause: Invalid API key")
            print("  → Fix: Check SENDGRID_API_KEY in .env file")
            
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("  Check that you have internet connection")

print()
print("=" * 60)
