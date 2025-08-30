# AI SaaS Factory New Features Template - Feature Development & Implementation

## 1. Task Overview

### Task Title
**Title:** [Brief, descriptive title - e.g., "Add User Authentication System" or "Implement Real-time Chat Feature"]

### Goal Statement
**Goal:** [Clear statement of the end result you want and the business/user value it provides]

---

## 2. Feature Analysis & Current State

### Technology & Architecture Context
- **Frameworks & Versions:** Python 3.12, FastAPI, React 18, TypeScript 5.8.3, Vite 5
- **Language:** Python (Backend), TypeScript (Frontend)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** Tailwind CSS 3.4.17, shadcn/ui components, glassmorphism design system with natural olive greens
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path

### Current State
[Analysis of your current codebase state, existing functionality, and what needs to be changed]

### Feature Integration Points
[Define how this new feature will integrate with existing systems and components]

---

## 3. Context & Problem Definition

### Problem Statement
[Detailed explanation of the problem, including user impact, pain points, and why it needs to be solved now]

### Success Criteria
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]

---

## 4. Feature Development Context & Standards

### Feature Development Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Breaking Changes:** Must maintain backward compatibility with existing tenant data and API contracts
- **Data Handling:** Must preserve existing tenant data and maintain isolation using existing `tenant_db.py` patterns
- **User Base:** Multi-tenant SaaS users with different subscription tiers (starter, pro, growth)
- **Priority:** Production stability with feature velocity, maintain glassmorphism design consistency

---

## 5. Feature Requirements & Standards

### Functional Requirements
- **Multi-tenant Support:** All features must respect tenant isolation and subscription limits
- **Role-based Access:** Implement proper RBAC using existing `access_control.py` patterns
- **Database Integration:** Use existing database schema patterns and migration system
- **API Consistency:** Follow existing FastAPI route patterns in `api_gateway/`
- **Frontend Components:** Leverage existing shadcn/ui components and glassmorphism theme

### Non-Functional Requirements
- **Performance:** API responses under 200ms, support 1000+ concurrent users per tenant
- **Security:** Tenant isolation, input validation, SQL injection prevention, use existing `access_control.py` patterns
- **Usability:** Consistent with existing glassmorphism design, mobile responsive, maintain natural olive green theme
- **Responsive Design:** Mobile-first approach with Tailwind CSS breakpoints (320px+, 768px+, 1024px+)
- **Theme Support:** Maintain glassmorphism design system with natural olive greens (green-800 to green-900 gradients)

### Technical Constraints
- [Must use existing tenant isolation system from `tenant_db.py` and `access_control.py`]
- [Cannot modify existing database tables without proper migrations in `dev/migrations/`]
- [Must maintain compatibility with existing agent architecture and orchestration patterns]
- [Must follow existing FastAPI route patterns and Pydantic models from `api_gateway/`]
- [Must use existing glassmorphism design system from `ui/src/index.css`]

---

## 6. Feature Database & Data Standards

### Database Schema Standards
- **New Tables:** Follow existing migration pattern in `dev/migrations/` with proper tenant_id foreign keys
- **Schema Updates:** Use existing patterns from `001_create_tenant_model.sql` with row-level security
- **Indexes:** Include proper indexes for tenant_id and common query patterns
- **Constraints:** Maintain referential integrity with existing tables using UUID primary keys

### Data Model Standards
- **Backend Models:** Create Pydantic models following existing patterns in route files (e.g., `ideas_routes.py`, `user_routes.py`)
- **Frontend Types:** Define TypeScript interfaces in `ui/src/lib/types.ts` following existing patterns
- **Validation:** Use existing validation patterns from route files with proper error handling

### Data Migration Standards
- **Migration Scripts:** Create numbered migration files in `dev/migrations/` following existing pattern
- **Testing:** Test migration on development database with existing tenant data
- **Rollback:** Include rollback procedures for safe deployment
- **Documentation:** Update `dev/init.sql` if needed

---

## 7. Feature API & Backend Standards

### API Pattern Standards
- **Database Access:** Use `TenantDatabase` and `TenantContext` from `agents/shared/tenant_db.py`
- **Route Structure:** Follow existing patterns in `api_gateway/` route files
- **Authentication:** Use existing `access_control.py` decorators and patterns
- **Error Handling:** Follow existing HTTP status code patterns and error response formats

### Backend Pattern Standards
- **CRUD Operations:** Implement standard create, read, update, delete endpoints
- **Background Tasks:** Use FastAPI `BackgroundTasks` for long-running operations
- **WebSocket Support:** Leverage existing `websocket_manager.py` for real-time features
- **Event Publishing:** Use existing event patterns for cross-agent communication

### Database Pattern Standards
- **Connection Management:** Use async context managers with tenant isolation
- **Query Patterns:** Follow existing SQL patterns with proper parameterization
- **Performance:** Include proper indexes and use existing query optimization patterns
- **Tenant Isolation:** Always use existing `TenantDatabase` patterns for all operations

---

## 8. Feature Frontend Standards

### Component Structure Standards
- **UI Components:** Place in `ui/src/components/ui/` for reusable elements, following shadcn/ui patterns
- **Page Components:** Place in `ui/src/pages/` for route-specific components
- **Custom Components:** Place in `ui/src/components/` for business logic components
- **Utility Functions:** Place in `ui/src/lib/` for shared functionality

### Frontend Pattern Standards
- **Component Architecture:** Follow existing React component patterns
- **State Management:** Use existing patterns (useState, AuthContext, useWebSocket)
- **Styling:** Maintain glassmorphism design system with natural olive greens
- **Responsiveness:** Mobile-first approach with existing Tailwind breakpoints

### State Management Standards
- **Local State:** Use React hooks (useState, useEffect) for component state
- **Global State:** Leverage existing context patterns if needed
- **API Integration:** Use existing `ui/src/lib/api.ts` patterns for backend communication
- **WebSocket:** Use existing `useWebSocket` hook for real-time updates

---

## 9. Implementation Plan

### Phase 1: Backend Foundation
- [ ] Create database migration file
- [ ] Implement Pydantic models and validation
- [ ] Create FastAPI routes with proper tenant isolation
- [ ] Add access control and authentication
- [ ] Implement database operations

### Phase 2: Frontend Implementation
- [ ] Create new React components
- [ ] Implement TypeScript interfaces
- [ ] Add routing and navigation updates
- [ ] Apply glassmorphism styling and theme

### Phase 3: Integration & Testing
- [ ] Connect frontend to backend APIs
- [ ] Test tenant isolation and access control
- [ ] Validate responsive design and theme consistency
- [ ] Run existing test suite

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
- [ ] Database schema implemented and tested
- [ ] Backend API endpoints working with proper tenant isolation
- [ ] Frontend components created with consistent styling
- [ ] Integration tests passing
- [ ] Documentation updated

---

## 11. File Structure & Organization

### New Files to Create
- `dev/migrations/XXX_new_feature.sql` - Database migration
- `api_gateway/new_feature_routes.py` - API endpoints
- `ui/src/components/NewFeature/` - React components
- `ui/src/pages/NewFeature.tsx` - Feature page
- `tests/test_new_feature.py` - Test coverage

### Existing Files to Modify
- `api_gateway/app.py` - Add new router
- `ui/src/App.tsx` - Add new route
- `ui/src/components/Navigation.tsx` - Add navigation item
- `dev/init.sql` - Include new migration if needed

---

## 12. Feature AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS FOR NEW FEATURES:**
1. **Analyze Existing Patterns:** Study similar features in the codebase for consistency
2. **Database First:** Start with database schema and migration
3. **Backend Implementation:** Create FastAPI routes with proper tenant isolation
4. **Frontend Development:** Build React components with existing design patterns
5. **Integration Testing:** Ensure end-to-end functionality works correctly
6. **Code Review:** Follow existing code quality standards and patterns

### Feature-Specific Instructions
**Every new feature must include:**
- **Tenant Isolation Verification:** Ensure feature maintains proper tenant boundaries
- **Pattern Compliance:** Follow existing SaaS Factory patterns and conventions
- **Design Consistency:** Maintain glassmorphism theme with natural olive greens
- **Performance Validation:** Ensure feature meets existing performance standards

### Communication Preferences
- Provide clear progress updates at each phase
- Highlight any deviations from existing patterns
- Ask for clarification if existing patterns are unclear
- Document any new patterns created for future reference

### Code Quality Standards
- Follow existing naming conventions (snake_case for Python, camelCase for TypeScript)
- Use proper TypeScript typing and Python type hints
- Include comprehensive docstrings and comments
- Maintain existing error handling patterns
- Follow existing logging and monitoring patterns
- Maintain tenant isolation patterns from `tenant_db.py`

---

## 13. Second-Order Impact Analysis

### Impact Assessment
- **Tenant Isolation:** Ensure new features don't break existing tenant boundaries
- **Performance:** Monitor impact on existing API response times
- **Security:** Maintain existing security patterns and access control
- **User Experience:** Ensure consistency with existing UI/UX patterns
- **Agent Integration:** Consider impact on existing agent workflows

### Risk Mitigation
- [Test thoroughly in development environment]
- [Use feature flags for gradual rollout]
- [Monitor performance metrics during implementation]
- [Have rollback plan ready]
- [Update existing tests to cover new functionality]

---

## 14. SaaS Factory Feature Patterns

### Backend Patterns
- **Route Structure:** Follow `api_gateway/ideas_routes.py` pattern for new features
- **Database Access:** Use `TenantDatabase` and `TenantContext` from `agents/shared/tenant_db.py`
- **Validation:** Use Pydantic models with proper validators
- **Error Handling:** Follow existing HTTP status code patterns
- **Logging:** Use structured logging with tenant context

### Frontend Patterns
- **Component Structure:** Follow existing component patterns in `ui/src/components/`
- **Styling:** Use Tailwind CSS with glassmorphism effects and natural olive greens
- **State Management:** Use React hooks following existing patterns
- **API Integration:** Use existing `ui/src/lib/api.ts` patterns
- **Routing:** Follow existing route structure in `ui/src/App.tsx`

### Database Patterns
- **Schema Design:** Follow existing table patterns with proper tenant isolation
- **Migrations:** Use existing migration system in `dev/migrations/`
- **Indexes:** Include proper indexes for tenant_id and common queries
- **Constraints:** Maintain referential integrity with existing tables

### Agent Integration Patterns
- **Agent Communication:** Follow existing agent-to-agent communication patterns
- **Event Handling:** Use existing WebSocket and event relay patterns
- **Orchestration:** Integrate with existing Vertex AI Agent Engine patterns

---

## 15. Testing Strategy

### Test Coverage Requirements
- **Unit Tests:** Test individual components and functions
- **Integration Tests:** Test API endpoints with database integration
- **Frontend Tests:** Test React components and user interactions
- **Tenant Isolation Tests:** Verify proper tenant boundary enforcement
- **Performance Tests:** Ensure new features don't degrade performance

### Testing Tools
- **Backend:** pytest with async support
- **Frontend:** React Testing Library
- **Database:** Test database with proper tenant isolation
- **API:** httpx for async HTTP testing
- **Coverage:** Maintain existing test coverage standards
