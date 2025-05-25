# User Authentication - Technical Design

## Overview
This document details the technical design and implementation plan for the user authentication system in the Core Backend API & Auth module. It covers database schema, API endpoints, authentication flows, and security considerations.

---

## 1. Database Schema

### Tables
- **users**: Stores user credentials and profile data.
  - Fields: 
    - id (UUID, PK)
    - email (unique)
    - hashed_password
    - is_active
    - created_at
    - updated_at
    - last_login_at
    - session_token (for persistent browser sessions)

### Security
- Passwords are hashed using bcrypt
- Unique constraints on email
- Indexes for efficient lookup
- Session tokens are stored securely and have long expiration

---

## 2. API Endpoints

### Registration (Signup)
- **POST /api/auth/signup**
  - Input: email, password
  - Validates input, enforces password policy, checks uniqueness
  - Hashes password and creates user record
  - Returns session token for immediate login

### Login
- **POST /api/auth/login**
  - Input: email, password
  - Verifies credentials and password hash
  - Creates/updates session token
  - Returns session token for persistent browser session
  - Updates last_login_at timestamp

### Password Reset
- **POST /api/auth/request-password-reset**
  - Input: email
  - Generates and sends a password reset token (email)
- **POST /api/auth/reset-password**
  - Input: token, new_password
  - Validates token and updates password
  - Invalidates existing session tokens

### Logout
- **POST /api/auth/logout**
  - Invalidates current session token
  - Requires valid session token

---

## 3. Session Management
- Session tokens are stored in the users table
- Tokens persist until:
  - User explicitly logs out
  - Password is reset
  - Account is deactivated
- Session tokens are sent as HTTP-only cookies
- Tokens are validated on each request
- Secure cookie settings (SameSite, Secure flags)

---

## 4. Security Considerations
- All passwords are hashed using bcrypt
- Rate limiting on login and password reset endpoints
- Secure error messages (no user enumeration)
- All sensitive config (DB credentials) in environment variables
- Audit logging for critical actions (login, password reset)
- CSRF protection for all endpoints
- XSS protection through secure cookie settings

---

## 5. Testing & Quality
- Unit and integration tests for all auth flows
- Edge case and error condition coverage
- Automated test runs in CI/CD pipeline
- Security testing (OWASP guidelines)

---

## 6. Documentation & OpenAPI
- All endpoints documented with OpenAPI/Swagger
- Example requests and responses for each flow
- Security schemes and error codes clearly described

---

## 7. Integration Points
- User context (user_id) is propagated to downstream services via session token
- Auth service exposes OpenAPI docs for frontend integration

---

## 8. Future Enhancements
- Email verification
- Two-factor authentication (2FA)
- Account lockout after failed attempts
- Session management dashboard
- Advanced audit logging 