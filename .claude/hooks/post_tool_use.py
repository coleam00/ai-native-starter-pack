#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
PostToolUse hook — the visibility pillar.

Fires AFTER every tool call. It can't block (the tool already ran), so its job is
to *observe*: append the full event to logs/post_tool_use.json. The result is a
complete audit trail of exactly what the agent did — every command, every edit —
that you can read back or pipe into a dashboard.

Pre = gate. Post = log.

Fails OPEN: any error exits 0, so logging can never break your session.

MAKE IT YOURS: this is the simplest useful PostToolUse hook. The common upgrades
are auto-formatting a file the moment it's edited, or notifying you on a specific
tool. Describe what you want to your agent and have it write the hook for you.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    try:
        data = json.load(sys.stdin)

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "post_tool_use.json"

        if log_path.exists():
            try:
                entries = json.loads(log_path.read_text())
            except (json.JSONDecodeError, ValueError):
                entries = []
        else:
            entries = []

        entries.append(data)
        log_path.write_text(json.dumps(entries, indent=2))

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
