---
paths:
  - "*/src/routes/**/*"
---

# routes/ — Layer Standards

## Purpose
FastAPI HTTP boundary. Each router maps URLs to a service entry-point — nothing more. A file may declare **several routers** grouped by area; each is registered independently in `api.py`.

## Coding Rules (specific to this directory)
- `api.py` is the `api_router` aggregator; it registers every other router via `include_router(...)`.
- A route handler is a **thin shim**: parse request → generate `flow_id` (`str(uuid4())`) → call exactly one service entry-point → return its result.
- `response_model=` uses a `BaseModel` imported from `schemas/` (the shared `Response`).
- One or more routers per file — each `<area>_router = APIRouter(prefix="/<area>", tags=["<area>"])`, grouped by area. A single-router file may name it `router`.
- Register every router in `api.py` via `api_router.include_router(<module>.<name>_router)` — alphabetical or grouped by domain.
- Dependencies (auth, request-scoped objects) live in `src/dependencies.py` and are pulled via `Depends(...)`.

## Forbidden in this directory
- No business logic — every branch, validation, or transformation moves to a service.
- No `try/except` here. This is the one layer with none: the service entry-point absorbs its own failures and returns a safe default, so a handler has nothing to catch.
- No prefix duplication across files.