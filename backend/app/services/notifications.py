import os
import re
import json

import httpx


class NotificationService:

    @staticmethod
    def send_telegram(chat_id: str, message: str):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("Telegram skipping: no token")
            return
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            httpx.post(url, json={"chat_id": chat_id, "text": message}, timeout=15.0)
        except Exception as e:
            print(f"Telegram error: {e}")

    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str) -> bool:
        api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "").strip()
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if not api_key:
            print("❌ SendGrid skipping: SENDGRID_API_KEY not set in .env")
            if demo_mode:
                print(f"  [DEMO] Would send email to {to_email}: {subject}")
            return False
        
        if not from_email:
            print("❌ SendGrid skipping: SENDGRID_FROM_EMAIL not set in .env")
            return False
        
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", from_email):
            print(f"❌ SendGrid error: Invalid from_email format: {from_email}")
            return False
        
        try:
            print(f"📧 Sending email to {to_email} from {from_email}...")
            r = httpx.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": from_email},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_body}],
                },
                timeout=20.0,
            )
            
            print(f"   SendGrid Response Status: {r.status_code}")
            
            if r.status_code in (200, 202):
                print(f"✓ Email sent successfully to {to_email}")
                return True
            else:
                print(f"   Response Body: {r.text}")
                try:
                    error_data = r.json()
                    if "errors" in error_data and error_data["errors"]:
                        error_msg = error_data["errors"][0].get("message", "Unknown error")
                    else:
                        error_msg = json.dumps(error_data, ensure_ascii=False)
                except:
                    error_msg = r.text
                
                print(f"❌ SendGrid error ({r.status_code}): {error_msg}")
                
                # Parse common errors
                if r.status_code == 401:
                    print("   → FIX: Invalid or expired API key")
                    print("   → Check SENDGRID_API_KEY in .env")
                elif r.status_code == 403:
                    print("   → FIX: Forbidden (sender not verified or no permission)")
                    print(f"   → Verify {from_email} in SendGrid: Verified Senders")
                elif r.status_code == 400:
                    print("   → FIX: Bad request format - check email addresses")
                elif "not verified" in error_msg.lower():
                    print(f"   → FIX: {from_email} is not verified in SendGrid")
                    print("   → Go to SendGrid Dashboard → Verified Senders → Add and verify email")
                
                return False
        except httpx.ConnectError as e:
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
            return False

    @staticmethod
    def send_sms(to_phone: str, message: str):
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        raw_from = os.getenv("TWILIO_FROM_NUMBER") or ""
        # Twilio E.164: без пробелов, например +16415353660
        _from = re.sub(r"\s+", "", raw_from.strip())
        if not sid or not token or not _from:
            print("Twilio skipping: missing creds")
            return
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = {"To": to_phone, "From": _from, "Body": message}
        httpx.post(url, data=data, auth=(sid, token), timeout=20.0)
