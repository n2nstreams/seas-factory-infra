# AI SaaS Factory Code Review Template - Quality Assurance & Security Review

## 1. Task Overview

### Task Title
**Title:** [Code Review: Component/Feature Name] - [Review Type: Security/Quality/Performance/Architecture]

### Goal Statement
**Goal:** Conduct comprehensive code review to ensure code quality, security, performance, and adherence to SaaS Factory standards. Identify issues, provide actionable feedback, and maintain the high-quality bar required for production deployment.

---

## 2. Code Review Analysis & Current State

### Technology & Architecture Context
- **Frameworks & Versions:** Python 3.12, FastAPI, React 18, TypeScript 5.8.3, Vite 5
- **Language:** Python (Backend), TypeScript (Frontend)
- **Database & ORM:** PostgreSQL 15 + pgvector, asyncpg, custom tenant isolation system
- **UI & Styling:** Tailwind CSS 3.4.17, shadcn/ui components, glassmorphism design system with natural olive greens
- **Authentication:** Multi-tenant JWT with tenant isolation, role-based access control
- **Key Architectural Patterns:** Multi-agent orchestration (Vertex AI + LangGraph), microservices on Cloud Run, shared-first tenancy with isolation upgrade path

### Current State
[Analysis of the current code being reviewed - what exists, what's being changed, and the context of the review]

### Review Scope & Focus Areas
[Define the specific scope of the code review and key areas of focus]

## 3. Context & Problem Definition

### Problem Statement
[Detailed explanation of what code is being reviewed, the purpose of the review, and any specific concerns or areas of focus]

### Success Criteria
- [ ] Code meets SaaS Factory quality standards (80%+ test coverage)
- [ ] Security vulnerabilities identified and addressed
- [ ] Performance implications assessed and optimized
- [ ] Tenant isolation properly maintained
- [ ] Code follows established patterns and conventions
- [ ] Documentation and comments are comprehensive
- [ ] All automated checks pass (tests, linting, security scans)

---

## 4. Code Review Context & Standards

### Code Review Standards
- **🚨 Project Stage:** Production-ready SaaS platform with established multi-agent architecture
- **Breaking Changes:** Must be avoided - maintain backward compatibility
- **Data Handling:** Strict tenant isolation required using existing `tenant_db.py` patterns, GDPR compliance mandatory
- **User Base:** Multi-tenant SaaS customers with production workloads
- **Priority:** Quality and security over speed, maintain system stability and glassmorphism design consistency

---

## 5. Code Review Requirements & Standards

### Functional Requirements
- **Code Quality Assessment:** Evaluate code structure, readability, and maintainability
- **Security Review:** Identify security vulnerabilities and compliance issues
- **Performance Analysis:** Assess performance impact and optimization opportunities
- **Pattern Compliance:** Verify adherence to established SaaS Factory patterns
- **Testing Validation:** Ensure comprehensive test coverage and quality
- **Documentation Review:** Verify code documentation and API specifications

### Non-Functional Requirements
- **Performance:** Maintain <200ms API response times, <2s UI load times
- **Security:** Zero critical vulnerabilities, proper tenant isolation
- **Usability:** Follow glassmorphism design theme, natural olive green palette
- **Responsive Design:** Mobile-first approach with comprehensive device support
- **Theme Support:** Consistent with existing design system and branding

### Technical Constraints
- [Must use existing tenant isolation system from `tenant_db.py` and `access_control.py`]
- [Cannot modify existing database tables without proper migrations in `dev/migrations/`]
- [Must maintain compatibility with existing agent architecture and orchestration patterns]
- [Must follow existing FastAPI route patterns and Pydantic models from `api_gateway/`]
- [Must use existing glassmorphism design system from `ui/src/index.css`]

---

## 6. Code Review Focus Areas

### 1. **Security Review**
- **Tenant Isolation:** Verify Row-Level Security (RLS) policies
- **Input Validation:** Check Pydantic models and sanitization
- **Authentication:** Verify proper JWT handling and authorization
- **Secret Management:** Ensure no hardcoded secrets or credentials
- **API Security:** Validate rate limiting and access controls
- **Dependency Security:** Check for known vulnerabilities

### 2. **Code Quality Assessment**
- **Python Standards:** PEP 8 compliance, type hints, docstrings
- **TypeScript Standards:** Proper typing, ESLint compliance
- **Architecture Patterns:** Follow established SaaS Factory patterns
- **Error Handling:** Comprehensive exception handling and logging
- **Code Structure:** Logical organization and separation of concerns
- **Naming Conventions:** Consistent with project standards

### 3. **Performance Analysis**
- **Database Queries:** Efficient queries with proper indexing
- **API Response Times:** Maintain performance targets
- **Resource Usage:** Memory and CPU optimization
- **Caching Strategy:** Appropriate use of Redis and CDN
- **Async Operations:** Proper use of asyncio and async/await
- **Frontend Optimization:** React performance best practices

### 4. **Testing Validation**
- **Test Coverage:** Minimum 80% coverage for backend, comprehensive frontend tests
- **Test Quality:** Meaningful tests that validate functionality
- **Integration Tests:** End-to-end workflow validation
- **Performance Tests:** Load testing for critical paths
- **Security Tests:** Vulnerability scanning and penetration testing
- **Tenant Isolation Tests:** Verify multi-tenant boundaries

---

## 7. Review Process & Workflow

### 1. **Pre-Review Setup**
- [ ] Identify code scope and review boundaries
- [ ] Set up review environment with proper access
- [ ] Review related documentation and requirements
- [ ] Check automated test results and CI/CD status
- [ ] Prepare review checklist and focus areas

### 2. **Code Analysis Phase**
- [ ] **Static Analysis:** Run linting, security scans, and code quality tools
- [ ] **Pattern Review:** Verify adherence to established SaaS Factory patterns
- [ ] **Security Assessment:** Identify vulnerabilities and compliance issues
- [ ] **Performance Review:** Analyze performance implications
- [ ] **Testing Validation:** Review test coverage and quality
- [ ] **Documentation Check:** Verify code comments and API docs

### 3. **Issue Documentation**
- [ ] **Critical Issues:** Security vulnerabilities, breaking changes, data loss risks
- [ ] **High Priority:** Performance degradation, major architectural concerns
- [ ] **Medium Priority:** Code quality issues, pattern violations
- [ ] **Low Priority:** Minor improvements, style suggestions
- [ ] **Documentation:** Missing or unclear documentation

### 4. **Feedback Generation**
- [ ] **Actionable Recommendations:** Specific steps to address issues
- [ ] **Code Examples:** Provide corrected code snippets where helpful
- [ ] **Resource References:** Link to relevant documentation and patterns
- [ ] **Priority Ranking:** Clear indication of issue importance
- [ ] **Timeline Estimates:** Realistic effort estimates for fixes

---

## 8. Review Tools & Automation

### Automated Tools
- **Python:** pytest, black, ruff, mypy, bandit (security)
- **TypeScript:** ESLint, Prettier, TypeScript compiler
- **Security:** Snyk CLI, OWASP ZAP, license scanning
- **Coverage:** pytest-cov, coverage.py, Istanbul (frontend)
- **Performance:** k6 load testing, Lighthouse (frontend)

### Manual Review Areas
- **Architecture Decisions:** Design pattern choices and trade-offs
- **Business Logic:** Complex algorithms and business rules
- **User Experience:** UI/UX consistency and accessibility
- **Integration Points:** API contracts and data flow
- **Error Handling:** Exception scenarios and edge cases

---

## 9. Review Output & Deliverables

### Review Report Structure
```markdown
## Code Review Summary

### 📊 Overall Assessment
- **Quality Score:** [0-100]
- **Security Status:** [Pass/Fail with details]
- **Performance Impact:** [Low/Medium/High]
- **Recommendation:** [Approve/Approve with Changes/Request Changes]

### 🚨 Critical Issues
[List of critical issues that must be addressed]

### ⚠️ High Priority Issues
[List of high priority issues to address]

### 📝 Medium Priority Issues
[List of medium priority issues to consider]

### 💡 Improvement Suggestions
[List of optional improvements]

### ✅ Positive Aspects
[Highlight good practices and well-implemented features]
```

### Action Items
- [ ] **Immediate Actions:** Critical issues that block approval
- [ ] **Required Changes:** High priority issues that must be addressed
- [ ] **Optional Improvements:** Medium/low priority suggestions
- [ ] **Follow-up Items:** Areas for future review or monitoring

---

## 10. Quality Standards & Thresholds

### Approval Criteria
- **✅ Approve:** No critical issues, <3 high priority issues, quality score >80
- **⚠️ Approve with Changes:** No critical issues, <5 high priority issues, quality score >70
- **❌ Request Changes:** Critical issues present or quality score <70

### Quality Metrics
- **Test Coverage:** Backend ≥80%, Frontend ≥70%
- **Security Score:** ≥90 (no critical vulnerabilities)
- **Performance:** <200ms API response, <2s UI load
- **Code Quality:** <5 linting errors, <3 code smell warnings
- **Documentation:** All public APIs documented, inline comments for complex logic

---

## 11. Code Review AI Agent Instructions

### Implementation Workflow
🎯 **MANDATORY PROCESS FOR CODE REVIEWS:**
1. **Setup Review Environment:** Configure tools and access for comprehensive analysis
2. **Automated Analysis:** Run all automated tools (linting, security, tests, coverage)
3. **Pattern Compliance Check:** Verify adherence to established SaaS Factory patterns
4. **Security Deep Dive:** Comprehensive security assessment using multiple tools
5. **Performance Analysis:** Assess performance implications and optimization opportunities
6. **Manual Code Review:** Detailed examination of business logic and architecture
7. **Issue Documentation:** Document all findings with clear priority levels
8. **Feedback Generation:** Create actionable recommendations with code examples
9. **Review Report:** Generate comprehensive review summary with clear next steps

### Code Review Specific Instructions
**Every code review must include:**
- **Tenant Isolation Verification:** Ensure changes maintain proper tenant boundaries
- **Pattern Compliance:** Verify adherence to established SaaS Factory patterns
- **Design Consistency:** Maintain glassmorphism theme and natural olive greens
- **Security Validation:** Comprehensive security assessment and vulnerability scanning

### Communication Preferences
- Provide clear, actionable feedback with specific examples
- Use priority levels (Critical/High/Medium/Low) for all issues
- Include code snippets and specific line references
- Link to relevant documentation and established patterns
- Provide realistic effort estimates for addressing issues

### Code Quality Standards
- Enforce SaaS Factory established patterns and conventions
- Maintain strict security and tenant isolation requirements
- Ensure comprehensive test coverage and quality
- Follow established naming conventions and code structure
- Verify proper error handling and logging patterns
- Maintain tenant isolation patterns from `tenant_db.py`

---

## 12. Second-Order Impact Analysis

### Impact Assessment
- **Tenant Isolation:** Verify changes don't break multi-tenant boundaries
- **Performance:** Assess impact on existing API response times and user experience
- **Security:** Ensure no new vulnerabilities are introduced
- **Integration:** Consider impact on other agents and services
- **User Experience:** Maintain consistency with existing UI/UX patterns
- **Maintenance:** Ensure code remains maintainable and well-documented

### Risk Mitigation
- [ ] **Security Testing:** Comprehensive security scanning and penetration testing
- [ ] **Performance Testing:** Load testing to verify performance impact
- [ ] **Integration Testing:** End-to-end testing of affected workflows
- [ ] **Rollback Plan:** Ensure changes can be safely reverted if needed
- [ ] **Monitoring:** Enhanced monitoring during and after deployment

---

## 13. SaaS Factory Code Review Patterns

### Backend Patterns to Verify
- **Agent Structure:** Follow established agent template patterns from `agents/` directory
- **Database Access:** Use `TenantDatabase` and `TenantContext` from `agents/shared/tenant_db.py`
- **API Design:** Follow FastAPI patterns with proper validation from `api_gateway/` files
- **Error Handling:** Use established HTTP status codes and error formats
- **Logging:** Structured logging with tenant context and proper levels
- **Testing:** pytest patterns with async support and proper fixtures

### Frontend Patterns to Verify
- **Component Structure:** Follow established React component patterns from `ui/src/components/`
- **Styling:** Use Tailwind CSS with glassmorphism design theme and natural olive greens
- **State Management:** Proper use of React hooks and context
- **API Integration:** Use established API client patterns from `ui/src/lib/api.ts`
- **Routing:** Follow existing route structure and navigation patterns
- **Testing:** React Testing Library patterns with proper mocking

### Security Patterns to Verify
- **Tenant Isolation:** Row-Level Security (RLS) policies enforced using existing patterns
- **Authentication:** JWT validation and proper authorization checks
- **Input Validation:** Pydantic models with comprehensive validation
- **Secret Management:** No hardcoded secrets, use Google Secret Manager
- **Access Control:** Proper subscription tier enforcement using `access_control.py`
- **Data Encryption:** Sensitive data properly encrypted

### Agent Integration Patterns to Verify
- **Agent Communication:** Follow existing agent-to-agent communication patterns
- **Event Handling:** Use existing WebSocket and event relay patterns
- **Orchestration:** Integrate with existing Vertex AI Agent Engine patterns

---

## 14. Review Completion Checklist

### Final Review Steps
- [ ] **Automated Checks:** All tools run successfully with results documented
- [ ] **Manual Review:** Business logic and architecture thoroughly examined
- [ ] **Issue Documentation:** All findings documented with clear priorities
- [ ] **Feedback Generation:** Actionable recommendations provided
- [ ] **Review Report:** Comprehensive summary generated
- [ ] **Next Steps:** Clear action plan for addressing issues
- [ ] **Follow-up Plan:** Schedule for re-review if changes are needed

### Review Artifacts
- [ ] **Review Report:** Complete review summary with findings
- [ ] **Issue Log:** Detailed list of all issues with priorities
- [ ] **Code Examples:** Corrected code snippets for major issues
- [ ] **Performance Data:** Benchmark results and optimization suggestions
- [ ] **Security Findings:** Vulnerability scan results and remediation steps
- [ ] **Test Results:** Coverage reports and test quality assessment

---

## 15. Continuous Improvement

### Review Process Enhancement
- [ ] **Pattern Updates:** Identify new patterns to add to templates
- [ ] **Tool Improvements:** Suggest enhancements to automated tools
- [ ] **Process Refinement:** Optimize review workflow and efficiency
- [ ] **Knowledge Sharing:** Document lessons learned and best practices
- [ ] **Training Updates:** Identify areas for team skill development

### Template Evolution
- [ ] **Pattern Recognition:** Identify recurring issues for template updates
- [ ] **Tool Integration:** Add new automated tools to review process
- [ ] **Standard Updates:** Revise quality thresholds based on project evolution
- [ ] **Best Practices:** Incorporate new industry best practices
- [ ] **Feedback Integration:** Update templates based on review feedback

---

## 16. Emergency Procedures

### Critical Issue Response
- **🚨 Security Breach:** Immediate security review and incident response
- **💥 System Failure:** Performance degradation requiring immediate attention
- **🔒 Data Breach:** Tenant isolation failure or data exposure
- **⚡ Production Impact:** Changes affecting production system stability

### Escalation Process
1. **Immediate Notification:** Alert relevant stakeholders
2. **Issue Assessment:** Rapid evaluation of impact and scope
3. **Mitigation Steps:** Implement immediate fixes and workarounds
4. **Root Cause Analysis:** Identify underlying causes
5. **Prevention Measures:** Implement safeguards to prevent recurrence
6. **Documentation:** Record incident details and lessons learned

---

This template provides a comprehensive framework for conducting thorough code reviews in the SaaS Factory environment, ensuring code quality, security, and adherence to established patterns while maintaining the high standards required for production deployment.
