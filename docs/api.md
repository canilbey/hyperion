# API Documentation

## Overview
The **Hyperion** backend exposes RESTful APIs for user management, document upload, model training, query execution, and monitoring. All endpoints are secured using JWT-based authentication and support role-based access control (RBAC).

## Base URL
All API endpoints are relative to the base URL:  
`https://api.hyperion.com/v1`

## Authentication
- **Method**: JWT (JSON Web Token)  
- **How It Works**:  
  1. User logs in using `/api/auth/login` to receive a JWT.  
  2. The JWT is included in the `Authorization` header of subsequent requests:  
     `Authorization: Bearer <JWT>`  
- **Token Expiry**: Tokens expire after 24 hours and must be refreshed.  

## Endpoints

### 1. User Management
#### `POST /api/auth/signup`
- **Description**: Register a new user.  
- **Request Body**:  
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe"
  }
- **Response**:  
  ```json
  {
  "message": "User registered successfully",
  "userId": "12345"
  }

#### `POST /api/auth/login`
- **Description**: Authenticate a user and return a JWT.  
- **Request Body**:  
  ```json
  {
  "email": "user@example.com",
  "password": "securepassword123"
  }
- **Response**:  
  ```json
  {
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 86400
  }

### 2. Document Upload
#### `POST /api/upload`
- **Description**: Upload PDFs or text files for processing.
- **Request Body**:  
  file: Multipart form data (PDF or text file).
- **Response**:  
  ```json
  {
  "message": "File uploaded successfully",
  "documentId": "67890"
  }

### 3. Model Training
#### `POST /api/model/train`
- **Description**: Train a new RAG model.
- **Request Body**: 
  ```json 
  {
  "modelName": "My RAG Model",
  "endpoint": "https://llm-endpoint.com",
  "apiKey": "apikey123",
  "description": "Model for customer support",
  "trainingData": ["documentId1", "documentId2"]
  }
- **Response**:  
  ```json
  {
  "message": "Model training started",
  "modelId": "54321"
  }

#### `GET /api/model/list`
- **Description**: List all trained models.
- **Response**:  
  ```json
  [
    {
    "modelId": "54321",
    "modelName": "My RAG Model",
    "endpoint": "https://llm-endpoint.com",
    "description": "Model for customer support",
    "status": "trained"
    }
  ]

### 4. Query Execution
#### `POST /api/query`
- **Description**: Submit a query to a trained model.
- **Request Body**:  
  ```json
  {
  "modelId": "54321",
  "query": "What is Retrieval-Augmented Generation?"
  }
- **Response**:  
  ```json
  {
  "response": "Retrieval-Augmented Generation (RAG) is a framework...",
  "citations": ["documentId1", "documentId2"]
  }

### 5. Monitoring & Logging
#### `GET /api/logs`
- **Description**: Fetch logs and performance metrics.
- **Response**:  
  ```json
  [
   {
    "timestamp": "2023-10-01T12:00:00Z",
    "action": "query",
    "userId": "12345",
    "details": "Query submitted to model 54321"
   }
  ]

## Error Handling
- 400 Bad Request: Invalid input data.
- 401 Unauthorized: Missing or invalid JWT.
- 403 Forbidden: Insufficient permissions.
- 500 Internal Server Error: Server-side issue.
- **Error Response Format**:  
  ```json
  {
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "statusCode": 401
  }

---

*This document outlines the API endpoints and usage for Hyperion. Feedback is welcome before proceeding to the next document.*