---
name: spec
description: Slice an epic or next-epic doc into PIV-sized tickets with a dependency graph. Turns a large strategic doc into the discrete units of work that the PIV loop consumes. Accepts a Confluence page id OR a local PRD/epic doc path; optionally cross-references a Jira epic key. Writes the breakdown to docs/specs/ and, when the input was a Confluence page, publishes it back as a child page of the PRD. When a Jira epic key is passed, it also creates the tickets as issues under that epic, skipping any that already exist.
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

### Step 5 — Publish the breakdown back to Confluence

The breakdown is a PM artifact, so it belongs where the PM works, not only in the repo. If the PRD came from
Confluence (i.e. `$1` was a page id), publish the breakdown as a **child page of the PRD**:

1. Obtain the `cloudId` via `mcp__atlassian__getAccessibleAtlassianResources` if not already fetched.
2. Look for an existing page titled `Spec: <epic name> - Ticket Breakdown` in the same space
   (`mcp__atlassian__searchConfluenceUsingCql`, scoped to the space key).
3. If none exists, call `mcp__atlassian__createConfluencePage` with:
   - `cloudId`, the PRD's `spaceId`
   - `parentId` = the PRD page id (so it nests under the PRD)
   - `title` = `Spec: <epic name> - Ticket Breakdown`
   - `body` = the same markdown you wrote in Step 4
   If one already exists, call `mcp__atlassian__updateConfluencePage` instead, incrementing its version.
4. Report the resulting page id and URL back to the user.

If `$1` was a local file path rather than a Confluence page id, **skip this step** and say so. Do not invent a
space to publish into.

> Publishing is additive. The repo copy at `docs/specs/<epic-slug>.md` stays the source the PIV loop reads;
> the Confluence page is the shareable view for people who do not live in the repo.

### Step 6 — File the tickets in Jira

**If `$2` (a Jira epic key) was provided, this step is REQUIRED.** A breakdown nobody can assign is only half
the job. Create the tickets for real:

1. Get the `cloudId` via `mcp__atlassian__getAccessibleAtlassianResources` if not already fetched.
2. Read the epic with `mcp__atlassian__getJiraIssue` to learn its `project` key and confirm it exists.
3. **Check for existing children first.** Run `mcp__atlassian__searchJiraIssuesUsingJql` with
   `parent = <epic-key>`. For every ticket in your breakdown, compare against those summaries.
   - If a child already covers that slice, **skip it** and report it as already existing.
   - Only create the slices that are genuinely missing. Never create a near-duplicate of an existing child.
4. For each missing slice call `mcp__atlassian__createJiraIssue` with:
   - `cloudId`, `projectKey` (from step 2), `issueTypeName: "Story"` (or `"Task"` for pure chores)
   - `parent_epic`/`parent` = the epic key from `$2`
   - `summary` = the ticket title from your breakdown
   - `description` = scope, acceptance criteria, files likely touched, and the `Depends on:` line
5. Report a table of what you created (key + summary + URL) and what you skipped as already present.

If `$2` was **not** provided, skip this step and tell the user which epic key to pass to file the tickets.

> Order matters: write the breakdown document first (Step 4), publish to Confluence (Step 5), then create
> issues. If issue creation fails partway, the breakdown still exists and the run is re-runnable, because
> step 3 makes creation idempotent.

## Output

1. A ticket breakdown at `docs/specs/<epic-slug>.md` (always).
2. A Confluence child page under the PRD (when the input was a Confluence page id).
3. Real Jira issues under the epic, when an epic key was passed (Step 6). Existing children are never duplicated.

Each ticket then enters its own PIV loop starting at `/prime` → `/plan-feature`.

## Notes

- Issue management: the course standardizes on Jira (via Atlassian MCP); GitHub Issues, Asana, and Archon's task system are equivalent — the slicing logic is the same.
- Greenfield: the same slicing applies to MVP phases instead of epic tickets.
