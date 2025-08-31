FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/health || exit 1

# Start command
CMD cd backend && python -m uvicorn server:app --host 0.0.0.0 --port $PORT