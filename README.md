# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

A backend-focused lead-capture platform where customers can create embeddable widgets, install them on external websites with a single script tag, and receive validated, abuse-protected, enriched submissions.

## Architecture sketch

- Owner -> Authenticated Widget Management API -> Database
- Customer website -> widget.js -> public config endpoint -> render widget
- Visitor -> public submission endpoint -> validation / rate limit / spam check / geo enrichment -> database
- Owner -> Dashboard API -> stored submissions and stats

## Planned stack

- Python + FastAPI
- SQLite
- Localhost only
- Console email side effect
- Two geo providers with fallback

## Limitations

- No production hosting
- No real email provider
- Minimal frontend
- Local-only demo setup