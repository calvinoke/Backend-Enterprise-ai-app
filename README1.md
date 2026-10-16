# Enterprise AI Platform

> A full-stack enterprise AI and Retrieval-Augmented Generation (RAG) platform for secure document-based knowledge discovery, conversational AI, user management, and enterprise knowledge workflows.

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)](https://github.com/calvinoke/enterprise-ai-frontend)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-green)](https://github.com/calvinoke/Backend-Enterprise-ai-app)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)](https://www.postgresql.org/)
[![Vector Search](https://img.shields.io/badge/Vector%20Search-pgvector-purple)](https://github.com/pgvector/pgvector)
[![Deployment](https://img.shields.io/badge/Frontend-Vercel-black)](https://vercel.com/)
[![Deployment](https://img.shields.io/badge/Backend-Render-blue)](https://render.com/)

---

## Overview

**Enterprise AI Platform** is a full-stack AI application designed to provide organizations with a secure and extensible environment for interacting with enterprise knowledge using modern Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

The platform combines:

- Secure user authentication and authorization
- Enterprise user and administrator management
- Document ingestion and processing
- Text chunking and metadata management
- Semantic embeddings
- PostgreSQL with `pgvector`
- Retrieval-Augmented Generation
- Conversational AI
- LLM integration
- Password reset and account recovery
- Email verification
- Refresh-token based sessions
- Role-based access control
- RESTful APIs
- Modern React frontend
- Cloud deployment

The system is designed as a foundation that can evolve into a broader enterprise AI platform supporting internal knowledge assistants, organizational copilots, document intelligence, AI-powered search, and other AI workflows.

---

# Project Goals

The platform is being developed around several core goals:

### 1. Enterprise Knowledge Access

Allow authorized users to interact with organizational documents and knowledge using natural language rather than manually searching through large collections of files.

### 2. Grounded AI Responses

Use Retrieval-Augmented Generation to retrieve relevant enterprise knowledge before generating an AI response.

This reduces the dependence on the model's general training knowledge and allows responses to be grounded in an organization's own information.

### 3. Secure Access

Provide authentication, authorization, account management, and role-based access controls so that enterprise AI functionality is not exposed as an anonymous chatbot.

### 4. Modular Architecture

Separate authentication, users, documents, embeddings, retrieval, conversations, and LLM functionality into independent backend modules.

### 5. Production-Oriented Deployment

The application is designed to run as separate frontend and backend services:

```text
React / Vite frontend
        |
        | HTTPS / REST API
        v
FastAPI backend
        |
        +--------------------+
        |                    |
        v                    v
 PostgreSQL             LLM / AI Services
        |
        v
     pgvector
```

---

# System Architecture

The platform consists of two primary repositories.

## Frontend

Repository:

**Enterprise AI Frontend**

https://github.com/calvinoke/enterprise-ai-frontend

The frontend is implemented using:

- React
- TypeScript
- Vite
- Axios
- Modern component-based UI architecture
- Client-side authentication state
- REST API integration

Production deployment:

```text
https://enterprise-ai-frontend-nine.vercel.app
```

The frontend communicates with the backend exclusively through the REST API.

---

## Backend

Repository:

**Enterprise AI Backend**

https://github.com/calvinoke/Backend-Enterprise-ai-app

The backend is implemented using:

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- PostgreSQL `pgvector`
- Alembic
- Async database access
- JWT authentication
- Refresh tokens
- Password hashing
- RAG services
- Embedding services
- LLM services
- Email services

Production deployment:

```text
https://backend-enterprise-ai-app.onrender.com
```

Interactive API documentation:

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

---

# Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React | User interface |
| TypeScript | Static typing |
| Vite | Development/build tooling |
| Axios | HTTP client |
| React-based component architecture | UI composition |
| Vercel | Production deployment |

---

## Backend

| Technology | Purpose |
|---|---|
| Python | Application language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM / database access |
| asyncpg | Asynchronous PostgreSQL driver |
| PostgreSQL | Primary relational database |
| pgvector | Vector similarity search |
| Alembic | Database migrations |
| JWT | Authentication |
| Password hashing | Credential protection |
| HTTPX | External HTTP integrations |
| Resend | Transactional email delivery |
| Render | Backend deployment |

---

## AI / RAG Layer

The AI layer is designed around the following pipeline:

```text
User Question
      |
      v
Question Processing
      |
      v
Embedding Generation
      |
      v
Vector Similarity Search
      |
      v
Relevant Document Chunks
      |
      v
Context Construction
      |
      v
LLM
      |
      v
Grounded AI Response
```

The system uses vector embeddings to represent document chunks and user queries in the same semantic space.

The vector representation is stored in PostgreSQL using `pgvector`.

---

# Retrieval-Augmented Generation

## What is RAG?

Retrieval-Augmented Generation combines information retrieval with generative AI.

Instead of asking an LLM to answer a question entirely from its pretrained knowledge, the application first retrieves relevant information from an organization's knowledge base.

The retrieved information is then supplied to the LLM as context.

Conceptually:

```text
                ┌─────────────────┐
                │   User Question │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │ Query Embedding │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │ Vector Search   │
                │   PostgreSQL    │
                │   + pgvector    │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │ Relevant Chunks │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │ Context Builder │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │      LLM        │
                └────────┬────────┘
                         │
                         v
                ┌─────────────────┐
                │ Grounded Answer │
                └─────────────────┘
```

---

# Document Processing Pipeline

Documents are processed through a multi-stage ingestion pipeline.

```text
Document Upload
       |
       v
Document Validation
       |
       v
Document Processing
       |
       v
Text Extraction
       |
       v
Text Chunking
       |
       v
Embedding Generation
       |
       v
Vector Storage
       |
       v
Ready for Retrieval
```

The application maintains document and chunk metadata so that retrieved content can be associated with its originating document.

The current chunking strategy has been designed around approximately:

```text
Chunk size: 1000
Overlap:    200
```

This can be adjusted as retrieval evaluation evolves.

---

# Embeddings

The embedding layer converts text into numerical vector representations.

Conceptually:

```text
"Enterprise security policy"
             |
             v
       Embedding Model
             |
             v
      [0.021, -0.44, ...]
             |
             v
        pgvector
```

The current implementation uses Gemini embeddings with a 768-dimensional vector representation.

Embeddings are used for:

- Document chunks
- User queries
- Semantic similarity search
- RAG retrieval

---

# Vector Search

The platform uses PostgreSQL with the `pgvector` extension rather than maintaining a separate vector database.

This provides a unified data architecture:

```text
PostgreSQL
│
├── Users
├── Refresh Tokens
├── Password Reset Tokens
├── Email Verification Tokens
├── Conversations
├── Messages
├── Documents
├── Document Chunks
└── Vector Embeddings
```

This approach keeps transactional and semantic data in the same database while allowing the platform to evolve toward more sophisticated retrieval strategies.

---

# Authentication

Authentication is based on JWT access tokens and refresh tokens.

The authentication flow is:

```text
User
 |
 | Login
 v
FastAPI
 |
 | Validate credentials
 v
Access Token + Refresh Token
 |
 v
Frontend
 |
 | Authorization: Bearer <access-token>
 v
Protected API
```

The platform supports:

- User registration
- User login
- JWT access tokens
- Refresh tokens
- Logout
- Current-user retrieval
- Password changes
- Password reset
- Email verification
- Resending verification emails

---

# Authorization and Roles

The platform supports role-based access control.

Current roles include:

```text
user
admin
```

Regular users can access their own profile and authorized application functionality.

Administrators can perform additional user-management operations.

Administrative functionality includes:

- Create users
- List users
- Retrieve users
- Update users
- Change user roles
- Activate users
- Deactivate users
- Delete users

Authorization is enforced by backend dependencies rather than relying solely on frontend UI restrictions.

---

# User Management

The users API exposes functionality for:

```text
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

Administrative operations are protected by backend authorization dependencies.

---

# Password Management

The authentication system supports:

### Forgot Password

```text
POST /api/v1/auth/password/forgot
```

### Reset Password

```text
POST /api/v1/auth/password/reset
```

### Change Password

```text
POST /api/v1/auth/password/change
```

The password recovery flow is designed to avoid exposing whether a particular email address exists in the system.

---

# Email Verification

The platform supports email verification during account onboarding.

Relevant endpoints include:

```text
POST /api/v1/auth/email/verify
POST /api/v1/auth/email/resend-verification
```

Production email delivery is designed around the Resend HTTP API.

This avoids relying on direct SMTP connectivity from the cloud deployment environment.

The frontend receives the verification workflow through the configured frontend URL.

---

# API Structure

The backend API is versioned under:

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

This separation allows each domain to evolve independently.

---

# Backend Architecture

The backend is organized around domain modules.

A simplified structure is:

```text
backend/
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
│   ├── ai/
│   │   └── ...
│   │
│   ├── database/
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
└── README.md
```

The actual repository may evolve as additional modules and services are introduced.

---

# Frontend Architecture

The frontend follows a modular React/TypeScript structure.

Conceptually:

```text
enterprise-ai-frontend/
│
├── public/
│
├── src/
│   ├── api/
│   ├── components/
│   ├── contexts/
│   ├── pages/
│   ├── types/
│   ├── services/
│   └── ...
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

The frontend is responsible for:

- Presentation
- Navigation
- Authentication state
- User interaction
- API communication
- Form validation
- Rendering AI conversations
- User management interfaces
- Document-related interfaces

The backend remains the source of truth for authorization, validation, persistence, and business rules.

---

# API Client

The frontend communicates with the backend using a centralized Axios API client.

The production architecture is:

```text
Browser
   |
   v
Vercel
   |
   | HTTPS
   v
Render
   |
   v
FastAPI
```

The frontend API base URL is configured through environment variables rather than hard-coded throughout the application.

---

# Database

PostgreSQL is the primary persistence layer.

The application uses asynchronous SQLAlchemy database access.

Important entities include:

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

The database schema is managed using Alembic migrations.

---

# Database Migrations

Alembic is used to manage schema evolution.

Typical migration workflow:

```bash
python -m alembic upgrade head
```

New migrations can be created with:

```bash
python -m alembic revision --autogenerate -m "describe change"
```

Migrations should be reviewed before being applied to production.

---

# Environment Configuration

Sensitive configuration must never be committed to Git.

Create a local environment configuration containing values appropriate for the environment.

Typical backend configuration includes:

```env
DATABASE_URL=
JWT_SECRET_KEY=

GEMINI_API_KEY=
GROQ_API_KEY=

RESEND_API_KEY=

EMAIL_FROM=
FRONTEND_URL=

APP_ENV=
```

The exact variable names should always match the configuration used by the current backend implementation.

---

# Security

Security is a core concern of the platform.

The project follows several principles:

### Secrets

API keys, database credentials, JWT secrets, email credentials, and other secrets must be stored in environment variables or a managed secret store.

Never commit:

```text
.env
API keys
JWT secrets
database passwords
refresh tokens
access tokens
SMTP credentials
```

### Authentication

Protected endpoints require authentication.

### Authorization

Administrative operations are protected at the backend.

### Password Security

Passwords are never stored as plaintext.

### Account Enumeration Protection

Password-reset and email-verification workflows are designed to avoid unnecessarily revealing whether an account exists.

### CORS

The backend is configured to permit the deployed frontend origin rather than allowing unrestricted browser access.

---

# Deployment

The current production architecture uses:

```text
                 ┌──────────────────────┐
                 │       Browser        │
                 └──────────┬───────────┘
                            │
                            v
                 ┌──────────────────────┐
                 │        Vercel        │
                 │   React Frontend     │
                 └──────────┬───────────┘
                            │ HTTPS
                            v
                 ┌──────────────────────┐
                 │        Render        │
                 │    FastAPI Backend   │
                 └──────────┬───────────┘
                            │
                            v
                 ┌──────────────────────┐
                 │      PostgreSQL      │
                 │       pgvector       │
                 └──────────────────────┘

                       + AI Services
                       + Email Services
```

## Production Frontend

```text
https://enterprise-ai-frontend-nine.vercel.app
```

## Production Backend

```text
https://backend-enterprise-ai-app.onrender.com
```

## API Documentation

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

---

# Running the Backend Locally

Clone the backend repository:

```bash
git clone https://github.com/calvinoke/Backend-Enterprise-ai-app.git
cd Backend-Enterprise-ai-app
```

Create a virtual environment:

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables.

Run database migrations:

```bash
python -m alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API should then be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Running the Frontend Locally

Clone the frontend repository:

```bash
git clone https://github.com/calvinoke/enterprise-ai-frontend.git
cd enterprise-ai-frontend
```

Install dependencies:

```bash
npm install
```

Configure the frontend environment variables.

Start the development server:

```bash
npm run dev
```

Vite will provide the local development URL in the terminal.

---

# Frontend Environment

The frontend should point to the backend API through an environment variable.

For example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

For production:

```env
VITE_API_BASE_URL=https://backend-enterprise-ai-app.onrender.com/api/v1
```

Do not place backend secrets or AI provider keys in frontend environment variables.

Anything prefixed with `VITE_` should be considered potentially visible to users of the application.

---

# Typical User Flow

## Registration

```text
User
 |
 | Register
 v
Frontend
 |
 v
POST /api/v1/auth/register
 |
 v
FastAPI
 |
 v
User created
 |
 v
Verification email
```

---

## Login

```text
User
 |
 | Email + Password
 v
Frontend
 |
 v
POST /api/v1/auth/login
 |
 v
FastAPI
 |
 v
Access Token
+
Refresh Token
 |
 v
Frontend Authentication State
 |
 v
GET /api/v1/users/me
```

---

## Ask a Knowledge Question

```text
User
 |
 | Question
 v
Frontend
 |
 v
FastAPI
 |
 v
RAG Pipeline
 |
 +--> Generate Query Embedding
 |
 +--> Search pgvector
 |
 +--> Retrieve Relevant Chunks
 |
 +--> Build Context
 |
 +--> Call LLM
 |
 v
Grounded Response
 |
 v
Frontend
```

---

# Conversation Architecture

The platform includes conversation-oriented entities for maintaining interactions between users and the AI system.

A conceptual conversation consists of:

```text
Conversation
│
├── User
│
└── Messages
    ├── User Message
    ├── Assistant Message
    ├── User Message
    └── Assistant Message
```

This provides the foundation for persistent AI conversations and future conversation-memory capabilities.

---

# AI Provider Architecture

The platform separates AI functionality into dedicated services.

This makes it possible to evolve the application from a single-provider implementation toward a provider-agnostic architecture.

Conceptually:

```text
Application
     |
     v
AI Service
     |
     +-------------------+
     |                   |
     v                   v
Embedding Provider    LLM Provider
     |                   |
     v                   v
Gemini Embeddings     Groq / LLM
```

This abstraction can later support additional providers without requiring the entire application to be rewritten.

---

# Observability and Logging

The backend includes structured application logging and startup/router import logging.

The API startup process records important events such as:

```text
router_import_start
router_import_success
all_api_routers_registered
```

This makes deployment and startup failures easier to diagnose.

---

# API Documentation

FastAPI automatically provides interactive OpenAPI documentation.

Production:

```text
https://backend-enterprise-ai-app.onrender.com/docs
```

Local:

```text
http://127.0.0.1:8000/docs
```

The API documentation can be used to test authenticated endpoints, inspect request/response schemas, and validate backend functionality.

---

# Testing Strategy

The project follows an incremental development and testing approach.

Each major feature should be validated at several levels:

### Backend

- Application startup
- Database connectivity
- Migration execution
- API endpoint tests
- Authentication tests
- Authorization tests
- RAG retrieval tests
- Document processing tests

### Frontend

- TypeScript compilation
- Development server
- Production build
- Authentication flow
- API integration
- Protected routes
- User management UI

### Integration

Important end-to-end flows include:

```text
Registration
    ↓
Email Verification
    ↓
Login
    ↓
Current User
    ↓
Protected Application
    ↓
Document / Knowledge Workflow
    ↓
RAG Query
    ↓
AI Response
```

---

# Current Development Status

The platform is under active development.

## Implemented Foundation

- [x] React + TypeScript frontend
- [x] FastAPI backend
- [x] PostgreSQL database
- [x] SQLAlchemy integration
- [x] Alembic migrations
- [x] pgvector support
- [x] User registration
- [x] User login
- [x] JWT authentication
- [x] Refresh tokens
- [x] Logout
- [x] Current-user endpoint
- [x] User profile management
- [x] Role-based authorization foundation
- [x] Administrator user management
- [x] Password change
- [x] Password reset workflow
- [x] Email verification workflow
- [x] Resend verification workflow
- [x] Document domain
- [x] Document chunking
- [x] Embedding domain
- [x] RAG domain
- [x] LLM domain
- [x] Conversation domain
- [x] Production frontend deployment
- [x] Production backend deployment

## In Progress / Future Enhancements

- [ ] Comprehensive automated test suite
- [ ] Advanced RAG evaluation
- [ ] Hybrid keyword + semantic retrieval
- [ ] Retrieval reranking
- [ ] Source citation UX
- [ ] Streaming LLM responses
- [ ] Advanced document ingestion
- [ ] OCR support
- [ ] Additional file formats
- [ ] Background document processing
- [ ] Enterprise audit logging
- [ ] Advanced observability
- [ ] Usage analytics
- [ ] Rate limiting
- [ ] Fine-grained permissions
- [ ] Organization / tenant support
- [ ] SSO integration
- [ ] Enterprise identity providers
- [ ] Production-grade CI/CD
- [ ] Automated end-to-end testing
- [ ] Containerized deployment
- [ ] Horizontal scaling
- [ ] Advanced caching
- [ ] RAG evaluation and benchmarking

---

# Roadmap

The long-term roadmap is organized around several stages.

## Phase 1 — Core Platform

- Authentication
- Users
- Roles
- Database
- API architecture
- Frontend foundation

## Phase 2 — Knowledge Platform

- Document upload
- Document processing
- Chunking
- Embeddings
- Vector search
- RAG

## Phase 3 — Conversational AI

- Persistent conversations
- Conversation history
- Context-aware responses
- Streaming responses
- Source citations

## Phase 4 — Enterprise Governance

- Organizations
- Multi-tenancy
- Fine-grained permissions
- Audit logs
- Usage tracking
- Administrative dashboards

## Phase 5 — Enterprise AI Platform

Potential future capabilities include:

- AI agents
- Workflow automation
- Tool calling
- Enterprise integrations
- Knowledge connectors
- SharePoint/Google Drive/OneDrive integrations
- Slack/Teams integrations
- MCP integrations
- Advanced analytics
- Evaluation pipelines
- Model routing
- Provider failover

---

# Design Principles

The project follows several architectural principles.

### Separation of Concerns

Authentication, users, documents, retrieval, embeddings, conversations, and LLM functionality are kept in separate modules.

### Backend as the Security Boundary

The frontend can hide UI controls, but the backend is responsible for enforcing authorization.

### API-First Architecture

The frontend communicates with the backend through documented REST APIs.

### Database as the Source of Truth

Persistent business data is stored in PostgreSQL rather than relying on browser state.

### Provider Abstraction

AI providers should remain replaceable wherever practical.

### Security by Default

Secrets are externalized, passwords are hashed, protected endpoints require authentication, and administrative operations require authorization.

### Incremental Development

Features are implemented and tested in small, verifiable steps before moving to the next architectural layer.

---

# Contributing

Contributions, improvements, bug reports, and architectural suggestions are welcome.

Recommended workflow:

```text
1. Fork the repository
2. Create a feature branch
3. Make the change
4. Run tests/build checks
5. Commit the changes
6. Push the branch
7. Open a Pull Request
```

Example:

```bash
git checkout -b feature/my-feature

git add .

git commit -m "feat: add my feature"

git push origin feature/my-feature
```

---

# Security Disclosure

If you discover a security vulnerability, do not publish credentials, tokens, API keys, database passwords, or other sensitive information in a public issue.

Instead, report the issue privately to the project maintainer.

Never commit:

```text
.env
.env.local
.env.production
API keys
JWT secrets
Database credentials
Cloud credentials
Private tokens
```

---

# License

This project is currently under active development.

A formal open-source license should be added before distributing the project as an open-source product.

---

# Project Repositories

## Frontend

**Enterprise AI Frontend**

https://github.com/calvinoke/enterprise-ai-frontend

## Backend

**Enterprise AI Backend**

https://github.com/calvinoke/Backend-Enterprise-ai-app

---

# Live Application

Frontend:

https://enterprise-ai-frontend-nine.vercel.app

Backend:

https://backend-enterprise-ai-app.onrender.com

API Documentation:

https://backend-enterprise-ai-app.onrender.com/docs

---

# Project Vision

The goal of Enterprise AI Platform is to move beyond a simple chatbot and provide a foundation for building secure, knowledge-grounded AI applications for organizations.

The long-term vision is an enterprise AI environment where users can securely interact with organizational knowledge, documents, workflows, and AI-powered services through a unified platform.

```text
                  ENTERPRISE AI PLATFORM
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          v                v                v
     Knowledge          AI / RAG        Enterprise
      Layer              Layer          Governance
          │                │                │
          v                v                v
     Documents         Embeddings       Users
     Chunking          Retrieval        Roles
     Metadata          LLM              Permissions
     pgvector          Conversations   Audit
          │                │                │
          └────────────────┼────────────────┘
                           │
                           v
                    Enterprise AI
                     Applications
```

**Built as an evolving foundation for secure, grounded, and extensible enterprise AI.**