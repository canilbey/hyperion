# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version first (avoid CUDA dependencies)
RUN pip install --no-cache-dir --user \
    torch==2.7.1+cpu \
    torchvision==0.22.1+cpu \
    torchaudio==2.7.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install other Python dependencies
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy the backend code
COPY src/backend /app/backend

# Set Python path to include the app directory and user packages
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Create upload directory
RUN mkdir -p /uploads && chmod 777 /uploads

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with health check endpoint
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 