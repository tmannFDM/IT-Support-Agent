# Phase 0 Research: RAG Policy Answers Slice

## Decision 1: Policy source corpus and ingestion boundary
- Decision: Ingest exactly the five existing markdown files in `src/rag/policy_docs/` as-is.
- Rationale: Matches scope and avoids accidental content drift from generation or rewriting.
- Alternatives considered:
  - Regenerating policy docs from templates: rejected because source documents are authoritative.
  - Broad filesystem ingestion: rejected due to scope and predictability concerns.

## Decision 2: Chunking strategy
- Decision: Chunk conservatively by section/paragraph boundaries rather than fixed-size splits.
- Rationale: Policy docs are short; coherent sections improve grounding fidelity and reduce fragmentary retrieval.
- Alternatives considered:
  - Aggressive token-count chunking: higher recall but poorer semantic coherence for small docs.

## Decision 3: Metadata mapping
- Decision: For every chunk, store `policy_category` from file header field and `source_document` from filename.
- Rationale: Required for traceability, filtering, and user-visible provenance.
- Alternatives considered:
  - Category inference from filename/body: rejected because explicit header field is already authoritative.

## Decision 4: Embedding model choice
- Decision: Use sentence-transformers `all-MiniLM-L6-v2` for both ingestion and query embeddings.
- Rationale: Meets no-API-key local requirement and keeps embedding space consistent between indexing and retrieval.
- Alternatives considered:
  - Mixed embedding models for indexing/query: rejected due to retrieval quality mismatch risk.
  - Hosted embedding API: rejected by local/offline preference.

## Decision 5: Retrieval policy and threshold
- Decision: Retrieve top-3 chunks and require minimum relevance score 0.35 for usable context.
- Rationale: 0.35 balances answer coverage with hallucination risk for small curated corpus.
- Alternatives considered:
  - No threshold: rejected because low-signal context can induce unsupported answers.
  - Higher threshold (0.50+): rejected as too restrictive for cross-category questions.

## Decision 6: No-context behavior
- Decision: Skip LLM call when no retrieved chunk meets threshold and return exact fixed response `I don't have information on that policy.`
- Rationale: Enforces fail-safe behavior and deterministic testability.
- Alternatives considered:
  - Let LLM answer from priors when retrieval weak: rejected by constitution and feature constraints.

## Decision 7: Policy answer generation path
- Decision: Add `answer_policy_question` graph node that retrieves context then calls local Ollama `llama3.2:3b` with a grounded-only prompt when threshold pass is satisfied.
- Rationale: Keeps policy logic explicit in orchestration and preserves existing route contract.
- Alternatives considered:
  - Inline generation in route layer: rejected for graph-state clarity and maintainability.

## Decision 8: Provenance exposure
- Decision: Append `source_document` filename citations in final answer token text.
- Rationale: Improves transparency and supports acceptance validation.
- Alternatives considered:
  - Hidden provenance in logs only: rejected because user-visible grounding confirmation is required.

## Decision 9: Error behavior
- Decision: On LLM generation failure after retrieval, emit `intent` then `error` and terminate without `done`.
- Rationale: Aligns with established direct-response failure contract and avoids ambiguous stream state.
- Alternatives considered:
  - Fallback to no-information on generation failure: rejected to preserve error-contract consistency.
