# API Design Review Checklist

## Review Info

| Field | Value |
|-------|-------|
| **API Name** | [Name] |
| **Version** | [v1.0.0] |
| **Reviewer** | [Name] |
| **Review Date** | [YYYY-MM-DD] |
| **Spec Format** | [OpenAPI 3.1 / Other] |

---

## REST Maturity Level

- [ ] **Level 0:** Single URI, single HTTP verb -- NOT acceptable
- [ ] **Level 1:** Individual URIs per resource
- [ ] **Level 2:** Proper HTTP verbs (GET/POST/PUT/PATCH/DELETE)
- [ ] **Level 3:** HATEOAS / hypermedia links (optional, document if skipped)

**Current Level:** [1 / 2 / 3]

---

## URL Naming Conventions

- [ ] Resources use **plural nouns** (`/users`, `/orders`)
- [ ] No verbs in URLs (`/users`, not `/getUsers` or `/createUser`)
- [ ] Consistent casing (kebab-case: `/user-profiles`)
- [ ] No uppercase letters in paths
- [ ] Nested resources max 2 levels deep (`/users/{id}/orders`)
- [ ] Actions modeled as sub-resources (`/users/{id}/actions/activate`)

---

## HTTP Method Usage

- [ ] **GET** -- Read-only, safe, cacheable, idempotent
- [ ] **POST** -- Create new resource (returns 201 + Location header)
- [ ] **PUT** -- Full replacement of resource (idempotent)
- [ ] **PATCH** -- Partial update (not necessarily idempotent)
- [ ] **DELETE** -- Remove resource (idempotent, returns 204)
- [ ] No state mutations via GET requests

---

## Status Code Correctness

- [ ] **200** -- Successful GET, PUT, PATCH
- [ ] **201** -- Successful POST (resource created)
- [ ] **204** -- Successful DELETE (no content)
- [ ] **400** -- Validation errors, malformed request
- [ ] **401** -- Missing or invalid authentication
- [ ] **403** -- Authenticated but not authorized
- [ ] **404** -- Resource not found
- [ ] **409** -- Conflict (duplicate, version mismatch)
- [ ] **422** -- Unprocessable entity (semantic errors)
- [ ] **429** -- Rate limit exceeded (with Retry-After header)
- [ ] **500** -- Internal server error (no details leaked)

---

## Pagination

- [ ] All list endpoints are paginated
- [ ] Maximum page size enforced (e.g., `limit` max 100)
- [ ] Default page size set (e.g., `limit` default 20)
- [ ] Response includes pagination metadata (`page`, `limit`, `total`, `totalPages`)
- [ ] Cursor-based pagination available for large datasets (optional)
- [ ] `Link` headers for navigation (optional)

---

## Versioning Strategy

- [ ] Versioning scheme documented: [URL path (`/v1/`) / Header / Query param]
- [ ] Deprecation policy defined
- [ ] `Deprecation` and `Sunset` headers used for deprecated endpoints
- [ ] Migration guide available for version transitions

---

## Error Response Format

- [ ] Consistent error envelope across all endpoints
- [ ] Error includes: `error` (human-readable), `code` (machine-readable)
- [ ] Validation errors include `details` array with field-level messages
- [ ] `requestId` included for debugging
- [ ] No stack traces or internal details in production errors

---

## Rate Limiting

- [ ] Rate limiting applied to all endpoints
- [ ] Stricter limits on authentication endpoints
- [ ] Rate limit headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- [ ] `Retry-After` header on 429 responses

---

## Authentication and Authorization

- [ ] Authentication required on all non-public endpoints
- [ ] Authentication scheme documented (Bearer JWT / API key / OAuth2)
- [ ] Authorization checked per resource (no IDOR)
- [ ] Sensitive operations require re-authentication or MFA

---

## CORS Configuration

- [ ] Allowed origins explicitly listed (no wildcard `*` in production)
- [ ] Allowed methods restricted to those actually used
- [ ] Credentials mode set correctly
- [ ] Preflight caching configured (`Access-Control-Max-Age`)

---

## Summary

| Area | Status | Notes |
|------|--------|-------|
| URL Naming | [Pass/Fail] | [Notes] |
| HTTP Methods | [Pass/Fail] | [Notes] |
| Status Codes | [Pass/Fail] | [Notes] |
| Pagination | [Pass/Fail] | [Notes] |
| Versioning | [Pass/Fail] | [Notes] |
| Error Format | [Pass/Fail] | [Notes] |
| Rate Limiting | [Pass/Fail] | [Notes] |
| Auth | [Pass/Fail] | [Notes] |
| CORS | [Pass/Fail] | [Notes] |
