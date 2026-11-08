# Security Architecture

## 1. Objective

Define the principles and considerations for designing secure application architectures.

Security architecture should identify threats, establish trust boundaries, define security controls, and ensure that security requirements are addressed by the proposed architecture.

Security decisions should be driven by:
- Functional and non-functional requirements.
- Data sensitivity and business impact.
- Application architecture and deployment environment.
- Organizational security standards and regulatory obligations.
- Operating environment and runtime restrictions.
- External integrations and dependencies.

Do not introduce security technologies or controls without establishing their relevance to the system.

## 2. Security Architecture Principles

Apply the following principles when designing the architecture:

- **Least privilege:** Grant only the permissions necessary to perform a task.
- **Defense in depth:** Use multiple complementary security controls.
- **Zero trust:** Do not implicitly trust users, services, devices, or network locations.
- **Secure by default:** Prefer restrictive defaults and explicit authorization.
- **Separation of duties:** Separate sensitive responsibilities where appropriate.
- **Minimize attack surface:** Expose only necessary interfaces and capabilities.
- **Fail securely:** Ensure failures do not bypass security controls.
- **Explicit trust boundaries:** Identify where trust changes between components, users, and systems.
- **Accountability:** Ensure security-relevant actions can be attributed to an identity.
- **Data minimization:** Collect, process, and retain only necessary data.

## 3. Identity and Access Management

Identify the identities that interact with the system and determine how they are managed.

### 3.1 Human Identities

Consider:

- Identity provider and federation.
- Authentication mechanisms.
- Single sign-on (SSO).
- Multi-factor authentication (MFA).
- Session management and expiration.
- Account provisioning and deprovisioning.
- Privileged user access.
- Role-based or attribute-based access control (RBAC/ABAC).

Clearly distinguish authentication (who the user is) from authorization (what the user can do).

### 3.2 Workload and Service Identities

For application components and services, consider:

- Service accounts or workload identities.
- Machine-to-machine authentication.
- Identity federation.
- Credential issuance and rotation.
- Service-to-service authorization.
- Identity lifecycle and revocation.
- Prevention of shared or hardcoded credentials.

Prefer short-lived credentials and platform-managed identity mechanisms where supported.

### 3.3 Authorization Model

Define:

- Authorization enforcement points.
- Roles, permissions, and resource boundaries.
- Access to APIs, data, and infrastructure.
- Tenant isolation where applicable.
- Administrative and privileged operations.
- Delegated access.
- Default-deny behavior.
- Permission changes and revocation.

Authorization should be enforced by trusted application or platform components, not solely by frontend controls or caller-supplied claims.

## 4. Application and API Security

Evaluate security controls for application interfaces and APIs.

Consider:

- Input validation and output encoding.
- Authentication and authorization on protected endpoints.
- API gateway and ingress controls.
- Rate limiting and abuse prevention.
- Request size and payload restrictions.
- Protection against injection vulnerabilities.
- Cross-site scripting (XSS).
- Cross-site request forgery (CSRF), where applicable.
- Server-side request forgery (SSRF).
- Secure session and cookie configuration.
- API versioning and deprecation.
- Error handling that avoids exposing internal details.

Validate that security controls are enforced consistently across all relevant entry points.

## 5. Data Security and Privacy

Classify the data handled by the system and determine the protection required throughout its lifecycle.

### 5.1 Data Classification

Identify relevant categories, such as:

- Public information.
- Internal business information.
- Confidential information.
- Sensitive personal information.
- Credentials, tokens, and secrets.
- Regulated or legally restricted information.

Use the organization's classification standards where available.

### 5.2 Data Protection Controls

Evaluate:

- Encryption in transit.
- Encryption at rest.
- Key management and key rotation.
- Access control at data-store level.
- Data masking and tokenization.
- Backup encryption.
- Secure data deletion.
- Data retention and archival.
- Data residency and cross-border transfer restrictions.

Identify which components can access sensitive data and why.

### 5.3 Data Lifecycle

Consider security across:

1. Data collection.
2. Data transmission.
3. Data processing.
4. Data storage.
5. Data sharing.
6. Data archival.
7. Data deletion.

Ensure retention and deletion requirements are reflected in the architecture.

## 6. Network Security

Define how network boundaries and communication paths are protected.

Consider:

- Public and private network segmentation.
- Ingress and egress restrictions.
- Firewalls and security groups.
- Private endpoints.
- Network access control lists.
- Service-to-service communication security.
- TLS and certificate management.
- DNS security where relevant.
- Network isolation between environments.
- Administrative access paths.

Identify external communication requirements and restrict outbound access to approved destinations where appropriate.

Do not assume that components in the same private network are inherently trusted.

## 7. Secrets and Cryptographic Key Management

Identify how credentials, secrets, certificates, and cryptographic keys are managed.

Consider:

- Centralized secrets management.
- Managed identity integration.
- Secret injection at runtime.
- Secret rotation and revocation.
- Certificate issuance and renewal.
- Key storage and access restrictions.
- Separation of encryption keys from encrypted data.
- Prevention of secrets in source code, logs, configuration files, and artifacts.
- Auditability of secret access.

Prefer managed secret and key management services where supported by the operating environment.

## 8. Infrastructure and Runtime Security

Evaluate security controls for the underlying runtime and infrastructure.

Consider:

- Operating system and container hardening.
- Runtime isolation.
- Container image provenance and scanning.
- Dependency and vulnerability scanning.
- Patch management.
- Secure configuration baselines.
- Restricted process and filesystem permissions.
- Resource and execution limits.
- Administrative access controls.
- Infrastructure-as-code security checks.
- Environment separation.
- Software supply-chain security.

For containerized systems, evaluate image trust, runtime privileges, mounted volumes, capabilities, and network access.

For serverless or managed platforms, identify the platform security responsibilities and the controls that remain the application's responsibility.

## 9. Integration and Third-Party Security

Assess security risks introduced by external systems and dependencies.

For each significant integration, consider:

- Authentication mechanism.
- Authorization and scope of access.
- Credential storage and rotation.
- Transport security.
- Data exchanged and its classification.
- Network connectivity restrictions.
- Third-party trust and security posture.
- API rate limits and abuse controls.
- Failure behavior and timeout handling.
- Dependency availability and compromise scenarios.

Distinguish between trusted internal systems, approved external providers, and untrusted sources.

## 10. AI and Agentic System Security

For systems that use AI models, agents, or tool execution, evaluate the additional security boundaries introduced by AI capabilities.

### 10.1 Agent Identity and Authorization

Consider:

- Unique identity for each agent or workload.
- User-to-agent delegation.
- Agent-to-agent authentication and authorization.
- Tool-specific permissions.
- Resource-level access restrictions.
- Permission inheritance and delegation boundaries.
- Credential isolation.
- Human approval for sensitive actions.

An agent should not automatically inherit all permissions of the user or runtime in which it executes.

### 10.2 Tool and MCP Security

For tools, plugins, and MCP servers, consider:

- Explicit tool registration and trust.
- Authentication between agents and tool servers.
- Authorization for individual tools and resources.
- Input validation and output handling.
- Restrictions on filesystem, network, and process access.
- Credential exposure through tool responses.
- Tool invocation auditing.
- Confirmation requirements for destructive or sensitive actions.

Treat tool outputs and external content as untrusted input.

### 10.3 Model and Prompt Security

Consider:

- Prompt injection.
- Indirect prompt injection through retrieved content.
- Sensitive information disclosure.
- Unsafe or unauthorized tool execution.
- Model output validation.
- Data leakage through prompts and context.
- Model provider data retention and processing policies.
- Model and prompt version governance.

Do not rely on prompt instructions alone as a security boundary.

### 10.4 Agent Runtime Isolation

Evaluate:

- Execution sandboxing.
- Filesystem and process restrictions.
- Network egress restrictions.
- Resource and execution limits.
- Isolation between concurrent agent sessions.
- Secrets access restrictions.
- Audit trails for agent actions.
- Human intervention and termination mechanisms.

Security enforcement should reside in trusted runtime, platform, and tool authorization controls.

## 11. Logging, Monitoring, and Auditability

Define how security-relevant activities are recorded and monitored.

Consider logging:

- Authentication successes and failures.
- Authorization denials.
- Privileged operations.
- Sensitive data access.
- Configuration and permission changes.
- Secret access.
- Security policy violations.
- Administrative activities.
- Agent and tool execution, where applicable.

Ensure logs:

- Include sufficient identity and correlation information.
- Are protected against unauthorized modification.
- Have appropriate access restrictions.
- Follow retention requirements.
- Avoid recording passwords, tokens, or unnecessary sensitive data.
- Can be forwarded to centralized monitoring or SIEM platforms where required.

Identify alerting and incident-response requirements for significant security events.

## 12. Threat Modeling

Perform threat analysis proportionate to system complexity and risk.

Use an established methodology, such as STRIDE, where appropriate.

Evaluate threats across:

- External entry points.
- Trust boundaries.
- Identity and authorization.
- Data flows and storage.
- External integrations.
- Administrative interfaces.
- Infrastructure and runtime.
- Sensitive business operations.

For each significant threat, identify:

| Field | Description |
|---|---|
| Threat | The potential security threat |
| Affected Component | Component or interface exposed to the threat |
| Impact | Potential business or technical consequence |
| Likelihood | Estimated likelihood, based on available evidence |
| Mitigation | Proposed architectural or operational control |
| Residual Risk | Risk remaining after mitigation |
| Owner / Status | Responsibility and resolution status |

Do not claim that a system is secure merely because a threat-modeling exercise has been performed. Record unresolved threats and residual risks.

## 13. Security Architecture Decisions

Security-related architectural decisions should be documented when they materially influence the design.

Examples include:

- Identity provider selection.
- Authentication and federation approach.
- Authorization model.
- API security strategy.
- Network segmentation approach.
- Encryption and key management.
- Secrets management.
- Runtime isolation.
- Audit and monitoring architecture.
- AI agent permission and execution model.

For each significant decision, record:

- Decision context.
- Requirements and constraints.
- Selected approach.
- Alternatives considered.
- Security implications.
- Trade-offs.
- Residual risks.

## 14. Security Architecture Validation

Validate that proposed security controls address the relevant requirements and threats.

Consider:

- Authentication and authorization coverage.
- Least-privilege access.
- Trust boundary enforcement.
- Sensitive data protection.
- Network access restrictions.
- Secrets and key management.
- Secure failure behavior.
- Audit and monitoring coverage.
- Third-party integration risks.
- Runtime and supply-chain security.
- AI agent and tool permissions, where applicable.

Identify controls that require implementation-level verification or operational validation.

Do not claim that a control has been implemented or tested merely because it is described in the HLD.

## 15. Security Architecture Principles for HLD

- Security controls must be traceable to requirements, risks, standards, or constraints.
- Distinguish confirmed security requirements from recommendations and assumptions.
- Prefer existing organizational security standards and approved platforms.
- Avoid introducing unnecessary security infrastructure.
- Identify security responsibilities across application, platform, and infrastructure layers.
- Make trust boundaries and enforcement points explicit.
- Document unresolved security decisions and residual risks.
- Do not invent compliance certifications or claim regulatory compliance without evidence.
- Treat security as an architectural concern, not a separate implementation phase.
- Ensure security controls are reflected in relevant architecture diagrams and requirements traceability.