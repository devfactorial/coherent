---
name: high-level-design
description: Create high-level software architecture designs from functional requirements, non-functional requirements, and existing system context. Use when designing a new system, adding capabilities to an existing system, or making architectural changes.
---

# High-Level Design Skill

## 1. Purpose

Create a comprehensive High-Level Design (HLD) document that translates functional and non-functional requirements into a technology-aware, secure, scalable, maintainable, and deployable architecture.

The HLD must:

- Address functional and non-functional requirements explicitly.
- Respect existing architecture, technology choices, and organizational constraints.
- Prefer incremental architectural changes for existing systems.
- Select appropriate architecture and design patterns based on their applicability.
- Document technology choices, architectural decisions, assumptions, constraints, and trade-offs.
- Include relevant architecture diagrams.
- Maintain traceability between requirements and architecture.
- Address security, deployment, and operational considerations.

The output must describe the architecture and significant design decisions without becoming a low-level implementation specification.

## 2. Inputs and Context Discovery

### 2.1 Mandatory inputs

Discover and analyze:

1. Functional Requirements Document(s) (FRDs).
2. Non-Functional Requirements Document(s) (NFRDs).

Use the original requirement identifiers and descriptions. Do not silently modify or reinterpret approved requirements.

### 2.2 Contextual inputs

Discover relevant project context, where available:

- System context documentation.
- Existing HLDs and LLDs.
- Architecture Decision Records (ADRs).
- Technology stack documentation.
- Deployment and infrastructure documentation.
- Security architecture documentation.
- API and integration specifications.
- Relevant source code and project configuration.
- Organizational technology and architecture standards.

Inspect the project documentation and relevant configuration files when necessary.

Do not assume that all contextual documents exist.

### 2.3 Missing information and conflicts

Identify:

- Missing requirements or architecture information.
- Ambiguous requirements.
- Contradictory requirements.
- Unresolved architectural decisions.
- Constraints that may affect the proposed design.

Do not silently resolve material conflicts or invent missing requirements.

Ask the user for clarification when missing information materially affects the architecture. Distinguish confirmed information from assumptions and recommendations.

## 3. Execution Workflow

Follow the phases below in sequence. Do not skip mandatory analysis activities.

### Phase 1: Required Input: Requirements Baseline

The HLD skill must receive the path to a specific, versioned, approved requirements baseline.

Example:
requirements/baselines/v1.0/

The baseline contains the authoritative FRD, NFRD, and relevant system context documents (optional).

Mandatory rules:
- Use only documents belonging to the supplied baseline.
- Do not search other baseline folders.
- Do not combine documents from different baselines.
- Do not independently select or substitute requirement documents.
- Preserve requirement IDs and traceability.

### Phase 2: Understand the System Context

Determine whether the design concerns:

- A completely new system.
- A new capability within an existing system.
- An architectural change to an existing system.

#### For an existing system

Establish the relevant existing architecture baseline.

Understand, where applicable:

- Application architecture and component responsibilities.
- Existing services, APIs, and integration mechanisms.
- Technology stack and frameworks.
- Database architecture and data ownership.
- Deployment and infrastructure architecture.
- Network architecture and communication boundaries.
- Security architecture, identities, and access controls.
- Existing architectural patterns and decisions.
- Operational and organizational constraints.

Use existing documentation as the primary source of context. Inspect relevant source code and configuration when documentation is insufficient.

Preserve existing architectural decisions unless requirements or constraints justify changing them.

**Mandatory:** Before proposing changes, perform the incremental architecture and change impact analysis described in `references/incremental-architecture.md`.

#### For a new system

When no existing architecture baseline is available, gather the necessary architectural context through an interactive discovery process.

Read and follow `references/architecture-discovery.md`.

Ask one question at a time. Do not ask for information already available in project documentation or previous answers.

For each question:

- Explain why the information is needed.
- Provide reasonable options where applicable.
- Recommend a default when sufficient information is available.
- Allow a custom answer.
- Allow the user to defer non-essential decisions.

Discovery must cover relevant areas, including:

- Application architecture: monolith, modular monolith, microservices, or event-driven architecture.
- Frontend: whether a UI is required, framework, technology stack, and hosting.
- Backend: programming language, framework, and runtime.
- Infrastructure: cloud, on-premises, hybrid, hosting, and orchestration platform.
- Repository strategy: monorepo or multiple repositories.
- CI/CD: tooling, release process, and deployment approvals.
- Data architecture: databases, caching, search, messaging, and storage.
- Integration: external systems, APIs, protocols, and event mechanisms.
- Operating environment: execution identities, permissions, network access, filesystem access, secrets, runtime restrictions, and data constraints.
- Security and identity: authentication, authorization, identity provider, and security requirements.
- Observability and operations: logging, metrics, tracing, alerting, support, and disaster recovery.

Ask only questions relevant to the proposed system.

### Phase 3: Architecture Analysis

Analyze the requirements and system context to identify:

1. Major system capabilities.
2. Logical components and their responsibilities.
3. External systems and integration boundaries.
4. Data flows and ownership.
5. Communication mechanisms.
6. Security boundaries and access requirements.
7. Deployment topology.
8. Scalability, availability, and reliability requirements.
9. Operational and monitoring requirements.

Determine the architectural style that best addresses the requirements.

Consider alternatives. Do not automatically select microservices, event-driven architecture, or other complex patterns without a justified need.

For existing systems, base the analysis on the existing architecture and the proposed change delta.

### Phase 4: Architecture Pattern Selection

Read `references/architecture-patterns.md` (if available) before selecting architecture patterns.

Consider applicable patterns from:

- Application architecture.
- Integration.
- Distributed systems.
- Data architecture.
- Resilience.
- Security.
- Deployment.

For each significant pattern selected, document:

- Pattern name.
- Problem being addressed.
- Reason for selection.
- Where it is applied.
- Benefits.
- Trade-offs and limitations.
- Alternatives considered.

Do not force pattern usage when it adds no architectural value.

If a relevant pattern is missing from the supplied catalog, identify it as an additional candidate. Do not represent it as an existing catalog entry.

### Phase 5: Develop the Architecture

Develop the proposed architecture with sufficient detail to establish the system structure, component responsibilities, interactions, and major design decisions.

Cover the following areas where applicable:

#### 5.1 System context

Document system boundaries, actors, external systems, and interactions.

#### 5.2 Component architecture

Identify major components, responsibilities, dependencies, interfaces, and communication mechanisms.

#### 5.3 Network architecture

Document network boundaries, communication paths, gateways, ingress and egress, and relevant network security controls.

#### 5.4 Security architecture

Document authentication, authorization, identities, permissions, secrets management, encryption, trust boundaries, and audit requirements.

#### 5.5 Data architecture

Document databases, data ownership, persistence mechanisms, caching, data flows, and storage decisions.

#### 5.6 Integration architecture

Document external integrations, protocols, APIs, messaging, event flows, and error-handling mechanisms.

#### 5.7 Deployment architecture

Document deployment topology, environments, infrastructure components, orchestration, scaling, and deployment strategy.

#### 5.8 Technology selection

Read `references/technology-selection.md` before making significant technology, framework, or library recommendations.

For every significant technology choice, document:

- Technology, framework, or library.
- Purpose and intended use.
- Reason for selection.
- Alternatives considered.
- Benefits and limitations.
- Relevant organizational or platform constraints.

Prefer existing organizational standards and approved technologies when applicable.

Do not introduce new technologies into an existing system without establishing a clear architectural need.

### Phase 6: NFR Realization and Validation

Read `references/hld-template.md` and `references/technology-selection.md` where relevant to document NFR realization.

For every applicable NFR, identify:

1. Requirement identifier and description.
2. Expected measurable target.
3. Architectural mechanism used to address it.
4. Components affected.
5. Design considerations and trade-offs.
6. Proposed validation approach.

Consider the following dimensions where applicable:

- Performance.
- Scalability.
- Availability.
- Reliability.
- Resilience.
- Security.
- Maintainability.
- Extensibility.
- Observability.
- Portability.
- Interoperability.
- Compliance.

Every applicable NFR must have explicit architectural coverage or be identified as unresolved, unsupported, or requiring further clarification.

Distinguish between architectural design coverage and actual verification. Do not claim an NFR has been verified unless supporting test or operational evidence exists.

### Phase 7: Architecture Decisions and Trade-offs

Document significant architectural decisions.

For each decision, include:

- Decision ID.
- Decision description.
- Context and problem.
- Options considered.
- Selected option.
- Rationale.
- Positive consequences.
- Negative consequences.
- Related requirements.

Document assumptions explicitly.

Do not present unverified assumptions as confirmed requirements or user-approved decisions.

Record unresolved questions and risks separately.

## 4. Architecture Diagrams

Read `references/architecture-diagrams.md` before creating architecture diagrams.

Use Mermaid diagrams embedded in the Markdown HLD.

Include the following diagrams whenever the corresponding architecture is relevant:

1. System Context Diagram.
2. Network Architecture Diagram.
3. Security Architecture Diagram.
4. Component Architecture Diagram.

Include other diagrams when they materially improve the architecture description.

Diagrams must:

- Reflect the actual proposed architecture.
- Include relevant actors, components, and boundaries.
- Show important interactions and communication flows.
- Identify security and trust boundaries where relevant.
- Be consistent with the written architecture.
- Clearly distinguish existing architecture from proposed changes when designing an enhancement to an existing system.

Do not generate misleading, speculative, or unsupported diagrams.

## 5. Industry Standards and Best Practices

Read `references/architecture-standards.md` and `references/security-architecture.md` where applicable.

Consider relevant standards and established practices, including:

- C4 Model for architecture visualization.
- ISO/IEC/IEEE 42010 for architecture description.
- OWASP guidance for application security.
- NIST Cybersecurity Framework and relevant NIST publications.
- Cloud provider architecture frameworks and well-architected guidance.
- Relevant regulatory and organizational standards.

Select standards based on the project's domain, requirements, and operating environment.

Do not claim compliance or certification simply because a design references a standard.

## 6. HLD Output Document

Generate the HLD as a Markdown document.

Read `references/hld-template.md` and use it as the authoritative document structure.

The HLD must contain the following sections:

1. Introduction
2. Scope and Objectives
3. Reference Documents
4. Requirements Overview
5. Existing System Context (if applicable)
6. Architecture Delta and Change Impact Analysis (mandatory for existing systems)
7. Architectural Drivers and Constraints
8. Proposed Architecture
9. System Context Diagram
10. Network Architecture
11. Security Architecture
12. Component Architecture
13. Data Architecture
14. Integration Architecture
15. Deployment Architecture
16. Technology Stack and Library Selection
17. Architecture Pattern Selection
18. NFR Realization and Traceability
19. Architecture Decisions
20. Trade-offs and Alternatives
21. Assumptions and Constraints
22. Operational Considerations
23. Risks and Open Questions
24. Requirements Traceability Matrix

For a new project, mark Section 6 as:

> Not Applicable - New Project. No existing architecture baseline is available.

Do not force sections that are genuinely irrelevant. Mark them as not applicable with a brief reason rather than introducing empty or speculative content.

## 7. Requirements Traceability

Maintain traceability between requirements and architecture.

For each functional requirement, identify the components, interfaces, or interactions responsible for realizing it.

For each NFR, identify the architectural mechanisms addressing it and the proposed validation approach.

Use the original requirement identifiers wherever available.

Do not invent requirement identifiers or modify source requirements.

The HLD must include a Requirements Traceability Matrix that makes gaps and unresolved coverage visible.

## 8. Reference File Usage

The skill's `references/` directory contains detailed guidance.

Read the relevant reference files before performing the associated activity:

| Activity | Reference |
|---|---|
| HLD structure and content | `references/hld-template.md` |
| New-system architecture discovery | `references/architecture-discovery.md` |
| Existing-system incremental design | `references/incremental-architecture.md` |
| Architecture pattern selection | `references/architecture-patterns.md` |
| Architecture diagrams | `references/architecture-diagrams.md` |
| Security architecture | `references/security-architecture.md` |
| Technology and library selection | `references/technology-selection.md` |
| Industry standards | `references/architecture-standards.md` |

Do not assume the contents of a reference file without reading it.

If a referenced file is missing:

- Do not claim to have followed its guidance.
- Continue using the instructions in this skill and established project context.
- Identify the missing reference when it materially affects the work.

## 9. Output Management

- Save the generated document as `HLD.md`.
- Save it in the project's documentation directory.
- If no documentation directory exists, propose an appropriate location or ask the user where the document should be created.
- Do not overwrite an existing approved HLD without explicit user approval.
- Preserve references to source requirements and contextual documents.
- Clearly identify unresolved architectural decisions.
- Do not modify source FRDs, NFRDs, or approved architecture documents as part of HLD generation unless explicitly requested.

## 10. Final Review

Before completing the HLD, verify:

- All relevant FRDs and NFRDs have been considered.
- Requirement identifiers and descriptions are preserved.
- Existing architecture and constraints have been respected.
- Incremental architecture analysis is complete for existing systems.
- Proposed changes are justified by requirements or constraints.
- Technology selections have documented rationale.
- Relevant architecture patterns have been evaluated.
- Required diagrams are present and consistent with the written design.
- Security and operating environment requirements are addressed.
- Every applicable NFR has explicit architectural coverage.
- Architecture decisions, assumptions, and trade-offs are documented.
- Requirements traceability is complete.
- Risks, dependencies, and unresolved questions are visible.
- No unsupported architectural, verification, or compliance claims exist.

After completing the HLD, present the user with:

1. A concise summary of the proposed architecture.
2. Significant architecture decisions and technology choices.
3. The approach to NFR realization.
4. Important assumptions, risks, and unresolved questions.
5. The HLD document location.
