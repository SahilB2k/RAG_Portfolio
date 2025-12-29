import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_resume_link_email(receiver_email, token):
    """Sends a time-limited download link directly to the recruiter"""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    # Direct link for the browser
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
    
    msg = MIMEMultipart()
    msg['From'] = f"Sahil's Assistant <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"📧 [Email] Download link sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"❌ [Email] Failed to send link: {e}")
        return False
