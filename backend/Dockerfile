# Backend Dockerfile to run the FastAPI app
FROM python:3.11-slim

# Install OS deps for build (if any)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app source
COPY backend /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
