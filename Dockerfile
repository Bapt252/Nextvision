# 🐍 Python 3.11 Slim Base Image
FROM python:3.11-slim

# 🏷️ Metadata
LABEL maintainer="NEXTEN Team <dev@nexten.fr>"
LABEL description="Nextvision - Algorithme de matching IA adaptatif"
LABEL version="1.0.0"

# 🔧 Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# 📦 System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 📁 Set working directory
WORKDIR /app

# 📋 Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 📂 Copy application code
COPY . .

# 🚀 Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 🌐 Expose port
EXPOSE 8000

# 🚀 Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
