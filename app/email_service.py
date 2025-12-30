import requests
import os
from datetime import datetime

def send_download_alert(requester_email, purpose, note):
    """Sends a notification to Sahil when someone downloads the resume"""
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL") # Your personal email where you want the alert

    if not api_key or not sender_email:
        print("❌ [Email] Missing configuration: Check RESEND_API_KEY and SENDER_EMAIL env vars")
        return False

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"🚀 New Resume Download: {purpose}"
    
    body = f"""
    Hello Sahil,
    
    Someone just downloaded your resume from your AI Portfolio!
    
    Details:
    - Email: {requester_email}
    - Purpose: {purpose}
    - Message: {note if note else "No message provided."}
    
    Time: {current_time}
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
        
        if response.status_code in [200, 201]:
            print(f"📧 [Email] Success: Alert sent to {sender_email}")
            return True
        else:
            print(f"❌ [Email] Resend Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [Email] Failed to send alert: {e}")
        return False