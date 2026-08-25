# Feature Specification: Unify Local LLM Configuration

**Feature Branch**: `[005-unify-local-llm-config]`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "Correct an unspecified default from stage 2 by aligning direct-response generation with the existing local model backend used for policy answers, and consolidate both conversational paths to one shared local LLM configuration without changing stream contracts or existing test behavior."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consistent Local Response Generation (Priority: P1)

As a product owner, I want both conversational response paths to use the same local model configuration so the system runs fully local without external credentials.

**Why this priority**: This is a correctness fix to align runtime behavior with project scope and avoid provider mismatch failures.

**Independent Test**: Run existing direct-response and policy-question contract tests and verify both paths continue to produce expected stream sequences while requiring no external API key.

**Acceptance Scenarios**:

1. **Given** a direct conversational request, **When** the system generates a response, **Then** it uses the same local model configuration already used for policy-question responses.
2. **Given** a policy question, **When** the system generates a response, **Then** it continues to use the shared local model configuration and preserves current behavior.

---

### User Story 2 - Remove Unused External-Provider Defaults (Priority: P1)

As an operator, I want unused external-provider defaults removed from active runtime behavior so local deployment does not depend on unavailable credentials.

**Why this priority**: External-provider defaults create misleading configuration expectations and runtime risk in a local-only project.

**Independent Test**: Execute existing tests that cover direct and policy flows without setting external-provider credentials and verify unchanged pass results.

**Acceptance Scenarios**:

1. **Given** no external provider key is set, **When** direct responses are requested, **Then** the flow still works under local configuration.
2. **Given** shared local LLM environment values are set once, **When** either conversational path runs, **Then** both read from the same configuration source.

---

### User Story 3 - Preserve Existing Stream and Regression Contracts (Priority: P2)

As a QA engineer, I want this correction to avoid behavioral regressions so all prior stage contracts remain valid.

**Why this priority**: This is a configuration correction, not a feature expansion, and should not alter contract semantics.

**Independent Test**: Re-run full existing test suite and confirm all stage-1/2/3/4 tests pass unchanged.

**Acceptance Scenarios**:

1. **Given** successful direct or policy generation, **When** events are streamed, **Then** the existing success sequence remains intent, token(s), done.
2. **Given** generation failure in any covered path, **When** events are streamed, **Then** the existing failure contract remains intent, error, and no done event.

---

### Edge Cases

- What happens when local model environment variables are not explicitly set? The system applies one shared local default configuration for both conversational paths.
- How does the system handle mixed historical configuration values from earlier stages? Only the shared local configuration is honored by active runtime behavior.
- What happens when one path succeeds and the other fails under the same local backend? Existing path-specific error handling contracts remain unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use one shared local LLM configuration source for both direct-response generation and policy-question generation.
- **FR-002**: System MUST ensure direct-response generation uses the same local backend endpoint and model selection as policy-question generation.
- **FR-003**: System MUST stop requiring or depending on external-provider API key configuration for active conversational behavior.
- **FR-004**: System MUST remove or deactivate legacy external-provider default configuration values from active runtime behavior.
- **FR-005**: System MUST preserve existing direct-response success and failure stream event sequencing.
- **FR-006**: System MUST preserve existing policy-question success and failure stream event sequencing.
- **FR-007**: System MUST preserve all existing stage-1, stage-2, stage-3, and stage-4 test expectations with no acceptance-criteria expansion.
- **FR-008**: System MUST limit this change to configuration alignment and path wiring needed for that alignment.

### Key Entities *(include if feature involves data)*

- **SharedLLMConfiguration**: Runtime configuration containing a single local API endpoint and single model identifier used by both conversational generation paths.
- **GenerationPath**: A conversational response path (direct response or policy question) that consumes the shared configuration.
- **StreamContractOutcome**: Existing event-sequence outcomes for success and error cases that must remain unchanged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing direct-response and policy-question contract tests pass without external-provider credentials configured.
- **SC-002**: 100% of existing stage-1/2/3/4 tests pass unchanged after the correction.
- **SC-003**: 100% of conversational generation paths read endpoint/model from one shared local configuration source.
- **SC-004**: 0 newly introduced contract-test expectation changes are required to validate this correction.

## Assumptions

- The local model runtime remains available in environments where these tests are executed.
- Existing tests already provide sufficient coverage for direct-response and policy-question stream contracts.
- This correction does not require adding new user-facing event types or request fields.
- Prior stage behavior outside LLM provider configuration is intentionally preserved.
