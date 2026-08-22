# Wallet API

Multi-user bank account API built with Django REST Framework. Users can register, authenticate via token cookie, manage bank accounts, and record income and expense transactions.

## About this project

Models are intentionally simple here: user, account, transaction. I wanted the repo to show Django/DRF basics without a heavy domain layer: custom user, token auth, permissions, migrations, API views, tests.

I've built more complex models in other projects (more relations, business rules, audit fields, soft delete across tables). This one is smaller on purpose. The point is a codebase you can open and follow in an afternoon.

Postgres, Docker, pytest, flake8, feature branches. Real setup, not a demo that only runs on my machine.

## Stack

- Django 5 + Django REST Framework
- PostgreSQL + Docker Compose
- DRF Token auth with HttpOnly cookie (`token`) or `Authorization: Token <key>` header
- drf-spectacular (OpenAPI / Swagger)
- pytest-django + flake8

## Project structure

```
core/           # settings, urls, TokenAuthSupportCookie middleware
accounts/       # UserABS, Account models, auth + account API
transactions/   # Income / expense, balance updates
tests/
requirements/
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

In another terminal:

```bash
docker compose exec web python manage.py migrate
```

Default seed user (from migration):

- Email: `admin@example.com`
- Password: `default_password`
- Account: `1234567890` (checking, balance 1000.00)

## API

Base path: `/api`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health/` | No | Health check |
| POST | `/auth/register/` | No | Register |
| POST | `/auth/login/` | No | Login (sets `token` cookie) |
| POST | `/auth/logout/` | Yes | Logout |
| GET | `/auth/me/` | Yes | Current user profile |
| GET | `/accounts/` | Yes | List own accounts |
| POST | `/accounts/` | Yes | Create account |
| GET | `/accounts/<account-uuid>` | Yes | Account detail |
| PATCH | `/accounts/<account-uuid>` | Yes | Update account type |
| DELETE | `/accounts/<account-uuid>` | Yes | Soft delete account |
| GET | `/accounts/<account-uuid>/summary` | Yes | Income/expense totals and current balance |
| GET | `/accounts/<account-uuid>/transactions/` | Yes | List account transactions |
| POST | `/accounts/<account-uuid>/transactions/` | Yes | Create income or expense |
| GET | `/accounts/<account-uuid>/transactions/<transaction-uuid>` | Yes | Transaction detail |
| DELETE | `/accounts/<account-uuid>/transactions/<transaction-uuid>` | Yes | Soft delete and reverse balance |

`account-uuid` is `__uuid__` from an account response. `transaction-uuid` is `__uuid__` from a transaction response.

List and summary accept query filters: `transaction_type` (`income` or `expense`), `date_from`, `date_to` (`YYYY-MM-DD`).

Responses use double-underscore keys: `__email__`, `__account_number__`, `__detail__`, etc.

**Auth:** After login, send the `token` cookie automatically, or use:

```
Authorization: Token <token_key>
```

Links:

- Swagger: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

# Set POSTGRES_HOST=localhost in .env
python manage.py migrate
python manage.py runserver
```

## Tests

```bash
pytest
./run.sh   # flake8
```

## Branch workflow

| Branch | Status | Scope |
|--------|--------|-------|
| `master` | stable releases | Production-ready merges from `develop` |
| `develop` | integration | Active development |
| `feature/users-auth` | merged | Register, login, logout, token auth |
| `feature/accounts-core` | merged | Account CRUD |
| `feature/transactions` | merged | Transaction model, balance updates |
| `feature/summary-reporting` | in progress | Summary endpoints, filters |

Built to show Django patterns I actually use. Not a JWT tutorial.
