import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_approval_email(request_id, ip_address, user_agent):
    """Sends an approval request email to Sahil"""
    sender_email = os.getenv("SENDER_EMAIL") # e.g., your-email@gmail.com
    sender_password = os.getenv("SENDER_PASSWORD") # Gmail App Password
    receiver_email = "jadhavssahil@gmail.com"
    
    # You'll need to update this BASE_URL based on your Render deployment
    base_url = "https://rag-portfolio-mvjo.onrender.com"
    approve_url = f"{base_url}/approve_resume/{request_id}"
    
    subject = "📄 Resume Download Request - Sahil's Digital Twin"
    
    body = f"""
    Hello Sahil,
    
    Someone is requesting to download your resume via the RAG Portfolio app.
    
    Requester Details:
    - IP Address: {ip_address}
    - User Agent: {user_agent}
    - Timestamp: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}
    
    If you want to allow this download, click the link below:
    {approve_url}
    
    Best regards,
    Your Digital Twin
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"📧 [Email] Approval request sent for {request_id}")
        return True
    except Exception as e:
        print(f"❌ [Email] Failed to send email: {e}")
        return False
