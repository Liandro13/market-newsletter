import os
import resend
from pathlib import Path


def load_subscribers() -> list[str]:
    subscribers_file = Path(__file__).parent.parent / "subscribers.txt"
    with open(subscribers_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def send_newsletter(html_content, subject):
    resend.api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("SENDER_EMAIL", "Market Newsletter <onboarding@resend.dev>")
    subscribers = load_subscribers()

    params = {
        "from": sender,
        "to": subscribers,
        "subject": subject,
        "html": html_content,
    }

    response = resend.Emails.send(params)
    print(f"Email enviado para {len(subscribers)} subscriber(s)!")
    return response
