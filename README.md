# Enterprise AI Platform — Backend

> FastAPI backend for a secure enterprise AI and Retrieval-Augmented Generation (RAG) platform.

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/Vector%20Search-pgvector-purple)](https://github.com/pgvector/pgvector)
[![Deployment](https://img.shields.io/badge/Deployment-Render-blue)](https://render.com/)

**Frontend:** https://github.com/calvinoke/enterprise-ai-frontend

**Production API:** https://backend-enterprise-ai-app.onrender.com

**API Documentation:** https://backend-enterprise-ai-app.onrender.com/docs

---

# Overview

The Enterprise AI Backend is a modular FastAPI application that provides the API, business logic, persistence, authentication, document processing, semantic retrieval, RAG, conversation management, and AI service integration for the Enterprise AI Platform.

The backend is designed around a domain-oriented architecture.

Major application domains include:

```text
Authentication
Users
AI
Conversations
Documents
Embeddings
RAG
LLM
Database
```

The backend acts as the security and business-logic boundary for the entire platform.

---

# Architecture

```text
                         ┌──────────────────┐
                         │     Frontend     │
                         │ React + TypeScript│
                         └────────┬─────────┘
                                  │
                                  │ HTTPS / REST
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │    /api/v1       │
                         └────────┬─────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       Authentication        Application            AI Layer
       & Authorization        Services
             │                    │                    │
             │          ┌─────────┼─────────┐          │
             │          │         │         │          │
             ▼          ▼         ▼         ▼          ▼
           Users     Documents Conversations RAG      LLM
                       │                    │
                       ▼                    ▼
                  Embeddings           Retrieval
                       │                    │
                       └─────────┬──────────┘
                                 ▼
                         PostgreSQL + pgvector
```

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend language |
| FastAPI | REST API |
| SQLAlchemy | ORM / database access |
| asyncpg | Async PostgreSQL driver |
| PostgreSQL | Relational database |
| pgvector | Vector similarity search |
| Alembic | Database migrations |
| JWT | Authentication |
| HTTPX | HTTP integrations |
| Gemini Embeddings | Text embeddings |
| Groq / LLM Provider | Language model integration |
| Resend | Transactional email |
| Render | Production deployment |

---

# Repository

GitHub:

https://github.com/calvinoke/Backend-Enterprise-ai-app

Frontend:

https://github.com/calvinoke/enterprise-ai-frontend

---

# Production

Production API:

```text
https://backend-enterprise-ai-app.onrender.com
```

Swagger UI:

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

OpenAPI documentation:

```text
https://backend-enterprise-ai-app.onrender.com/openapi.json
```

---

# Project Structure

The backend follows a modular application structure.

```text
Backend-Enterprise-ai-app/
│
├── app/
│   │
│   ├── api/
│   │   └── v1/
│   │       └── api.py
│   │
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   ├── password_service.py
│   │   ├── password_reset_service.py
│   │   └── email_verification_service.py
│   │
│   ├── users/
│   │   ├── router.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── dependencies.py
│   │
│   ├── documents/
│   │   └── ...
│   │
│   ├── embeddings/
│   │   └── ...
│   │
│   ├── rag/
│   │   └── ...
│   │
│   ├── llm/
│   │   └── ...
│   │
│   ├── conversations/
│   │   └── ...
│   │
│   ├── aiii/
│   │   └── ...
│   │
│   ├── database/
│   │   └── ...
│   │
│   ├── notifications/
│   │   └── ...
│   │
│   ├── core/
│   │   └── ...
│   │
│   └── main.py
│
├── alembic/
├── alembic.ini
├── requirements.txt
├── .gitignore
└── README.md
```

---

# API Versioning

The API is versioned under:

```text
/api/v1
```

Major API domains include:

```text
/api/v1/auth
/api/v1/users
/api/v1/ai
/api/v1/conversations
/api/v1/documents
/api/v1/embeddings
/api/v1/rag
/api/v1/llm
```

This provides a stable namespace for future API versions.

---

# Authentication

Authentication is based on JWT access tokens and refresh tokens.

## Registration

```http
POST /api/v1/auth/register
```

## Login

```http
POST /api/v1/auth/login
```

## Refresh

```http
POST /api/v1/auth/refresh
```

## Logout

```http
POST /api/v1/auth/logout
```

Protected requests use:

```http
Authorization: Bearer <access-token>
```

---

# Current User

The authenticated user can be retrieved through:

```http
GET /api/v1/users/me
```

The endpoint is protected by the authentication dependency.

The backend returns the authenticated `User` represented by the validated access token.

---

# User Management

The user domain provides:

```http
GET    /api/v1/users/me
PATCH  /api/v1/users/me

GET    /api/v1/users
POST   /api/v1/users

GET    /api/v1/users/{user_id}
PATCH  /api/v1/users/{user_id}

PATCH  /api/v1/users/{user_id}/role
PATCH  /api/v1/users/{user_id}/activate
PATCH  /api/v1/users/{user_id}/deactivate

DELETE /api/v1/users/{user_id}
```

Administrative operations are protected using authorization dependencies.

---

# Role-Based Access Control

The platform currently supports:

```text
user
admin
```

The backend provides authorization dependencies for operations such as:

```text
require_admin
require_self_or_admin
get_current_user
```

The frontend can hide or display functionality based on role, but the backend always enforces the actual authorization rules.

---

# Password Management

The backend supports three password workflows.

## Forgot Password

```http
POST /api/v1/auth/password/forgot
```

The API intentionally returns a generic response so that users cannot easily determine whether an email address belongs to an account.

## Reset Password

```http
POST /api/v1/auth/password/reset
```

## Change Password

```http
POST /api/v1/auth/password/change
```

Passwords are stored as hashes and are never stored as plaintext.

---

# Email Verification

Email verification is supported through:

```http
POST /api/v1/auth/email/verify
POST /api/v1/auth/email/resend-verification
```

The verification process uses a time-limited verification token.

Production email delivery uses the Resend HTTP API rather than depending on direct SMTP connectivity from the cloud runtime.

---

# RAG Architecture

Retrieval-Augmented Generation is one of the core capabilities of the backend.

The general pipeline is:

```text
Document
   │
   ▼
Text Extraction
   │
   ▼
Chunking
   │
   ▼
Embedding Generation
   │
   ▼
PostgreSQL + pgvector
   │
   │
   │
User Question
   │
   ▼
Query Embedding
   │
   ▼
Vector Similarity Search
   │
   ▼
Relevant Chunks
   │
   ▼
Context Construction
   │
   ▼
LLM
   │
   ▼
Grounded Response
```

---

# Document Processing

Documents pass through a processing pipeline before becoming searchable.

Conceptually:

```text
Upload
  │
  ▼
Validation
  │
  ▼
Text Extraction
  │
  ▼
Chunking
  │
  ▼
Embedding
  │
  ▼
Vector Storage
  │
  ▼
Available for Retrieval
```

The document domain tracks document metadata and processing state.

---

# Chunking

The current chunking strategy is approximately:

```text
Chunk size: 1000
Overlap:    200
```

The overlap helps preserve semantic continuity between adjacent chunks.

Chunking parameters can be tuned as retrieval evaluation develops.

---

# Embeddings

The embedding layer converts text into numerical vectors.

The current architecture uses Gemini embeddings with a 768-dimensional vector representation.

Conceptually:

```text
Text
 │
 ▼
Embedding Model
 │
 ▼
768-dimensional vector
 │
 ▼
pgvector
```

Both document chunks and user queries can be embedded into the same vector space.

---

# Vector Database

PostgreSQL is used as both the transactional database and vector store.

The `pgvector` extension enables semantic similarity search.

This allows the application to keep:

```text
Users
Documents
Conversations
Messages
Document Chunks
Embeddings
```

within the same primary database architecture.

---

# Database Models

Important database entities include:

```text
User

RefreshToken
PasswordResetToken
EmailVerificationToken

Conversation
Message

Document
DocumentChunk
DocumentType
DocumentStatus
```

The exact schema evolves through Alembic migrations.

---

# Database Migrations

Alembic manages schema changes.

Apply all migrations:

```bash
python -m alembic upgrade head
```

Create a migration:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Review generated migrations before applying them to production.

---

# Local Development

## Requirements

Install:

- Python
- PostgreSQL
- Git
- A PostgreSQL database with `pgvector` support

---

## Clone repository

```bash
git clone https://github.com/calvinoke/Backend-Enterprise-ai-app.git
cd Backend-Enterprise-ai-app
```

---

## Create virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Configure the required backend environment variables.

Example:

```env
DATABASE_URL=

JWT_SECRET_KEY=

GEMINI_API_KEY=
GROQ_API_KEY=

RESEND_API_KEY=

EMAIL_FROM=
FRONTEND_URL=

APP_ENV=development
```

The actual required variables should match the application's configuration implementation.

Never commit actual values to Git.

---

# Database Setup

Create the PostgreSQL database and ensure the `pgvector` extension is available.

The application requires vector support for semantic retrieval.

After configuring `DATABASE_URL`:

```bash
python -m alembic upgrade head
```

---

# Run the Backend

Start FastAPI locally:

```bash
uvicorn app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# API Testing

FastAPI provides interactive Swagger documentation.

Local:

```text
http://127.0.0.1:8000/docs
```

Production:

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

Swagger can be used to test:

- Authentication
- Users
- Documents
- RAG
- AI
- Conversations
- LLM endpoints

Protected endpoints require a valid bearer access token.

---

# Production Deployment

The backend is deployed on Render.

The production service runs the application using:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This ensures that database migrations are applied before the API server starts.

Production URL:

```text
https://backend-enterprise-ai-app.onrender.com
```

---

# Deployment Architecture

```text
                    Internet
                       │
                       ▼
              ┌─────────────────┐
              │     Vercel      │
              │ React Frontend  │
              └────────┬────────┘
                       │ HTTPS
                       ▼
              ┌─────────────────┐
              │     Render      │
              │ FastAPI Backend │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       PostgreSQL          AI Providers
       + pgvector          │
                           ├── Embeddings
                           └── LLM
```

---

# CORS

The backend is configured to allow the production frontend to communicate with the API.

Production frontend:

```text
https://enterprise-ai-frontend-nine.vercel.app
```

CORS should remain restricted to known application origins in production.

Avoid using unrestricted wildcard origins when authenticated requests are involved.

---

# AI Services

The backend separates AI functionality into dedicated modules.

The architecture allows the application to integrate:

- Embedding providers
- LLM providers
- Retrieval services
- RAG orchestration
- Future AI agents

Conceptually:

```text
                 AI Service Layer
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
      Embeddings      RAG           LLM
          │             │             │
          ▼             ▼             ▼
       Gemini        pgvector       Groq
```

This separation makes it possible to change providers without rewriting the entire application.

---

# Conversations

The conversation domain provides the foundation for persistent AI interactions.

Conceptually:

```text
Conversation
 │
 ├── User Message
 ├── Assistant Message
 ├── User Message
 └── Assistant Message
```

The architecture can support future functionality such as:

- Conversation history
- Conversation search
- Context-aware conversations
- Persistent AI sessions
- Source-aware responses
- Streaming responses

---

# Logging

The application includes structured logging during application and router initialization.

Important startup events include:

```text
router_import_start
router_import_success
all_api_routers_registered
```

This helps diagnose deployment and application startup issues.

---

# API Router Architecture

The central API router registers application domains.

Conceptually:

```python
api_router.include_router(
    auth_router,
    prefix="/auth",
)

api_router.include_router(
    users_router,
)

api_router.include_router(
    ai_router,
    prefix="/ai",
)

api_router.include_router(
    conversation_router,
    prefix="/conversations",
)
```

The users router already owns the `/users` prefix and therefore should not receive another `/users` prefix when registered.

This prevents accidental paths such as:

```text
/users/users/me
```

and ensures the intended endpoint remains:

```text
/api/v1/users/me
```

---

# Security

Security is a fundamental part of the backend architecture.

## Secrets

Never commit:

```text
.env
API keys
JWT secrets
Database passwords
Refresh tokens
Access tokens
Cloud credentials
Email API keys
```

## Authentication

Protected endpoints require authentication.

## Authorization

Administrative endpoints enforce role-based permissions at the backend.

## Passwords

Passwords are stored using secure password hashing.

## Password Reset

Password reset responses are designed to avoid unnecessary account enumeration.

## CORS

Production CORS configuration should only allow trusted frontend origins.

---

# Recommended Production Practices

Before operating the platform at enterprise scale, additional controls should be introduced, including:

- Rate limiting
- Automated security testing
- Dependency vulnerability scanning
- Centralized audit logging
- Secret rotation
- Database backups
- Database monitoring
- API monitoring
- Error tracking
- Request tracing
- Background job processing
- File scanning
- Upload size limits
- Content-type validation
- Stronger authorization policies
- Multi-tenancy isolation

---

# Development Workflow

Recommended development cycle:

```text
1. Define feature
2. Update database models if required
3. Create migration
4. Implement service logic
5. Implement API route
6. Test locally
7. Test Swagger endpoint
8. Integrate frontend
9. Run production build
10. Deploy
11. Test production
```

Example Git workflow:

```bash
git checkout -b feature/my-feature

git add .

git commit -m "feat: add my feature"

git push origin feature/my-feature
```

---

# Current Platform Capabilities

The backend currently provides the foundation for:

- User registration
- User authentication
- JWT access tokens
- Refresh tokens
- Logout
- Current-user retrieval
- User profile updates
- Role-based authorization
- Administrator user management
- Password changes
- Password resets
- Email verification
- Document management
- Document chunking
- Embedding generation
- Vector search
- RAG
- AI services
- LLM integration
- Conversations
- Production deployment

---

# Roadmap

Future backend development includes:

- [ ] Comprehensive automated test suite
- [ ] Integration tests
- [ ] End-to-end API tests
- [ ] Advanced RAG evaluation
- [ ] Hybrid search
- [ ] Retrieval reranking
- [ ] Source attribution
- [ ] Streaming LLM responses
- [ ] Background document processing
- [ ] OCR
- [ ] More document formats
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Usage tracking
- [ ] Multi-tenancy
- [ ] Organization management
- [ ] Fine-grained permissions
- [ ] SSO
- [ ] Enterprise identity providers
- [ ] AI agents
- [ ] Tool calling
- [ ] External knowledge connectors
- [ ] Advanced observability
- [ ] Model routing
- [ ] AI provider failover
- [ ] Horizontal scaling

---

# Frontend

The backend is consumed by the Enterprise AI frontend.

Frontend repository:

https://github.com/calvinoke/enterprise-ai-frontend

Production frontend:

```text
https://enterprise-ai-frontend-nine.vercel.app
```

---

# API Documentation

## Swagger UI

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

## OpenAPI

```text
https://backend-enterprise-ai-app.onrender.com/openapi.json
```

---

# License

This project is currently under active development.

A formal license should be added before distributing the project as an open-source product.

---

# Project Vision

The backend is being developed as the foundation for a secure enterprise AI platform.

The long-term architecture is intended to support:

```text
                  Enterprise AI Backend
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
 Authentication       Knowledge             AI
 & Authorization        Layer              Layer
       │                  │                  │
       ▼                  ▼                  ▼
     Users            Documents            RAG
     Roles             Chunks              LLM
     Sessions          Embeddings          Agents
     Permissions       pgvector            Tools
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                  Enterprise AI APIs
```

The goal is to provide a secure, modular and extensible foundation for building enterprise-grade AI applications.
