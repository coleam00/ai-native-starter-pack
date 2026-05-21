---
name: merge-worktrees
description: Merges two feature branches from worktrees through a safe integration branch with full testing and validation at each step. Use when parallel worktree development is done and the features need to be integrated.
argument-hint: [branch-1] [branch-2]
---

# Merge Worktrees

Merge two feature branches from worktrees with full testing and validation.

## Parameters

- Branch 1: $1 (e.g., "test1")
- Branch 2: $2 (e.g., "test2")

## Steps

### 1. Verify Preconditions

```bash
# Check we're in the repository root
pwd

# Store current branch
CURRENT_BRANCH=$(git branch --show-current)

# Verify both branches exist
git rev-parse --verify $1
git rev-parse --verify $2

# Ensure we're not in a worktree subdirectory
[[ $(pwd) =~ /worktrees/ ]] && echo "ERROR: Must run from main worktree" && exit 1
```

### 2. Create Integration Branch

```bash
git checkout -b integration-$1-$2
```

### 3. Merge First Feature

```bash
git merge $1 --no-ff -m "merge: integrate $1"
```

**If conflicts occur:**

- Stop execution
- Report conflict details
- Provide instructions:
  ```
  Conflicts detected in merge of $1
  Please resolve manually:
  1. Fix conflicts in the listed files
  2. git add .
  3. git commit
  4. Re-run this skill
  ```

### 4. Test First Merge

```bash
uv run pytest -v
```

**If tests fail:**

- Report which tests failed
- Abort merge process
- Provide rollback instructions:
  ```bash
  git checkout $CURRENT_BRANCH
  git branch -D integration-$1-$2
  ```

### 5. Merge Second Feature

```bash
git merge $2 --no-ff -m "merge: integrate $2"
```

**If conflicts occur:**

- Same conflict handling as step 3

### 6. Run Full Validation Suite

Run all checks in parallel if possible:

```bash
# Run tests
uv run pytest -v

# Run type checkers
uv run mypy app/
uv run pyright app/
```

**If any validation fails:**

- Report which check failed with details
- Abort process
- Provide rollback instructions

### 7. Merge to Original Branch

```bash
git checkout $CURRENT_BRANCH
git merge integration-$1-$2 --no-ff -m "merge: integrate features from $1 and $2"
```

### 8. Cleanup Integration Branch

```bash
git branch -d integration-$1-$2
```

### 9. Ask About Worktree Cleanup

Use AskUserQuestion tool:

```
Question: "Remove worktrees and delete feature branches?"
Options:
  - "Yes, clean up everything" → Remove worktrees and branches
  - "No, keep them for now" → Skip cleanup
```

**If user chooses yes:**

```bash
# Remove worktrees
git worktree remove worktrees/$1
git worktree remove worktrees/$2

# Delete branches
git branch -d $1 $2
```

## Report

### Success Output

```
✓ Integration branch created: integration-{branch1}-{branch2}
✓ Merged {branch1} → integration branch
✓ Tests passed after first merge (X tests, Xs)
✓ Merged {branch2} → integration branch
✓ All validation passed:
  - pytest: X tests passed in Xs
  - mypy: no errors
  - pyright: no errors
✓ Merged to {original_branch}
✓ Cleaned up integration branch

[If worktrees kept]
Worktrees still active:
  - worktrees/{branch1} (branch: {branch1})
  - worktrees/{branch2} (branch: {branch2})

To clean up manually:
  git worktree remove worktrees/{branch1} worktrees/{branch2}
  git branch -d {branch1} {branch2}

[If worktrees removed]
✓ Removed worktrees and deleted branches

Both features successfully integrated into {original_branch}!
```

### Failure Output

```
✗ Merge failed at step: {step_name}

Error: {error_details}

Current state:
  - On branch: integration-{branch1}-{branch2}
  - Original branch: {original_branch}

To rollback:
  git checkout {original_branch}
  git branch -D integration-{branch1}-{branch2}

To continue after fixing:
  1. Resolve the issue
  2. Re-run the merge-worktrees skill with {branch1} {branch2}
```

## Error Handling

- **Conflict during merge**: Stop, provide resolution instructions, allow retry
- **Missing branch**: Verify branches exist before starting
- **Wrong directory**: Check not running from inside worktrees/

## Notes

- Uses `--no-ff` (no fast-forward) to preserve feature branch history
- Creates temporary integration branch for safe testing
- Original branch only updated after all validations pass
- Worktrees can be kept for continued development
- All validation must pass before merge is finalized
