# Third-Party Libraries Documentation

## Overview
The **Hyperion** application leverages several third-party libraries to enhance functionality, improve performance, and simplify development. This document lists and describes these libraries, including their purpose, compatibility, and integration details.

---

## Frontend Libraries

### 1. **React**
- **Purpose**: A JavaScript library for building user interfaces.  
- **Version**: 18.x  
- **Integration**: Used as the core framework for the frontend.  

### 2. **Material-UI (MUI)**
- **Purpose**: A React UI framework with pre-built components and styling.  
- **Version**: 5.x  
- **Integration**: Used for building the app’s UI (e.g., buttons, forms, modals).  

### 3. **Redux**
- **Purpose**: A state management library for managing global state.  
- **Version**: 4.x  
- **Integration**: Used for managing app-wide state (e.g., user authentication, selected model).  

### 4. **React Query**
- **Purpose**: A library for managing server state and caching API responses.  
- **Version**: 3.x  
- **Integration**: Used for fetching and caching data from the backend.  

### 5. **Cypress**
- **Purpose**: A testing framework for end-to-end testing.  
- **Version**: 10.x  
- **Integration**: Used for testing user workflows (e.g., sign up, upload documents, chat).  

---

## Backend Libraries

### 1. **FastAPI**
- **Purpose**: A modern, fast (high-performance) web framework for building APIs with Python.  
- **Version**: 0.85.x  
- **Integration**: Used as the core framework for the backend.  

### 2. **PyTest**
- **Purpose**: A testing framework for writing unit and integration tests.  
- **Version**: 7.x  
- **Integration**: Used for testing backend functionality (e.g., API endpoints, database queries).  

### 3. **Milvus**
- **Purpose**: A vector database for storing and querying embeddings.  
- **Version**: 2.x  
- **Integration**: Used for storing vector embeddings and enabling semantic search.  

### 4. **Redis**
- **Purpose**: An in-memory data store for caching and message brokering.  
- **Version**: 6.x  
- **Integration**: Used for caching frequently accessed data (e.g., query results, model configurations).  

### 5. **PostgreSQL**
- **Purpose**: A relational database for storing structured data.  
- **Version**: 13.x  
- **Integration**: Used for storing user data, model configurations, and monitoring logs.  

### 6. **RabbitMQ**
- **Purpose**: A message broker for handling real-time messaging.  
- **Version**: 3.x  
- **Integration**: Used for managing real-time LLM requests and responses.  

### 7. **Kafka**
- **Purpose**: A distributed event streaming platform for high-throughput logging.  
- **Version**: 3.x  
- **Integration**: Used for logging and event streaming during RAG training processes.  

### 8. **Sentry**
- **Purpose**: A real-time error tracking and performance monitoring tool.  
- **Version**: 1.x  
- **Integration**: Used for tracking errors and exceptions in the backend.  

### 9. **Winston**
- **Purpose**: A logging library for Node.js and Python.  
- **Version**: 3.x  
- **Integration**: Used for server-side logging.  

### 10. **Prometheus**
- **Purpose**: A monitoring and alerting toolkit.  
- **Version**: 2.x  
- **Integration**: Used for collecting and storing performance metrics.  

### 11. **Grafana**
- **Purpose**: A visualization tool for monitoring and analytics.  
- **Version**: 9.x  
- **Integration**: Used for creating dashboards to visualize Prometheus metrics.  

---

## DevOps Libraries

### 1. **Docker**
- **Purpose**: A platform for containerizing applications.  
- **Version**: 20.x  
- **Integration**: Used for containerizing the frontend, backend, and databases.  

### 2. **Kubernetes**
- **Purpose**: A container orchestration platform for managing containerized applications.  
- **Version**: 1.25.x  
- **Integration**: Used for deploying and scaling the application in production.  

### 3. **Helm**
- **Purpose**: A package manager for Kubernetes.  
- **Version**: 3.x  
- **Integration**: Used for managing Kubernetes deployments.  

### 4. **GitHub Actions**
- **Purpose**: A CI/CD platform for automating builds, tests, and deployments.  
- **Version**: N/A  
- **Integration**: Used for automating the CI/CD pipeline.  

---

## Compatibility & Requirements
- All libraries are **open-source** and compatible with the project’s tech stack.  
- Libraries are regularly updated to ensure compatibility and security.  

---

## Security & Compliance
- Libraries are chosen based on their **security track record** and **community support**.  
- Sensitive data (e.g., API keys, user credentials) is encrypted and securely stored.  

---

*This document outlines the third-party libraries used in Hyperion. Feedback is welcome before proceeding to the final handoff.*