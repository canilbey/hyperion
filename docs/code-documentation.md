# Code Documentation

## Overview
The **Hyperion** codebase will be well-documented to ensure maintainability, readability, and ease of collaboration. This document outlines the standards and practices for documenting the code, including inline comments, API documentation, and architecture diagrams.

---

## Inline Comments

### 1. **Purpose**
- Explain complex logic, algorithms, or non-obvious code.  
- Provide context for future developers.  

### 2. **Standards**
- Use **clear and concise** comments.  
- Avoid redundant comments (e.g., `// Increment counter` for `counter++`).  
- Follow the language-specific commenting conventions.  

### 3. **Examples**
- **JavaScript**:  
  ```javascript
  // Calculate the cosine similarity between two vectors
  function cosineSimilarity(vecA, vecB) {
    const dotProduct = vecA.reduce((sum, val, i) => sum + val * vecB[i], 0);
    const magnitudeA = Math.sqrt(vecA.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(vecB.reduce((sum, val) => sum + val * val, 0));
    return dotProduct / (magnitudeA * magnitudeB);
  }
  ```  

- **Python**:  
  ```python
  def cosine_similarity(vec_a, vec_b):
      """
      Calculate the cosine similarity between two vectors.
      :param vec_a: First vector (list of floats).
      :param vec_b: Second vector (list of floats).
      :return: Cosine similarity (float).
      """
      dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
      magnitude_a = sum(a ** 2 for a in vec_a) ** 0.5
      magnitude_b = sum(b ** 2 for b in vec_b) ** 0.5
      return dot_product / (magnitude_a * magnitude_b)
  ```

---

## API Documentation

### 1. **Purpose**
- Provide clear and comprehensive documentation for all API endpoints.  
- Enable developers to understand and use the API without reading the source code.  

### 2. **Tools**
- **Swagger/OpenAPI**: Automatically generate API documentation from code.  
- **FastAPI**: Built-in support for OpenAPI documentation.  

### 3. **Example**
- **FastAPI Endpoint**:  
  ```python
  from fastapi import FastAPI
  from pydantic import BaseModel

  app = FastAPI()

  class User(BaseModel):
      email: str
      password: str

  @app.post("/api/auth/login")
  def login(user: User):
      """
      Authenticate a user and return a JWT.
      - **email**: User's email address.
      - **password**: User's password.
      - **Returns**: JWT token and expiry time.
      """
      return {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "expiresIn": 86400}
  ```  

- **Swagger UI**:  
  - Accessible at `/docs` (e.g., `http://localhost:8000/docs`).  
  - Provides interactive API documentation.  

---

## README File

### 1. **Purpose**
- Provide a high-level overview of the project.  
- Include setup instructions, usage examples, and contribution guidelines.  

### 2. **Structure**
- **Project Description**: Brief overview of the app.  
- **Installation**: Step-by-step setup instructions.  
- **Usage**: Examples of how to use the app.  
- **API Documentation**: Link to Swagger UI or OpenAPI docs.  
- **Contributing**: Guidelines for contributing to the project.  
- **License**: Project license (e.g., MIT).  

### 3. **Example**
# Hyperion

## Overview
Hyperion is a fully customizable, open-source RAG (Retrieval-Augmented Generation) application built with Python and React. It allows users to upload documents, train models, and interact with LLM endpoints.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/hyperion.git
   ```
2. Install dependencies:
   ```bash
   cd hyperion
   npm install
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   docker-compose up
   ```

## Usage
- Upload documents via the web interface.  
- Train models using the "Train" section.  
- Chat with models using the "Chat" section.  

## API Documentation
Access the API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License
This project is licensed under the MIT License.

---

## Architecture Diagrams

### 1. **Purpose**
- Visualize the system architecture and data flow.  
- Help developers understand the overall structure of the application.  

### 2. **Tools**
- **Mermaid.js**: For creating diagrams in Markdown.  
- **Draw.io**: For creating standalone diagrams.  

### 3. **Example**
flowchart TD
    A[Frontend] --> B[Backend]
    B --> C[PostgreSQL]
    B --> D[Milvus]
    B --> E[Redis]
    B --> F[RabbitMQ]
    B --> G[Kafka]
    F --> H[LLM Endpoints]
    G --> I[Prometheus]
    I --> J[Grafana]

---

## Code Style & Linting

### 1. **Purpose**
- Ensure consistent code style across the codebase.  
- Catch potential errors and enforce best practices.  

### 2. **Tools**
- **Frontend**: ESLint + Prettier.  
- **Backend**: Flake8 + Black.  

### 3. **Configuration**
- **ESLint**:  
  ```json
  {
    "extends": ["react-app", "prettier"],
    "rules": {
      "no-unused-vars": "warn",
      "react/prop-types": "off"
    }
  }
  ```  

- **Flake8**:  
  ```ini
  [flake8]
  max-line-length = 88
  ignore = E203, E266, E501, W503
  ```

---

*This document outlines the code documentation standards for Hyperion. Feedback is welcome before proceeding to the next document.*
