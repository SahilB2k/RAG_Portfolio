# Production Dockerfile for Resume RAG API
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn gevent

# Copy application code
COPY . .

# Expose the API port
EXPOSE 5000

# Run with Gunicorn using gevent workers for streaming support
CMD gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5 app.api:app
