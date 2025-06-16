FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları (OpenCV ve unstructured için GL/X11 kütüphaneleri dahil)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1-mesa \
    libglvnd0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libsm6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# PyTorch ve diğer ana bağımlılıklar
RUN pip install --no-cache-dir \
    torch==2.7.1+cpu \
    torchvision==0.22.1+cpu \
    torchaudio==2.7.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Diğer Python bağımlılıkları
COPY src/backend/requirements.txt ./
# Sadece headless OpenCV kullan
RUN pip uninstall -y opencv-python || true
RUN pip install --no-cache-dir opencv-python-headless
RUN pip install --no-cache-dir -r requirements.txt

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