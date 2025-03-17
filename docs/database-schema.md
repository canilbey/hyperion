# Database Schema Documentation

## Overview
The **Hyperion** application uses three databases:  
1. **PostgreSQL**: For user data, model configurations, and monitoring/analytics.  
2. **Milvus**: For storing vector embeddings and enabling semantic search.  
3. **Redis**: For caching frequently accessed data (e.g., query results, model configurations).  

---

## PostgreSQL Schema

### 1. **Users Table**
Stores user account information and preferences.  
- **Fields**:  
  - `user_id` (UUID, Primary Key): Unique identifier for the user.  
  - `email` (String, Unique): User's email address.  
  - `password_hash` (String): Hashed password for authentication.  
  - `name` (String): User's full name.  
  - `role` (String): User role (`admin` or `user`).  
  - `created_at` (Timestamp): Account creation date.  
  - `updated_at` (Timestamp): Last account update date.  

- **Indexes**:  
  - `email`: For fast lookup during login.  
  - `role`: For role-based access control.  

---

### 2. **Models Table**
Stores information about trained RAG models.  
- **Fields**:  
  - `model_id` (UUID, Primary Key): Unique identifier for the model.  
  - `user_id` (UUID, Foreign Key): ID of the user who created the model.  
  - `model_name` (String): Name of the model.  
  - `endpoint` (String): LLM endpoint URL.  
  - `api_key` (String): API key for the LLM endpoint.  
  - `description` (Text): Description of the model.  
  - `status` (String): Model status (`training`, `trained`, `failed`).  
  - `created_at` (Timestamp): Model creation date.  
  - `updated_at` (Timestamp): Last model update date.  

- **Indexes**:  
  - `user_id`: For fetching models by user.  
  - `status`: For filtering models by status.  

---

### 3. **Documents Table**
Stores metadata about uploaded documents.  
- **Fields**:  
  - `document_id` (UUID, Primary Key): Unique identifier for the document.  
  - `user_id` (UUID, Foreign Key): ID of the user who uploaded the document.  
  - `file_name` (String): Name of the uploaded file.  
  - `file_size` (Integer): Size of the file in bytes.  
  - `file_type` (String): File type (e.g., `pdf`, `txt`).  
  - `uploaded_at` (Timestamp): Document upload date.  

- **Indexes**:  
  - `user_id`: For fetching documents by user.  
  - `file_type`: For filtering documents by type.  

---

### 4. **Training Data Table**
Stores relationships between models and training documents.  
- **Fields**:  
  - `training_id` (UUID, Primary Key): Unique identifier for the training record.  
  - `model_id` (UUID, Foreign Key): ID of the trained model.  
  - `document_id` (UUID, Foreign Key): ID of the training document.  

- **Indexes**:  
  - `model_id`: For fetching training data by model.  
  - `document_id`: For fetching models by document.  

---

### 5. **Logs Table**
Stores user actions and system logs for monitoring and analytics.  
- **Fields**:  
  - `log_id` (UUID, Primary Key): Unique identifier for the log entry.  
  - `user_id` (UUID, Foreign Key): ID of the user who triggered the action.  
  - `action` (String): Action performed (e.g., `query`, `upload`, `train`).  
  - `details` (Text): Additional details about the action.  
  - `timestamp` (Timestamp): Time of the action.  

- **Indexes**:  
  - `user_id`: For fetching logs by user.  
  - `action`: For filtering logs by action type.  

---

## Milvus Schema
Milvus is used for storing vector embeddings and enabling semantic search.  

### 1. **Collections**
- **Collection Name**: `document_embeddings`  
- **Fields**:  
  - `embedding_id` (String): Unique identifier for the embedding.  
  - `document_id` (String): ID of the document the embedding belongs to.  
  - `embedding` (Float Vector): Vector representation of the document chunk.  
  - `metadata` (JSON): Additional metadata (e.g., chunk text, chunk index).  

- **Indexes**:  
  - `document_id`: For fetching embeddings by document.  
  - `embedding`: For semantic search using vector similarity.  

---

## Redis Schema
Redis is used for caching frequently accessed data.  

### 1. **Keys**
- **Key Format**: `user:<user_id>:<data_type>`  
  - Example: `user:12345:model_config`  
- **Data Types**:  
  - `model_config`: Cached model configurations.  
  - `query_results`: Cached query results.  
  - `recent_activity`: Cached recent user activity.  

---

## Relationships
1. **Users → Models**: One-to-many (a user can create multiple models).  
2. **Users → Documents**: One-to-many (a user can upload multiple documents).  
3. **Models → Training Data**: One-to-many (a model can be trained on multiple documents).  
4. **Documents → Embeddings**: One-to-many (a document can have multiple embeddings).  

---

## Indexing Strategy
- **PostgreSQL**:  
  - Indexes on `user_id`, `model_id`, and `document_id` for fast lookups.  
  - Composite indexes for frequently queried fields (e.g., `user_id + status`).  
- **Milvus**:  
  - Index on `embedding` for efficient semantic search.  
- **Redis**:  
  - Key-based lookups for fast caching.  

---

*This document outlines the database schema design for Hyperion. Feedback is welcome before proceeding to the next document.*