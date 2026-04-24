import os
import resend


def send_newsletter(html_content, subject, recipient=None):
    resend.api_key = os.getenv("RESEND_API_KEY")
    recipient = recipient or os.getenv("RECIPIENT_EMAIL", "liandrodacruz@outlook.pt")
    sender = os.getenv("SENDER_EMAIL", "Market Newsletter <onboarding@resend.dev>")

    params = {
        "from": sender,
        "to": [recipient],
        "subject": subject,
        "html": html_content,
    }

    response = resend.Emails.send(params)
    return response
