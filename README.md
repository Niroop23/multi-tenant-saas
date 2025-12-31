# Multi-tenant SaaS Example

A minimal, practical FastAPI-based multi-tenant SaaS starter project with organizations, memberships, invites, and token-based auth. It includes database migrations (Alembic), a modular app layout, and basic tests.

## Features

- Multi-organization (multi-tenant) data model
- Users, organizations, memberships, and invites
- JWT authentication and refresh tokens
- Alembic migrations for schema management
- Clear, modular project layout for quick extension

## Tech stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- Uvicorn

## Requirements

Install dependencies from `requirements.txt` in a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment variables

Create a `.env` or export the following values in your environment (examples):

- `DATABASE_URL` — SQLAlchemy database URL (e.g. `sqlite:///./dev.db` or a Postgres DSN)
- `SECRET_KEY` — secret for signing tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES` — integer

Adjust values in `app/core/config.py` if needed.

## Database migrations

Initialize and apply migrations with Alembic (already configured in the project):

```bash
alembic upgrade head
```

To create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Run the application

Start the app locally with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs for the interactive OpenAPI docs.

## Tests

Note: There are currently no tests in the `tests/` directory.

When you add tests, run them with pytest:

```bash
pytest -q
```

## Project structure

- `app/` — application package
	- `core/` — configuration, dependencies, security helpers
	- `database/` — SQLAlchemy base and session setup
	- `models/` — ORM models (user, organization, membership, tokens)
	- `routes/` — FastAPI route modules
	- `schemas/` — Pydantic request/response schemas
	- `services/` — business logic helpers
- `alembic/` — migration configs and versions
- `tests/` — test suite

Refer to individual modules as needed for implementation details.

