---
name: code-review-fix
description: Fixes bugs surfaced by a manual or AI code review, one at a time, with tests, then runs full validation. Use after a code review has produced a list of issues or a review file.
argument-hint: [code-review-file-or-issues] [scope]
---

# Code Review Fix

I ran/performed a code review and found these issues:

Code-review (file or description of issues): $1

Please fix these issues one by one. If the Code-review is a file, read the entire file first to understand all of the issue(s) presented there.

Scope: $2

## Process

For each fix:
1. Explain what was wrong
2. Show the fix
3. Create and run relevant tests to verify

## Output

After all fixes, run the `validate` skill to finalize your fixes.
