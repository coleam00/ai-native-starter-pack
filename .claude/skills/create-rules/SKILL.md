---
name: create-rules
description: Derive the AI Layer's global rules (CLAUDE.md) and on-demand context modules FROM an existing codebase by analyzing its real structure, conventions, and patterns. Use on a brownfield codebase that has no CLAUDE.md yet (Brownfield Type A) to build the foundation of the AI Layer.
argument-hint: [optional focus areas]
---

# /create-rules — Derive the AI Layer from the codebase

Build the foundation of the AI Layer for a codebase that doesn't have one yet, by
**deriving the rules from what the code already does** — not from a template. This is
the Brownfield **Type A** move: you do it once, from the existing reality.

## Process

### 1. Analyze the real codebase
- `git ls-files`; read the entry points, configs, models, services, routes, and tests.
- Identify the *actual* conventions in use: naming, error handling, the auth pattern(s),
  datetime/timezone handling, how tests are written, logging, and the build/validation
  commands.
- Note inconsistencies or competing patterns (e.g. two auth systems) and decide which is
  the intended/forward one — capture that, mark the other as legacy.

### 2. Draft a LEAN CLAUDE.md (global rules)
Keep it short. Capture only the few hard rules + how to run/validate + pointers to
on-demand context. **Every rule must trace to something real in the code — cite it.**
Do not invent aspirational rules the code doesn't follow; capture the *intended*
convention and mark legacy exceptions explicitly.

### 3. Extract on-demand context modules (`.claude/context/`)
For the areas a task would need depth on (architecture map, the subtle/risky pattern,
auth, the IO/export pattern, testing), write a focused `.claude/context/<topic>.md` that
the agent loads only when relevant. Layered, not bloated (on-demand over nested rules).

### 4. Confirm with the human
Show the drafted rules + context, cite the code each came from, and let the human refine.
The rules are the team's implicit knowledge made explicit.

## Output
- `CLAUDE.md` at the repo root — lean global rules + the skill workflow + an on-demand
  context table.
- `.claude/context/<topic>.md` modules derived from the real code.

## Notes
- For a codebase that already has an AI Layer, you **evolve** it for the new epic
  (Type B: update CLAUDE.md, add epic-specific context) rather than deriving from scratch.
- Pair with `prime` (which can pull the ticket/spec) so the rules are anchored to the work.
