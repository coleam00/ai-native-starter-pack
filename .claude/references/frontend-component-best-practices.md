# Frontend Component Best Practices

On-demand context for agents touching frontend code. Load this before building or modifying UI components.

---

## Component Structure

- One component per file; filename matches the exported component name (PascalCase).
- Order within a file: imports → types/interfaces → component function → helper functions → exports.
- Keep components focused — if a component has more than ~150 lines it likely needs splitting.
- Co-locate related files: `Button/Button.tsx`, `Button/Button.test.tsx`, `Button/index.ts`.

## Props & State

- Define props with a TypeScript interface named `<ComponentName>Props`; export it if consumers need it.
- Prefer explicit prop types over `any` or `React.FC` (which hides return type).
- Default props via destructuring defaults, not `defaultProps`.
- Lift state to the lowest common ancestor that needs it; avoid prop-drilling beyond two levels — use context or a state manager.
- Derive values from state instead of syncing duplicate state variables.

## Styling

- Follow whatever CSS strategy the project already uses (CSS Modules, Tailwind, styled-components) — check existing components first.
- Never mix approaches within the same component.
- Avoid inline styles except for genuinely dynamic values (e.g. calculated widths).
- Use design-system tokens (colors, spacing, typography) rather than raw hex/px values.

## Accessibility

- Every interactive element must be reachable by keyboard and have a visible focus ring.
- Provide `aria-label` or `aria-labelledby` when the label isn't visible text.
- Use semantic HTML (`<button>`, `<nav>`, `<main>`, `<section>`) before reaching for generic `<div>`.
- Images need `alt` text; decorative images use `alt=""`.
- Announce dynamic content updates with `aria-live` regions where appropriate.

## Testing

- Test behavior, not implementation: interact via user-visible queries (`getByRole`, `getByLabelText`).
- Cover: renders without error, key user interactions, edge cases (empty state, loading, error).
- Mock only external dependencies (API calls, timers) — do not mock internal child components.
- Aim for one test file per component; keep each test case small and independent.

## Common Anti-Patterns to Avoid

- `useEffect` for data that can be derived during render — compute it inline instead.
- Mutating props or state objects directly — always return new references.
- Deeply nested conditional JSX — extract into named variables or sub-components.
- Hardcoded strings that belong in constants or i18n keys.
