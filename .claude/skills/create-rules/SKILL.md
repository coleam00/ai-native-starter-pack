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
Keep it short. **Every rule must trace to something real in the code — cite it (file:line).**
Do not invent aspirational rules the code doesn't follow; capture the *intended* convention
and mark legacy exceptions explicitly.

#### CLAUDE.md structure — order sections by DESCENDING generality

The generated CLAUDE.md must follow this section order, from most general (applies to every
single task) at the top, to most specific at the bottom:

1. **Project one-liner** — what the codebase is and its primary tech stack (1–2 sentences).
2. **Naming conventions** — file names, module names, function/variable casing across the project.
3. **Core code patterns** — the universal patterns every file follows (error handling, logging,
   async conventions, etc.).
4. **Build & validation commands** — how to lint, type-check, test, and build. These are needed
   before every PR and must be accurate.
5. **On-demand context table** — a Markdown table listing `.claude/context/<topic>.md` modules
   and when to load each. Keep this section; it is mandatory.
6. **Hard rules** — GENERAL constraints that apply to every task type. Examples of correct scope:
   "always run the validation gate before opening a PR", "never commit secrets", "migrations
   must be reversible". **Do NOT put ultra-specific implementation one-offs here** (e.g.
   "render meeting datetimes through TimezoneAwareTime" or "auth routes use JWT not legacy
   session") — those belong in on-demand `.claude/context/<topic>.md` modules, not in global
   rules. Hard rules go near the **bottom** of CLAUDE.md, not the top.
7. **Miscellaneous / Gotchas** — a running-list catch-all section (see below).

#### Testing conventions — be honest

Document the testing conventions that *actually exist* in the repo. If the project has no tests,
say so. If it only has integration tests but no unit tests, say that. Do not claim a coverage
standard the codebase doesn't enforce.

#### Miscellaneous / Gotchas (mandatory final section)

Add this section at the very bottom of CLAUDE.md:

```markdown
## Miscellaneous / Gotchas

<!-- Running list — add entries as you discover things the agent repeatedly misunderstands -->
- <first entry derived from codebase analysis, if any>
```

This is a catch-all for anything that doesn't fit neatly into the sections above: surprising
import paths, an environment variable that must be set locally, a tool that breaks on Windows,
a pattern the auto-formatter changes back, etc. It grows over time as the team finds new edge
cases.

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
