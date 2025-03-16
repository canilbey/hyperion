# Local Development Setup

## Prerequisites
- Docker 20.10+
- Docker Compose 2.20+
- Python 3.10+

## Installation Steps

1. Clone repository:
```bash
git clone https://github.com/yourorg/hyperion.git
cd hyperion
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start services:
```bash
docker-compose up -d --build
```

4. Verify containers:
```bash
docker-compose ps
```

## Key Services:
- API: http://localhost:8000
- Frontend: http://localhost:3003
- Milvus: localhost:19530
- Redis: localhost:6379