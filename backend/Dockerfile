FROM python:3.10-slim as builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
ENV PATH=/usr/local/bin:$PATH
RUN useradd -m appuser && chown -R appuser /app && chmod -R 755 /usr/local
USER appuser

# Removed uvicorn CMD since we're using gunicorn via docker-compose