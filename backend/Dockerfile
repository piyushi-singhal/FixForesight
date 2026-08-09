# FixForesight Backend Dockerfile
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and supporting pipeline codebases
COPY backend/ /app/backend/
COPY src/ /app/src/
COPY models/ /app/models/
COPY config.ini /app/

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
