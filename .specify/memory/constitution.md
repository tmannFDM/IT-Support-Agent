<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Modified principles:
	- [PRINCIPLE_1_NAME] -> Vertical Slice First, End-to-End Always Works
	- [PRINCIPLE_2_NAME] -> RAG-Only, Policy-Grounded Answers
	- [PRINCIPLE_3_NAME] -> Secure Tooling via Schema-Validated FastMCP
	- [PRINCIPLE_4_NAME] -> Privacy by Default with Pre-LLM PII Redaction
	- [PRINCIPLE_5_NAME] -> Prompt Injection Resistance and Fail-Safe Outcomes
- Added sections:
	- Stateful Orchestration and Data Contracts
	- Delivery Workflow and Assurance Gates
- Removed sections:
	- None
- Follow-up TODOs:
	- None
-->

# IT Support System Constitution

## Core Principles

### I. Vertical Slice First, End-to-End Always Works
The MVP MUST prioritize one complete, operational ticket-resolution path across API, agent,
tools, and RAG before adding breadth. New capabilities MUST not be merged unless the
end-to-end path remains runnable and demonstrably functional. Teams MAY optimize or polish
only after the full slice is working.

Rationale: Partial layers create false progress and hide integration risk. A working slice
proves system viability and accelerates trustworthy iteration.

### II. RAG-Only, Policy-Grounded Answers
User-facing responses MUST be grounded in retrieved, approved policy or knowledge-base
sources. The system MUST NOT answer operational or policy questions from general model
priors alone. If retrieval yields insufficient evidence, the system MUST escalate or create a
ticket instead of guessing.

Rationale: IT support decisions require auditable, organization-specific truth and must resist
hallucinated guidance.

### III. Secure Tooling via Schema-Validated FastMCP
All tool execution MUST occur through FastMCP tools with explicit schema validation on
inputs and outputs. Direct shelling, dynamic command composition without validation, and
implicit parameter coercion are prohibited. Tool permissions MUST be least-privilege and
bounded by use-case.

Rationale: Strong contracts and constrained execution reduce injection, misuse, and accidental
unsafe actions.

### IV. Privacy by Default with Pre-LLM PII Redaction
Potentially sensitive user content MUST be redacted before any prompt is sent to the LLM.
Raw PII MUST NOT be included in model-bound payloads, logs, traces, or analytics artifacts.
Redaction behavior MUST be testable and versioned.

Rationale: Privacy controls are foundational in support workflows where user-submitted data
often contains personal or confidential details.

### V. Prompt Injection Resistance and Fail-Safe Outcomes
The system MUST treat all external content as untrusted, detect likely prompt-injection
patterns, and refuse unsafe instructions. When confidence, context, or policy grounding is
insufficient, the system MUST fail safe by escalating to a human or opening a ticket rather
than fabricating an answer.

Rationale: Safety in production support depends on robust refusal behavior and conservative
decision policies under uncertainty.

## Stateful Orchestration and Data Contracts

Conversation control MUST be stateful and implemented through LangGraph. Each state
transition MUST be explicit, observable, and recoverable, including handoff and escalation
paths.

Pydantic v2 schema-first contracts MUST be used for all cross-layer boundaries, including API
requests/responses, tool payloads, retrieval artifacts, agent state objects, and escalation
records. Raw string parsing as the primary boundary mechanism is prohibited.

## Delivery Workflow and Assurance Gates

Every change touching API, agent, tool, RAG, or orchestration MUST include an end-to-end
verification demonstrating the vertical slice still works.

Security and safety tests MUST cover at least: PII redaction before LLM calls, injection
attempt handling, schema validation failures, and fail-safe escalation paths.

GitHub Copilot usage MUST be documented honestly in PRs or equivalent records, including
where assistance was used, what was accepted or modified, and what was independently
verified by engineers.

## Governance

This constitution is authoritative for MVP engineering and supersedes conflicting local
conventions.

Amendment procedure:
1. Propose a change with rationale, impacted principles, and migration impact.
2. Obtain approval from at least one engineering owner and one security or compliance owner.
3. Update this constitution and related guidance in the same change set.

Versioning policy:
1. MAJOR for backward-incompatible governance changes or principle removals/redefinitions.
2. MINOR for new principles/sections or materially expanded obligations.
3. PATCH for wording clarifications or non-semantic edits.

Compliance review expectations:
1. Every PR review MUST include a constitution compliance check.
2. Violations MUST be tracked with explicit remediation or approved exception records.
3. Release readiness for MVP increments MUST include evidence of end-to-end slice health,
	 safety controls, and escalation correctness.

**Version**: 1.0.0 | **Ratified**: 2026-08-25 | **Last Amended**: 2026-08-25
