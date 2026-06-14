# ESL-voice

M1 walking skeleton: adaptive ESL tutoring for immigrant service workers.

## Quick start (local)

```bash
# 1. Install all deps
make install

# 2. Start Postgres + Redis
make db

# 3. Dev servers
make dev
```

## Running tests

```bash
make test-backend
make test-acceptance
make lint-content
```

## Production deployment

```bash
cp .env.example .env
# edit .env with real secrets
make prod
```

Production uses `infra/docker-compose.prod.yml` with Nginx, backend, frontend, Postgres, and Redis.

## Project structure

- `backend/` — FastAPI + SQLModel
- `frontend/` — Next.js 15 + next-intl
- `content/lessons/` — YAML lesson catalog
- `infra/` — Docker Compose, Nginx, systemd
- `scripts/` — content lint and seed helpers
