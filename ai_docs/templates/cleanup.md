# AI SaaS Factory Cleanup Template - Codebase Maintenance & Optimization

## 1. Task Overview

### Task Title
**Title:** [Specific cleanup task - e.g., "Cleanup Deprecated Agent Dependencies" or "Remove Unused Infrastructure Code"]

### Goal Statement
**Goal:** [Clear statement of what needs to be cleaned up and why it matters for project maintainability and performance]

---

## 2. Cleanup Analysis & Current State

### Technology & Architecture Context
- **Frameworks & Versions:** Python 3.12, FastAPI, React 18, TypeScript 5.8.3, Vite 5
- **Language:** Python (Backend), TypeScript (Frontend)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** Tailwind CSS 3.4.17, shadcn/ui components, glassmorphism design system with natural olive greens
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path

### Current State
[Analysis of current codebase state, identifying what's working, what's broken, what's deprecated, and what needs cleanup]

### Cleanup Scope & Priority
[Define the scope of cleanup and prioritize areas based on impact and effort]

---

## 3. Context & Problem Definition

### Problem Statement
[Detailed explanation of the cleanup problem, including technical debt, deprecated code, unused dependencies, and why cleanup is needed now]

### Success Criteria
- [ ] [Specific, measurable cleanup outcome 1]
- [ ] [Specific, measurable cleanup outcome 2]
- [ ] [Specific, measurable cleanup outcome 3]

---

## 4. Cleanup Context & Standards

### Cleanup Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Breaking Changes:** Must avoid breaking existing functionality, focus on safe cleanup
- **Data Handling:** Preserve all tenant data and user configurations using existing `tenant_db.py` patterns
- **User Base:** Multi-tenant SaaS users, internal development team
- **Priority:** Stability and maintainability over speed, maintain glassmorphism design consistency

---

## 5. Cleanup Requirements & Standards

### Functional Requirements
- **Code Quality:** Remove deprecated functions, unused imports, dead code
- **Dependency Management:** Clean up unused packages, update outdated versions safely
- **File Organization:** Remove orphaned files, consolidate duplicate functionality
- **Documentation:** Update outdated docs, remove obsolete references
- **Testing:** Clean up test files, remove broken tests, consolidate test utilities

### Non-Functional Requirements
- **Performance:** Remove code that impacts build times or runtime performance
- **Security:** Clean up exposed secrets, deprecated security patterns
- **Maintainability:** Improve code organization and reduce technical debt
- **Compatibility:** Maintain backward compatibility with existing APIs
- **Standards:** Enforce project coding standards (PEP 8, ESLint, Prettier)

### Technical Constraints
- [Must preserve existing API contracts]
- [Cannot remove active tenant data or configurations]
- [Must maintain multi-tenant isolation patterns from `tenant_db.py`]
- [Must preserve agent orchestration functionality]
- [Must maintain glassmorphism design system from `ui/src/index.css`]

---

## 6. Data & Database Changes

### Database Schema Changes
[Specify any database cleanup needed - deprecated tables, unused columns, etc.]

### Data Model Updates
[Define any TypeScript/Python type cleanup, interface consolidation]

### Data Migration Plan
[Plan for safely removing deprecated data while preserving active data]

---

## 7. API & Backend Changes

### Data Access Pattern Rules
- **Cleanup Scope:** Focus on agents/, api_gateway/, shared/ directories
- **Preservation Rules:** Keep core access control, tenant isolation, and orchestration logic
- **Removal Rules:** Remove deprecated agent implementations, unused API endpoints

### Server Actions
- **Cleanup Operations:** Remove deprecated functions, consolidate duplicate logic
- **Preservation Operations:** Maintain core business logic and security patterns

### Database Queries
- **Cleanup Approach:** Remove unused queries, optimize existing ones
- **Data Integrity:** Ensure cleanup doesn't affect active tenant data

---

## 8. Frontend Changes

### New Components
[Any new cleanup-related UI components needed]

### Page Updates
[Pages that need cleanup-related modifications]

### State Management
[Clean up unused state, consolidate state management patterns]

---

## 9. Implementation Plan

### Phase 1: Code Analysis & Inventory
1. **Scan for Deprecated Code**
   - Search for TODO/FIXME comments
   - Identify unused imports and functions
   - Find duplicate code patterns
   - Locate orphaned files

2. **Dependency Analysis**
   - Audit requirements-*.txt files
   - Check package.json for unused packages
   - Identify version conflicts
   - Find security vulnerabilities

3. **Documentation Review**
   - Update outdated README files
   - Remove obsolete documentation
   - Consolidate duplicate guides

### Phase 2: Safe Removal
1. **Remove Dead Code**
   - Delete unused functions and classes
   - Remove deprecated API endpoints
   - Clean up unused database tables
   - Remove orphaned configuration files

2. **Dependency Cleanup**
   - Remove unused packages
   - Update outdated versions safely
   - Consolidate duplicate requirements files

3. **File Organization**
   - Remove empty directories
   - Consolidate similar functionality
   - Reorganize for better maintainability

### Phase 3: Testing & Validation
1. **Run Test Suite**
   - Execute pytest with coverage
   - Run UI build tests
   - Verify tenant isolation still works
   - Test critical user flows

2. **Integration Testing**
   - Verify agent orchestration
   - Test API gateway functionality
   - Validate multi-tenant operations

---

## 10. Task Completion Tracking

### Real-Time Progress Tracking
- **Phase Completion:** Mark each phase as complete with verification
- **File Counts:** Track files removed, modified, and added
- **Test Results:** Monitor test coverage and pass rates
- **Performance Metrics:** Measure build time improvements

---

## 11. File Structure & Organization

### Files to Remove
- [List specific files identified for removal]
- [Orphaned test files]
- [Deprecated configuration files]
- [Unused documentation]

### Files to Modify
- [Update requirements files]
- [Clean up main application files]
- [Update documentation]
- [Consolidate shared utilities]

### Files to Create
- [New consolidated utilities]
- [Updated documentation]
- [Cleanup scripts]

---

## 12. Cleanup AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS FOR CLEANUP:**
1. **Start with Analysis:** Use codebase search to identify cleanup targets
2. **Create Inventory:** Document all items to be cleaned up
3. **Prioritize Safety:** Focus on non-breaking changes first
4. **Test Incrementally:** Verify each cleanup step doesn't break functionality
5. **Update Documentation:** Keep track of all changes made
6. **Final Validation:** Run full test suite before completion

### Cleanup-Specific Instructions
**Every cleanup task must include:**
- **Tenant Isolation Verification:** Ensure cleanup doesn't affect tenant boundaries
- **Pattern Preservation:** Maintain existing SaaS Factory patterns and conventions
- **Design Consistency:** Preserve glassmorphism theme and natural olive greens
- **Agent Integration:** Ensure cleanup doesn't break agent communication

### Communication Preferences
- **Progress Updates:** Report on each phase completion
- **Risk Assessment:** Flag any potentially breaking changes
- **Recommendations:** Suggest additional cleanup opportunities
- **Documentation:** Update relevant docs as cleanup progresses

### Code Quality Standards
- **Python:** Follow PEP 8, use type hints, maintain docstrings
- **TypeScript:** Follow ESLint rules, use proper typing
- **Terraform:** Follow terraform fmt standards
- **Documentation:** Keep README files current and accurate
- **Pattern Compliance:** Maintain existing SaaS Factory architectural patterns

---

## 13. Second-Order Impact Analysis

### Impact Assessment
- **Agent Orchestration:** Ensure cleanup doesn't break agent communication
- **Tenant Isolation:** Verify multi-tenant functionality remains intact
- **API Compatibility:** Maintain backward compatibility for existing integrations
- **Build Process:** Ensure cleanup improves build times and reliability
- **Deployment Pipeline:** Verify CI/CD continues to work properly

### Risk Mitigation
- **Backup Strategy:** Keep backups of removed code for rollback
- **Incremental Approach:** Clean up in small, testable batches
- **Rollback Plan:** Document how to restore if issues arise
- **Monitoring:** Watch for any performance or functionality regressions

---

## 14. Cleanup-Specific Guidelines

### Safe Removal Patterns
- **Unused Imports:** Remove only if confirmed unused across entire codebase
- **Deprecated Functions:** Check for any remaining callers before removal
- **Unused Dependencies:** Verify no transitive dependencies exist
- **Orphaned Files:** Confirm no references from active code

### Preservation Rules
- **Core Business Logic:** Never remove tenant isolation, access control, or orchestration
- **Active API Endpoints:** Preserve all documented and used endpoints
- **Configuration Files:** Keep environment-specific configurations
- **Test Utilities:** Preserve shared testing infrastructure

### Validation Steps
- **Pre-Cleanup:** Run full test suite and document baseline
- **Post-Cleanup:** Verify all tests still pass
- **Integration Check:** Test critical user workflows
- **Performance Test:** Ensure cleanup doesn't degrade performance
