# Research: Frontend Polish Features

**Feature**: Feature 014 (Frontend Polish – Demo Features)

**Status**: COMPLETE — No research tasks required.

## Summary

Feature 014 is frontend-only polish for the existing Vite + React + TypeScript + Tailwind frontend (Feature 013). All technologies, clarifications, and design decisions are explicit and documented. No external research, integrations, or technology unknowns remain.

## Clarifications Completed

All 5 pre-planning clarification questions have been answered and integrated into spec.md:

1. **Persona UUID Storage** ✓
   - Answer: Store in `frontend/src/constants.ts` with three fixed personas
   - Resolution: constants.ts becomes source of truth for persona definitions; can be easily adjusted for testing or additional personas in future iterations

2. **Quick-Prompt Content** ✓
   - Answer: Five exact text prompts, each verified in this session for backend behavior
   - Resolution: `constants.ts` contains the exact 5 prompts; implementation uses this constant array for button labels and message sending

3. **Intent Badge Fallback Behavior** ✓
   - Answer: Hide badge completely when no intent event received (no "Unknown" placeholder)
   - Resolution: Badge rendering checks for non-null intent value; only renders if received

4. **Intent Badge Styling** ✓
   - Answer: Intent-specific TailwindCSS colors (blue/amber/gray/orange/red)
   - Resolution: Constants.ts includes color mapping; IntentBadge component applies mapped classes to badge element

5. **Default Persona Selection** ✓
   - Answer: Alex (first persona in array)
   - Resolution: App.tsx initializes selectedPersonaId from localStorage or defaults to first array element

## Technology Stack Validation

| Technology | Version | Status | Notes |
|-----------|---------|--------|-------|
| React | 18.3.1 | ✓ In Use | Already used for ChatView, MessageBubble, tool cards |
| TypeScript | 5.4.5 | ✓ In Use | Strict mode, existing codebase patterns apply |
| TailwindCSS | 3.4.3 | ✓ In Use | All new styling uses existing Tailwind classes (no new packages) |
| Vite | 5.2.10 | ✓ No Change | No build config changes needed |
| Browser localStorage | Standard | ✓ Available | No polyfill needed (ES2020 target) |
| crypto.randomUUID() | ES2020 | ✓ In Use | Already used in App.tsx for session generation |

## Design Patterns Applied

- **Component Composition**: New IntentBadge and QuickPromptRow follow existing component patterns (props-based, stateless rendering)
- **State Management**: React hooks (useState, useEffect) used consistently with Feature 013
- **localStorage Integration**: Simple key-value pattern for persona persistence (no complex serialization needed)
- **Event Handling**: Quick-prompt buttons reuse existing handleSendMessage logic; no new event flow required
- **Styling**: TailwindCSS utility classes; no new CSS files or stylesheets

## No External Dependencies Required

- No new npm packages needed (React, TypeScript, TailwindCSS, Vite all already installed)
- No backend API changes (existing `/chat/stream` endpoint is sufficient)
- No new streaming event types (intent event already exists and is parsed)
- No new database or storage beyond browser localStorage

## Known Constraints & Mitigations

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| localStorage may be disabled (incognito/private mode) | Persona selection won't persist | Default to first persona on each load; no error thrown |
| Intent event may arrive out of order | Badge may be associated with wrong message | Spec assumes in-order delivery per existing contract; edge case only in rare failure scenarios |
| Browser support for crypto.randomUUID() | Breaks on IE 11 or old browsers | Target is modern browsers (ES2020); Feature 013 already requires this |
| Persona UUID hardcoding | Not flexible for runtime persona lists | By design (per clarification Q1); future enhancement can load from backend if needed |

## Next Steps

- **Task Generation**: Run `/speckit.tasks` to generate implementation tasks from this plan
- **Implementation Phase**: Build 5 features in order: constants.ts → App.tsx persona state → New chat button → Persona dropdown → Intent badges → Quick-prompt row
- **Testing**: Manual end-to-end validation per quickstart.md scenarios
