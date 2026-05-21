# Backend API Best Practices

On-demand context for agents touching API endpoints. Load this before building or modifying backend routes.

---

## Routing

- Group routes by resource (`/users`, `/documents`, `/sessions`); nest sub-resources sparingly.
- Use plural nouns for collections, no verbs in URLs (`GET /documents` not `GET /getDocuments`).
- Version the API when breaking changes are possible (`/api/v1/...`).
- Keep route handlers thin — delegate business logic to a service layer.

## Input Validation

- Validate and parse all incoming data at the boundary before it touches business logic.
- Use a schema library (Pydantic, Zod, Marshmallow) — never trust raw request data.
- Return `422 Unprocessable Entity` (or `400 Bad Request`) with field-level error details on invalid input.
- Sanitize string inputs to prevent injection; never interpolate user data into raw SQL.

## Error Handling

- Use a centralized error handler / exception middleware rather than per-route try/except.
- Return structured JSON errors: `{ "error": "...", "detail": "...", "code": "..." }`.
- Never expose stack traces or internal paths to the client in production.
- Log the full exception server-side; return a safe, human-readable message to the client.

## HTTP Status Codes

| Situation | Code |
|-----------|------|
| Created successfully | 201 |
| No content (delete) | 204 |
| Bad request / validation | 400 |
| Unauthenticated | 401 |
| Forbidden (authenticated but unauthorized) | 403 |
| Not found | 404 |
| Conflict (duplicate) | 409 |
| Unprocessable entity | 422 |
| Server error | 500 |

## Authentication & Authorization

- Authenticate at the middleware/dependency level, not inside individual handlers.
- Check authorization (ownership, roles) after authentication, before business logic.
- Never store secrets in code; load from environment variables.
- Use short-lived tokens; implement refresh-token rotation for sensitive flows.

## Pagination

- Paginate all collection endpoints; never return unbounded lists.
- Prefer cursor-based pagination for large or frequently-updated datasets.
- Include pagination metadata in responses: `{ "items": [...], "next_cursor": "...", "total": N }`.
- Default page size should be reasonable (20–50); allow clients to override up to a max (e.g. 100).

## Testing

- Write at least one happy-path and one error-path test per endpoint.
- Use a real (or in-memory) database in integration tests — do not mock the ORM.
- Test authentication and authorization separately from business logic.
- Validate response shape, not just status code.

## Common Anti-Patterns to Avoid

- Fat controllers — if a handler exceeds ~30 lines, move logic to a service.
- Catching all exceptions with a bare `except Exception` that swallows the error.
- Synchronous blocking calls inside async handlers.
- Returning `200 OK` for errors just because the HTTP call succeeded.
- N+1 queries — use eager loading or batch fetching for related data.
