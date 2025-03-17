# Testing Plan

## Overview
The **Hyperion** application will undergo rigorous testing to ensure functionality, reliability, and performance. This document outlines the testing strategy, including unit testing, integration testing, end-to-end testing, and error handling.

---

## Testing Strategy

### 1. **Unit Testing**
- **Purpose**: Test individual components and functions in isolation.  
- **Tools**:  
  - **Frontend**: Jest + React Testing Library.  
  - **Backend**: PyTest.  
- **Scope**:  
  - Test Redux actions, reducers, and selectors.  
  - Test API endpoints and utility functions.  
- **Example (Frontend)**:  
  ```javascript
  test('login action updates state correctly', () => {
    const initialState = { isAuthenticated: false };
    const action = { type: 'LOGIN', payload: { userId: '12345' } };
    const newState = authReducer(initialState, action);
    expect(newState.isAuthenticated).toBe(true);
  });
  ```  
- **Example (Backend)**:  
  ```python
  def test_login_endpoint():
      response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
      assert response.status_code == 200
      assert "token" in response.json()
  ```

---

### 2. **Integration Testing**
- **Purpose**: Test interactions between components, services, and APIs.  
- **Tools**:  
  - **Frontend**: Jest + React Testing Library.  
  - **Backend**: PyTest.  
- **Scope**:  
  - Test interactions between frontend components and Redux store.  
  - Test API integrations (e.g., document upload, model training).  
- **Example (Frontend)**:  
  ```javascript
  test('ChatInterface fetches and displays chat history', async () => {
    render(<ChatInterface />);
    await waitFor(() => expect(screen.getByText('What is RAG?')).toBeInTheDocument());
  });
  ```  
- **Example (Backend)**:  
  ```python
  def test_document_upload_integration():
      response = client.post("/api/upload", files={"file": ("test.pdf", open("test.pdf", "rb"))})
      assert response.status_code == 200
      assert "documentId" in response.json()
  ```

---

### 3. **End-to-End Testing**
- **Purpose**: Test the entire application workflow from start to finish.  
- **Tools**: Cypress.  
- **Scope**:  
  - Test user flows (e.g., sign up, upload documents, train models, chat).  
  - Validate UI interactions and API responses.  
- **Example**:  
  ```javascript
  describe('User Workflow', () => {
    it('should sign up, upload a document, train a model, and chat', () => {
      cy.visit('/signup');
      cy.get('input[name="email"]').type('user@example.com');
      cy.get('input[name="password"]').type('password123');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/main');
      cy.get('input[type="file"]').attachFile('test.pdf');
      cy.get('button').contains('Train Model').click();
      cy.get('input[name="query"]').type('What is RAG?');
      cy.get('button').contains('Send').click();
      cy.contains('Retrieval-Augmented Generation').should('be.visible');
    });
  });
  ```

---

### 4. **Error Handling Testing**
- **Purpose**: Ensure the application handles errors gracefully.  
- **Scope**:  
  - Test invalid inputs (e.g., wrong email/password, invalid file types).  
  - Test API failures (e.g., server errors, network issues).  
- **Example (Frontend)**:  
  ```javascript
  test('displays error message on invalid login', async () => {
    render(<Login />);
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'invalid@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrongpassword' } });
    fireEvent.click(screen.getByText('Log In'));
    await waitFor(() => expect(screen.getByText('Invalid email or password')).toBeInTheDocument());
  });
  ```  
- **Example (Backend)**:  
  ```python
  def test_invalid_login():
      response = client.post("/api/auth/login", json={"email": "invalid@example.com", "password": "wrongpassword"})
      assert response.status_code == 401
      assert response.json() == {"error": "Unauthorized", "message": "Invalid email or password"}
  ```

---

## Testing Environment

### 1. **Local Development**
- **Purpose**: Run tests during development to catch issues early.  
- **Setup**:  
  - Use Docker Compose to spin up local services (e.g., PostgreSQL, Redis, Milvus).  
  - Run tests using `npm test` (frontend) and `pytest` (backend).  

### 2. **CI/CD Pipeline**
- **Purpose**: Automate testing in the CI/CD pipeline.  
- **Setup**:  
  - Use GitHub Actions to run tests on every push to the `main` branch.  
  - Example workflow:  
    ```yaml
    name: CI/CD Pipeline
    on:
      push:
        branches:
          - main
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v2
          - name: Run frontend tests
            run: npm test
          - name: Run backend tests
            run: pytest
    ```

---

## Test Coverage
- **Goal**: Achieve at least **90% test coverage** for both frontend and backend.  
- **Tools**:  
  - **Frontend**: Jest coverage reports.  
  - **Backend**: PyTest coverage reports.  
- **Example**:  
  ```bash
  npm test -- --coverage
  pytest --cov=backend tests/
  ```

---

*This document outlines the testing strategy for Hyperion. Feedback is welcome before proceeding to the next document.*
