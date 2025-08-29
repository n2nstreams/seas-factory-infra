# SaaS Factory - Complete Tech Stack Documentation

## Overview
This document provides a comprehensive analysis of the entire tech stack used in the SaaS Factory project, covering frontend, backend, containerization, and Google Cloud Platform (GCP) infrastructure.

---

## 🎨 Frontend Technology Stack

### Core Framework & Runtime
- **React 19.1.0** - Modern React with latest features and performance improvements
- **TypeScript 5.8.3** - Strong typing and enhanced developer experience
- **Vite 7.0.0** - Fast build tool and development server with HMR

### UI Component Library
- **Radix UI** - Headless, accessible component primitives
  - `@radix-ui/react-accordion` - Collapsible content sections
  - `@radix-ui/react-dialog` - Modal dialogs and overlays
  - `@radix-ui/react-label` - Form labels with accessibility
  - `@radix-ui/react-scroll-area` - Custom scrollable areas
  - `@radix-ui/react-separator` - Visual dividers
  - `@radix-ui/react-slot` - Component composition utility
  - `@radix-ui/react-switch` - Toggle switches
  - `@radix-ui/react-tabs` - Tabbed interface components

### Styling & Design System
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
  - Custom color palette with stone and green themes
  - Glassmorphism design elements with backdrop blur
  - Enhanced typography scale and spacing
  - Custom shadows and animations
- **CSS Variables** - Dynamic theming support
- **PostCSS 8.5.6** - CSS processing and optimization
- **Autoprefixer 10.4.21** - Vendor prefix automation

### State Management & Data Fetching
- **React Router DOM 7.8.0** - Client-side routing and navigation
- **WebSocket Support** - Real-time communication capabilities
- **Custom API Client** - Tenant-aware HTTP client with authentication

### Development Tools
- **ESLint 9.29.0** - Code quality and consistency
- **TypeScript ESLint** - TypeScript-specific linting rules
- **React Hooks ESLint Plugin** - React best practices enforcement

### Additional Libraries
- **Lucide React 0.525.0** - Icon library
- **Class Variance Authority 0.7.1** - Component variant management
- **Clsx 2.1.1** - Conditional className utility
- **Tailwind Merge 3.3.1** - Tailwind class merging utility
- **Recharts 3.1.0** - Chart and data visualization
- **GrowthBook React 1.6.0** - Feature flag and A/B testing
- **Stripe.js 7.5.0** - Payment processing integration

---

## 🚀 Backend Technology Stack

### Core Web Framework
- **FastAPI 0.115.14** - Modern, fast web framework for building APIs
- **Uvicorn 0.34.0** - ASGI server for running FastAPI applications
- **Starlette 0.46.2** - ASGI toolkit and framework

### Data Validation & Serialization
- **Pydantic 2.11.1** - Data validation using Python type annotations
- **Pydantic Settings 2.7.0** - Settings management with validation

### Database & ORM
- **SQLAlchemy 2.0.36** - SQL toolkit and Object-Relational Mapping
- **Psycopg2 Binary 2.9.9** - PostgreSQL adapter for Python
- **AsyncPG 0.29.0** - Async PostgreSQL driver
- **Redis 5.2.0** - In-memory data structure store for caching

### Authentication & Security
- **Python JOSE 3.3.0** - JavaScript Object Signing and Encryption
- **Passlib 1.7.4** - Password hashing library with bcrypt
- **Cryptography 45.0.5** - Cryptographic recipes and primitives
- **BCrypt 4.1.2** - Password hashing for secure storage

### HTTP & WebSocket
- **HTTPX 0.28.1** - Fully featured HTTP client for Python
- **WebSockets 13.0** - WebSocket client and server library
- **Requests 2.32.0** - HTTP library for Python

### Background Tasks & Queues
- **Celery 5.4.0** - Distributed task queue system

### External Service Integrations
- **Stripe 12.3.0** - Payment processing and billing
- **SendGrid 6.11.0** - Email delivery service

### AI & Machine Learning
- **OpenAI 1.93.0** - GPT-4o model access
- **Google GenAI 1.24.0** - Google's generative AI models
- **Vertex AI 1.38.1** - Google Cloud AI platform integration
- **LangGraph 0.5.1** - AI agent orchestration framework
- **LangSmith 0.4.4** - LLM observability and debugging
- **MCP 1.10.1** - Model Context Protocol for AI agents

### Google Cloud Platform Services
- **Google Cloud Logging 3.12.1** - Centralized logging
- **Google Cloud Pub/Sub 2.31.1** - Messaging and streaming
- **Google Cloud Storage 2.19.0** - Object storage
- **Google Cloud AI Platform 1.101.0** - Machine learning services
- **Google Cloud Secret Manager 2.24.0** - Secret management
- **Google Cloud Monitoring 2.27.2** - Infrastructure monitoring
- **Google Cloud Error Reporting 1.10.0** - Error tracking
- **Google Cloud Deploy 2.7.1** - Continuous deployment
- **Google Auth 2.40.3** - Authentication library

### Development & Testing
- **Pytest 8.3.4** - Testing framework
- **Pytest AsyncIO 0.24.0** - Async testing support
- **Pytest Coverage 6.1.0** - Code coverage measurement
- **Python Dotenv 1.0.1** - Environment variable management
- **Black 23.11.0** - Code formatting
- **Flake8 6.1.0** - Linting and style checking
- **MyPy 1.7.1** - Static type checking
- **Alembic 1.13.1** - Database migration management

### Utilities & Helpers
- **Python JSON Logger 2.0.7** - Structured logging
- **PyYAML 6.0.2** - YAML parser and emitter
- **Python Multipart 0.0.17** - Multipart form data parsing
- **Email Validator 2.2.0** - Email address validation
- **Jinja2 3.1.6** - Template engine
- **Click 8.2.1** - Command line interface creation
- **Aiofiles 24.1.0** - Async file operations
- **Python Decouple 3.8** - Configuration management
- **Diskcache 5.6.3** - Persistent caching
- **Flaml 2.3.5** - Fast and lightweight machine learning
- **Graphviz 0.21** - Graph visualization

---

## 🐳 Containerization & Orchestration

### Docker Configuration
- **Multi-stage Builds** - Optimized production images
- **Alpine Linux Base** - Lightweight container images
- **Python 3.12-slim** - Backend service base images
- **Node.js 22-alpine** - Frontend build environment
- **Nginx 1.25-alpine** - Frontend runtime server

### Container Architecture
- **API Gateway Container** - FastAPI service with uvicorn
- **Frontend Container** - Static files served by Nginx
- **Orchestrator Container** - Project orchestration service
- **Agent Containers** - Specialized AI agent services
- **QA Testing Container** - Automated testing and security scanning
- **DevOps Container** - Infrastructure management and monitoring
- **Secrets Manager Container** - Multi-cloud secret management

### Container Orchestration
- **Docker Compose** - Local development and testing
- **Cloud Run** - Serverless container deployment
- **Artifact Registry** - Container image storage

---

## ☁️ Google Cloud Platform (GCP) Infrastructure

### Compute & Serverless
- **Cloud Run v2** - Serverless container platform
  - API Gateway service (api_gateway)
  - Frontend web application (web-frontend)
  - Auto-scaling with 0-10 instances
  - Resource limits: 1 CPU, 512Mi memory

### Networking & Load Balancing
- **VPC Network** - Custom virtual private cloud
  - Public subnet: 10.10.10.0/24
  - Private subnet: 10.10.20.0/24
  - Global routing with flow logs
- **Cloud NAT** - Network address translation
  - All subnetwork IP ranges
  - Error-only logging
- **Load Balancer** - Global HTTP(S) load balancer
  - Custom domain support (forge95.com)
  - SSL certificate management
  - HTTP to HTTPS redirects
  - SPA fallback routing

### Domain & SSL Management
- **Custom Domains** - forge95.com with subdomains
  - API subdomain: api.forge95.com
  - Frontend subdomain: www.forge95.com
  - Apex domain mapping
- **Managed SSL Certificates** - Automatic certificate provisioning
- **Domain Mappings** - Cloud Run domain routing

### Security & Identity
- **Workload Identity** - GitHub Actions OIDC authentication
  - GitHub repository integration
  - Service account impersonation
- **Service Accounts** - Fine-grained access control
  - Gateway service account
  - GitHub Actions deployer
  - Orchestrator service account
- **IAM Roles** - Role-based access control
  - Cloud Run admin
  - Artifact Registry writer
  - Cloud SQL client
  - Storage admin

### Storage & Data
- **Cloud Storage** - Object storage for UI builds
  - Staging bucket for build artifacts
  - 14-day lifecycle management
  - CORS configuration for web access
- **Secret Manager** - Secure secret storage
  - OpenAI API key management
  - Service account access control

### Monitoring & Observability
- **Cloud Logging** - Centralized log management
- **Cloud Monitoring** - Infrastructure metrics
- **Error Reporting** - Application error tracking
- **OpenTelemetry** - Distributed tracing support
- **Custom Metrics** - Application-specific monitoring
- **Health Checks** - Service availability monitoring
- **Performance Monitoring** - Real-time performance analysis

### CI/CD & Deployment
- **GitHub Actions Integration** - Automated deployments
- **Cloud Build** - Container image building
- **Artifact Registry** - Container image storage
- **Terraform** - Infrastructure as Code

---

## 🔧 Development & DevOps Tools

### Version Control
- **Git** - Source code version control
- **GitHub** - Repository hosting and collaboration

### Infrastructure as Code
- **Terraform** - GCP resource provisioning
- **Terraform Modules** - Reusable infrastructure components
- **State Management** - GCS backend for state storage

### CI/CD Pipeline
- **GitHub Actions** - Automated workflows
- **Cloud Build** - Container building and deployment
- **Workload Identity** - Secure GCP authentication

### Testing & Quality Assurance
- **Pytest** - Python testing framework
- **Playwright** - End-to-end testing and automation
- **ESLint** - JavaScript/TypeScript code quality
- **TypeScript** - Static type checking
- **OWASP ZAP** - Dynamic application security testing (DAST)
- **Snyk** - Static application security testing (SAST)
- **License Scanning** - Automated license compliance checking
- **Security Scanning** - Vulnerability assessment and reporting

### Monitoring & Alerting
- **Cloud Monitoring** - GCP native monitoring
- **Custom Metrics** - Application-specific monitoring
- **Health Checks** - Service availability monitoring
- **Cost Monitoring** - Budget and spending alerts
- **Load Testing** - K6 performance testing framework
- **Database Failover Monitoring** - Automated failover detection
- **Status Page Management** - Public incident communication
- **Rollback Automation** - Error budget-based rollback triggers

---

## 🏗️ Architecture Patterns

### Microservices Architecture
- **API Gateway Pattern** - Centralized request routing
- **Service Mesh** - Inter-service communication
- **Event-Driven Architecture** - Asynchronous processing

### Security Patterns
- **Tenant Isolation** - Multi-tenant data separation
- **OAuth 2.0** - Authentication and authorization
- **JWT Tokens** - Stateless authentication
- **Secret Management** - Secure credential storage

### Performance Patterns
- **Caching Strategy** - Redis-based caching
- **Load Balancing** - Global load distribution
- **Auto-scaling** - Dynamic resource allocation
- **CDN Integration** - Content delivery optimization
- **Load Testing** - K6-based performance validation
- **Database Failover** - Automated read replica promotion
- **Performance Monitoring** - Real-time metrics analysis

### Data Patterns
- **Repository Pattern** - Data access abstraction
- **Unit of Work** - Transaction management
- **Event Sourcing** - Audit trail and history
- **CQRS** - Command Query Responsibility Segregation
- **Multi-Cloud Secret Management** - GCP, AWS, Azure secret rotation
- **Tenant Isolation** - Multi-tenant data separation
- **Database Migration** - Alembic-based schema management

---

## 📊 Technology Stack Summary

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Frontend** | React | 19.1.0 | UI Framework |
| **Frontend** | TypeScript | 5.8.3 | Type Safety |
| **Frontend** | Vite | 7.0.0 | Build Tool |
| **Frontend** | Tailwind CSS | 3.4.17 | Styling |
| **Frontend** | Radix UI | Latest | Components |
| **Backend** | FastAPI | 0.115.14 | API Framework |
| **Backend** | SQLAlchemy | 2.0.36 | ORM |
| **Backend** | PostgreSQL | - | Database |
| **Backend** | Redis | 5.2.0 | Caching |
| **Container** | Docker | Latest | Containerization |
| **Container** | Cloud Run | v2 | Serverless |
| **Cloud** | GCP | - | Infrastructure |
| **Cloud** | Terraform | - | IaC |
| **DevOps** | GitHub Actions | - | CI/CD |
| **DevOps** | Cloud Build | - | Building |
| **DevOps** | K6 | - | Load Testing |
| **DevOps** | OWASP ZAP | - | Security Testing |
| **DevOps** | Playwright | - | E2E Testing |
| **DevOps** | Alembic | 1.13.1 | Database Migration |
| **DevOps** | Black/Flake8/MyPy | Latest | Code Quality |

---

## 🚀 Deployment Architecture

### Production Environment
- **Region**: us-central1
- **Project ID**: summer-nexus-463503-e1
- **Domain**: forge95.com
- **Load Balancer**: Global HTTP(S) with SSL
- **Auto-scaling**: 0-10 instances per service
- **Monitoring**: Comprehensive GCP monitoring stack

### Development Environment
- **Local Development**: Docker Compose
- **Hot Reloading**: Vite dev server
- **Database**: Local PostgreSQL
- **Testing**: Pytest with coverage

---

## 📈 Scalability & Performance

### Horizontal Scaling
- **Cloud Run Auto-scaling** - Automatic instance scaling
- **Load Balancer Distribution** - Global traffic distribution
- **Database Connection Pooling** - Efficient database connections

### Performance Optimization
- **Redis Caching** - Fast data access
- **CDN Integration** - Static asset delivery
- **Database Indexing** - Query optimization
- **Async Processing** - Non-blocking operations
- **Load Testing** - K6-based performance validation
- **Database Failover** - Automated read replica promotion
- **Performance Monitoring** - Real-time metrics analysis
- **Auto-scaling** - Cloud Run automatic scaling

### Monitoring & Observability
- **Distributed Tracing** - Request flow tracking
- **Custom Metrics** - Business-specific monitoring
- **Alerting** - Proactive issue detection
- **Log Aggregation** - Centralized logging
- **AIOps Integration** - AI-powered anomaly detection
- **Status Page Management** - Public incident communication
- **Cost Guard Monitoring** - Budget alert automation
- **Database Health Monitoring** - Failover detection and management

## 🤖 AI Agents & Specialized Services

### Project Orchestration
- **Project Orchestrator** - AI-powered project coordination and management
- **Idea Generation Agent** - Creative concept development and validation
- **Development Agent** - Code generation and technical implementation
- **QA Agent** - Automated testing and quality assurance
- **Design Agent** - UI/UX design and prototyping
- **Marketing Agent** - Content creation and copywriting
- **Support Agent** - FAQ generation and customer support

### Operations & DevOps Agents
- **AIOps Agent** - AI-driven operations with anomaly detection
- **DevOps Agent** - Infrastructure management and Terraform review
- **Health Monitoring Agent** - Service health and resource monitoring
- **Database Failover Agent** - Automated database failover management
- **Rollback Controller** - Error budget-based deployment rollbacks
- **Status Page Agent** - Incident communication and status management
- **Cost Guard Agent** - Budget monitoring and cost optimization
- **Secrets Manager Agent** - Multi-cloud secret rotation and management

### Security & Testing Agents
- **Security Agent** - Vulnerability assessment and security scanning
- **License Scan Agent** - Open source license compliance checking
- **ZAP Penetration Agent** - Dynamic application security testing
- **Playwright Generator** - Automated test case generation
- **Review Agent** - Code review and quality assessment

### Specialized Tools
- **K6 Load Testing** - Performance testing and validation
- **OWASP ZAP** - Security vulnerability scanning
- **Terraform Diff Review** - AI-powered infrastructure change analysis
- **Multi-Cloud Support** - GCP, AWS, and Azure integration
- **Workload Identity** - GitHub Actions OIDC authentication

---

*This document provides a comprehensive overview of the SaaS Factory tech stack. For specific implementation details, refer to the individual component documentation and source code.*
