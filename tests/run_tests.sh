#!/bin/bash

set -e  # Exit on error

# Start only required services for backend tests
echo "Starting backend test environment..."
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d backend redis db

# Wait for services to be ready
echo "Waiting for services to start..."
while ! docker-compose exec backend curl -s http://localhost:8000/health >/dev/null; do
  sleep 1
done

# Run migrations
echo "Running migrations..."
docker-compose exec backend python migrations/run_migrations.py

# Run tests with coverage
echo "Running tests..."
docker-compose exec backend pytest \
  tests/test_redis_connection.py \
  tests/test_redis_integration.py \
  tests/test_backend_integration.py \
  -v \
  --cov=src/backend \
  --cov-report=term-missing

# Stop containers when done
echo "Tests complete, stopping containers..."
docker-compose down