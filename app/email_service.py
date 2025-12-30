import requests
import os

def send_download_alert(requester_email, purpose, note):
    """Sends a notification to Sahil when someone downloads the resume"""
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL") # Your email

    if not api_key or not sender_email:
        print("❌ [Email] Missing configuration")
        return False

    subject = f"🚀 New Resume Download: {purpose}"
    body = f"""
    Hello Sahil,
    
    Someone just downloaded your resume from your AI Portfolio!
    
    Details:
    - Email: {requester_email}
    - Purpose: {purpose}
    - Message: {note if note else "No message provided."}
    
    Time: {os.popen('date').read()}
    """

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": "Portfolio Alert <onboarding@resend.dev>",
                "to": [sender_email],
                "subject": subject,
                "text": body,
            },
            timeout=10
        )
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ [Email] Failed to send alert: {e}")
        return False