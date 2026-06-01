# DECISIONS.md

## Purpose

This file records important technical decisions.

All developers and AI coding agents should consult this file before proposing architecture changes.

---

# 2026-06-01

## Decision

Use FastAPI for backend services.

### Alternatives Considered

* Express.js
* NestJS

### Reason

Team expertise and strong typing support through Pydantic.

---

# 2026-06-01

## Decision

Use PostgreSQL as primary database.

### Alternatives Considered

* MongoDB
* MySQL

### Reason

Strong transactional support and relational consistency.

---

# 2026-06-01

## Decision

Use JWT authentication.

### Alternatives Considered

* Session cookies
* OAuth-only

### Reason

Mobile application compatibility and stateless APIs.

---

# 2026-06-01

## Decision

Store currency as integer paise.

### Alternatives Considered

* Floating-point decimal values

### Reason

Avoid rounding and precision issues.

Example

Correct:

9950

Incorrect:

99.50

---

# 2026-06-01

## Decision

Follow Repository Pattern.

Architecture

UI
→ API
→ Services
→ Repositories
→ Database

### Reason

Separation of concerns and easier testing.

---

# 2026-06-01

## Decision

Every new feature must include automated tests.

### Reason

Maintain deployment quality and reduce regressions.

```
```
