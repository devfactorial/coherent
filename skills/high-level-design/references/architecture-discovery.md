# Architecture Discovery

## 1. Objective

This reference defines the information to discover before designing the architecture of a new software system.

The objective is to establish sufficient understanding of:

- The system's intended capabilities and boundaries.
- Its users, actors, and external dependencies.
- Its execution and operating environment.
- Technology and platform constraints.
- Security, infrastructure, and operational requirements.
- Architectural decisions that influence the proposed design.

Architecture discovery should focus on information that materially influences architectural decisions. Avoid asking questions whose answers are already available in the supplied requirements or project context.

## 2. System Context

Establish the system's business and technical context.

Understand:

- What problem the system solves.
- Its primary business capabilities.
- Its intended users and actors.
- Whether it is an internal, external, or customer-facing system.
- Whether it operates independently or as part of a larger ecosystem.
- Upstream and downstream systems.
- External services and third-party dependencies.
- System boundaries and responsibilities.

Identify which capabilities belong inside the proposed system and which are provided by external systems.

## 3. Application Architecture Considerations

Discover the expected application structure.

### 3.1 Application Type

Determine whether the system is primarily:

- Web application.
- Mobile application.
- API or backend service.
- Event-driven processing system.
- Batch processing application.
- Data-intensive application.
- AI-enabled or agentic application.
- Combination of multiple application types.

### 3.2 Architectural Style

Determine whether the system should use:

- Modular monolith.
- Microservices.
- Service-oriented architecture.
- Event-driven architecture.
- Serverless architecture.
- Layered architecture.
- Other styles justified by the requirements.

Evaluate the choice based on:

- Business and domain boundaries.
- Independent deployment requirements.
- Scaling characteristics.
- Team ownership and development structure.
- Operational maturity.
- Integration complexity.
- Expected system evolution.

Do not default to microservices simply because the system has multiple functional capabilities. A modular monolith may be more appropriate when independent deployment and scaling are not required.

### 3.3 Component and Service Boundaries

Identify:

- Major business capabilities.
- Candidate application modules or services.
- Responsibilities of each component.
- Expected dependencies.
- Ownership of business logic.
- Areas requiring independent scaling or deployment.

Avoid prematurely splitting components into services without sufficient architectural justification.

## 4. Technology Stack Discovery

Identify technology preferences, organizational standards, and constraints.

### 4.1 Frontend

If the system requires a user interface, discover:

- Whether a frontend is required.
- Web, mobile, desktop, or other client platforms.
- Preferred frontend framework.
- UI component library or design system.
- Authentication integration requirements.
- Accessibility and browser compatibility requirements.

Potential frameworks include React, Angular, Vue, and other technologies appropriate to the project.

### 4.2 Backend

Discover:

- Preferred programming language.
- Backend framework.
- Runtime requirements.
- API development approach.
- Existing organizational technology standards.
- Developer expertise and maintainability considerations.

Potential technologies include Python/FastAPI, Java/Spring Boot, Node.js/NestJS, and other suitable frameworks.

### 4.3 Data Storage

Determine the data persistence requirements.

Consider:

- Relational databases.
- Document databases.
- Key-value stores.
- Graph databases.
- Object storage.
- Search engines.
- Analytical data platforms.

Evaluate based on:
- Data structure and relationships.
- Transactional requirements.
- Consistency requirements.
- Query patterns.
- Data volume and growth.
- Performance and availability.
- Backup and recovery requirements.

Do not introduce multiple database technologies unless distinct data access or workload requirements justify them.

### 4.4 Messaging and Asynchronous Processing

Determine whether the system requires:

- Synchronous request-response communication.
- Message queues.
- Event streaming.
- Publish-subscribe messaging.
- Background job processing.
- Scheduled tasks.

If asynchronous processing is required, identify relevant delivery, ordering, retry, idempotency, and failure-handling requirements.

## 5. Deployment and Infrastructure Discovery

Understand where and how the system will execute.

### 5.1 Hosting Environment

Determine whether deployment will use:

- Public cloud.
- Private cloud.
- On-premises infrastructure.
- Hybrid infrastructure.
- Managed application platforms.
- Serverless platforms.

Identify any organizational restrictions on cloud providers, regions, or infrastructure services.

### 5.2 Containerization and Orchestration

Determine whether the system requires:

- Direct runtime deployment.
- Container-based deployment.
- Container orchestration.
- Serverless execution.
- Platform-managed deployment.

If container orchestration is required, identify whether an existing organizational platform or Kubernetes environment must be used.

Do not introduce orchestration platforms without a justified operational need.

### 5.3 Deployment Topology

Understand:

- Number of environments.
- Development, testing, staging, and production requirements.
- Expected deployment regions.
- Availability zone requirements.
- Network segmentation.
- Load balancing and ingress.
- Disaster recovery requirements.

### 5.4 CI/CD

Discover:

- Existing CI/CD platform.
- Build and packaging requirements.
- Deployment automation.
- Infrastructure-as-code standards.
- Release approval requirements.
- Rollback expectations.
- Automated testing and quality gates.

Prefer existing organizational CI/CD standards where applicable.

## 6. Operating Environment and Runtime Constraints

This section is particularly important because application architecture must account for the environment in which the system actually executes.

Establish the following constraints.

### 6.1 Execution Identity

Determine:

- Which user or service identity executes the application?
- Does the application run under a dedicated service account?
- Are workloads assigned separate identities?
- Is workload identity or federated identity available?
- Are identities managed centrally?

### 6.2 Permissions and Access

Determine:

- Which filesystem locations can the application access?
- Can it read and write files?
- Can it execute external processes?
- Can it access system resources?
- What database permissions are available?
- What cloud resources can it access?
- Are privileged operations restricted?

### 6.3 Network Access

Determine:

- Is outbound internet access permitted?
- Which internal services can be reached?
- Are external APIs accessible?
- Are inbound connections restricted?
- Are proxies, gateways, or firewalls mandatory?
- Are network destinations allowlisted?

### 6.4 Runtime Restrictions

Determine:

- Supported operating systems.
- Supported runtime and language versions.
- CPU and memory limits.
- Execution time limits.
- Process and thread restrictions.
- Container or sandbox restrictions.
- Availability of persistent storage.
- Restrictions on installing dependencies.

### 6.5 Secrets and Configuration

Determine:

- How secrets are provisioned.
- Whether a centralized secrets manager is available.
- How application configuration is managed.
- Whether environment variables are permitted.
- How credentials are rotated.
- Whether secrets can be accessed at runtime.

Never assume that credentials can be embedded in application configuration or source code.

### 6.6 Data Residency and Retention

Determine:

- Permitted data storage locations.
- Data residency requirements.
- Data classification and sensitivity.
- Data retention and deletion requirements.
- Encryption requirements.
- Restrictions on transferring data across regions or external services.

## 7. Security and Identity Discovery

Establish the security constraints that influence architecture.

Discover:

- User authentication requirements.
- Application authorization model.
- Role-based or attribute-based access control requirements.
- Identity provider and federation requirements.
- Service-to-service authentication.
- API security requirements.
- Encryption in transit and at rest.
- Audit logging requirements.
- Compliance and regulatory obligations.

For systems involving AI agents, also investigate:

- Agent execution identity.
- Tool and resource permissions.
- Agent-to-agent authorization.
- Runtime isolation.
- Human approval requirements for sensitive operations.
- Auditability of agent actions.

## 8. Integration and External Dependencies

Identify dependencies on systems outside the proposed application boundary.

For each integration, establish:

- External system or service.
- Purpose of integration.
- Direction of communication.
- API, event, file, or messaging interface.
- Authentication mechanism.
- Expected availability.
- Rate limits and usage restrictions.
- Failure and retry behavior.
- Data exchanged.

Distinguish between mandatory dependencies and optional integrations.

## 9. Operational and Organizational Constraints

Discover constraints that affect architecture and long-term operation.

Consider:

- Existing monitoring and observability platforms.
- Centralized logging requirements.
- Distributed tracing standards.
- Alerting and incident management.
- Backup and disaster recovery.
- Support and maintenance ownership.
- Development team capabilities.
- Technology licensing and procurement restrictions.
- Vendor and third-party dependency policies.
- Required architecture and security reviews.

Prefer established organizational capabilities over introducing new operational platforms.

## 10. Discovery Outcome

The discovery activity should establish the following architectural inputs:

| Area | Expected outcome |
|---|---|
| System context | System boundary, actors, capabilities, external dependencies |
| Application architecture | Architectural style and candidate component boundaries |
| Technology | Technology preferences, constraints, and existing standards |
| Data | Data characteristics and persistence requirements |
| Infrastructure | Hosting, runtime, deployment, and networking constraints |
| Security | Identity, authorization, permissions, and protection requirements |
| Integration | External systems and communication requirements |
| Operations | CI/CD, monitoring, recovery, and ownership constraints |

Distinguish between:

- Confirmed constraints.
- User preferences.
- Organizational standards.
- Architectural assumptions.
- Unresolved decisions.

Do not treat a preference as a mandatory constraint unless explicitly confirmed.

## 11. Architecture Discovery Principles

Apply these principles during discovery:

- Reuse information already available in the requirements and project context.
- Ask only questions that materially influence architectural decisions.
- Prefer organizational technology standards when they satisfy the requirements.
- Do not introduce technologies merely because they are popular.
- Distinguish mandatory constraints from preferences.
- Identify operational and security constraints before proposing deployment architecture.
- Avoid making irreversible technology choices when important information is unavailable.
- Document assumptions explicitly when decisions must proceed with incomplete information.