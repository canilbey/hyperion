# Core Backend API & Auth - Project Overview

## Purpose
The Core Backend API & Auth sub-project is responsible for all foundational backend services related to user management, authentication, authorization, and the provision of essential API endpoints. This component ensures secure access, user context propagation, and system health monitoring for the entire Hyperion platform.

## Scope
- User registration, login, profile management, and password reset
- Stateless authentication using JWT
- Role-based access control (RBAC) for admin and user separation
- Health and status endpoints for system observability
- Logging and error handling for all API operations
- Integration with monitoring and analytics infrastructure

## Architecture
- Built on a modular FastAPI service structure
- Utilizes PostgreSQL for persistent storage of user and session metadata
- Optionally leverages Redis for session caching and quick lookups
- JWT tokens are used for stateless authentication and session management
- RBAC is enforced at the API layer to restrict access to sensitive operations
- Logging and monitoring are integrated with external observability tools

## Technologies
- FastAPI (Python 3.10+)
- PostgreSQL (user/session data)
- Redis (optional, for session caching)
- JWT (authentication)
- Monitoring: Prometheus, ELK stack

## Dependencies
- Requires a running PostgreSQL instance with the appropriate user and session tables, including indexes for efficient lookup and uniqueness constraints on user identifiers
- Redis instance is optional but recommended for scalable session management
- Environment variables must be set for database connections, JWT secrets, and monitoring endpoints
- Logging and monitoring infrastructure must be available for full observability

## Configuration Requirements
- Database schema must include user, session, and role tables with appropriate indexes
- JWT secret and expiration settings must be configured securely
- RBAC roles and permissions must be defined and mapped to API endpoints
- Health and status endpoints must be accessible for monitoring tools

## Integration Points
- Provides user authentication and context to all backend services, including chat, document processing, and RAG retrieval
- Exposes OpenAPI/Swagger documentation for frontend and external integration
- Relies on PostgreSQL for persistent user data and session management
- Integrates with system-wide logging and monitoring for error tracking and analytics

## Workflow Description
- User initiates registration or login, providing required credentials
- System validates input, creates or verifies user records, and issues JWT tokens
- Authenticated requests include JWT, which is validated and decoded to provide user context
- Role-based access is enforced for protected endpoints
- Health and status endpoints provide real-time system information for observability
- All actions are logged and monitored for security and operational insights

## References
- See prd.md for full requirements, user scenarios, and system architecture
- Related sub-projects: Chat & Conversation Engine, Frontend Application, Observability & DevOps 