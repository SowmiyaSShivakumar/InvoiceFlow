# INTERFACES.md

## Purpose

This document defines the contracts shared between teams.

All developers and AI coding agents must follow these interfaces.

Changes require a pull request and team review.

---

# User Model

## User

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "fullName": "John Doe",
  "createdAt": "2026-06-01T10:00:00Z"
}
```

---

# Authentication API

## Register

POST /api/auth/register

Request

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "fullName": "John Doe"
}
```

Response

```json
{
  "userId": "uuid",
  "message": "Registration successful"
}
```

---

## Login

POST /api/auth/login

Request

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123"
}
```

Response

```json
{
  "accessToken": "jwt-token",
  "expiresIn": 3600
}
```

---

# Invoice Model

## Invoice

```json
{
  "invoiceId": "uuid",
  "customerId": "uuid",
  "status": "draft",
  "totalInPaise": 9950,
  "currency": "INR"
}
```

Important:

Monetary values must always be stored as integer paise.

Never use floating-point currency values.

---

# Invoice API

POST /api/invoices

Response

```json
{
  "invoiceId": "uuid",
  "status": "draft"
}
```

---

# Payment Event

Event Name

invoice.paid

Payload

```json
{
  "invoiceId": "uuid",
  "paymentId": "uuid",
  "amountInPaise": 9950,
  "timestamp": "2026-06-01T10:00:00Z"
}
```

---

# Ownership

Authentication Team

* Auth APIs
* JWT handling

Invoice Team

* Invoice APIs
* Invoice data model

Billing Team

* Payment processing
* Payment events

Notification Team

* Email delivery
* Invoice notifications

```
```
