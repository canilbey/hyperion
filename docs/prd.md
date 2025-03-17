# Product Requirements Document (PRD)

## App Overview
- **Name**: Hyperion  
- **Tagline**: Easy-use, Fully Customizable, RAG-powered AI  
- **Description**:  
  Hyperion is a fully customizable, open-source RAG (Retrieval-Augmented Generation) application designed for both common users and developers. It allows users to upload documents, create vector-based knowledge bases, and connect to various LLM endpoints (e.g., ollama, lmstudio, OpenRouter) for generating contextually enriched responses. The app is containerized for easy deployment and built entirely with open-source tools.

## Target Audience
- **Common Users**: Individuals or small businesses who want to use AI for tasks like document analysis, research, or customer support.  
- **Developers**: Engineers and data scientists who want to integrate Hyperion into their own projects.  
- **Open Source Community**: Contributors and users who will install, customize, and extend the project for their needs.

## Key Features
### For Common Users:
- **Document Upload**: Upload PDFs and text files for processing.  
- **Chat Interface**: Interact with trained models using a ChatGPT-like interface.  
- **Model Training**: Train custom RAG models with user-defined data.  
- **Pre-defined Models**: Use pre-configured models for quick setup.  

### For Developers:
- **Modular Architecture**: Customize embedding models, LLM connectors, and retrieval parameters.  
- **RESTful APIs**: Integrate Hyperion into other applications.  
- **Containerized Deployment**: Deploy locally or in production using Docker and Kubernetes.  

### For Both:
- **Real-time Messaging**: RabbitMQ for low-latency LLM request/response handling.  
- **Event Streaming**: Kafka for high-throughput logging and training data processing.  
- **Monitoring & Analytics**: Built-in Grafana dashboards for real-time insights.  

## Success Metrics
- **Primary Goal**: The project is primarily for personal use, with no formal success metrics.  
- **Secondary Goal**: Encourage adoption and contributions from the open-source community.  

## Assumptions & Risks
- **Assumptions**:  
  - Users have basic technical knowledge to set up and use the app.  
  - Open-source tools and libraries will meet all functional requirements.  
- **Risks**:  
  - Scalability challenges with high user loads.  
  - Security vulnerabilities in third-party integrations.  

---

*This document outlines the purpose, features, and target audience for Hyperion. Feedback is welcome before proceeding to the next document.*