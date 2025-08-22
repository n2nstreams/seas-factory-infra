# AI Task Planning Template - Python Backend Development Framework

## 1. Task Overview

### Template Name
**Template Name:** Python Backend Development Template

### Template Purpose
**Purpose:** This template will be used for creating specific Python backend development tasks, API endpoint creation, database operations, business logic implementation, and backend service development for the SaaS Factory platform. It covers FastAPI development, database modeling, authentication, and backend integration patterns.

---

## 2. Template Scope & Feature Analysis

### Feature Category
**Category:** Backend Development, API Development, Database Operations, Business Logic Implementation

### Technology & Architecture Requirements
- **Frameworks & Versions:** Python 3.12, FastAPI, SQLAlchemy, asyncpg, Pydantic
- **Language:** Python (Backend), TypeScript (Frontend integration)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** N/A (Backend-focused, but must support frontend glassmorphism design system)
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path

### Feature Requirements Analysis
This Python template needs to cover comprehensive backend development scenarios including API endpoint creation, database model development, business logic implementation, authentication and authorization, data validation, error handling, and integration with existing systems. It should follow established Python patterns and integrate with existing tenant isolation and access control systems.

---

## 3. Template Structure & Content Planning

### Template Sections to Include
**Required Sections:**
- [x] **Task Overview** - Clear title, goal, and scope definition
- [x] **Technical Requirements** - Backend, database, and integration needs
- [x] **Implementation Steps** - Phase-by-phase development plan
- [x] **Testing Strategy** - Unit, integration, and API testing requirements
- [x] **Deployment Considerations** - Backend deployment and monitoring needs
- [x] **Success Metrics** - How to measure completion and API performance

### Template Customization Points
- **Backend Scope:** Can be customized for specific backend features (CRUD operations, business logic, integrations, etc.)
- **Complexity Levels:** Can be adapted for different development complexity (simple CRUD, complex workflows, integrations)
- **Team Involvement:** Can specify which teams need to be involved (Backend, DevOps, QA)
- **Timeline:** Can be adjusted based on feature complexity and business requirements

---

## 4. Template Standards & Consistency

### Template Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Consistency Requirements:** Must maintain consistent structure and terminology across all Python development templates
- **Pattern Preservation:** Must preserve existing architectural patterns and Python development workflows
- **User Base:** Multi-tenant SaaS users with different subscription tiers (starter, pro, growth)
- **Priority:** Template reusability and consistency while maintaining Python development-specific customization

---

## 5. Template Content Requirements

### Standard Template Sections
**Every Python development template must include:**
- **Performance Standards:** API responses under 200ms, support 1000+ concurrent users per tenant
- **Security Requirements:** Tenant isolation, input validation, SQL injection prevention, use existing `access_control.py` patterns
- **Design Consistency:** N/A (Backend-focused, but must support frontend glassmorphism design system)
- **Responsive Design:** N/A (Backend-focused)
- **Theme Support:** N/A (Backend-focused, but must support frontend design system integration)

### Python Development-Specific Customization
- **API Patterns:** RESTful endpoints, GraphQL, WebSocket support
- **Database Operations:** CRUD operations, complex queries, transactions, migrations
- **Business Logic:** Workflow automation, data processing, integration logic
- **Authentication:** JWT handling, role-based access, permission management

### Technical Constraints
- [Must use existing tenant isolation system from `tenant_db.py` and `access_control.py`]
- [Cannot modify existing database tables without proper migrations in `dev/migrations/`]
- [Must maintain compatibility with existing agent architecture and orchestration patterns]
- [Must follow existing FastAPI route patterns and Pydantic models from `api_gateway/`]
- [Must use existing Python patterns and coding standards]
- [Must preserve existing database connection and transaction patterns]

---

## 6. Template Pattern Requirements

### Python Pattern Standards
**Every Python development template must include:**
- **Code Structure:** Follow PEP 8 standards, use type hints, comprehensive docstrings
- **Error Handling:** Use existing exception handling patterns from route files
- **Logging Patterns:** Use existing logging patterns from `api_gateway/` and agent files
- **Configuration Management:** Use existing environment variable and configuration patterns

### Database Pattern Standards
- **Connection Patterns:** Use existing `TenantDatabase` class with `get_tenant_connection()` context manager
- **Query Patterns:** Follow existing SQL patterns with proper parameterization
- **Transaction Handling:** Use existing async transaction patterns from route files
- **Migration Patterns:** Follow existing migration pattern in `dev/migrations/` with proper tenant_id foreign keys

### API Pattern Standards
- **Route Structure:** Follow existing FastAPI router patterns from `api_gateway/` files
- **Request/Response Models:** Use Pydantic models following existing patterns
- **Validation:** Use existing validation patterns from route files with proper error handling
- **Background Tasks:** Use existing BackgroundTasks patterns for long-running operations

---

## 7. Template API & Backend Standards

### API Pattern Standards
**Every Python development template must include:**
- **Database Operations:** Use `TenantDatabase` class with `get_tenant_connection()` context manager
- **Tenant Context:** Always pass `TenantContext` with proper tenant_id isolation
- **Access Control:** Use `@require_subscription` decorators from `access_control.py` for endpoint protection
- **Error Handling:** Follow existing HTTPException patterns with proper status codes

### Backend Pattern Standards
- **Route Structure:** Follow existing FastAPI router patterns from `api_gateway/` files
- **Request/Response Models:** Use Pydantic models following existing patterns
- **Background Tasks:** Use existing BackgroundTasks patterns for long-running operations
- **Middleware:** Use existing middleware patterns for authentication and logging

### Database Pattern Standards
- **Connection Pattern:** Use existing async connection pool with tenant isolation
- **Query Structure:** Follow existing SQL patterns with proper parameterization
- **Transaction Handling:** Use existing async transaction patterns from route files
- **Indexing Strategy:** Include proper indexes for tenant_id and common query patterns

---

## 8. Template Frontend Integration Standards

### Frontend Integration Requirements
**Every Python development template must include:**
- **API Contract:** Clear API specifications for frontend integration
- **Data Models:** TypeScript interfaces that match Pydantic models
- **Error Handling:** Consistent error response formats for frontend consumption
- **Authentication:** JWT token handling and refresh mechanisms

### Frontend Pattern Standards
- **API Integration:** Use existing patterns from `ui/src/lib/api.ts`
- **Type Safety:** Ensure TypeScript interfaces match backend Pydantic models
- **Error Handling:** Use existing frontend error handling patterns
- **State Management:** Integrate with existing frontend state management patterns

---

## 9. Template Agent Integration Standards

### Agent Selection Standards
**Every Python development template must include:**
- **DevAgent** (`agents/dev/`): For code generation and module creation
- **QA Agent** (`agents/qa/`): For testing, security scans, and quality assurance
- **Ops Agent** (`agents/ops/`): For infrastructure and deployment tasks
- **Docs Agent** (`agents/docs/`): For documentation generation

### Agent Communication Standards
- **Database Integration:** Use existing tenant database patterns
- **API Communication:** Follow existing agent-to-agent communication patterns
- **Event Handling:** Use existing WebSocket and event relay patterns
- **Orchestration:** Integrate with existing Vertex AI Agent Engine patterns

---

## 10. Template Implementation Standards

### Standard Implementation Phases
**Every Python development template must include these phases:**

#### Phase 1: Backend Foundation
1. [Create database migrations following existing patterns]
2. [Implement Pydantic models following existing route patterns]
3. [Create API endpoints with proper tenant isolation]
4. [Add access control using existing decorators]

#### Phase 2: Business Logic Implementation
1. [Implement core business logic following existing patterns]
2. [Add data validation and error handling]
3. [Implement background tasks if needed]
4. [Add comprehensive logging and monitoring]

#### Phase 3: Testing & Integration
1. [Write comprehensive tests following existing patterns]
2. [Test tenant isolation and access control]
3. [Validate API performance and response times]
4. [Perform integration testing with existing systems]

### Phase Customization
- **Feature Complexity:** Can adjust phases based on feature complexity
- **Integration Requirements:** Can modify phases based on external system integration needs
- **Performance Requirements:** Can prioritize phases based on performance requirements

---

## 11. Template Quality Standards

### Template Completion Checklist
**Every Python development template must include:**
- [x] **Task Overview Section** - Clear scope and success criteria
- [x] **Technical Requirements** - Backend, database, and integration specifications
- [x] **Implementation Steps** - Phase-by-phase development plan
- [x] **Testing Strategy** - Unit, integration, and API testing requirements
- [x] **Deployment Considerations** - Backend deployment and monitoring needs
- [x] **Success Metrics** - How to measure completion and API performance
- [x] **File Structure** - Clear organization of new and modified files
- [x] **AI Agent Instructions** - Specific guidance for Python development implementation

### Template Validation
- Ensure all required development phases are covered
- Validate that development steps don't conflict with existing security measures
- Confirm that database migrations follow existing patterns
- Verify that API endpoints follow existing route patterns

---

## 12. Template File Organization Standards

### Standard File Structure
**Every Python development template must define:**
- **New Files to Create:** Backend, database, and configuration files following existing patterns
- **Existing Files to Modify:** Backend, configuration, and documentation files that need updates
- **File Naming Conventions:** Follow existing naming patterns in your codebase
- **Directory Organization:** Maintain existing folder structure and organization

### File Pattern Standards
- **Backend Files:** Follow existing patterns from `api_gateway/` and `agents/` directories
- **Database Files:** Follow existing migration patterns in `dev/migrations/`
- **Configuration Files:** Follow existing patterns for environment and deployment configs
- **Documentation Files:** Follow existing patterns for README and API documentation

---

## 13. Template AI Agent Instructions

### Standard AI Agent Workflow
🎯 **MANDATORY PROCESS FOR ALL PYTHON DEVELOPMENT TEMPLATES:**
1. **Analyze Existing Patterns:** Study existing Python code in similar files to understand patterns
2. **Maintain Consistency:** Use existing naming conventions, error handling, and architectural patterns
3. **Respect Tenant Isolation:** Always implement proper tenant isolation using existing `tenant_db.py` patterns
4. **Follow Python Standards:** Maintain PEP 8 compliance, use type hints, comprehensive docstrings
5. **Test Thoroughly:** Create comprehensive tests following existing testing patterns
6. **Document Changes:** Update relevant documentation and README files

### Template-Specific Instructions
**Every Python development template must include:**
- **Feature Context:** Clear explanation of what backend feature this template covers
- **Integration Points:** How this feature integrates with existing backend systems
- **Custom Patterns:** Any feature-specific patterns that differ from standard patterns
- **Testing Requirements:** Feature-specific testing needs beyond standard requirements

### Code Quality Standards
- **Python:** Follow PEP 8, use type hints, comprehensive docstrings
- **FastAPI:** Use existing route patterns, Pydantic models, and middleware
- **Database:** Use parameterized queries, proper error handling, transaction management
- **Security:** Implement proper input validation, maintain tenant isolation, use existing access control

---

## 14. Template Impact Analysis Standards

### Standard Impact Considerations
**Every Python development template must address:**
- **Tenant Isolation:** Ensure changes don't break existing tenant data separation
- **Performance:** Monitor impact on existing API response times
- **Database Performance:** Monitor impact on existing query performance with new tables/indexes
- **Agent Integration:** Ensure changes don't break existing agent communication patterns
- **API Compatibility:** Ensure changes don't break existing API contracts

### Python Development-Specific Impact Analysis
**Every Python development template must include:**
- **Backend Performance:** How new features affect existing backend performance
- **Database Impact:** Specific database performance requirements and monitoring needs
- **API Changes:** Any breaking changes to existing API endpoints
- **Integration Impact:** How new features affect existing system integrations

### Risk Mitigation Standards
- **Backward Compatibility:** Test with existing API consumers and workflows
- **Performance Testing:** Load test new endpoints to ensure they meet performance requirements
- **Database Testing:** Test with existing tenant data to ensure isolation is maintained
- **Integration Testing:** Test with existing agent workflows and orchestration

---

## 15. Template Deployment Standards

### Standard Deployment Requirements
**Every Python development template must include:**
- **Cloud Run:** Follow existing deployment patterns for new backend services
- **Database Migrations:** Use existing migration system for schema changes
- **Environment Variables:** Use existing Secret Manager patterns for configuration
- **Health Checks:** Implement proper health check endpoints following existing patterns

### Standard Testing Requirements
**Every Python development template must include:**
- **Unit Tests:** Comprehensive test coverage for all new functionality
- **Integration Tests:** Test with existing tenant isolation and access control
- **API Tests:** Validate API endpoints and response formats
- **Performance Tests:** Ensure new features meet existing performance standards

### Python Development-Specific Deployment Considerations
- **Backend Service Deployment:** Follow existing Cloud Run deployment patterns
- **Database Schema Changes:** Use existing migration and rollback procedures
- **API Versioning:** Consider API versioning strategies for breaking changes
- **Monitoring Integration:** Integrate with existing monitoring and alerting systems

---

## 16. Template Documentation Standards

### Standard Documentation Requirements
**Every Python development template must include:**
- **API Documentation:** Update FastAPI auto-generated docs
- **Code Documentation:** Comprehensive docstrings and inline comments
- **Database Schema:** Update database documentation with new tables/relationships
- **Deployment Guides:** Update deployment documentation for new features

### Documentation Standards
- **Code Comments:** Comprehensive docstrings and inline comments
- **README Updates:** Update relevant README files with new functionality
- **API Examples:** Provide clear examples for new endpoints
- **Database Schema:** Document new tables, relationships, and migration procedures

### Template Documentation
**Every Python development template must include:**
- **Usage Instructions:** How to use this template for specific backend development tasks
- **Customization Guide:** What can be modified vs. what should remain standard
- **Example Output:** Sample backend development task document created from this template

---

## 17. Template Validation & Usage

### Template Completion Checklist
**Before using a Python development template, ensure it includes:**
- [x] All required sections from this meta-template
- [x] Python development-specific customization points clearly defined
- [x] Standard patterns and requirements properly documented
- [x] AI agent instructions tailored to Python development
- [x] Example task output or usage instructions
- [x] Integration points with existing backend systems clearly defined

### Template Usage Instructions
**To use a Python development template:**
1. **Review the template** to ensure it covers all required backend development aspects
2. **Customize for your specific backend feature** by filling in the template sections
3. **Validate the template** against this meta-template checklist
4. **Use the template** to generate specific backend development task documents
5. **Iterate and improve** the template based on development results

### Template Maintenance
- **Version Control:** Track template versions and updates
- **Feedback Loop:** Collect feedback from development usage to improve future versions
- **Pattern Evolution:** Update templates as your Python development patterns evolve

---

**Template Version:** 1.0  
**Last Updated:** [Current Date]  
**Project:** AI SaaS Factory  
**Architecture:** Multi-agent orchestration with glassmorphism design system  
**Purpose:** Template for creating Python backend development tasks
