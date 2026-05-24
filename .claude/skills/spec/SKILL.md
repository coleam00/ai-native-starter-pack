---
name: spec
description: Slice an epic or next-epic doc into PIV-sized tickets with a dependency graph. Turns a large strategic doc into the discrete units of work that the PIV loop consumes. Accepts a Confluence page id OR a local PRD/epic doc path; optionally cross-references a Jira epic key.
argument-hint: "[confluence-page-id OR local-doc-path] [optional-jira-epic-key]"
---

# /spec — Slice an Epic into PIV-Sized Tickets

The bridge between a strategic doc and the PIV loop. The epic doc is the destination; the PIV loop is the unit of motion; **tickets are the bridge.** `/spec` does the slicing.

## Recommended two-session PM flow

**Session 1 — Draft the PRD.**
The PM works with the agent to write or refine the PRD: goals, user stories, acceptance criteria, out-of-scope. At the end of the session, upload (or paste) the finished PRD into Confluence and note its page id. Keeping this separate from slicing avoids a bloated context window and lets the PRD stabilize before it is decomposed.

**Session 2 — Run `/spec`.**
With a primed session and the stable Confluence page id (or local file path) in hand, run `/spec` to decompose the PRD into tickets. The PRD is the source of truth; the agent does not re-draft it here.

> **Why two sessions?** PRD drafting and ticket decomposition are cognitively different tasks. Mixing them in one long session inflates the context window, often causes the agent to start slicing before requirements are settled, and makes it harder to review the PRD independently. The boundary also mirrors a real PM workflow.

## Input

- `$1` — **Confluence page id** (numeric, e.g. `123456`) **or** a **local file path** to the epic doc, next-epic doc (brownfield), or PRD (greenfield).
  - Detection: if `$1` is all digits → treat as a Confluence page id and fetch it via MCP.
  - Otherwise → treat as a local file path and read it directly.
- `$2` *(optional)* — a **Jira epic key** (e.g. `PROJ-42`) to cross-reference. If provided, fetch the epic and include its summary, description, and child issues as additional context alongside the PRD.
- A primed session — `/prime` should already have loaded the relevant codebase surface.

## Process

### Step 1 — Load the PRD (source of truth)

The PRD is the source of truth for this entire decomposition. Load it before doing anything else.

**If `$1` is numeric (Confluence page id):**

1. Call `mcp__atlassian__getAccessibleAtlassianResources` to obtain the `cloudId`.
2. Call `mcp__atlassian__getConfluencePage` with that `cloudId`, the page id, and `contentFormat: "markdown"`.
3. Use the returned page content as the PRD.

**If `$1` is a file path:**

Read the file directly. Use its contents as the PRD.

**If `$2` is provided (Jira epic key):**

1. Obtain the `cloudId` via `mcp__atlassian__getAccessibleAtlassianResources` if not already fetched.
2. Call `mcp__atlassian__getJiraIssue` with that `cloudId`, the epic key, and `responseContentFormat: "markdown"`.
3. Treat the returned issue (summary, description, child issues) as supplementary context. If the Jira epic and the PRD conflict, the PRD wins.

Read the loaded PRD fully: the goal, user stories, architectural impact, acceptance criteria, out-of-scope.

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
