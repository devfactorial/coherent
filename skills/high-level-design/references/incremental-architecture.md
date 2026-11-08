# Incremental Architecture Analysis

## 1. Objective

This reference describes the analytical approach for evaluating architectural changes to an existing software system.

The objective is to determine how new or modified requirements affect the existing architecture and identify the minimum necessary changes.

The analysis must distinguish between:
- Existing capabilities that can be reused.
- Existing capabilities that need modification or extension.
- New capabilities that must be introduced.
- Existing capabilities that can be retired.

The existing architecture should remain the default design unless requirements or technical constraints justify a change.

## 2. Establish the Architecture Baseline

Build an understanding of the existing architecture using the available system documentation and technical context.

Focus on the architectural elements relevant to the proposed change.

| Architecture area | Information to establish |
|---|---|
| Application | Applications, services, components, responsibilities, and dependencies |
| Integration | APIs, events, messaging, external systems, and communication protocols |
| Data | Databases, data ownership, schemas, data flows, and persistence mechanisms |
| Infrastructure | Hosting, runtime, deployment topology, compute, and storage |
| Network | Network zones, connectivity, ingress, egress, and trust boundaries |
| Security | Identities, authentication, authorization, permissions, and secrets |
| Operations | Logging, monitoring, tracing, scaling, backup, and recovery |

Do not reconstruct the entire architecture if only a limited part is relevant to the proposed change.

If documentation is incomplete, distinguish documented facts from assumptions and request clarification when necessary.

## 3. Determine the Architecture Delta

Compare the proposed requirements with the existing architecture.

Classify affected components:

| Classification | Interpretation |
|---|---|
| REUSE | Existing capability satisfies the requirement without changes |
| MODIFY | Existing behavior or responsibility must change |
| EXTEND | Additional capability is added to an existing component |
| NEW | A new component or architectural capability is required |
| RETIRE | An existing component or capability is removed |

For each affected component, determine:

- Which requirement introduces the change?
- What existing capability is affected?
- What change is necessary?
- Which other components depend on it?
- Can the change be implemented without introducing a new architectural element?

Do not introduce new services, databases, frameworks, infrastructure, or platforms merely to accommodate a design preference.

## 4. Analyze Cross-Architecture Impact

Evaluate the consequences of the identified changes across related architectural elements.

### 4.1 Component and Dependency Impact

Determine whether:
- Component responsibilities change.
- Existing dependencies are affected.
- New dependencies are introduced.
- Component boundaries or ownership need to change.
- Changes create additional coupling.

### 4.2 API and Integration Impact

Determine whether:
- Existing API contracts change.
- New interfaces or integrations are required.
- Existing consumers are affected.
- Communication protocols or interaction patterns change.
- Event schemas or message contracts change.

Evaluate backward compatibility and the impact on upstream and downstream consumers.

### 4.3 Data Impact

Determine whether:
- Existing schemas or data models change.
- New entities or attributes are required.
- Data ownership changes.
- New persistence capabilities are necessary.
- Existing data needs migration, transformation, or backfill.
- Data consistency or synchronization mechanisms are affected.

### 4.4 Security and Network Impact

Determine whether:
- New identities, permissions, or authorization policies are needed.
- Existing trust boundaries change.
- New service-to-service communication is introduced.
- Network connectivity or firewall rules change.
- New ingress or egress paths are required.
- Data protection requirements change.

### 4.5 Infrastructure and Deployment Impact

Determine whether:
- Existing infrastructure can support the change.
- New compute, storage, or network resources are required.
- Runtime or deployment configurations change.
- Scaling and capacity requirements change.
- Deployment sequencing or rollback mechanisms are affected.

### 4.6 Non-Functional Impact

Evaluate whether the change affects existing:
- Performance and latency.
- Availability and resilience.
- Scalability.
- Security and compliance.
- Maintainability.
- Observability.
- Recoverability.

Identify potential regressions against existing NFR targets, not just the NFRs introduced by the new requirements.

## 5. Evaluate Change and Migration Strategies

Where existing interfaces, data, or components are affected, evaluate suitable transition strategies.

Examples include:

- Backward-compatible API evolution.
- Versioned API contracts.
- Expand-and-contract database migrations.
- Parallel execution of old and new implementations.
- Gradual traffic migration.
- Feature flags.
- Phased component retirement.
- Data migration and backfill.

Select a strategy based on the actual change and its operational constraints.

For breaking changes, identify affected consumers, migration sequencing, deployment dependencies, and rollback considerations.

Do not prescribe migration mechanisms when the change does not require them.

## 6. Evaluate New Architectural Elements

When a new component, service, database, platform, framework, or infrastructure resource is proposed, evaluate:

1. Why existing capabilities are insufficient.
2. Whether the requirement can be satisfied by modifying or extending an existing component.
3. Additional operational and maintenance responsibilities.
4. New integration and dependency costs.
5. Security and infrastructure implications.
6. Impact on existing NFRs.

A new architectural element should be introduced only when its benefits justify the additional complexity.

## 7. Architecture Delta Representation

Represent the analysis in a change matrix.

| Element | Existing State | Proposed State | Classification | Reason |
|---|---|---|---|---|
| Order Service | Processes orders | Adds order validation | MODIFY | New validation requirement |
| Customer Service | Manages customer data | No change | REUSE | Existing capability sufficient |
| Notification Service | Not present | New notification capability | NEW | New notification requirement |

The entries are illustrative.

For complex changes, include dependencies and affected interfaces in the analysis rather than limiting the matrix to individual components.

Architecture diagrams should distinguish unchanged, modified, extended, new, and retired elements.

## 8. Analytical Principles

Apply these principles throughout the analysis:

- **Preserve before replacing:** Retain existing architectural capabilities unless there is a justified reason to change them.
- **Extend before introducing:** Prefer extending an existing component over creating a new one when responsibilities and boundaries remain coherent.
- **Minimize architectural disruption:** Limit changes to the components and interfaces necessary to satisfy requirements.
- **Evaluate indirect impact:** Consider dependencies and downstream consequences, not just the component directly implementing a requirement.
- **Protect existing consumers:** Evaluate compatibility whenever interfaces, events, or data contracts change.
- **Preserve existing NFRs:** Ensure that new functionality does not unintentionally degrade established architectural qualities.
- **Justify new complexity:** Every additional architectural element must have a requirement or technical justification.
- **Make uncertainty explicit:** Distinguish verified architecture information from assumptions and unresolved questions.