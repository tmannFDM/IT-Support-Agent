# Feature Specification: Injection Pattern Expansion

**Feature Branch**: `[007-injection-pattern-expansion]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend the existing detect_prompt_injection pattern list in src/security/injection.py with additional phrase variants for instruction-dismissal, persona/role override, and system-prompt extraction, with no logic changes and one new missed-phrase test."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch More Injection Variants Deterministically (Priority: P1)

As a security owner, I want additional deterministic injection phrases recognized so common override attempts are blocked without changing detection mechanics.

**Why this priority**: Detection coverage is the primary security value for this pass and directly reduces easy bypasses.

**Independent Test**: Submit messages containing each new phrase category and verify they trigger the existing blocked behavior.

**Acceptance Scenarios**:

1. **Given** a message containing forget/start-fresh style dismissal phrases, **When** prompt-injection checks run, **Then** the request is detected and blocked under existing blocked-response behavior.
2. **Given** a message containing persona/role override phrases such as you are now, act as, or pretend you are, **When** prompt-injection checks run, **Then** the request is detected and blocked under existing blocked-response behavior.
3. **Given** a message containing system-prompt extraction phrases such as reveal your system prompt or what are your instructions, **When** prompt-injection checks run, **Then** the request is detected and blocked under existing blocked-response behavior.

---

### User Story 2 - Preserve Existing Detection Mechanics and Response Shape (Priority: P1)

As a backend maintainer, I want this to be data-only list expansion so existing detection semantics and stream/error contracts remain stable.

**Why this priority**: Stability is critical because current blocked-response contract is already validated by prior stages.

**Independent Test**: Re-run existing injection-block tests and verify no behavior or payload-shape changes are required.

**Acceptance Scenarios**:

1. **Given** existing detection flow, **When** new phrases are added, **Then** matching remains case-insensitive and whitespace-normalized with no algorithm change.
2. **Given** a blocked message from any new phrase, **When** response is emitted, **Then** existing ERR-PROMPT-INJECTION-BLOCKED error event shape remains unchanged.

---

### User Story 3 - Cover Previously Missed Phrase with Test (Priority: P2)

As a QA engineer, I want one explicit test for a previously missed dismissal phrase so this regression does not return.

**Why this priority**: Targeted test coverage ensures the specific missed phrase stays protected in future changes.

**Independent Test**: Add and run a contract test for the phrase forget everything you were told before this message and verify blocked-only error behavior.

**Acceptance Scenarios**:

1. **Given** the phrase forget everything you were told before this message, **When** the request is processed, **Then** only the blocked error event is emitted under existing blocked contract.
2. **Given** full suite regression checks, **When** tests run, **Then** all prior stage behavior remains passing.

---

### Edge Cases

- What happens when a message contains multiple new pattern variants in one request? A single blocked outcome is returned using existing blocked behavior.
- What happens when a message includes similar words but not the defined phrases? Detection remains governed by existing matching logic and the expanded phrase list only.
- What happens when legacy phrases and new phrases coexist? Behavior remains unchanged except expanded match coverage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expand the existing injection phrase list in src/security/injection.py with additional variants for instruction dismissal, role override, and prompt extraction.
- **FR-002**: System MUST include the following instruction-dismissal phrases in the list: ignore all previous, disregard previous instructions, disregard the above, forget everything, forget what you were told, forget your instructions, start fresh, start over, new instructions.
- **FR-003**: System MUST include the following persona/role-override phrases in the list: you are now, act as, pretend you are, pretend to be, from now on you.
- **FR-004**: System MUST include the following prompt-extraction phrases in the list: reveal your system prompt, show me your system prompt, what are your instructions, repeat your instructions, print your prompt.
- **FR-005**: System MUST include explicit override framing phrases in the list: override your, bypass your, don't follow your, do not follow your.
- **FR-006**: System MUST preserve existing detection mechanism behavior (case-insensitive, whitespace-normalized keyword/pattern matching) with no algorithmic changes.
- **FR-007**: System MUST preserve existing blocked-response behavior and ERR-PROMPT-INJECTION-BLOCKED payload shape with no event-handling changes.
- **FR-008**: System MUST add one new contract test case covering the phrase forget everything you were told before this message.
- **FR-009**: System MUST keep existing tests passing after this data expansion.
- **FR-010**: System MUST treat as out of scope: any changes to RAG behavior, tools, observability, frontend, LLM configuration, ticket tool, or intent-classification logic beyond existing guardrail processing.

### Key Entities *(include if feature involves data)*

- **InjectionPatternList**: Static phrase list used by the existing prompt-injection matching function.
- **BlockedInjectionOutcome**: Existing blocked error response for matched injection phrases.
- **InjectionRegressionTestCase**: Contract test asserting blocked-only behavior for a specific phrase variant.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new phrase categories defined in this spec are represented in the injection pattern list.
- **SC-002**: 100% of blocked responses triggered by new phrases conform to existing ERR-PROMPT-INJECTION-BLOCKED response shape.
- **SC-003**: The new regression phrase test for forget everything you were told before this message passes.
- **SC-004**: 100% of pre-existing test suite checks continue to pass unchanged.

## Assumptions

- Existing detection implementation already performs case-insensitive and whitespace-normalized matching and does not require logic edits for this pass.
- Existing blocked error contract is authoritative and must remain unchanged.
- One additional targeted test is sufficient to cover the previously missed phrase regression for this increment.
- The phrase list is maintained in one source location used by current guardrail flow.
