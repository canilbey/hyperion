FROM python:3.11-slim

WORKDIR /app

# Extraction için gerekli sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    poppler-utils \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Gereksiz tekrar kurulumları önlemek için önce requirements.txt'yi kopyala ve yükle
COPY src/backend/requirements.txt ./
RUN pip install -r requirements.txt

# NLTK averaged_perceptron_tagger_eng modelini indir
RUN python -m nltk.downloader averaged_perceptron_tagger_eng

# Backend kodunu kopyala
COPY src/backend /app/backend

# Ortam değişkenleri ve PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/usr/local/bin:$PATH

# Upload klasörü
RUN mkdir -p /uploads && chmod 777 /uploads

# Port ve healthcheck
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Uygulamayı başlat
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--limit-max-requests", "1000", "--timeout-keep-alive", "30"] 