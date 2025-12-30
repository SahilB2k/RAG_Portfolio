from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS
from app.rag_answer import generate_answer_with_sources
from app.db import get_connection
import json
import uuid
import os
import threading
from app.config import get_config
from datetime import datetime, timedelta
import hashlib
from app.email_service import send_download_alert

config = get_config()
app = Flask(__name__)
# Enhanced CORS for production
CORS(app, resources={r"/*": {"origins": config.CORS_ORIGINS}})

def get_platform_from_ua(ua):
    if not ua: return "Unknown"
    ua = ua.lower()
    if "android" in ua: return "Android"
    if "iphone" in ua or "ipad" in ua: return "iOS"
    if "windows" in ua: return "Windows"
    if "macintosh" in ua: return "macOS"
    if "linux" in ua: return "Linux"
    return "Other"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "unhealthy" if not config.DATABASE_URL else "healthy", "env": config.APP_ENV}), 200

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    mode = data.get('mode', 'auto')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    def generate():
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
        print(f"🌍 [API] Request from IP: {user_ip} | Mode: {mode}")
        
        for chunk in generate_answer_with_sources(question, user_ip=user_ip, mode=mode):
            yield json.dumps(chunk) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

@app.route('/request_resume', methods=['POST'])
def request_resume():
    """Initiates the resume_access_control flow with rate limiting and neutral wording"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
    hashed_ip = hashlib.sha256(user_ip.encode()).hexdigest()
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Rate Limiting: Max 3 requests per IP per hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cur.execute(
            "SELECT count(*) FROM resume_requests WHERE hashed_ip = %s AND created_at > %s",
            (hashed_ip, one_hour_ago)
        )
        request_count = cur.fetchone()[0]
        
        if request_count >= 3:
            cur.close()
            conn.close()
            return jsonify({
                "error": "Rate limit exceeded. Please try again later.",
                "message": "To ensure system availability, requests are limited. Please wait an hour."
            }), 429

        # 2. Generate Access Request
        user_agent = request.headers.get('User-Agent', 'Unknown')
        platform = get_platform_from_ua(user_agent)
        country = request.headers.get('CF-IPCountry', 'Unknown')
        
        token = str(uuid.uuid4())
        # Updated Expiry: 24 hours
        expires_at = datetime.now() + timedelta(hours=24)
        
        cur.execute(
            """INSERT INTO resume_requests 
               (email, token, status, expires_at, hashed_ip, user_agent, platform, country) 
               VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s)""",
            (email, token, expires_at, hashed_ip, user_agent, platform, country)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Notify owner in background
        thread = threading.Thread(
            target=send_download_alert, 
            args=(email, token)
        )
        thread.start()
        
        return jsonify({
            "status": "success",
            "token": token, # Provided for polling
            "message": "Your request is being processed. Resume access will be enabled shortly. This helps ensure availability and prevent misuse."
        }), 200
    except Exception as e:
        print(f"❌ [Access Control] Error: {e}")
        return jsonify({"error": "Internal system error. Please try again later."}), 500

@app.route('/check_access_status/<token>', methods=['GET'])
def check_access_status(token):
    """Internal: Part of access_gate. App polls this to see if owner enabled access."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM resume_requests WHERE token = %s", (token,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return jsonify({"status": "not_found"}), 404
            
        return jsonify({"status": result[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gate_control/<token>', methods=['GET'])
def gate_control(token):
    """Internal: Secret endpoint for owner to enable resume access."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, email FROM resume_requests WHERE token = %s", (token,))
        result = cur.fetchone()
        
        if not result:
            return "<h1>❌ Invalid Request</h1>", 404
            
        status, email = result
        if status == 'approved':
            return f"<h1>✅ Already Enabled</h1><p>Access for {email} is already active.</p>"
            
        cur.execute("UPDATE resume_requests SET status = 'approved' WHERE token = %s", (token,))
        conn.commit()
        cur.close()
        conn.close()
        
        return f"<h1>✅ Access Enabled</h1><p>Resume access for <b>{email}</b> has been unlocked in-app.</p>"
    except Exception as e:
        return f"<h1>❌ Error</h1><p>{str(e)}</p>", 500

@app.route('/download_resume', methods=['GET'])
def download_resume():
    """Validates if access_gate is cleared and serves the file (Single Use)"""
    token = request.args.get('token')
    
    if not token:
        return "<h1>❌ Access Denied</h1><p>Request access via the app first.</p>", 403
        
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT status, expires_at FROM resume_requests WHERE token = %s", 
            (token,)
        )
        result = cur.fetchone()
        
        if not result:
            return "<h1>❌ Link Invalid</h1>", 404
            
        status, expires_at = result
        
        if status == 'pending':
            return "<h1>⏳ Access Pending</h1><p>Your request is still being processed.</p>", 403
            
        if status == 'used':
            return "<h1>❌ Link Expired</h1><p>This single-use access has already been consumed.</p>", 403
            
        if datetime.now() > expires_at:
            return "<h1>❌ Request Timed Out</h1><p>Please initiate a new request (24h limit).</p>", 403
            
        if status != 'approved':
            return "<h1>❌ Access Restricted</h1>", 403

        # Success! Mark as used and serve
        cur.execute("UPDATE resume_requests SET status = 'used' WHERE token = %s", (token,))
        conn.commit()
        cur.close()
        conn.close()
        
        resume_dir = os.path.join(app.root_path, '..', 'data')
        filename = 'resume.pdf' if os.path.exists(os.path.join(resume_dir, 'resume.pdf')) else 'resume.md'
        
        return send_from_directory(resume_dir, filename, as_attachment=True)
        
    except Exception as e:
        print(f"❌ [API] Download Error: {e}")
        return f"<h1>❌ System Error</h1><p>{str(e)}</p>", 500

@app.route('/ask_sync', methods=['POST'])
def ask_sync():
    """Non-streaming endpoint for simpler mobile integration if needed"""
    data = request.json
    question = data.get('question')
    mode = data.get('mode', 'auto')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    full_answer = ""
    metadata = None
    
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
    
    for chunk in generate_answer_with_sources(question, user_ip=user_ip, mode=mode):
        if chunk.get("answer_chunk"):
            full_answer += chunk["answer_chunk"]
        if chunk.get("metadata"):
            metadata = chunk["metadata"]
            
    return jsonify({
        "answer": full_answer,
        "metadata": metadata
    })


@app.route('/log_download', methods=['POST'])
def log_download():
    """Logs a resume download event with secret tracking data"""
    data = request.json
    email = data.get('email', 'Anonymous')
    purpose = data.get('purpose', 'Quick Download')
    source_ref = data.get('source_ref', 'Direct/Organic')
    
    # Capture Digital Fingerprint
    user_agent = request.headers.get('User-Agent', 'Unknown')
    platform = get_platform_from_ua(user_agent)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    try:
        from app.db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        
        # Make sure you added these columns to your resume_requests or a new table
        # If using your existing resume_requests table:
        cur.execute(
            """INSERT INTO resume_requests 
               (email, status, hashed_ip, user_agent, platform, token) 
               VALUES (%s, 'downloaded', %s, %s, %s, %s)""",
            (email, hashlib.sha256(user_ip.encode()).hexdigest(), user_agent, platform, f"REF:{source_ref}")
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Optional: Trigger the notification alert
        # from app.email_service import send_download_alert
        # send_download_alert(email, purpose, f"Source: {source_ref}\nPlatform: {platform}")
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"❌ [API] Log Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so mobile device can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
