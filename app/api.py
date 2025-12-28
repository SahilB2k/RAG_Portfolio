from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from app.rag_answer import generate_answer_with_sources
import json

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
