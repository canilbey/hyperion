# Core Backend API & Auth - Usage Guide

## Purpose
This document explains how to use the Core Backend API & Auth module in a process- and workflow-oriented manner. No code or command examples are included.

## User Management
- New users are added to the system via the registration (signup) endpoint.
- Input data is validated during registration, and passwords are securely stored.
- After registration, users authenticate via the login endpoint and receive a JWT.

## Authentication
- Access to all protected endpoints requires a valid JWT.
- JWT is generated during the login process and provided to the user.
- The JWT authentication middleware validates the token on every request.

## Authorization
- User roles (admin/user) define access levels.
- Each endpoint is protected according to its required role.
- Role assignments and permissions are managed in the database.

## Password Reset & Profile Update
- Users can reset their passwords and update their profile information.
- Secure verification and audit logging are applied to these operations.

## Observability & Quality
- System health and status are monitored via dedicated endpoints.
- All operations and errors are logged.
- The API is documented using OpenAPI/Swagger.
- Monitoring and logging are integrated with Prometheus and ELK.

## Integration with Other Services
- Authenticated user information is propagated to other backend modules (chat, document, RAG).
- This is achieved via request headers or service calls.

## References
- For more information, see project.md and prd.md. 