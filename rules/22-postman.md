---
paths:
  - "*/postman/**/*"
---

# postman/ — Shared-Root Standards

## Purpose
Postman collections + environments for manually exercising a microservice's HTTP API. Used by developers, QA, and integration partners. Not consumed by the runtime.

## Coding Rules (specific to this directory)
- `*.postman_collection.json` — exported Postman collections (one per service / domain). Self-contained: endpoints and docs credentials are baked directly into each request — no separate environment file.
- Optional `README.md` per collection describing what it covers.
- Every endpoint in a service's `src/routes/` should have at least one corresponding Postman request — happy path minimum.
- Endpoints and credentials are inline per request (no `{{variable}}` placeholders, no environment file). Real tokens live in each developer's local copy, never committed with real values.
- Multiple environments are modeled as one top-level folder per environment (`Local` / `Dev` / `Preprod` / `Prod`), each holding the full request set with its base URL baked into every request.
- Enumerated endpoint options get one dedicated request each — never a single request the user must edit. Read the enumeration from the service's own source of truth (the route's schema, its constants, or the directory the options are defined in); every option is its own request with the value baked into the body, plus one "all options" request carrying the empty value — in every environment folder.
- Each request carries an example response in the `example` block — keeps the collection self-documenting.
- Re-export from Postman after every meaningful change (new route, contract change). Stale collections are worse than missing ones.
- Collection name + filename must match the service / domain (e.g. `<feature_name>.postman_collection.json` for that service's `src/routes/<feature_name>.py`).

## Forbidden in this directory
- No executable code — `.json` files only (plus optional `.md`).
- No production hosts baked into requests without an explicit warning.
