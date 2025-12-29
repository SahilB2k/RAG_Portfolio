import requests
import os
import json

# def send_gate_notification(requester_email, token):
#     """
#     Part of 'resume_access_control' system (Internal Naming).
#     Sends a system-level notification to the owner to trigger the access gate.
#     """
#     api_key = os.getenv("RESEND_API_KEY")
#     sender_email = os.getenv("SENDER_EMAIL") # This is also the receiver (the owner)
    
#     if not api_key:
#         print("❌ [Access Gate] Error: RESEND_API_KEY missing.")
#         return False
    
#     if not sender_email:
#         print("❌ [Access Gate] Error: SENDER_EMAIL missing.")
#         return False

#     base_url = "https://rag-portfolio-mvjo.onrender.com"
#     # Internal naming: gate_control
#     control_url = f"{base_url}/gate_control/{token}"
    
#     subject = f"[System] Resume Access Request: {requester_email}"
    
#     body = f"""
#     A new resume access request has been initiated.
    
#     Requester: {requester_email}
    
#     To enable access for this user, please clear the gate by clicking below:
#     {control_url}
    
#     Note: This link is single-use and valid for 24 hours. 
#     If you do not recognize this request, no action is required.
#     """
    
#     try:
#         # Resend HTTP API
#         # Simple Display Name following 422 fix
#         from_field = f"Access Control <{sender_email}>"
        
#         response = requests.post(
#             "https://api.resend.com/emails",
#             headers={
#                 "Authorization": f"Bearer {api_key}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "from": from_field,
#                 "to": [sender_email], # Sent to the owner
#                 "subject": subject,
#                 "text": body,
#             },
#             timeout=10
#         )
        
#         if response.status_code in [200, 201]:
#             print(f"📧 [Access Gate] Notification sent to owner for {requester_email}")
#             return True
#         else:
#             print(f"❌ [Access Gate] Resend API Error: {response.status_code} - {response.text}")
#             return False
            
#     except Exception as e:
#         print(f"❌ [Access Gate] Notification failed: {e}")
#         return False


def send_gate_notification(requester_email, token):
    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")  # receiver only

    if not api_key or not sender_email:
        print("❌ Missing email configuration")
        return False

    base_url = "https://rag-portfolio-mvjo.onrender.com"
    control_url = f"{base_url}/gate_control/{token}"

    subject = f"[System] Resume Access Request"
    body = f"""
A new resume access request has been initiated.

Requester: {requester_email}

To enable access, click below:
{control_url}

This link is single-use.
"""

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": "Access Control <onboarding@resend.dev>",
                "to": [sender_email],
                "subject": subject,
                "text": body,
            },
            timeout=10
        )

        print("📨 Resend response:", response.status_code, response.text)

        return response.status_code in [200, 201]

    except Exception as e:
        print("❌ Email failed:", e)
        return False
