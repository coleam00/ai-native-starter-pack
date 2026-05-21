---
name: new-worktrees
description: Sets up one or two git worktrees with dependency sync and health-check verification, running parallel setup with two agents when two branches are given. Use when starting parallel feature development in isolated worktrees.
argument-hint: [branch-1] [branch-2]
---

# New Worktree

Quick worktree setup with health check verification. Supports parallel creation with 2 agents.

## Parameters

- Branch 1: $1 (e.g., "feature/search")
- Branch 2 (optional): $2 (e.g., "feature/export")

## Logic

**If only $1 provided:**

- Create single worktree sequentially

**If both $1 and $2 provided:**

- Spawn 2 agents in parallel using Task tool
- Each agent sets up their own worktree independently
- Combine results from both agents
- Ensure you start the server on a different port to avoid conflicts: worktree 1 dedicated port 8124, worktree 2 dedicated port 8125

## Steps

### Single Worktree (when only $1 provided)

1. **Create worktree**

   ```bash
   git worktree add worktrees/$1 -b $1
   ```

2. **Navigate to worktree**

   ```bash
   cd worktrees/$1
   ```

3. **Sync dependencies**

   ```bash
   uv sync
   ```

4. **Start server in background**

   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8124 &
   SERVER_PID=$!
   ```

5. **Wait for server to be ready**

   ```bash
   sleep 3
   ```

6. **Test health endpoint — make sure you use the correct port**

   ```bash
   curl -f http://localhost:8124/health || echo "Health check failed"
   ```

7. **Kill server**

   ```bash
   kill $SERVER_PID
   ```

8. **Report ready**

### Parallel Worktrees (when both $1 and $2 provided)

1. **Spawn Agent 1 using Task tool**

   Prompt for Agent 1:

   ```
   Set up worktree for branch: $1

   Steps:
   1. Create worktree: git worktree add worktrees/$1 -b $1
   2. Navigate: cd worktrees/$1
   3. Sync dependencies: uv sync
   4. Start server: uv run uvicorn app.main:app --host 0.0.0.0 --port 8124 &
   5. Wait 3 seconds: sleep 3
   6. Test health: curl -f http://localhost:8124/health
   7. Kill server (find PID and kill it)

   Report:
   - Worktree path
   - Branch name
   - Health check result (PASS/FAIL)
   - Any errors encountered
   ```

2. **Spawn Agent 2 using Task tool (simultaneously with Agent 1)**

   Prompt for Agent 2:

   ```
   Set up worktree for branch: $2

   Steps:
   1. Create worktree: git worktree add worktrees/$2 -b $2
   2. Navigate: cd worktrees/$2
   3. Sync dependencies: uv sync
   4. Start server: uv run uvicorn app.main:app --host 0.0.0.0 --port 8125 &
      (Note: Use port 8125 to avoid conflict with Agent 1)
   5. Wait 3 seconds: sleep 3
   6. Test health: curl -f http://localhost:8125/health
   7. Kill server (find PID and kill it)

   Report:
   - Worktree path
   - Branch name
   - Health check result (PASS/FAIL)
   - Any errors encountered
   ```

3. **Wait for both agents to complete**

4. **Combine and report results from both agents**

## Report

### Single Worktree Output:

```
✓ Worktree initialized
  Path: worktrees/feature-search
  Branch: feature/search

✓ Dependencies synced (uv sync)
✓ Health check passed (http://localhost:8124/health)
✓ Server stopped

Ready for development!
```

### Parallel Worktrees Output:

```
✓ 2 worktrees initialized in parallel

Agent 1 (feature/search):
  Path: worktrees/feature-search
  Branch: feature/search
  ✓ Dependencies synced
  ✓ Health check passed (port 8124)
  ✓ Server stopped

Agent 2 (feature/export):
  Path: worktrees/feature-export
  Branch: feature/export
  ✓ Dependencies synced
  ✓ Health check passed (port 8125)
  ✓ Server stopped

Both worktrees ready for parallel development!
```

## Notes

- Exact ports and the server entry point may differ per project — check `pyproject.toml` and the
  project README for project-specific values.
