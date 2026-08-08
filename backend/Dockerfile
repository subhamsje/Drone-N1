# Sovereign Cognitive Kernel & FastAPI Gateway Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for aerospace math & networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir mavsdk ecdsa

COPY . .

ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

EXPOSE 8080

CMD ["python", "backend/run.py"]
