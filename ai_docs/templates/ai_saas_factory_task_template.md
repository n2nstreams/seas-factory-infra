# AI SaaS Factory Template Generator - Meta-Template for Creating Feature Templates

## 1. Task Overview

### Template Name
**Template Name:** [Specific feature template name - e.g., "Stripe Payment Integration Template" or "User Analytics Dashboard Template"]

### Template Purpose
**Purpose:** [Clear statement of what this template will be used for and what types of tasks it will generate for the SaaS Factory platform]

---

## 2. Template Scope & Feature Analysis

### Feature Category
**Category:** [e.g., "Payment Integration", "User Management", "Analytics", "Security", "Infrastructure"]

### Technology & Architecture Requirements
- **Frameworks & Versions:** Python 3.12, FastAPI, React 18, TypeScript 5.8.3, Vite 5
- **Language:** Python (Backend), TypeScript (Frontend)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** Tailwind CSS 3.4.17, shadcn/ui components, glassmorphism design system with natural olive greens
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path

### Feature Requirements Analysis
[Analysis of what this feature template needs to cover, existing related functionality, and what patterns it should follow]

---

## 3. Template Structure & Content Planning

### Template Sections to Include
**Required Sections:**
- [ ] **Task Overview** - Clear title, goal, and scope definition
- [ ] **Technical Requirements** - Backend, frontend, and database needs
- [ ] **Implementation Steps** - Phase-by-phase development plan
- [ ] **Testing Strategy** - Unit, integration, and UI testing requirements
- [ ] **Deployment Considerations** - CI/CD and infrastructure needs
- [ ] **Success Metrics** - How to measure completion and quality

### Template Customization Points
[Define what aspects of this feature template should be customizable vs. standardized across all templates]

---

## 4. Template Standards & Consistency

### Template Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Consistency Requirements:** Must maintain consistent structure and terminology across all feature templates
- **Pattern Preservation:** Must preserve existing architectural patterns and design systems
- **User Base:** Multi-tenant SaaS users with different subscription tiers (starter, pro, growth)
- **Priority:** Template reusability and consistency while maintaining feature-specific customization

---

## 5. Template Content Requirements

### Standard Template Sections
**Every feature template must include:**
- **Performance Standards:** API responses under 200ms, support 1000+ concurrent users per tenant
- **Security Requirements:** Tenant isolation, input validation, SQL injection prevention, use existing `access_control.py` patterns
- **Design Consistency:** Glassmorphism design with natural olive greens, mobile responsive
- **Responsive Design:** Mobile-first approach with Tailwind CSS breakpoints (320px+, 768px+, 1024px+)
- **Theme Support:** Maintain glassmorphism design system with natural olive greens (green-800 to green-900 gradients)

### Feature-Specific Customization
[Define what aspects should be customized for each specific feature type]

### Technical Constraints
- [Must use existing tenant isolation system from `tenant_db.py` and `access_control.py`]
- [Cannot modify existing database tables without proper migrations in `dev/migrations/`]
- [Must maintain compatibility with existing agent architecture and orchestration patterns]
- [Must follow existing FastAPI route patterns and Pydantic models from `api_gateway/`]
- [Must use existing glassmorphism design system from `ui/src/index.css`]

---

## 6. Template Pattern Requirements

### Database Pattern Standards
**Every feature template must include:**
- **Migration Patterns:** Follow existing migration pattern in `dev/migrations/` with proper tenant_id foreign keys
- **Schema Standards:** Use existing patterns from `001_create_tenant_model.sql` with row-level security
- **Indexing Strategy:** Include proper indexes for tenant_id and common query patterns
- **Data Integrity:** Maintain referential integrity with existing tables using UUID primary keys

### Model Pattern Standards
- **Backend Models:** Create Pydantic models following existing patterns in route files (e.g., `ideas_routes.py`, `user_routes.py`)
- **Frontend Types:** Define TypeScript interfaces in `ui/src/lib/types.ts` following existing patterns
- **Validation:** Use existing validation patterns from route files with proper error handling

### Migration Standards
- **Backup Strategy:** Use existing database backup patterns
- **Migration Scripts:** Create numbered migration files in `dev/migrations/` following existing pattern
- **Data Validation:** Test with existing tenant data to ensure isolation is maintained

---

## 7. Template API & Backend Standards

### API Pattern Standards
**Every feature template must include:**
- **Database Operations:** Use `TenantDatabase` class with `get_tenant_connection()` context manager
- **Tenant Context:** Always pass `TenantContext` with proper tenant_id isolation
- **Access Control:** Use `@require_subscription` decorators from `access_control.py` for endpoint protection
- **Error Handling:** Follow existing HTTPException patterns with proper status codes

### Backend Pattern Standards
- **Route Structure:** Follow existing FastAPI router patterns from `api_gateway/` files
- **Request/Response Models:** Use Pydantic models following existing patterns
- **Background Tasks:** Use existing BackgroundTasks patterns for long-running operations

### Database Pattern Standards
- **Connection Pattern:** Use existing async connection pool with tenant isolation
- **Query Structure:** Follow existing SQL patterns with proper parameterization
- **Transaction Handling:** Use existing async transaction patterns from route files

---

## 8. Template Frontend Standards

### Component Structure Standards
**Every feature template must include:**
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
- **Local State:** Use `useState` for component-specific state
- **Global State:** Use existing AuthContext for user-related state
- **API Integration:** Use existing patterns from `ui/src/lib/api.ts`
- **WebSocket:** Use existing `useWebSocket` hook for real-time updates

---

## 9. Template Agent Integration Standards

### Agent Selection Standards
**Every feature template must include:**
- **DevAgent** (`agents/dev/`): For code generation and module creation
- **DesignAgent** (`agents/design/`): For UI/UX design and Figma integration
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
**Every feature template must include these phases:**

#### Phase 1: Backend Foundation
1. [Create database migrations following existing patterns]
2. [Implement Pydantic models following existing route patterns]
3. [Create API endpoints with proper tenant isolation]
4. [Add access control using existing decorators]

#### Phase 2: Frontend Implementation
1. [Create TypeScript interfaces following existing patterns]
2. [Build React components using glassmorphism design system]
3. [Implement state management and API integration]
4. [Add responsive design and accessibility features]

#### Phase 3: Testing & Integration
1. [Write comprehensive tests following existing patterns]
2. [Test tenant isolation and access control]
3. [Validate glassmorphism design consistency]
4. [Perform integration testing with existing systems]

### Phase Customization
[Define what phases can be customized for specific features vs. what should remain standard]

---

## 11. Template Quality Standards

### Template Completion Checklist
**Every feature template must include:**
- [ ] **Task Overview Section** - Clear scope and success criteria
- [ ] **Technical Requirements** - Backend, frontend, and database specifications
- [ ] **Implementation Steps** - Phase-by-phase development plan
- [ ] **Testing Strategy** - Unit, integration, and UI testing requirements
- [ ] **Deployment Considerations** - CI/CD and infrastructure needs
- [ ] **Success Metrics** - How to measure completion and quality
- [ ] **File Structure** - Clear organization of new and modified files
- [ ] **AI Agent Instructions** - Specific guidance for implementation

### Template Validation
[Define how to validate that a feature template is complete and ready for use]

---

## 12. Template File Organization Standards

### Standard File Structure
**Every feature template must define:**
- **New Files to Create:** Backend, frontend, and database files following existing patterns
- **Existing Files to Modify:** Backend, frontend, and configuration files that need updates
- **File Naming Conventions:** Follow existing naming patterns in your codebase
- **Directory Organization:** Maintain existing folder structure and organization

### File Pattern Standards
- **Backend Files:** Follow existing patterns from `api_gateway/` and `agents/` directories
- **Frontend Files:** Follow existing patterns from `ui/src/` directory structure
- **Database Files:** Follow existing migration patterns in `dev/migrations/`
- **Configuration Files:** Follow existing patterns for environment and deployment configs

---

## 13. Template AI Agent Instructions

### Standard AI Agent Workflow
🎯 **MANDATORY PROCESS FOR ALL FEATURE TEMPLATES:**
1. **Analyze Existing Patterns:** Study existing code in similar files to understand patterns
2. **Maintain Consistency:** Use existing naming conventions, error handling, and architectural patterns
3. **Respect Tenant Isolation:** Always implement proper tenant isolation using existing `tenant_db.py` patterns
4. **Follow Design System:** Maintain glassmorphism design with natural olive green theme
5. **Test Thoroughly:** Create comprehensive tests following existing testing patterns
6. **Document Changes:** Update relevant documentation and README files

### Template-Specific Instructions
**Every feature template must include:**
- **Feature Context:** Clear explanation of what this feature does and why it's needed
- **Integration Points:** How this feature integrates with existing systems
- **Custom Patterns:** Any feature-specific patterns that differ from standard patterns
- **Testing Requirements:** Feature-specific testing needs beyond standard requirements

### Code Quality Standards
- **Python:** Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript:** Use strict typing, follow React best practices, maintain accessibility
- **Database:** Use parameterized queries, proper error handling, transaction management
- **Security:** Implement proper input validation, maintain tenant isolation, use existing access control

---

## 14. Template Impact Analysis Standards

### Standard Impact Considerations
**Every feature template must address:**
- **Tenant Isolation:** Ensure changes don't break existing tenant data separation
- **Performance:** Monitor impact on existing API response times
- **Design Consistency:** Maintain glassmorphism theme across all new components
- **Agent Integration:** Ensure changes don't break existing agent communication patterns
- **Database Performance:** Monitor impact on existing query performance with new tables/indexes

### Feature-Specific Impact Analysis
**Every feature template must include:**
- **Integration Risks:** How this feature might affect existing systems
- **Performance Considerations:** Specific performance requirements and monitoring needs
- **Security Implications:** Any security considerations specific to this feature
- **User Experience Impact:** How this feature affects existing user workflows

### Risk Mitigation Standards
- **Backward Compatibility:** Test with existing tenant data and workflows
- **Performance Testing:** Load test new endpoints to ensure they meet performance requirements
- **Design Review:** Validate new components against existing glassmorphism design system
- **Integration Testing:** Test with existing agent workflows and orchestration

---

## 15. Template Deployment Standards

### Standard Deployment Requirements
**Every feature template must include:**
- **Cloud Run:** Follow existing deployment patterns for new services
- **Database Migrations:** Use existing migration system for schema changes
- **Environment Variables:** Use existing Secret Manager patterns for configuration
- **Health Checks:** Implement proper health check endpoints following existing patterns

### Standard Testing Requirements
**Every feature template must include:**
- **Unit Tests:** Comprehensive test coverage for all new functionality
- **Integration Tests:** Test with existing tenant isolation and access control
- **UI Tests:** Validate glassmorphism design consistency and responsiveness
- **Performance Tests:** Ensure new features meet existing performance standards

### Feature-Specific Deployment Considerations
[Define what deployment aspects should be customized for specific features]

---

## 16. Template Documentation Standards

### Standard Documentation Requirements
**Every feature template must include:**
- **API Documentation:** Update FastAPI auto-generated docs
- **Component Documentation:** Document new React components and their usage
- **Database Schema:** Update database documentation with new tables/relationships
- **User Guides:** Update user documentation for new features

### Documentation Standards
- **Code Comments:** Comprehensive docstrings and inline comments
- **README Updates:** Update relevant README files with new functionality
- **API Examples:** Provide clear examples for new endpoints
- **Component Props:** Document all component props and usage examples

### Template Documentation
**Every feature template must include:**
- **Usage Instructions:** How to use this template to create specific tasks
- **Customization Guide:** What can be modified vs. what should remain standard
- **Example Output:** Sample task document created from this template

---

## 17. Template Validation & Usage

### Template Completion Checklist
**Before using a feature template, ensure it includes:**
- [ ] All required sections from this meta-template
- [ ] Feature-specific customization points clearly defined
- [ ] Standard patterns and requirements properly documented
- [ ] AI agent instructions tailored to the specific feature
- [ ] Example task output or usage instructions
- [ ] Integration points with existing systems clearly defined

### Template Usage Instructions
**To use a feature template:**
1. **Review the template** to ensure it covers all required aspects
2. **Customize for your specific feature** by filling in the template sections
3. **Validate the template** against this meta-template checklist
4. **Use the template** to generate specific task documents
5. **Iterate and improve** the template based on usage results

### Template Maintenance
- **Version Control:** Track template versions and updates
- **Feedback Loop:** Collect feedback from template usage to improve future versions
- **Pattern Evolution:** Update templates as your codebase patterns evolve

---

**Template Version:** 1.0  
**Last Updated:** [Current Date]  
**Project:** AI SaaS Factory  
**Architecture:** Multi-agent orchestration with glassmorphism design system  
**Purpose:** Meta-template for creating feature-specific templates (e.g., stripe_template.md, analytics_template.md)
