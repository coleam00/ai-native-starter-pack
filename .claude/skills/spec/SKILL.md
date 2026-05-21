---
name: spec
description: Slice an epic or next-epic doc into PIV-sized tickets with a dependency graph. Turns a large strategic doc into the discrete units of work that the PIV loop consumes.
argument-hint: "[path to the epic / next-epic doc / PRD]"
---

# /spec — Slice an Epic into PIV-Sized Tickets

The bridge between a strategic doc and the PIV loop. The epic doc is the destination; the PIV loop is the unit of motion; **tickets are the bridge.** `/spec` does the slicing.

## Input

- `$1` — path to the epic doc, next-epic doc (brownfield), or PRD (greenfield).
- A primed session — `/prime` should already have loaded the relevant codebase surface.

## Process

### Step 1 — Read the destination

Read the epic / next-epic doc fully: the goal, user stories, architectural impact, acceptance criteria, out-of-scope.

### Step 2 — Decompose into PIV-sized slices

Break the epic into tickets. A well-sized ticket:

- Maps to **one structured plan** of 500-700 lines.
- Is one coherent unit — a vertical slice of behavior, not a horizontal layer.
- Has clear acceptance criteria of its own.
- Is small enough to execute in a single PIV loop (roughly 20-60 minutes of execute time).

If a slice would produce a plan longer than ~700 lines, split it further.

### Step 3 — Slice for parallelizability

Map dependencies between tickets. **Independent tickets** — ones that don't touch the same files or rely on each other's output — can run in **parallel worktrees** (see `/new-worktrees`). Mark which tickets are independent and which form a dependency chain. Slicing along vertical-slice-architecture seams maximizes independence.

### Step 4 — Write the ticket breakdown

Write to `docs/specs/<epic-slug>.md`:

```
# Spec: <epic name>

## Epic summary — goal in 2-3 lines
## Tickets
   ### TICKET-1 — <title>
   - Scope / acceptance criteria
   - Files touched (estimate)
   - Depends on: <none / TICKET-x>
   ### TICKET-2 — ...
## Dependency graph
   <text or mermaid graph showing the order + parallel groups>
## Suggested execution order
   Wave 1 (parallel): TICKET-1, TICKET-3
   Wave 2: TICKET-2 (after TICKET-1)
```

## Output

A ticket breakdown at `docs/specs/<epic-slug>.md`. Each ticket then enters its own PIV loop starting at `/prime` → `/plan-feature`.

## Notes

- Issue management: the course standardizes on Jira (via Atlassian MCP); GitHub Issues, Asana, and Archon's task system are equivalent — the slicing logic is the same.
- Greenfield: the same slicing applies to MVP phases instead of epic tickets.
