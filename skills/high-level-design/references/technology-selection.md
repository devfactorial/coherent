# Technology Selection

## 1. Objective

Define a systematic approach for evaluating and selecting technologies during High-Level Design (HLD).

Technology selection should ensure that proposed technologies:

- Satisfy functional and non-functional requirements.
- Fit the application architecture and deployment model.
- Comply with organizational standards and constraints.
- Operate within the available runtime and infrastructure environment.
- Meet security, reliability, scalability, and maintainability expectations.
- Can be supported and operated over their expected lifecycle.

Technology selection should be evidence-based and proportionate to the significance of the decision.

Do not introduce a new technology merely because it is popular, modern, or technically interesting.

## 2. Technology Selection Principles

Apply the following principles:

- **Requirements first:** Derive technology needs from functional requirements, NFRs, and architectural constraints.
- **Reuse before introducing:** Prefer existing organizational platforms, approved technologies, and established capabilities.
- **Fit for purpose:** Select technology based on the problem it solves.
- **Operational compatibility:** Consider deployment, monitoring, support, and maintenance requirements.
- **Security by design:** Evaluate security capabilities and known risks.
- **Simplicity:** Avoid unnecessary technologies and architectural complexity.
- **Interoperability:** Consider integration with existing systems and standards.
- **Lifecycle awareness:** Evaluate maintenance, support, upgrade, and end-of-life implications.
- **Evidence-based decisions:** Use documentation, benchmarks, prototypes, or established organizational experience where appropriate.
- **Avoid premature optimization:** Do not select complex technologies to address hypothetical future requirements.

## 3. Identify Technology Constraints

Before evaluating technologies, identify the constraints that influence selection.

### 3.1 Mandatory Constraints

Examples include:

- Organization-approved technology stack.
- Existing application language or framework.
- Cloud provider or hosting restrictions.
- Supported operating systems and runtime versions.
- Database platform restrictions.
- Licensing and procurement requirements.
- Data residency and regulatory obligations.
- Security and compliance standards.
- Runtime permissions and execution restrictions.
- Existing integration protocols and interfaces.

Mandatory constraints must be treated as selection criteria, not optional preferences.

### 3.2 Preferences

Examples include:

- Preferred programming languages.
- Existing team expertise.
- Preferred frameworks and libraries.
- Preferred deployment platforms.
- Open-source versus commercial solutions.
- Existing organizational tooling.

Preferences should influence evaluation but should not override mandatory requirements.

### 3.3 Existing Technology Inventory

For existing systems, identify:

- Technologies currently in use.
- Supported versions.
- Existing platform capabilities.
- Organizationally approved alternatives.
- Dependencies that must be retained.
- Technologies approaching end of support.
- Existing operational and support capabilities.

Prefer extending existing technology capabilities when they adequately satisfy the requirements.

## 4. Technology Evaluation Criteria

Evaluate candidate technologies using criteria relevant to the decision.

| Criterion | Evaluation Considerations |
|---|---|
| Functional fit | Does the technology support required capabilities? |
| Performance | Can it meet latency, throughput, and processing requirements? |
| Scalability | Can it support expected growth and workload patterns? |
| Reliability | Does it support required availability and fault tolerance? |
| Security | Does it provide appropriate security controls and integration capabilities? |
| Compatibility | Does it integrate with existing systems and platforms? |
| Maintainability | Is it maintainable, upgradeable, and understandable? |
| Operational maturity | Can the organization deploy, monitor, troubleshoot, and support it? |
| Developer productivity | Does it support efficient development and testing? |
| Ecosystem | Are documentation, libraries, community, and vendor support adequate? |
| Licensing | Are licensing terms and usage restrictions acceptable? |
| Cost | What are the infrastructure, licensing, operational, and maintenance costs? |
| Portability | Does it create significant platform or vendor lock-in? |
| Lifecycle | Is it actively maintained with a credible support lifecycle? |

Not every criterion needs equal weighting. Prioritize criteria based on the system's architectural drivers.

## 5. Technology Selection by Category

### 5.1 Programming Languages and Runtime

Evaluate:

- Language capabilities and suitability.
- Runtime performance and resource consumption.
- Concurrency and asynchronous processing support.
- Type safety and error handling.
- Library and ecosystem maturity.
- Security and vulnerability management.
- Supported runtime versions.
- Developer expertise.
- Compatibility with the deployment environment.

Select a language and runtime that satisfy application requirements without introducing unnecessary operational or organizational complexity.

### 5.2 Application Frameworks

Evaluate:

- Architectural style compatibility.
- Dependency injection and modularity.
- API and integration support.
- Authentication and authorization capabilities.
- Validation and error handling.
- Observability support.
- Testing capabilities.
- Performance and scalability.
- Upgrade and maintenance practices.

Avoid introducing multiple frameworks that provide overlapping capabilities without a clear architectural justification.

### 5.3 Frontend Technologies

For frontend applications, evaluate:

- Target platform: web, mobile, desktop, or other.
- Framework and component ecosystem.
- State management.
- Routing and navigation.
- API integration.
- Authentication and session management.
- Accessibility.
- Browser and device compatibility.
- Performance and rendering strategy.
- Build and deployment tooling.

Select frontend technology based on user experience requirements and the target operating environment.

### 5.4 Database and Data Storage

Evaluate data technologies based on:

- Data structure and relationships.
- Transaction requirements.
- Consistency requirements.
- Query and access patterns.
- Data volume and growth.
- Read/write workload.
- Availability and recovery requirements.
- Backup and restore capabilities.
- Data security and encryption.
- Retention and archival.
- Operational complexity.

Consider the following technology categories:

| Category | Typical Use Cases |
|---|---|
| Relational database | Structured data, transactions, relational queries |
| Document database | Flexible document-oriented data |
| Key-value store | Low-latency key-based access and caching |
| Graph database | Relationship-centric queries and graph traversal |
| Object storage | Files, documents, media, and large unstructured objects |
| Search engine | Full-text search and indexing |
| Analytical warehouse | Reporting and analytical workloads |
| Time-series database | Time-oriented measurements and metrics |

Do not select a database based only on its category or popularity. Evaluate actual data and access requirements.

### 5.5 Messaging and Event Technologies

Evaluate:

- Messaging model: queue, pub/sub, or event streaming.
- Delivery guarantees.
- Ordering requirements.
- Throughput and latency.
- Retry and dead-letter handling.
- Idempotency support.
- Message durability.
- Consumer scaling.
- Schema and event versioning.
- Monitoring and operational complexity.

Select the simplest messaging capability that satisfies the required interaction and reliability model.

### 5.6 API and Integration Technologies

Evaluate:

- REST, GraphQL, gRPC, messaging, or other integration styles.
- Synchronous versus asynchronous communication.
- Contract and schema management.
- Authentication and authorization.
- Versioning and backward compatibility.
- Rate limiting and throttling.
- Error handling and retry behavior.
- Integration ecosystem compatibility.

Prefer established organizational interface standards where available.

### 5.7 Cloud and Infrastructure Services

Evaluate infrastructure services based on:

- Hosting and deployment requirements.
- Compute and storage needs.
- Availability and disaster recovery.
- Network architecture.
- Security and identity integration.
- Scaling and elasticity.
- Monitoring and operational capabilities.
- Regional availability.
- Pricing and consumption model.
- Portability and vendor dependency.

Consider whether a managed service, self-managed platform, containerized deployment, or serverless model is appropriate.

### 5.8 Containers and Orchestration

Where containerization is relevant, evaluate:

- Container runtime compatibility.
- Orchestration requirements.
- Deployment complexity.
- Scaling and scheduling.
- Service discovery.
- Networking and ingress.
- Secrets management.
- Workload isolation.
- Observability.
- Operational expertise.

Do not introduce an orchestration platform when the application can be deployed effectively using a simpler managed runtime.

### 5.9 CI/CD and Developer Tooling

Evaluate:

- Source control integration.
- Build and packaging.
- Automated testing.
- Security and dependency scanning.
- Artifact management.
- Deployment automation.
- Environment promotion.
- Approval gates.
- Rollback and recovery.
- Auditability.

Ensure tooling supports the organization's development and release governance requirements.

### 5.10 AI and Agentic Technologies

For AI-enabled systems, evaluate relevant technologies across the following categories:

**Model providers and serving**
- Hosted model APIs versus self-hosted models.
- Model capability and suitability.
- Latency and throughput.
- Context window and output limits.
- Availability and reliability.
- Data handling and retention policies.
- Model versioning and lifecycle.
- Cost and rate limits.

**Agent frameworks and runtimes**
- Tool invocation and execution model.
- Workflow and state management.
- Human approval support.
- Retry and failure handling.
- Runtime isolation.
- Observability and tracing.
- Identity and authorization integration.

**Retrieval and knowledge infrastructure**
- Embedding models.
- Vector databases.
- Search engines.
- Hybrid retrieval.
- Reranking.
- Document ingestion and indexing.
- Data access control and filtering.

**AI integration and governance**
- Model Context Protocol (MCP), where applicable.
- Tool and resource authorization.
- Agent identity.
- Prompt and model version governance.
- Evaluation and testing infrastructure.
- Auditability.
- Sensitive data protection.

Do not introduce an agent framework, vector database, or additional AI infrastructure unless the requirements justify it.

## 6. Candidate Evaluation and Comparison

For significant technology decisions, identify reasonable candidates and evaluate them against the relevant criteria.

Use a comparison matrix where it helps make trade-offs explicit.

Example:

| Criterion | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Functional fit | High | High | Medium |
| Performance | High | Medium | High |
| Operational maturity | High | High | Low |
| Team expertise | High | Medium | Low |
| Cost | Medium | Low | High |
| Organizational compatibility | High | Medium | Low |

Use qualitative ratings such as High, Medium, and Low only when supported by available evidence.

For important decisions, document the evidence behind ratings. Avoid false precision and arbitrary numerical scoring.

### 6.1 Evaluation Evidence

Depending on the decision, evidence may include:

- Official product documentation.
- Vendor support and lifecycle information.
- Organizational technology standards.
- Existing implementation experience.
- Benchmark results.
- Proof-of-concept results.
- Security assessments.
- Licensing documentation.
- Cost estimates.

Clearly distinguish verified information from assumptions and estimates.

## 7. Build, Buy, or Reuse Evaluation

For significant capabilities, evaluate whether to:

- Build a custom solution.
- Adopt an existing open-source technology.
- Purchase a commercial product.
- Use a managed cloud service.
- Reuse an existing organizational platform.

Consider:

- Business differentiation.
- Functional fit.
- Customization requirements.
- Total cost of ownership.
- Operational responsibility.
- Security and compliance.
- Vendor dependency.
- Support and lifecycle.
- Integration complexity.

Prefer reuse or managed capabilities when they satisfy requirements and reduce unnecessary maintenance burden.

## 8. Licensing and Lifecycle Assessment

Evaluate licensing and lifecycle implications before recommending a technology.

Consider:

- License type and obligations.
- Commercial usage restrictions.
- Redistribution requirements.
- Source availability.
- Dependency licensing.
- Vendor support model.
- Maintenance activity.
- Release frequency.
- Security patch availability.
- End-of-life policy.
- Migration and replacement complexity.

Do not assume that an open-source technology is automatically free of licensing, support, or operational obligations.

Flag licensing or lifecycle concerns that require legal, procurement, or organizational review.

## 9. Technology Selection for Existing Systems

For incremental changes, evaluate technologies in the context of the existing architecture.

Apply these principles:

- Preserve existing technologies when they remain fit for purpose.
- Prefer extending existing frameworks and platform capabilities.
- Avoid introducing a new language, framework, database, or infrastructure platform without justification.
- Evaluate compatibility with existing components and interfaces.
- Consider migration and coexistence requirements.
- Assess operational impact and team supportability.
- Identify technology upgrades that are necessary to meet requirements or address risks.
- Separate technology changes required by the feature from unrelated modernization opportunities.

A technology replacement should have an explicit rationale and impact assessment.

## 10. Technology Decisions and Documentation

Document significant technology selections in the HLD.

For each decision, record:

| Field | Description |
|---|---|
| Decision ID | Unique architecture decision identifier |
| Technology Area | Category of technology being selected |
| Requirement / Driver | Requirement or constraint motivating the decision |
| Selected Technology | Chosen technology, product, framework, or service |
| Version / Offering | Relevant version, edition, or service offering, if known |
| Alternatives | Other candidates considered |
| Rationale | Why the selected option is appropriate |
| Trade-offs | Limitations and compromises |
| Risks | Known risks and dependencies |
| Evidence | Documentation, benchmark, POC, or other supporting evidence |
| Status | Proposed, Accepted, Rejected, or Deferred |

Distinguish between:

- **Mandatory selection:** Required by an organizational or technical constraint.
- **Recommended selection:** Preferred based on the evaluation.
- **Existing selection:** Retained from the current architecture.
- **Deferred selection:** Requires further investigation or approval.

Do not present a proposed technology as an approved organizational standard.

## 11. Technology Selection Validation

Before finalizing technology recommendations, verify:

- Each major technology choice supports identifiable requirements or architectural drivers.
- Mandatory constraints have been satisfied.
- Existing technology capabilities have been considered.
- Relevant alternatives have been evaluated for significant decisions.
- Security and operational requirements have been considered.
- Licensing and lifecycle implications are understood or flagged.
- Technology versions and service offerings are supported, where known.
- Interoperability and integration requirements are satisfied.
- Technology choices do not introduce unjustified complexity.
- Unresolved selections and assumptions are documented.

## 12. Technology Selection Principles for HLD

- Select technology only at the level of detail appropriate for HLD.
- Avoid prematurely specifying implementation-level libraries and minor dependencies.
- Use established organizational standards unless a justified exception is required.
- Prefer fewer technologies with clear responsibilities.
- Consider total cost of ownership rather than acquisition cost alone.
- Do not claim performance or scalability without supporting evidence.
- Do not assume a technology's features are available in every version, edition, or deployment model.
- Record uncertainty rather than inventing technical facts.
- Ensure technology decisions are consistent with the proposed architecture, security design, and deployment model.
- Revisit technology choices when requirements or constraints materially change.