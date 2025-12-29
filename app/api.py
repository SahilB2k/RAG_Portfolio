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
from app.email_service import send_resume_link_email

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
    """Generates a secure token and emails a download link"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Secure passive tracking
    hashed_ip = hashlib.sha256(user_ip.encode()).hexdigest()
    platform = get_platform_from_ua(user_agent)
    country = request.headers.get('CF-IPCountry', 'Unknown') # Works if behind Cloudflare/Render
    
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=10)
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO resume_requests 
               (email, token, status, expires_at, hashed_ip, user_agent, platform, country) 
               VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s)""",
            (email, token, expires_at, hashed_ip, user_agent, platform, country)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Send email in background
        thread = threading.Thread(
            target=send_resume_link_email, 
            args=(email, token)
        )
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "A secure download link has been sent to your email."
        }), 200
    except Exception as e:
        print(f"❌ [API] Error in request_resume: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_resume', methods=['GET'])
def download_resume():
    """Validates token and serves the resume file"""
    token = request.args.get('token')
    
    if not token:
        return "<h1>❌ Missing Token</h1><p>Please use the link sent to your email.</p>", 400
        
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Check token existence, expiry, and status
        cur.execute(
            "SELECT status, expires_at FROM resume_requests WHERE token = %s", 
            (token,)
        )
        result = cur.fetchone()
        
        if not result:
            return "<h1>❌ Invalid Link</h1><p>The link is invalid or does not exist.</p>", 404
            
        status, expires_at = result
        
        if status == 'used':
            return "<h1>❌ Link Already Used</h1><p>This download link has already been used.</p>", 403
            
        if datetime.now() > expires_at:
            cur.execute("UPDATE resume_requests SET status = 'expired' WHERE token = %s", (token,))
            conn.commit()
            return "<h1>❌ Link Expired</h1><p>This link was only valid for 10 minutes.</p>", 403
            
        # Success! Mark as used and serve file
        cur.execute("UPDATE resume_requests SET status = 'used' WHERE token = %s", (token,))
        conn.commit()
        cur.close()
        conn.close()
        
        resume_dir = os.path.join(app.root_path, '..', 'data')
        filename = 'resume.md'
        if os.path.exists(os.path.join(resume_dir, 'resume.pdf')):
            filename = 'resume.pdf'
        
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

if __name__ == '__main__':
    # Listen on all interfaces so mobile device can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
