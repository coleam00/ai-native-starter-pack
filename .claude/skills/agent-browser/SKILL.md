---
name: agent-browser
description: Drive a real browser to validate web apps end-to-end. Use when you need to navigate to a URL, interact with UI elements, fill forms, click buttons, take screenshots, assert page state, or run a full end-to-end validation flow for a web feature. The primary tool for automated browser-based E2E testing in the AI Layer.
---

# agent-browser — Automated E2E Browser Testing

`agent-browser` is a CLI-driven browser automation tool (by [Vercel Labs](https://github.com/vercel-labs/agent-browser)) that the AI agent controls directly via shell commands. No Playwright/Puppeteer code required — the agent issues commands, reads the structured output, and makes decisions.

## Installation

```bash
# Install globally
npm install -g agent-browser

# Download browser engine (Chrome for Testing)
agent-browser install
```

**Platform notes:**
- **macOS/Linux**: Works natively after install.
- **Windows**: Has a [known issue](https://github.com/vercel-labs/agent-browser/issues/56) with Unix domain sockets. Use WSL as a workaround, or run from a Linux container.
- **Docker/CI**: Install in the image with the two commands above.

## Core workflow

1. Navigate: `agent-browser open <url>`
2. Snapshot: `agent-browser snapshot -i` — returns interactive elements tagged with refs (`@e1`, `@e2`, …)
3. Interact using those refs
4. Re-snapshot after navigation or significant DOM changes
5. Assert state with `get`, `is`, or `wait` commands
6. Screenshot for evidence: `agent-browser screenshot path.png`

## E2E Testing Protocol

When using `agent-browser` to validate a feature end-to-end:

1. **Start the dev/preview server** if it is not already running (check CLAUDE.md for the project's start command).
2. **Navigate** to the feature's entry URL.
3. **Snapshot** to discover the interactive elements.
4. **Exercise the happy path** — fill inputs, click buttons, submit forms, assert success state.
5. **Exercise key error/edge paths** — missing required fields, invalid input, auth-required pages.
6. **Screenshot at each key moment** — before interaction, after success, after error. Save to `screenshots/` with descriptive names.
7. **Check console errors** with `agent-browser errors` at the end of the session.
8. **Close** the browser: `agent-browser close`.

## Commands

### Navigation
```bash
agent-browser open <url>      # Navigate to URL
agent-browser back            # Go back
agent-browser forward         # Go forward
agent-browser reload          # Reload page
agent-browser close           # Close browser
```

### Snapshot (page analysis)
```bash
agent-browser snapshot            # Full accessibility tree
agent-browser snapshot -i         # Interactive elements only (recommended for testing)
agent-browser snapshot -c         # Compact output
agent-browser snapshot -d 3       # Limit depth to 3
agent-browser snapshot -s "#main" # Scope to CSS selector
```

### Interactions (use @refs from snapshot)
```bash
agent-browser click @e1           # Click
agent-browser dblclick @e1        # Double-click
agent-browser focus @e1           # Focus element
agent-browser fill @e2 "text"     # Clear and type
agent-browser type @e2 "text"     # Type without clearing
agent-browser press Enter         # Press key
agent-browser press Control+a     # Key combination
agent-browser hover @e1           # Hover
agent-browser check @e1           # Check checkbox
agent-browser uncheck @e1         # Uncheck checkbox
agent-browser select @e1 "value"  # Select dropdown option
agent-browser scroll down 500     # Scroll page
agent-browser scrollintoview @e1  # Scroll element into view
agent-browser drag @e1 @e2        # Drag and drop
agent-browser upload @e1 file.pdf # Upload file
```

### Get information / Assert state
```bash
agent-browser get text @e1        # Get element text
agent-browser get html @e1        # Get innerHTML
agent-browser get value @e1       # Get input value
agent-browser get attr @e1 href   # Get attribute
agent-browser get title           # Get page title
agent-browser get url             # Get current URL
agent-browser get count ".item"   # Count matching elements
agent-browser get box @e1         # Get bounding box

agent-browser is visible @e1      # Check if visible
agent-browser is enabled @e1      # Check if enabled
agent-browser is checked @e1      # Check if checked
```

### Wait / Synchronization
```bash
agent-browser wait @e1                     # Wait for element to appear
agent-browser wait 2000                    # Wait milliseconds
agent-browser wait --text "Success"        # Wait for text to appear
agent-browser wait --url "**/dashboard"    # Wait for URL pattern
agent-browser wait --load networkidle      # Wait for network idle
agent-browser wait --fn "window.ready"    # Wait for JS condition
```

### Screenshots & PDF
```bash
agent-browser screenshot                  # Screenshot to stdout
agent-browser screenshot screenshots/step1.png  # Save to file
agent-browser screenshot --full           # Full page screenshot
agent-browser pdf output.pdf             # Save page as PDF
```

### Semantic locators (alternative to @refs)
```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find first ".item" click
agent-browser find nth 2 "a" text
```

### Debugging
```bash
agent-browser open <url> --headed    # Show browser window (useful locally)
agent-browser console                # View console messages
agent-browser errors                 # View page errors (run at end of test)
agent-browser highlight @e1          # Highlight element
agent-browser trace start            # Start recording trace
agent-browser trace stop trace.zip   # Stop and save trace
agent-browser record start ./demo.webm  # Record video session
agent-browser record stop               # Stop and save video
```

### JavaScript
```bash
agent-browser eval "document.title"       # Run JavaScript and get result
```

### Network (mocking/interception)
```bash
agent-browser network route <url>              # Intercept requests
agent-browser network route <url> --abort      # Block requests
agent-browser network route <url> --body '{}'  # Mock response body
agent-browser network unroute [url]            # Remove routes
agent-browser network requests                 # View tracked requests
```

### Sessions (parallel browsers)
```bash
agent-browser --session test1 open site-a.com
agent-browser --session test2 open site-b.com
agent-browser session list
```

### Saved auth state
```bash
# Login once, save state
agent-browser open https://app.example.com/login
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# Reuse in subsequent test runs
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### JSON output (for programmatic checks)
```bash
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

## Example: End-to-end form submission test

```bash
# 1. Start
agent-browser open http://localhost:3000/signup

# 2. Discover
agent-browser snapshot -i
# → textbox "Email" [ref=e1], textbox "Password" [ref=e2], button "Create account" [ref=e3]

# 3. Happy path
agent-browser fill @e1 "test@example.com"
agent-browser fill @e2 "SecurePass123!"
agent-browser screenshot screenshots/before-submit.png
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser screenshot screenshots/after-signup.png
agent-browser get title
# → Expected: "Dashboard"

# 4. Error path — submit empty form
agent-browser open http://localhost:3000/signup
agent-browser snapshot -i
agent-browser click @e3          # Submit without filling in
agent-browser wait --text "required"
agent-browser screenshot screenshots/validation-errors.png

# 5. Check for console errors
agent-browser errors

# 6. Clean up
agent-browser close
```

## Integration with plan-feature validation levels

When a plan's **Level 5 (E2E / Browser Automation)** is reached:

1. Confirm the dev server is running.
2. Follow the E2E Testing Protocol above.
3. Save screenshots to `screenshots/<ticket-id>-<description>.png`.
4. Paste the screenshot paths and a pass/fail summary into the plan's completion checklist.

## Notes

- Always re-snapshot after a navigation or significant DOM mutation — refs are invalidated.
- Prefer `agent-browser wait --load networkidle` after form submissions before asserting state.
- For CI environments, omit `--headed`; for local debugging, add it so you can watch the browser.
- `agent-browser errors` at the end of a session catches JS exceptions that wouldn't otherwise surface.
