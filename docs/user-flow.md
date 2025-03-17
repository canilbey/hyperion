# User Flow Documentation

## Overview
The **Hyperion** application is designed to provide a seamless experience for users to upload documents, train RAG models, and interact with them via a ChatGPT-like interface. This document outlines the user flows, including onboarding, core interactions, error handling, and edge cases.

---

## Onboarding Flow

### 1. **Sign Up**
- **Steps**:  
  1. User navigates to the signup page.  
  2. User enters email, password, and name.  
  3. User submits the form.  
  4. Backend validates the input and creates a new user account.  
  5. User is redirected to the login page.  

- **Interactions**:  
  - Email and password input fields.  
  - "Sign Up" button.  

- **Error Handling**:  
  - Invalid email or password: Display error message below the form.  
  - Email already exists: Display error message and prompt user to log in.  

---

### 2. **Log In**
- **Steps**:  
  1. User navigates to the login page.  
  2. User enters email and password.  
  3. User submits the form.  
  4. Backend authenticates the user and returns a JWT.  
  5. User is redirected to the main screen.  

- **Interactions**:  
  - Email and password input fields.  
  - "Log In" button.  
  - Optional "Sign in with Google" button.  

- **Error Handling**:  
  - Invalid email or password: Display error message below the form.  
  - Account not found: Display error message and prompt user to sign up.  

---

## Core User Journey

### 1. **Upload Documents**
- **Steps**:  
  1. User navigates to the main screen.  
  2. User clicks "Upload" button.  
  3. User selects PDF or text files to upload.  
  4. Backend processes the files and stores them in the database.  
  5. User sees a confirmation message.  

- **Interactions**:  
  - Drag-and-drop file upload area.  
  - "Upload" button.  

- **Error Handling**:  
  - Invalid file type: Display error message and reject the file.  
  - File size exceeds limit: Display error message and reject the file.  

---

### 2. **Train a Model**
- **Steps**:  
  1. User navigates to the "Train" section.  
  2. User selects documents for training.  
  3. User configures model parameters (e.g., endpoint, API key, description).  
  4. User clicks "Train Model" button.  
  5. Backend starts the training process and returns a model ID.  
  6. User sees a confirmation message.  

- **Interactions**:  
  - Document selection dropdown.  
  - Input fields for model configuration.  
  - "Train Model" button.  

- **Error Handling**:  
  - Missing required fields: Display error message and highlight missing fields.  
  - Training failure: Display error message and log the issue.  

---

### 3. **Chat with a Model**
- **Steps**:  
  1. User navigates to the "Chat" section.  
  2. User selects a trained model from the dropdown.  
  3. User enters a query in the text input box.  
  4. User clicks "Send" button.  
  5. Backend processes the query and returns a response.  
  6. User sees the response in the chat interface.  

- **Interactions**:  
  - Model selection dropdown.  
  - Text input box.  
  - "Send" button.  

- **Error Handling**:  
  - No model selected: Display error message and prompt user to select a model.  
  - Query failure: Display error message and log the issue.  

---

## Error Handling

### 1. **Invalid Input**
- **Scenario**: User submits a form with missing or invalid data.  
- **Action**: Display error message below the form and highlight the invalid fields.  

### 2. **Authentication Failure**
- **Scenario**: User enters incorrect email or password.  
- **Action**: Display error message and prompt user to try again.  

### 3. **Server Errors**
- **Scenario**: Backend fails to process a request (e.g., training failure, query failure).  
- **Action**: Display error message and log the issue for debugging.  

---

## Edge Cases

### 1. **Offline Mode**
- **Scenario**: User loses internet connection.  
- **Action**: Display a warning message and disable actions that require connectivity.  

### 2. **Incomplete Data**
- **Scenario**: User tries to train a model without selecting documents.  
- **Action**: Display error message and prompt user to select documents.  

### 3. **Expired Session**
- **Scenario**: User’s JWT expires during a session.  
- **Action**: Redirect user to the login page and prompt them to log in again.  

---

## Alternative Flows

### 1. **Guest Mode**
- **Scenario**: User wants to explore the app without creating an account.  
- **Action**: Provide limited functionality (e.g., view demo models, try sample queries).  

### 2. **Skip Onboarding**
- **Scenario**: User wants to skip the onboarding tutorial.  
- **Action**: Provide a "Skip" button on the onboarding screens.  

---

## User Permissions

### 1. **Admin User**
- **Permissions**:  
  - Access monitoring and analytics dashboards.  
  - Manage system settings and user accounts.  

### 2. **Regular User**
- **Permissions**:  
  - Upload documents, train models, and execute queries.  
  - View their own activity logs.  

---

*This document outlines the user flows for Hyperion. Feedback is welcome before proceeding to the next document.*