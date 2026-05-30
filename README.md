# mpst — modern-python-service-template

A production-ready Python microservice template that wires together **FastAPI**, **FastStream** (NATS JetStream), **Dishka** DI, **SQLAlchemy 2.0 async**, **OpenTelemetry**, and **Structlog** into a cohesive, opinionated foundation.

The project demonstrates clean layered architecture: HTTP routers and NATS handlers delegate to domain services, which compose DAOs over an async SQLAlchemy session managed by a Unit of Work. Events are collected during business logic and flushed to NATS only after DB commit, guaranteeing atomicity. Everything is wired via Dishka — APP-scoped resources (engine, broker) are shared across the process; REQUEST-scoped objects (session, services) are injected per request or message. Full observability (logs, traces, metrics) is built in from the start.

The template is designed to be forked and extended — add domains under `src/services/`, register providers in `src/di/providers/`, and wire routers in `src/api/`.

---

## Stack

| Layer | Technology |
|---|---|
| HTTP | FastAPI |
| Messaging | FastStream + NATS JetStream |
| DI | Dishka |
| ORM | SQLAlchemy 2.0 + asyncpg |
| DB | PostgreSQL |
| Migrations | Alembic |
| Config | Pydantic Settings |
| Logs | Structlog |
| Traces | OpenTelemetry |
| Metrics | OpenTelemetry |

---

## Architecture

### Layer responsibilities

```
Router / Handler    — deserialize, call service, manage UoW+flush
    ↓
Service             — business logic, compose DAOs, collect events
    ↓
DAO                 — SQL queries (generic CRUD via BaseDAO + domain-specific methods)
    ↓
UnitOfWork          — DB session wrapper (explicit commit, rollback on exit)
```

### Event publishing (collect/flush)

Events are **collected** during service execution, then **flushed** after `uow.commit()` in the router. If the DB transaction fails, events are discarded — guaranteeing atomicity.

| Method | When | What |
|---|---|---|
| `publisher.collect(event)` | Inside service | Buffer event |
| `uow.commit()` | After service call | Persist DB changes |
| `publisher.flush()` | After commit | Publish all buffered events to NATS |
| `publisher.discard()` | On rollback | Drop buffered events |

NATS JetStream deduplication via `Nats-Msg-Id` header (event `event_id`).

### Unit of Work

Manages session only — does NOT publish events. Always rollbacks on `__aexit__`; caller must explicitly `commit`.

### DI wiring

- **APP scope**: engine, sessionmaker, NatsBroker (process lifetime)
- **REQUEST scope**: AsyncSession, UnitOfWork, MessagePublisher, services (per request/message)

Providers are split by concern: `database.py`, `broker.py`, `publisher.py`, `telemetry.py`, `services/`.

### Router manages UoW, not Service

```python
async with uow:
    user = await service.create(data)
    await uow.commit()
    await publisher.flush()
```

Services receive `session` and `publisher` — the UoW context belongs to the router/handler, keeping services testable without DI.

### DAO composition

`BaseDAO[M, PK, CS, US]` provides `get_by_id`, `get_many`, `create`, `update`, `delete`, `exists`. Domain DAOs extend it, adding custom queries. Services **compose** DAOs (no inheritance).

### Domain event messages

Frozen Pydantic models extending `DomainEvent` (auto `event_id`, `correlation_id`, `occurred_at`). NATS subject convention: `{service}.{domain}.{past-tense-verb}`.

### Observability

- **Logs**: Structlog enriches all events with `trace_id`/`span_id` via `TraceContextProcessor`.
- **Traces**: W3C trace context extracted/injected via middleware; custom spans via `tracer.start_as_current_span`.
- **Metrics**: Counters (e.g., user creation) exported via OTLP to Prometheus.

### Health endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness — always 200 |
| `GET /readiness` | Readiness — checks PostgreSQL + NATS |

---

## Layout

```
src/
├── __main__.py              # Entry point (uvicorn)
├── lifespan.py              # Startup/shutdown (broker, engine, migrations)
├── api/
│   ├── web.py               # FastAPI APIRouter aggregate
│   ├── events.py            # FastStream NatsRouter aggregate
│   └── health.py            # /health, /readiness
├── config/
│   └── env/                 # Per-domain Pydantic-Settings
├── core/
│   ├── exceptions.py        # AppError → NotFoundError, ConflictError, etc.
│   ├── publisher.py         # DomainEvent base, MessagePublisher
│   └── telemetry/           # Logging, traces, metrics, instrumentation, middleware
├── database/
│   ├── engine.py            # get_engine, get_sessionmaker
│   ├── migrations.py        # Alembic auto-runner
│   ├── uow.py               # UnitOfWork
│   ├── models/              # DeclarativeBase, mixins (UUID, Timestamp, SoftDelete)
│   └── dao/                 # BaseDAO generic CRUD, pagination/filter mixins
├── di/
│   └── providers/           # Dishka providers per concern + services
└── services/
    └── <domain>/            # Domain module: service, dao, web, events, types/
```

---

## Getting Started

### Prerequisites

- **Docker + Docker Compose** — runs PostgreSQL, NATS, and the observability stack
- **Python 3.12+** — runtime
- **uv** — [package manager](https://docs.astral.sh/uv/)

### Local development

```bash
# 1. Install dependencies
uv sync --frozen

# 2. Copy and adjust environment
cp .env.example .env

# 3. Run database migrations
uv run alembic upgrade head

# 4. Start the API server
uv run -m src

# API:  http://localhost:80
# Docs: http://localhost:80/docs
```

### Adding a new domain

1. Create `src/services/<domain>/` with `service.py`, `dao.py`, `web.py`, `events.py`, `types/`
2. Define SQLAlchemy model, Pydantic schemas, DTOs, and event messages
3. Create DAO extending `BaseDAO`, service composing the DAO
4. Wire FastAPI router and FastStream NATS handlers in `api/web.py` and `api/events.py`
5. Register the service in `src/di/providers/services/`

### Code quality
```bash
# Lint
uv run ruff check .
uv run ruff format --check .

# Type check
uv run mypy .

# Tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
```

---

### Contacts
**Telegram:** [@fxnxtic](https://t.me/fxnxtic)

`with 💜 by dinalt`
