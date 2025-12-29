import requests
import os
import json

def send_resume_link_email(receiver_email, token):
    """Sends a time-limited download link directly using Resend HTTP API"""
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL") # e.g., "onboarding@resend.dev" or your verified domain
    
    if not api_key:
        print("❌ [Email] Error: RESEND_API_KEY not found in environment.")
        return False

    base_url = "https://rag-portfolio-mvjo.onrender.com"
    download_url = f"{base_url}/download_resume?token={token}"
    
    subject = "📄 Resume Download Link - Sahil Jadhav"
    
    body = f"""
    Hello,
    
    Thank you for your interest in Sahil Jadhav's profile! 
    
    You can download his resume using the secure link below. 
    Note: This link is valid for one-time use and will expire in 10 minutes.
    
    Download Link:
    {download_url}
    
    Best regards,
    Sahil Jadhav's Digital Assistant
    """
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"Sahil's Assistant <{sender_email}>",
                "to": [receiver_email],
                "subject": subject,
                "text": body,
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"📧 [Email] Download link sent to {receiver_email} via Resend")
            return True
        else:
            print(f"❌ [Email] Resend API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [Email] HTTP Request failed: {e}")
        return False
