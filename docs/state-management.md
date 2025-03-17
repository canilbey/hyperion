# State Management Documentation

## Overview
The **Hyperion** application uses a combination of **global state management** (Redux), **server state management** (React Query), and **persistence** (local storage) to ensure a smooth and consistent user experience. This document outlines the state management strategies for both the frontend and backend.

---

## Global State Management (Redux)

### 1. **Purpose**
- Manage app-wide state that needs to be shared across multiple components (e.g., user authentication, selected model, chat history).  

### 2. **Key State Slices**
- **User Authentication**:  
  - Stores the authenticated user’s details (e.g., `userId`, `email`, `role`).  
  - Example:  
    ```javascript
    {
      userId: "12345",
      email: "user@example.com",
      role: "user",
      isAuthenticated: true
    }
    ```  

- **Selected Model**:  
  - Stores the currently selected RAG model (e.g., `modelId`, `modelName`).  
  - Example:  
    ```javascript
    {
      modelId: "54321",
      modelName: "My RAG Model",
      endpoint: "https://llm-endpoint.com"
    }
    ```  

- **Chat History**:  
  - Stores the chat history for the current session.  
  - Example:  
    ```javascript
    [
      { query: "What is RAG?", response: "Retrieval-Augmented Generation is..." },
      { query: "How does it work?", response: "It combines retrieval and generation..." }
    ]
    ```  

### 3. **Actions**
- **User Actions**:  
  - `LOGIN`: Update state when a user logs in.  
  - `LOGOUT`: Clear state when a user logs out.  
- **Model Actions**:  
  - `SELECT_MODEL`: Update state when a model is selected.  
  - `CLEAR_MODEL`: Clear state when no model is selected.  
- **Chat Actions**:  
  - `ADD_CHAT`: Add a new query/response pair to the chat history.  
  - `CLEAR_CHAT`: Clear the chat history.  

### 4. **Reducers**
- Combine all state slices into a single root reducer.  
- Example:  
  ```javascript
  const rootReducer = combineReducers({
    user: userReducer,
    model: modelReducer,
    chat: chatReducer
  });
  ``` 

  ---

## Server State Management (React Query)
### 1. **Purpose**
- Manage server-side data (e.g., API responses, model configurations) and handle caching, background updates, and error handling. 

### 2. **Key Queries**
- **Fetch Models**:  
  - Query to fetch the list of trained models.
  - Example:  
    ```javascript
    const { data: models, isLoading } = useQuery('models', fetchModels);
    ```  

- **Fetch Chat History**:  
  - Query to fetch the chat history for a specific model.  
  - Example:  
    ```javascript
    const { data: chatHistory, isLoading } = useQuery(['chat', modelId], fetchChatHistory);
    ```  

### 3. **Key Mutations**
- **Train Model**:  
  - Mutation to train a new RAG model.
  - Example:  
    ```javascript
    const { mutate: trainModel, isLoading } = useMutation(trainModelApi, {
    onSuccess: () => {
     queryClient.invalidateQueries('models');
        }
    });
    ```  

- **Submit Query**:  
  - Mutation to submit a query to a trained model.
  - Example:  
    ```javascript
    const { mutate: submitQuery, isLoading } = useMutation(submitQueryApi, {
        onSuccess: (data) => {
            queryClient.setQueryData(['chat', modelId], (oldData) => [...oldData, data]);
        }
    });
    ```  

---

## Persistence
### 1. **Purpose**
- Persist state across sessions to improve user experience (e.g., remember the latest chat, user preferences).

### 2. ** Strategies**
- **Local Storage**:  
  - Store non-sensitive data (e.g., selected model, chat history) in the browser’s local storage.
  - Example:  
    ```javascript
    localStorage.setItem('selectedModel', JSON.stringify(selectedModel));
    ```  

- **Session Storage**:  
  - Store session-specific data (e.g., authentication token) in the browser’s session storage.
  - Example:  
    ```javascript
    sessionStorage.setItem('authToken', authToken);
    ```  

---

## Error Handling
### 1. **Global State Errors**
- **Scenario**: Redux action fails (e.g., API call fails).
- **Action**: Dispatch an error action and update the state to reflect the error.

### 2. **Server State Errors**
- **Scenario**: React Query mutation or query fails.
- **Action**: Display an error message using React Query’s built-in error handling.

---

*This document outlines the state management strategies for Hyperion. Feedback is welcome before proceeding to the next document.*