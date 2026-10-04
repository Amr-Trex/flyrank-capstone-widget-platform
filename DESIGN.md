# Design — Embeddable Widget & Lead-Capture Platform

## Problem

Customers need to embed simple lead-capture widgets on any website using one script tag. Submissions come from untrusted browsers on arbitrary origins, so the backend must validate input, resist abuse, enrich safely, store reliably, and expose owner analytics.

## Actors

1. Widget owner: authenticated customer who manages widgets and views submissions
2. Customer website: external origin that loads the widget script and config
3. Visitor: untrusted public user who submits the widget form

## Data model

### owners
- id
- name
- api_key
- created_at

### widgets
- id
- owner_id
- public_id
- type
- title
- description
- button_text
- fields_json
- status
- created_at

Indexes:
- unique(public_id)
- index(owner_id)

### submissions
- id
- widget_public_id
- owner_id
- data_json
- ip_address
- geo_country
- geo_city
- geo_provider
- idempotency_key
- created_at

Indexes:
- index(widget_public_id)
- index(owner_id)
- index(created_at)
- unique(widget_public_id, idempotency_key) when idempotency_key present

## API surface

### Owner API, authenticated by X-API-Key
- POST /widgets
- GET /widgets
- GET /widgets/{id}
- PATCH /widgets/{id}
- DELETE /widgets/{id}
- GET /dashboard/submissions
- GET /dashboard/stats

### Public endpoints
- GET /public/widgets/{public_id}/config
- GET /public/widget.v1.js
- POST /public/submissions

## Layer sketch

- HTTP layer: FastAPI routes, auth dependency, CORS
- Service layer: widget service, submission service, enrichment service, notifier
- Data layer: SQLite repository functions
- External layer: geo provider A/B fallback, console email

## Explicit non-goal

This project will not build a polished frontend, a real form-builder product, production CDN hosting, or real email delivery.

## Key design decisions

- SQLite first for simplicity
- API-key auth for owners
- Public submission endpoint validates all input before business logic
- Geo enrichment is optional and must fail gracefully
- Email side effect runs after storage and must not block success
- Rate limiting and honeypot field protect public endpoint