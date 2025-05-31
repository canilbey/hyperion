# Chat & Conversation Engine - Checklist

## Milestone 1: Chat Session Management (High Priority)
- [x] Design chat session and message database schema  
  _Define tables and relationships for chat sessions and messages._
- [x] Implement chat session creation endpoint  
  _Allow users to start new chat sessions._
- [x] Implement message addition endpoint  
  _Enable users to send messages within a session._
- [x] Implement chat history retrieval endpoint  
  _Allow users to fetch previous messages in a session._

## Milestone 2: LLM Integration & Context (Medium Priority)
- [X] Integrate chat history with LLMs  
  _Provide chat context to LLMs for response generation._
- [X] Implement context window management logic  
  _Manage the amount of chat history sent to LLMs._
- [x] Integrate Redis cache for chat sessions  
  _Cache chat data for fast retrieval and scalability._

## Milestone 3: Quality & Observability (Medium/Low Priority)
- [X] Add logging and error handling to all endpoints  
  _Log all chat operations and handle errors consistently._
- [ ] Write unit and integration tests for chat endpoints  
  _Ensure reliability and correctness with automated tests._
- [x] Document API endpoints with OpenAPI/Swagger  
  _Provide interactive API documentation._

## General Dependencies
- [x] Set up and configure PostgreSQL or NoSQL database  
  _Install and configure the main database for chat data._
- [x] Set up and configure Redis  
  _Install and configure Redis for caching._
- [x] Set up FastAPI core  
  _Initialize FastAPI application structure._
- [x] Set up LLM API/service credentials  
  _Configure LLM API keys and endpoints._
- [X] Set up monitoring and logging infrastructure  
  _Prepare Prometheus, ELK, and related tools._

## Responsible Roles
- Backend Developer
- QA Engineer

## References
- See project.md and prd.md for more details.

## Added (2024-05)
- [x] Chat migration files are split into single statements (one file per table and index)
- [x] Automatic migration support added (migrations run automatically on backend startup)
- [x] LLM API calls (OpenRouter, OpenAI, Anthropic) are now logged
- [x] Faulty migrations fixed, now safe and idempotent

## Added (2024-06)
# The centralized Settings class integration is postponed for future development. All related tasks are removed from the current milestone.

# 2024-06: Context window, zincir, logging ve izleme tamamlandı.
