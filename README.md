# Ozue Backend

A Django backend for an Ozue-like advertising calendar system with GraphQL API and real-time WebSocket subscriptions.

## Tech Stack

- **Django 4.2** (LTS)
- **PostgreSQL**
- **Django Channels** (ASGI + WebSocket)
- **Redis** (channel layer)
- **Strawberry GraphQL**
- **JWT auth** (optional; session auth works out of the box)

## Features

- **Media plans** → campaigns → placements/events on a calendar
- **CalendarEvent** as the unit shown on the calendar (start/end, slot, page/section)
- **GraphQL queries** for events with date range and filters
- **GraphQL mutations** for create/update/cancel events
- **Real-time updates** via WebSocket subscriptions

## Quick Start

### Using Docker (recommended)

```bash
docker compose up --build
```

This starts PostgreSQL, Redis, and the Django app. The API is available at:

- **GraphQL (HTTP):** http://localhost:8000/graphql/
- **GraphiQL UI:** http://localhost:8000/graphql/ (interactive)
- **Admin:** http://localhost:8000/admin/
- **WebSocket:** ws://localhost:8000/ws/graphql/

### Local development (without Docker)

1. Create a PostgreSQL database named `ozue` and a Redis instance.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and adjust if needed.

4. Run migrations and create a superuser:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Run the server:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   For production-style ASGI (Daphne):

   ```bash
   daphne -b 0.0.0.0 -p 8000 ozue_backend.asgi:application
   ```

## GraphQL Examples

### Query events for a month

```graphql
query GetEvents($start: DateTime!, $end: DateTime!, $planId: Int!) {
  calendarEvents(start: $start, end: $end, planId: $planId) {
    id
    title
    startTs
    endTs
    status
    placement {
      id
      page
      section
      slot
      campaign { id name }
    }
  }
}
```

Variables:

```json
{
  "start": "2025-01-01T00:00:00Z",
  "end": "2025-01-31T23:59:59Z",
  "planId": 1
}
```

### Create event (requires authentication)

```graphql
mutation CreateEvent($data: CreateEventInput!) {
  createCalendarEvent(data: $data) {
    id
    title
    status
    startTs
    endTs
  }
}
```

### WebSocket subscription

Connect to `ws://localhost:8000/ws/graphql/` and send:

```json
{ "type": "SUBSCRIBE", "planId": 1 }
```

You’ll receive real-time pushes when events in that plan are created, updated, or canceled.

## Authentication

Mutations require an authenticated user. Options:

1. **Session auth:** Log in via Django admin or a login view; use the same session for GraphQL.
2. **JWT:** Add JWT middleware to the GraphQL view and pass a Bearer token in the `Authorization` header.

## Project structure

```
adpa-be/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── ozue_backend/
│   ├── settings.py
│   ├── asgi.py
│   ├── urls.py
│   └── routing.py
└── apps/
    ├── accounts/     # User model
    ├── planner/      # MediaPlan, Campaign, Placement, CalendarEvent + GraphQL
    └── realtime/     # WebSocket consumer for live updates
```
# adpa-be
