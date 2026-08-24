# Hooks — the deterministic layer of the AI Layer

Hooks are the fifth primitive. Rules, subagents, tools, and skills are all things the agent *reaches for*.
A hook is the one the agent never chooses: it fires automatically on a lifecycle event.

> **A rule asks the agent to behave. A hook guarantees it.**
>
> Reach for a rule when "usually" is fine. Reach for a hook when it **must** happen every single time.

## What ships here

| File | Event | What it does | Can it block? |
|---|---|---|---|
| `pre_tool_use.py` | **PreToolUse** | Blocks reading/writing/searching a real env file (committed `.env.example` templates are allowed) and blocks `rm -rf`. Prints the reason to stderr and `exit(2)` → the tool is stopped and the agent is told why, so it adapts. | **Yes** — this is the guarantee |
| `post_tool_use.py` | **PostToolUse** | Appends every tool call to `logs/post_tool_use.json` — a full audit trail of what the agent did. | No — the tool already ran; observe only |

That split *is* the mental model: **pre = gate, post = log.** This is deliberately the whole hooks layer this
pack ships — always-on safety, generic to any codebase. Anything more specific to *your* workflow (a checker
that gates completion, an artifact hand-off between two skills) is a conversation with your agent away, not a
file to copy — see below.

### Exit codes — the one thing to get right

**Only `exit 2` blocks.** Not exit 1, which is what every linter, type checker and test runner returns on
failure. Converting one into the other is most of what a gate-style hook does.

| Exit | Meaning |
|---|---|
| `0` | success. stdout goes to the debug log (except on `UserPromptSubmit` / `SessionStart`, where it becomes context) |
| **`2`** | **blocking error.** stderr is handed to the agent as the reason |
| anything else | non-blocking error: noise, no effect |

What `exit 2` blocks depends on the event:

| Event | Does `exit 2` block? |
|---|---|
| `PreToolUse` | **yes** — the tool call is stopped (`pre_tool_use.py` relies on this) |
| `Stop` | **yes** — the session is prevented from finishing |
| `PostToolUse` | **no** — the tool already ran; stderr is merely shown, so `post_tool_use.py` always exits 0 |

## Turning them on

Hooks are the one primitive that does something the moment it exists, so the pack ships the wiring as a
**template** rather than a live file:

```bash
cp .claude/settings.json.example .claude/settings.json
```

`.claude/settings.json` is gitignored here in the pack so the hooks don't fire while you're reading the
material. **In your own project, commit it** — that's how the whole team inherits the same guarantees. If you
already have a `settings.json`, merge the `hooks` block in rather than overwriting it.

## Try it

```
ask the agent to read your env file          -> blocked (exit 2, reason handed back)
ask it to read a committed .env.example       -> allowed
ask it to run `rm -rf ...`                    -> blocked
any normal command                            -> allowed, and logged to logs/post_tool_use.json
```

You can also test a hook directly, without the agent:

```bash
echo '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | uv run .claude/hooks/pre_tool_use.py; echo "exit=$?"
```

`exit=2` means the guard fired.

## Building your own — you don't have to write Python by hand, and this pack doesn't ship examples on purpose

The two hooks above are deliberately generic — safe defaults for any codebase. The moment you want something
specific to *your* workflow (gate completion on your own checks, hand an artifact from one skill to the next,
auto-format on edit), that's not something a generic starter pack can hand you as a ready file — it has to
know your commands, your paths, your checks. Describe it to your agent instead, in plain English, e.g.:

> "Don't let me finish until my tests pass — run my test command when I try to stop, and if it fails, block the
> stop and tell me why."

Claude Code (and most current coding agents) can pick the right lifecycle event, write the script, and wire it
into `settings.json` for you from a description like that — no need to hand-write hook JSON. Common shapes
worth knowing by name before you ask for one:

- **react** (`PostToolUse`) — something fires because a file changed. Auto-format on edit is the classic case.
- **gate** (`Stop`) — the agent can't declare done while your checks are red. **Bound it yourself** — a
  hook has no memory, so if it can retry, give it its own attempt counter on disk. Don't trust an
  undocumented flag to bound a loop for you; verify what actually happens before you rely on it.
- **baton** — one skill's artifact lands, and the hook starts the next skill in a **fresh** context. Guard it
  on file state (input present, output absent), never on memory — the guard is what makes it safe to fire a
  hundred times and act exactly once.

## Two things to know

- **Hooks run real code, automatically, with your credentials, with no sandbox.** Review a hook the way you'd
  review a CI script. Only run hooks you have read and trust. This is the same caution as MCP servers.
- **Coverage is yours.** The hook is guaranteed to *run*; what it *catches* is only as good as the check you
  wrote. It is the enforcement point, not omniscience.

## Portability

This is not a Claude Code party trick. Codex and Cursor use the same shape (a script, JSON on stdin,
`exit 2` to block); Gemini CLI does the same job by reading a structured JSON decision instead of the exit
code; Pi and opencode run hooks in-process as plugins. Learn it once, it transfers — the same way `AGENTS.md`
became the shared rules file.
