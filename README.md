# Wallet API

Multi-user bank account API built with Django REST Framework. Users can manage accounts, record income and expense transactions, and view balances.

## Stack

- Django 5 + Django REST Framework
- PostgreSQL + Docker Compose
- Session-based auth (HttpOnly cookies, not JWT)
- drf-spectacular (OpenAPI / Swagger)
- pytest-django

## Project structure

```
core/                   # Django settings, urls, wsgi
users/                  # Custom user model + auth (feature/users-auth)
accounts/               # Bank accounts (feature/accounts-core)
transactions/           # Income / expense (feature/transactions)
tests/
requirements/
```

## Quick start

```bash
cp .env.example .env

# Docker (recommended)
docker compose up --build

# In another terminal
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

API:

- Health: http://localhost:8000/api/health/
- Swagger: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

# PostgreSQL must be running; set POSTGRES_HOST=localhost in .env
python manage.py migrate
python manage.py runserver
```

## Tests

```bash
pytest
```

## Branch workflow

| Branch | Scope |
|--------|-------|
| `develop` | Integration branch |
| `feature/project-setup` | Django skeleton, Docker, DRF |
| `feature/users-auth` | Register, login, logout, session auth |
| `feature/accounts-core` | Account model + CRUD |
| `feature/transactions` | Transaction model, balance logic |
| `feature/summary-reporting` | Summary endpoints, filters |

Built to demonstrate real Django patterns — not a JWT tutorial.
