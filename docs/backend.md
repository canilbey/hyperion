# Backend Documentation

## Overview
The backend of **Hyperion** is built using **FastAPI** and is designed to be modular, scalable, and efficient. It handles document ingestion, model training, query processing, and real-time communication with LLM endpoints. The backend also integrates **RabbitMQ** for real-time messaging and **Kafka** for high-throughput event streaming and logging.

## Backend Framework
- **Framework**: FastAPI  
- **Why FastAPI?**:  
  - High performance for handling real-time requests.  
  - Built-in support for asynchronous programming.  
  - Automatic API documentation with Swagger/OpenAPI.  

## Database
- **Vector Database**: Milvus  
  - Stores vector embeddings for efficient semantic search.  
- **Caching**: Redis  
  - Used for caching frequently accessed data (e.g., query results, model configurations).  
- **Relational Database**: PostgreSQL  
  - Stores user data, model configurations, and monitoring/analytics data.  

## Authentication
- **Methods**:  
  - Email/password login.  
  - Optional Google Auth (OAuth).  
- **Security**:  
  - JWT-based authentication for secure API access.  
  - Role-based access control (RBAC) for admin vs. regular users.  

## API Design
- **Type**: RESTful APIs  
- **Key Endpoints**:  
  - **User Management**:  
    - `POST /api/auth/signup`: User registration.  
    - `POST /api/auth/login`: User login.  
    - `GET /api/auth/me`: Fetch user details.  
  - **Document Upload**:  
    - `POST /api/upload`: Upload PDFs or text files.  
  - **Model Training**:  
    - `POST /api/model/train`: Train a new RAG model.  
    - `GET /api/model/list`: List all trained models.  
  - **Query Execution**:  
    - `POST /api/query`: Submit a query to a trained model.  
  - **Monitoring & Logging**:  
    - `GET /api/logs`: Fetch logs and performance metrics.  

## Third-Party Integrations
- **RabbitMQ**:  
  - Handles real-time messaging for LLM requests and responses.  
  - Ensures low-latency communication between the frontend, backend, and LLM endpoints.  
- **Kafka**:  
  - Manages high-throughput event streaming for RAG training processes.  
  - Logs user actions, training data, and system metrics for real-time analytics.  
- **Other Integrations**:  
  - **Sentry**: Real-time error tracking and performance monitoring.  
  - **Winston**: Server-side logging.  
  - **Prometheus**: Application performance monitoring.  
  - **Swagger**: API documentation.  

## Messaging & Event Streaming
### RabbitMQ
- **Use Case**: Real-time LLM request/response handling.  
- **Workflow**:  
  1. Frontend sends a query to the backend.  
  2. Backend publishes the query to a RabbitMQ queue.  
  3. LLM endpoint consumes the query, processes it, and publishes the response back to the queue.  
  4. Backend receives the response and sends it to the frontend.  

### Kafka
- **Use Case**: High-throughput event streaming for RAG training and logging.  
- **Workflow**:  
  1. Training data is ingested and preprocessed.  
  2. Events (e.g., document upload, model training) are published to Kafka topics.  
  3. Kafka consumers process these events for logging, analytics, and monitoring.  

## Security
- **Data Encryption**:  
  - Sensitive data (e.g., API keys, user credentials) is encrypted at rest and in transit.  
- **Input Validation**:  
  - User inputs are sanitized to prevent SQL injection and XSS attacks.  
- **Rate Limiting**:  
  - Not implemented initially but can be added if needed.  

## Performance Optimization
- **Caching**: Redis is used to cache frequently accessed data.  
- **Asynchronous Processing**: FastAPI’s async capabilities ensure low-latency responses.  
- **Horizontal Scaling**: Designed to scale using Kubernetes and load balancers.  

---

*This document outlines the backend architecture and components for Hyperion. Feedback is welcome before proceeding to the next document.*