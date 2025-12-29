from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS
from app.rag_answer import generate_answer_with_sources
from app.db import get_connection
from app.email_service import send_approval_email
import json
import uuid
import os

from app.config import get_config

config = get_config()
app = Flask(__name__)
# Enhanced CORS for production
CORS(app, resources={r"/*": {"origins": config.CORS_ORIGINS}})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "unhealthy" if not config.DATABASE_URL else "healthy", "env": config.APP_ENV}), 200

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    def generate():
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
        print(f"🌍 [API] Request from IP: {user_ip}")
        
        for chunk in generate_answer_with_sources(question, user_ip=user_ip):
            yield json.dumps(chunk) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

@app.route('/request_resume', methods=['POST'])
def request_resume():
    """Starts the approval flow for resume download"""
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    request_id = str(uuid.uuid4())
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO resume_requests (id, ip_address, user_agent, status) VALUES (%s, %s, %s, 'pending')",
            (request_id, user_ip, user_agent)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Send email to Sahil
        email_sent = send_approval_email(request_id, user_ip, user_agent)
        
        return jsonify({
            "status": "success",
            "request_id": request_id,
            "message": "Approval request sent to Sahil.",
            "email_sent": email_sent
        }), 200
    except Exception as e:
        print(f"❌ [API] Error in request_resume: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/check_request/<request_id>', methods=['GET'])
def check_request(request_id):
    """Checks the status of a specific request"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM resume_requests WHERE id = %s", (request_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return jsonify({"status": result[0]}), 200
        return jsonify({"error": "Request not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/approve_resume/<request_id>', methods=['GET'])
def approve_resume(request_id):
    """Sahil clicks this link to approve the request"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE resume_requests SET status = 'approved' WHERE id = %s",
            (request_id,)
        )
        conn.commit()
        cur.close()
        conn.close()
        return "<h1>✅ Request Approved!</h1><p>The user can now download the resume in the app.</p>", 200
    except Exception as e:
        return f"<h1>❌ Error</h1><p>{str(e)}</p>", 500

@app.route('/download_resume/<request_id>', methods=['GET'])
def download_resume(request_id):
    """Downloads the resume if approved"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM resume_requests WHERE id = %s", (request_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result and result[0] == 'approved':
            # Check for resume.pdf in data folder or use resume.md
            resume_dir = os.path.join(app.root_path, '..', 'data')
            filename = 'resume.md' # Default fallback
            if os.path.exists(os.path.join(resume_dir, 'resume.pdf')):
                filename = 'resume.pdf'
            
            return send_from_directory(resume_dir, filename, as_attachment=True)
        
        return jsonify({"error": "Unauthorized or pending approval"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_sync', methods=['POST'])
def ask_sync():
    """Non-streaming endpoint for simpler mobile integration if needed"""
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400

    full_answer = ""
    metadata = None
    
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in user_ip: user_ip = user_ip.split(',')[0].strip()
    
    for chunk in generate_answer_with_sources(question, user_ip=user_ip):
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
