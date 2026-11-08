# Architecture Standards

## 1. Objective

Define how architecture standards, principles, policies, and technical guidelines are identified and applied during High-Level Design (HLD).

Architecture standards establish consistency, interoperability, security, maintainability, and governance across systems.

The proposed architecture should consider:

- Enterprise architecture principles.
- Organizational technology standards.
- Application and integration standards.
- Security and data governance policies.
- Infrastructure and deployment standards.
- Industry standards and protocols.
- Regulatory and contractual obligations.

Standards should be applied based on their relevance to the system and its operating environment.

Do not invent organizational standards or assume that a commonly adopted industry practice is mandatory.

## 2. Types of Architecture Standards

Distinguish between the following categories.

### 2.1 Enterprise Architecture Principles

High-level principles that guide architecture decisions across the organization.

Examples:

- Prefer reuse of existing enterprise capabilities.
- Minimize unnecessary technology diversity.
- Design for interoperability.
- Apply security by design.
- Prefer loosely coupled components.
- Design for operational resilience.
- Avoid unnecessary vendor dependency.
- Establish clear ownership of systems and data.

### 2.2 Organizational Technology Standards

Technologies, platforms, and products approved or mandated by the organization.

Examples:

- Approved programming languages and frameworks.
- Approved cloud providers.
- Standard database platforms.
- Enterprise identity providers.
- Approved messaging platforms.
- Standard observability platforms.
- Approved CI/CD tooling.
- Supported runtime versions.

Identify whether a technology is mandatory, preferred, permitted, or prohibited.

### 2.3 Technical Standards

Standards governing how systems and components are designed and implemented.

Examples:

- API design conventions.
- REST and HTTP conventions.
- OpenAPI specifications.
- OAuth 2.0 and OpenID Connect.
- TLS configuration standards.
- Database naming and schema conventions.
- Event and message schema standards.
- Logging and telemetry conventions.
- Container image standards.
- Infrastructure-as-code conventions.

### 2.4 Security Standards

Security policies and technical requirements applicable to the system.

Examples:

- Enterprise authentication and authorization policies.
- Encryption requirements.
- Secrets management standards.
- Vulnerability management requirements.
- Secure development practices.
- Audit logging requirements.
- Network security policies.
- Identity and access management standards.

Refer to `security-architecture.md` for security design methodology.

### 2.5 Regulatory and Industry Standards

External standards, frameworks, and obligations that may apply depending on the business domain and operating environment.

Examples include:

- ISO/IEC 27001 for information security management.
- ISO/IEC 27002 for information security controls.
- ISO/IEC 42001 for AI management systems.
- SOC 2 trust services criteria.
- PCI DSS for payment card data environments.
- GDPR for applicable personal data processing.
- HIPAA for applicable protected health information environments.
- OWASP guidance for application security.
- NIST Cybersecurity Framework.
- NIST SP 800-53 security and privacy controls.

These examples are not automatically applicable to every system. Determine applicability from actual business, legal, contractual, and organizational requirements.

## 3. Standards Discovery

Identify applicable standards before finalizing the architecture.

Use the following information sources where available:

1. Enterprise architecture documentation.
2. Organizational technology catalogs.
3. Architecture review board guidelines.
4. Security policies and standards.
5. Cloud and infrastructure reference architectures.
6. API and integration guidelines.
7. Data governance policies.
8. Regulatory and contractual requirements.
9. Existing approved system architecture documents.

Prefer authoritative organizational documentation over assumptions based on general industry practices.

### 3.1 Standards Classification

Classify identified standards as follows:

| Classification | Meaning |
|---|---|
| Mandatory | Must be followed unless an approved exception exists |
| Preferred | Recommended for new systems or changes |
| Permitted | Allowed but not required |
| Prohibited | Must not be used |
| Conditional | Applies only when specified conditions are met |
| Informational | Guidance that may influence architecture decisions |

Record the source and applicability of each important standard.

## 4. Architecture Principles

Evaluate the proposed architecture against relevant principles.

### 4.1 Modularity and Separation of Concerns

- Separate components according to their responsibilities.
- Minimize unnecessary coupling.
- Define clear component boundaries.
- Avoid duplicating shared capabilities without justification.
- Keep business logic separate from infrastructure concerns where appropriate.

### 4.2 Interoperability

- Prefer well-defined interfaces and contracts.
- Use established protocols and data formats.
- Avoid unnecessary proprietary interfaces.
- Define compatibility and versioning expectations.
- Ensure integration mechanisms are consistent with enterprise standards.

### 4.3 Reusability

- Prefer existing enterprise services and shared capabilities.
- Avoid building functionality already provided by approved platforms.
- Reuse common identity, logging, monitoring, and integration services where appropriate.
- Avoid introducing shared components without clear ownership and lifecycle management.

### 4.4 Scalability and Resilience

- Design for expected workload characteristics.
- Avoid unnecessary single points of failure.
- Consider horizontal or vertical scaling where appropriate.
- Define failure isolation and recovery mechanisms.
- Consider graceful degradation and back-pressure where relevant.

### 4.5 Maintainability and Evolvability

- Prefer clear component responsibilities.
- Avoid unnecessary architectural complexity.
- Support controlled changes to interfaces and data structures.
- Consider backward compatibility.
- Minimize dependencies between independently changing components.

### 4.6 Security and Privacy

- Apply least privilege.
- Define explicit trust boundaries.
- Protect sensitive data.
- Use approved identity and access mechanisms.
- Consider privacy and data retention requirements.

Refer to `security-architecture.md` for detailed security considerations.

## 5. Application and API Standards

Identify applicable application and interface standards.

Consider:

- API naming and resource conventions.
- HTTP methods and status codes.
- API authentication and authorization.
- API versioning.
- Request and response formats.
- Error response conventions.
- Pagination and filtering.
- Rate limiting.
- OpenAPI documentation.
- Backward compatibility.
- Event and message contract standards.

Where an organization has established API standards, use them instead of introducing alternative conventions.

For event-driven systems, consider:

- Event naming conventions.
- Event schema formats.
- Schema evolution.
- Message metadata.
- Correlation and causation identifiers.
- Idempotency conventions.
- Delivery and ordering expectations.

## 6. Data Architecture Standards

Identify standards governing data modeling, storage, access, and exchange.

Consider:

- Data ownership and stewardship.
- Data classification.
- Data modeling conventions.
- Naming conventions.
- Data quality requirements.
- Data retention and deletion.
- Data lineage and traceability.
- Data access and authorization.
- Data encryption.
- Data residency.
- Data interchange formats.
- Schema evolution and compatibility.

For systems with multiple data stores, define ownership and consistency responsibilities.

Avoid introducing competing sources of truth without an explicit architectural reason.

## 7. Security and Identity Standards

Identify applicable standards for identity, authentication, authorization, and security controls.

Consider:

- Enterprise identity provider integration.
- OAuth 2.0 and OpenID Connect where applicable.
- Workload and service identity.
- Role-based or attribute-based authorization.
- Multi-factor authentication.
- Secrets management.
- Encryption and key management.
- TLS configuration.
- Security logging and auditing.
- Vulnerability management.
- Secure software development practices.

Ensure the architecture uses approved enterprise security capabilities where available.

For AI-enabled systems, also consider standards governing agent identity, tool authorization, execution isolation, and auditability.

Refer to `security-architecture.md` for the detailed security design methodology.

## 8. Infrastructure and Deployment Standards

Identify standards governing infrastructure provisioning and application deployment.

Consider:

- Approved cloud and hosting environments.
- Network segmentation and connectivity.
- Infrastructure-as-code.
- Containerization and image management.
- Runtime and operating system versions.
- Deployment environments.
- Availability and disaster recovery.
- Backup and restoration.
- Monitoring and observability.
- Configuration and secrets management.
- Resource tagging and ownership.
- Environment isolation.

Prefer approved infrastructure patterns and managed platform capabilities where they satisfy requirements.

## 9. Observability and Operational Standards

Identify standards for monitoring, diagnostics, and operational support.

Consider:

- Centralized logging.
- Metrics collection.
- Distributed tracing.
- Correlation identifiers.
- Health checks.
- Alerting conventions.
- Service-level indicators and objectives.
- Incident management integration.
- Audit log retention.
- Operational dashboards.

Where appropriate, consider OpenTelemetry and other established observability standards.

Ensure that observability requirements are reflected in the component and deployment architecture.

## 10. AI and Agentic Architecture Standards

For AI-enabled systems, identify applicable AI governance, security, and interoperability standards.

Consider:

- Model and provider governance.
- Model version management.
- AI risk management.
- Data protection in model interactions.
- Agent identity and authorization.
- Tool access restrictions.
- Human oversight.
- Auditability and traceability.
- AI evaluation and monitoring.
- Prompt and context management.
- Agent execution isolation.

Relevant external frameworks and specifications may include:

- NIST AI Risk Management Framework.
- ISO/IEC 42001.
- OWASP guidance for LLM and generative AI application security.
- Model Context Protocol specifications, where MCP is used.

These should be evaluated for applicability rather than treated as universal implementation requirements.

## 11. Standards Compliance Assessment

Assess the proposed architecture against the identified standards.

Use a compliance matrix for relevant mandatory and preferred standards.

| Standard ID | Standard / Policy | Applicability | Architecture Area | Compliance Status | Evidence / Gap |
|---|---|---|---|---|---|
| STD-001 | Enterprise API Standard | Applicable | Integration | Compliant | REST API conventions followed |
| STD-002 | Enterprise Identity Policy | Applicable | Security | Partial | Workload identity approach requires confirmation |
| STD-003 | Approved Database Platform | Applicable | Data | Compliant | Approved platform selected |
| STD-004 | Container Runtime Standard | Not applicable | Deployment | N/A | Application uses managed runtime |

Use the following compliance statuses:

- **Compliant:** Architecture satisfies the applicable standard.
- **Partially Compliant:** Some requirements are addressed, but gaps remain.
- **Non-Compliant:** Architecture conflicts with an applicable standard.
- **Pending:** Further information or validation is required.
- **Not Applicable:** The standard does not apply to the system.

Do not mark a standard compliant solely because it is mentioned in the HLD. Identify the architectural evidence supporting the assessment.

## 12. Standards Exceptions and Deviations

Where a mandatory standard cannot be followed, document the deviation.

For each deviation, record:

| Field | Description |
|---|---|
| Deviation ID | Unique identifier |
| Standard Reference | Standard or policy being deviated from |
| Requirement | Specific standard requirement |
| Reason | Why compliance is not feasible or appropriate |
| Impact | Technical, security, operational, or business impact |
| Compensating Controls | Alternative controls that reduce the risk |
| Risk Assessment | Residual risk introduced by the deviation |
| Approval Authority | Required organizational approver |
| Status | Proposed, Submitted, Approved, Rejected, or Expired |

Do not treat an architectural recommendation as an approved exception.

An AI agent may identify and document a deviation, but approval must come from the authorized human or governance process.

## 13. Standards and Architecture Decisions

Document significant standards-related decisions in the HLD.

Examples include:

- Selecting an approved enterprise integration pattern.
- Retaining an existing framework despite a preferred alternative.
- Adopting a new API standard.
- Selecting an approved identity mechanism.
- Deviating from a deployment standard.
- Introducing an external technology not currently in the approved catalog.

Record the rationale, applicable standard, alternatives, implications, and approval status.

## 14. Standards Validation Checklist

Before finalizing the HLD, verify:

- Relevant organizational standards have been identified.
- Mandatory constraints have been distinguished from preferences.
- Standards have authoritative sources where available.
- Regulatory and industry standards have been evaluated for applicability.
- The proposed architecture follows applicable standards.
- Compliance claims are supported by architectural evidence.
- Gaps and deviations are explicitly documented.
- Required approval authorities are identified.
- Technology choices are consistent with organizational standards.
- Security, data, infrastructure, and operational standards have been considered.
- Unresolved standards questions are recorded.

## 15. Architecture Standards Principles for HLD

- Prefer organizational standards over individually selected conventions.
- Do not invent standards or claim compliance without evidence.
- Distinguish mandatory standards from recommended practices.
- Apply standards proportionately to the system and its risks.
- Avoid introducing unnecessary standards or frameworks.
- Reuse approved enterprise capabilities where practical.
- Document deviations and their consequences.
- Treat standards compliance as an ongoing governance concern, not merely a document checklist.
- Reassess applicability when requirements, regulations, or organizational policies change.