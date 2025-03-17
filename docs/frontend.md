# Frontend Documentation

## Overview
The frontend of **Hyperion** is built using **React** and **Material-UI (MUI)**. It provides a modern, intuitive interface for users to interact with the RAG-powered AI system. The design is inspired by ChatGPT, with a focus on simplicity and usability.

## UI Framework & Library
- **Framework**: React  
- **UI Library**: Material-UI (MUI) for pre-built components and consistent styling.  

## Navigation
The frontend navigation is divided into the following sections:
1. **Login/Signup Screen**:  
   - Users can log in or sign up using email/password or Google Auth.  
   - Simple forms with validation for email and password inputs.  

2. **Main Screen**:  
   - **Sidebar**:  
     - **Top Section**:  
       - Two buttons: **Chat** and **Train**.  
       - Model selection dropdown below the buttons for choosing trained (RAGed) models.  
       - Chat history section for managing multiple chat contexts.  
     - **Bottom Section**:  
       - **Pre-defined Models List**: A list of user-defined models with details (Provider, endpoint, API key, description, context, and trained data size).  
       - **Define Model Button**: Opens a form for creating new models.  
   - **Chat Interface**:  
     - Similar to ChatGPT, with a text input box and response display area.  
     - Model selection dropdown for switching between trained models.  
   - **Train Interface**:  
     - Drag-and-drop file upload for training data.  
     - Input fields for defining model parameters (e.g., endpoint, API key, description).  

## Styling
- **Design**: Modern and simple, inspired by ChatGPT.  
- **Styling Tools**:  
  - **CSS Modules**: For component-specific styles.  
  - **Material-UI Theming**: For consistent colors, typography, and spacing.  

## Forms
1. **Login/Signup Forms**:  
   - Email and password inputs with validation.  
   - Google Auth button for optional social login.  

2. **Train Data Input Form**:  
   - Drag-and-drop file upload for training data (PDFs, text files).  
   - Input fields for model configuration (e.g., endpoint, API key, description).  

3. **Chat Input Form**:  
   - Text input box for user queries.  
   - Send button for submitting queries.  

## State Management
- **Global State**: Redux for managing app-wide state (e.g., user authentication, selected model, chat history).  
- **Server State**: React Query for managing server-side data (e.g., API responses, model configurations).  
- **Persistence**:  
  - Latest chat and user preferences are persisted across sessions using local storage.  

## Key Components
1. **Login/Signup Component**: Handles user authentication.  
2. **Sidebar Component**: Manages navigation and model selection.  
3. **Chat Interface Component**: Displays chat history and handles user queries.  
4. **Train Interface Component**: Handles model training and configuration.  
5. **Model Selection Dropdown**: Allows users to switch between trained models.  
6. **Drag-and-Drop File Upload**: For uploading training data.  

---

*This document outlines the frontend architecture and components for Hyperion. Feedback is welcome before proceeding to the next document.*