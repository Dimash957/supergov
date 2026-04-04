import os
import httpx


class NotificationService:

    @staticmethod
    def send_telegram(chat_id: str, message: str):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("Telegram skipping: no token")
            return
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        httpx.post(url, json={"chat_id": chat_id, "text": message}, timeout=15.0)

    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str) -> bool:
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@supergov.local")
        if not api_key:
            print("SendGrid skipping: no SENDGRID_API_KEY")
            return False
        try:
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
            return r.status_code in (200, 202)
        except Exception as e:
            print(f"SendGrid error: {e}")
            return False

    @staticmethod
    def send_sms(to_phone: str, message: str):
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        _from = os.getenv("TWILIO_FROM_NUMBER")
        if not sid or not token or not _from:
            print("Twilio skipping: missing creds")
            return
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = {"To": to_phone, "From": _from, "Body": message}
        httpx.post(url, data=data, auth=(sid, token), timeout=20.0)
