# AI Task Planning Template - GCP Debugging & Troubleshooting Framework

## 1. Task Overview

### Template Name
**Template Name:** GCP Debugging & Troubleshooting Template

### Template Purpose
**Purpose:** This template will be used for creating specific GCP debugging tasks, infrastructure troubleshooting, and cloud platform issue resolution for the SaaS Factory platform. It covers debugging Cloud Run services, database connectivity, IAM issues, networking problems, and performance optimization.

---

## 2. Template Scope & Feature Analysis

### Feature Category
**Category:** Infrastructure & Operations, Cloud Platform Debugging, DevOps Troubleshooting

### Technology & Architecture Requirements
- **Frameworks & Versions:** Python 3.12, FastAPI, React 18, TypeScript 5.8.3, Vite 5
- **Language:** Python (Backend), TypeScript (Frontend), Terraform (Infrastructure)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** Tailwind CSS 3.4.17, shadcn/ui components, glassmorphism design system with natural olive greens
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path
- **Cloud Platform:** Google Cloud Platform (Cloud Run, Cloud SQL, IAM, VPC, Load Balancing)

### Feature Requirements Analysis
This debugging template needs to cover comprehensive GCP troubleshooting scenarios including service deployment issues, database connectivity problems, IAM permission errors, networking configuration issues, and performance bottlenecks. It should follow established debugging patterns and integrate with existing monitoring and logging systems.

---

## 3. Template Structure & Content Planning

### Template Sections to Include
**Required Sections:**
- [x] **Task Overview** - Clear title, goal, and scope definition
- [x] **Technical Requirements** - Backend, frontend, and infrastructure needs
- [x] **Implementation Steps** - Phase-by-phase debugging plan
- [x] **Testing Strategy** - Validation and verification requirements
- [x] **Deployment Considerations** - Infrastructure and monitoring needs
- [x] **Success Metrics** - How to measure resolution and system health

### Template Customization Points
- **Debugging Scope:** Can be customized for specific GCP services (Cloud Run, Cloud SQL, IAM, etc.)
- **Severity Levels:** Can be adapted for different incident severity (P1, P2, P3)
- **Team Involvement:** Can specify which teams need to be involved (DevOps, Backend, Frontend)
- **Timeline:** Can be adjusted based on issue complexity and business impact

---

## 4. Template Standards & Consistency

### Template Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Consistency Requirements:** Must maintain consistent structure and terminology across all debugging templates
- **Pattern Preservation:** Must preserve existing architectural patterns and debugging workflows
- **User Base:** Multi-tenant SaaS users with different subscription tiers (starter, pro, growth)
- **Priority:** Template reusability and consistency while maintaining debugging-specific customization

---

## 5. Template Content Requirements

### Standard Template Sections
**Every debugging template must include:**
- **Performance Standards:** Debugging should not impact existing API response times, maintain 99.9% uptime
- **Security Requirements:** Preserve tenant isolation, maintain existing access control, use existing `access_control.py` patterns
- **Design Consistency:** Maintain glassmorphism design with natural olive greens for any UI components
- **Responsive Design:** Mobile-first approach with Tailwind CSS breakpoints (320px+, 768px+, 1024px+)
- **Theme Support:** Maintain glassmorphism design system with natural olive greens (green-800 to green-900 gradients)

### Debugging-Specific Customization
- **Issue Categorization:** Network, Database, Authentication, Performance, Security
- **Escalation Paths:** When to involve senior engineers or external support
- **Rollback Procedures:** How to quickly revert problematic changes
- **Communication Protocols:** How to keep stakeholders informed during debugging

### Technical Constraints
- [Must use existing tenant isolation system from `tenant_db.py` and `access_control.py`]
- [Cannot modify existing database tables without proper migrations in `dev/migrations/`]
- [Must maintain compatibility with existing agent architecture and orchestration patterns]
- [Must follow existing FastAPI route patterns and Pydantic models from `api_gateway/`]
- [Must use existing glassmorphism design system from `ui/src/index.css`]
- [Must preserve existing GCP infrastructure patterns and Terraform configurations]

---

## 6. Template Pattern Requirements

### Debugging Pattern Standards
**Every debugging template must include:**
- **Investigation Steps:** Systematic approach to problem identification and root cause analysis
- **Logging Patterns:** Use existing logging patterns from `api_gateway/` and agent files
- **Monitoring Integration:** Leverage existing monitoring and alerting systems
- **Documentation Standards:** Update relevant documentation and runbooks

### Infrastructure Pattern Standards
- **Terraform Patterns:** Follow existing Terraform patterns from `infra/` directory
- **Cloud Run Patterns:** Use existing deployment and configuration patterns
- **Database Patterns:** Follow existing connection and query patterns
- **IAM Patterns:** Use existing permission and role patterns

### Monitoring Pattern Standards
- **Health Checks:** Use existing health check endpoints and patterns
- **Metrics Collection:** Leverage existing Cloud Monitoring and logging
- **Alerting:** Use existing alerting and notification systems
- **Performance Baselines:** Maintain existing performance benchmarks

---

## 7. Template API & Backend Standards

### API Pattern Standards
**Every debugging template must include:**
- **Health Check Endpoints:** Use existing health check patterns from route files
- **Debug Endpoints:** Create temporary debugging endpoints following existing patterns
- **Error Handling:** Follow existing HTTPException patterns with proper status codes
- **Logging:** Use existing logging patterns for debugging information

### Backend Pattern Standards
- **Route Structure:** Follow existing FastAPI router patterns from `api_gateway/` files
- **Request/Response Models:** Use Pydantic models following existing patterns
- **Background Tasks:** Use existing BackgroundTasks patterns for long-running debugging operations

### Database Pattern Standards
- **Connection Testing:** Use existing connection patterns to test database connectivity
- **Query Performance:** Use existing query patterns to identify performance issues
- **Transaction Handling:** Use existing async transaction patterns for debugging

---

## 8. Template Frontend Standards

### Component Structure Standards
**Every debugging template must include:**
- **Debug UI Components:** Place in `ui/src/components/ui/` for debugging interfaces
- **Status Components:** Place in `ui/src/components/` for system status displays
- **Utility Functions:** Place in `ui/src/lib/` for debugging utilities

### Frontend Pattern Standards
- **Component Architecture:** Follow existing React component patterns
- **State Management:** Use existing patterns (useState, AuthContext, useWebSocket)
- **Styling:** Maintain glassmorphism design system with natural olive greens
- **Responsiveness:** Mobile-first approach with existing Tailwind breakpoints

### State Management Standards
- **Local State:** Use `useState` for component-specific debugging state
- **Global State:** Use existing AuthContext for user-related state
- **API Integration:** Use existing patterns from `ui/src/lib/api.ts`
- **WebSocket:** Use existing `useWebSocket` hook for real-time debugging updates

---

## 9. Template Agent Integration Standards

### Agent Selection Standards
**Every debugging template must include:**
- **OpsAgent** (`agents/ops/`): For infrastructure debugging and deployment issues
- **DevAgent** (`agents/dev/`): For code-level debugging and performance issues
- **QA Agent** (`agents/qa/`): For testing and validation of fixes
- **Support Agent** (`agents/support/`): For user communication and issue tracking

### Agent Communication Standards
- **Debugging Coordination:** Use existing agent-to-agent communication patterns
- **Status Updates:** Use existing WebSocket and event relay patterns
- **Escalation:** Integrate with existing incident management workflows

---

## 10. Template Implementation Standards

### Standard Implementation Phases
**Every debugging template must include these phases:**

#### Phase 1: Issue Identification & Assessment
1. [Gather initial error reports and symptoms]
2. [Check existing monitoring and alerting systems]
3. [Assess impact on users and business operations]
4. [Determine issue severity and escalation requirements]

#### Phase 2: Investigation & Root Cause Analysis
1. [Examine logs and metrics from affected systems]
2. [Test connectivity and functionality of components]
3. [Identify the root cause of the issue]
4. [Document findings and create remediation plan]

#### Phase 3: Resolution & Validation
1. [Implement fixes following existing patterns]
2. [Test solutions in staging environment]
3. [Deploy fixes to production with rollback plan]
4. [Validate resolution and monitor system health]

### Phase Customization
- **Issue Complexity:** Can adjust phases based on issue complexity
- **Team Size:** Can modify phases based on available resources
- **Business Impact:** Can prioritize phases based on user impact

---

## 11. Template Quality Standards

### Template Completion Checklist
**Every debugging template must include:**
- [x] **Task Overview Section** - Clear scope and success criteria
- [x] **Technical Requirements** - Infrastructure, backend, and frontend specifications
- [x] **Implementation Steps** - Phase-by-phase debugging plan
- [x] **Testing Strategy** - Validation and verification requirements
- [x] **Deployment Considerations** - Infrastructure and monitoring needs
- [x] **Success Metrics** - How to measure resolution and system health
- [x] **File Structure** - Clear organization of debugging tools and documentation
- [x] **AI Agent Instructions** - Specific guidance for debugging implementation

### Template Validation
- Ensure all required debugging phases are covered
- Validate that debugging steps don't conflict with existing security measures
- Confirm that rollback procedures are clearly defined
- Verify that communication protocols are established

---

## 12. Template File Organization Standards

### Standard File Structure
**Every debugging template must define:**
- **New Files to Create:** Debugging tools, monitoring scripts, and documentation
- **Existing Files to Modify:** Configuration files, monitoring settings, and documentation
- **File Naming Conventions:** Follow existing naming patterns in your codebase
- **Directory Organization:** Maintain existing folder structure and organization

### File Pattern Standards
- **Debugging Tools:** Follow existing patterns from `agents/ops/` directory
- **Configuration Files:** Follow existing patterns for environment and deployment configs
- **Documentation:** Follow existing patterns for README and documentation files

---

## 13. Template AI Agent Instructions

### Standard AI Agent Workflow
🎯 **MANDATORY PROCESS FOR ALL DEBUGGING TEMPLATES:**
1. **Analyze Existing Patterns:** Study existing debugging workflows and monitoring systems
2. **Maintain Consistency:** Use existing naming conventions, error handling, and architectural patterns
3. **Respect Tenant Isolation:** Always maintain proper tenant isolation using existing `tenant_db.py` patterns
4. **Follow Design System:** Maintain glassmorphism design with natural olive green theme for any UI components
5. **Test Thoroughly:** Create comprehensive testing for debugging solutions following existing testing patterns
6. **Document Changes:** Update relevant documentation, runbooks, and incident reports

### Template-Specific Instructions
**Every debugging template must include:**
- **Issue Context:** Clear explanation of what debugging scenario this template covers
- **Integration Points:** How debugging integrates with existing monitoring and alerting systems
- **Custom Patterns:** Any debugging-specific patterns that differ from standard patterns
- **Testing Requirements:** Debugging-specific testing needs beyond standard requirements

### Code Quality Standards
- **Python:** Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript:** Use strict typing, follow React best practices, maintain accessibility
- **Infrastructure:** Use existing Terraform patterns and GCP best practices
- **Security:** Maintain proper access control, preserve tenant isolation, use existing security patterns

---

## 14. Template Impact Analysis Standards

### Standard Impact Considerations
**Every debugging template must address:**
- **Tenant Isolation:** Ensure debugging doesn't break existing tenant data separation
- **Performance:** Monitor impact on existing API response times during debugging
- **Design Consistency:** Maintain glassmorphism theme across any new debugging UI components
- **Agent Integration:** Ensure debugging doesn't break existing agent communication patterns
- **Infrastructure Stability:** Monitor impact on existing cloud resources and services

### Debugging-Specific Impact Analysis
**Every debugging template must include:**
- **Service Impact:** How debugging might affect existing services and users
- **Performance Considerations:** Specific performance requirements during debugging
- **Security Implications:** Any security considerations specific to debugging activities
- **User Experience Impact:** How debugging affects existing user workflows

### Risk Mitigation Standards
- **Rollback Procedures:** Clear procedures for reverting debugging changes
- **Performance Monitoring:** Monitor system performance during debugging activities
- **User Communication:** Clear communication about any service disruptions
- **Testing:** Test debugging solutions in staging before production deployment

---

## 15. Template Deployment Standards

### Standard Deployment Requirements
**Every debugging template must include:**
- **Cloud Run:** Follow existing deployment patterns for debugging tools
- **Monitoring Integration:** Use existing monitoring and alerting systems
- **Environment Variables:** Use existing Secret Manager patterns for configuration
- **Health Checks:** Implement proper health check endpoints following existing patterns

### Standard Testing Requirements
**Every debugging template must include:**
- **Unit Tests:** Comprehensive test coverage for debugging tools
- **Integration Tests:** Test with existing monitoring and alerting systems
- **UI Tests:** Validate any debugging UI components against existing design system
- **Performance Tests:** Ensure debugging tools don't impact existing performance

### Debugging-Specific Deployment Considerations
- **Emergency Access:** Ensure debugging tools are available during incidents
- **Rollback Capability:** Maintain ability to quickly revert debugging changes
- **Monitoring:** Enhanced monitoring during debugging activities
- **Documentation:** Clear documentation of debugging procedures and tools

---

## 16. Template Documentation Standards

### Standard Documentation Requirements
**Every debugging template must include:**
- **Runbook Documentation:** Clear procedures for common debugging scenarios
- **Tool Documentation:** Document debugging tools and their usage
- **Incident Reports:** Templates for documenting debugging activities and resolutions
- **User Communication:** Templates for communicating with users during debugging

### Documentation Standards
- **Code Comments:** Comprehensive docstrings and inline comments for debugging code
- **README Updates:** Update relevant README files with debugging procedures
- **API Examples:** Provide clear examples for debugging endpoints
- **Component Props:** Document all debugging component props and usage examples

### Template Documentation
**Every debugging template must include:**
- **Usage Instructions:** How to use this template for specific debugging scenarios
- **Customization Guide:** What can be modified vs. what should remain standard
- **Example Output:** Sample debugging task document created from this template

---

## 17. Template Validation & Usage

### Template Completion Checklist
**Before using a debugging template, ensure it includes:**
- [x] All required sections from this meta-template
- [x] Debugging-specific customization points clearly defined
- [x] Standard patterns and requirements properly documented
- [x] AI agent instructions tailored to debugging scenarios
- [x] Example task output or usage instructions
- [x] Integration points with existing monitoring systems clearly defined

### Template Usage Instructions
**To use a debugging template:**
1. **Review the template** to ensure it covers all required debugging aspects
2. **Customize for your specific debugging scenario** by filling in the template sections
3. **Validate the template** against this meta-template checklist
4. **Use the template** to generate specific debugging task documents
5. **Iterate and improve** the template based on debugging results

### Template Maintenance
- **Version Control:** Track template versions and updates
- **Feedback Loop:** Collect feedback from debugging usage to improve future versions
- **Pattern Evolution:** Update templates as your debugging workflows evolve

---

**Template Version:** 1.0  
**Last Updated:** [Current Date]  
**Project:** AI SaaS Factory  
**Architecture:** Multi-agent orchestration with glassmorphism design system  
**Purpose:** Template for creating GCP debugging and troubleshooting tasks
