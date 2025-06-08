FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY src/backend /app/backend

# Set Python path to include the app directory
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create upload directory
RUN mkdir -p /uploads && chmod 777 /uploads

# Expose the port
EXPOSE 8000

# Run the application with health check endpoint
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 