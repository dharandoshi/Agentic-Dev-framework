# Requirements Traceability Matrix
**Project:** [Project Name]
**Document ID:** RTM-[PROJECT]-[YYYY-MM-DD]
**Version:** 1.0
**Last Updated:** [Date]
**Maintained By:** Requirements Analyst

## Version History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Name] | Initial RTM |

## Purpose
This Requirements Traceability Matrix (RTM) maps and traces requirements from their origin through implementation and testing, ensuring complete coverage and accountability.

## Traceability Matrix

| Req ID | Requirement Description | Source | Priority | Design Ref | Code Module | Test Case | Status | Notes |
|--------|------------------------|--------|----------|------------|-------------|-----------|--------|-------|
| BR-001 | [Business requirement] | BRD §5.1 | High | DD-001 | Module.A | TC-001, TC-002 | Implemented | [Notes] |
| BR-002 | [Business requirement] | BRD §5.1 | Medium | DD-002 | Module.B | TC-003 | In Development | [Notes] |
| FR-001 | [Functional requirement] | FRS §3.1 | High | DD-003 | Module.C | TC-004, TC-005 | Testing | [Notes] |
| FR-002 | [Functional requirement] | FRS §3.2 | Low | DD-004 | Module.D | TC-006 | Not Started | [Notes] |
| NFR-001 | [Non-functional requirement] | FRS §8 | High | DD-005 | Module.E | TC-007 | Implemented | [Notes] |

## Requirement Status Legend
- **Not Started**: Requirement not yet addressed
- **In Design**: Being designed/architected
- **In Development**: Currently being implemented
- **Testing**: Under testing
- **Implemented**: Completed and tested
- **Deferred**: Postponed to future release
- **Cancelled**: No longer required

## Coverage Analysis

### Requirements Coverage
| Category | Total | Implemented | In Progress | Not Started | Coverage % |
|----------|-------|-------------|-------------|-------------|------------|
| Business Requirements | [#] | [#] | [#] | [#] | [%] |
| Functional Requirements | [#] | [#] | [#] | [#] | [%] |
| Non-Functional Requirements | [#] | [#] | [#] | [#] | [%] |
| **Total** | [#] | [#] | [#] | [#] | [%] |

### Test Coverage
| Requirement Type | Total Requirements | Requirements with Tests | Test Coverage % |
|------------------|-------------------|------------------------|-----------------|
| Business | [#] | [#] | [%] |
| Functional | [#] | [#] | [%] |
| Non-Functional | [#] | [#] | [%] |
| **Overall** | [#] | [#] | [%] |

## Backward Traceability
(From Test Cases back to Requirements)

| Test Case | Tests Requirement(s) | Test Type | Test Status |
|-----------|---------------------|-----------|-------------|
| TC-001 | BR-001 | Functional | Pass |
| TC-002 | BR-001, FR-003 | Integration | Pass |
| TC-003 | BR-002 | Functional | In Progress |
| TC-004 | FR-001 | Functional | Not Started |

## Forward Traceability
(From Requirements to Deliverables)

| Requirement | Impacts | Deliverables | Stakeholders |
|-------------|---------|--------------|--------------|
| BR-001 | User Login | Login Module, Auth Service | All Users |
| BR-002 | Reporting | Report Module, Dashboard | Managers |
| FR-001 | Data Entry | Form Component, Validation | Data Entry Team |

## Change Impact Analysis

| Change Request | Affected Requirements | Impact Assessment | Approval Status |
|----------------|----------------------|-------------------|-----------------|
| CR-001 | BR-001, FR-002, FR-003 | Medium - 3 modules affected | Approved |
| CR-002 | BR-003 | Low - UI change only | Pending |

## Dependency Mapping

| Requirement | Depends On | Required By | Critical Path |
|-------------|------------|-------------|---------------|
| BR-001 | None | BR-002, FR-001 | Yes |
| BR-002 | BR-001 | FR-003 | Yes |
| FR-001 | BR-001 | FR-002 | No |

## Risk Tracking

| Requirement | Risk Description | Probability | Impact | Mitigation |
|-------------|------------------|-------------|--------|------------|
| BR-001 | Complex integration | Medium | High | Early prototyping |
| FR-003 | Performance concerns | Low | Medium | Load testing |

## Compliance Mapping

| Requirement | Compliance Standard | Verification Method | Status |
|-------------|-------------------|-------------------|--------|
| NFR-001 | ISO 27001 | Security Audit | Compliant |
| NFR-002 | GDPR | Privacy Assessment | In Review |

## Review & Sign-off

| Role | Name | Signature | Date | Comments |
|------|------|-----------|------|----------|
| Business Analyst | | | | |
| Technical Lead | | | | |
| QA Lead | | | | |
| Project Manager | | | | |

## Notes & Assumptions
- [Note 1]
- [Note 2]
- [Assumption 1]
- [Assumption 2]