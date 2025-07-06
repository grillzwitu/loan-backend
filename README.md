# loan-backend

Django-based loan application backend service with REST API, JWT authentication, Redis caching, PostgreSQL (fallback to SQLite), fraud detection, and full test coverage.

## Tech Stack
- Python 3.12
- Django 5.x
- Django REST Framework
- Simple JWT for authentication
- PostgreSQL (fallback to SQLite for local)
- Redis (for caching)
- Poetry for dependency management
- Docker & Docker Compose
- pytest for tests

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/loan-backend.git
   cd loan-backend
   ```
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Apply migrations:
   ```bash
   poetry run python manage.py migrate
   ```
5. Start development server:
   ```bash
   poetry run python manage.py runserver
   ```

Or using Docker:

```bash
docker-compose up --build
```

Access the API at http://localhost:8000

## Environment Variables

See `.env.example` for required variables:
- SECRET_KEY
- DEBUG
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- USE_SQLITE
- REDIS_URL
- JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DELTA_SECONDS, JWT_REFRESH_EXPIRATION_DELTA_SECONDS
- CORS_ALLOWED_ORIGINS

## API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- Redoc: `http://localhost:8000/redoc/`
- OpenAPI JSON: `http://localhost:8000/swagger.json`

## Authentication
Endpoints:
- POST `/api/users/register/` (username, email, password)
- POST `/api/users/login/` (username, password) returns `refresh` & `access` tokens
- POST `/api/users/refresh/` (refresh token) returns new `access`
- POST `/api/users/logout/` (requires Bearer access token)

## Fraud Detection Logic
When a loan is submitted (`POST /api/loan/`):
- Flags if:
  - More than 3 loans in the past 24 hours
  - Requested amount exceeds NGN 5,000,000
  - User’s email domain is used by more than 10 different users
- Flagged loans:
  - Status set to `FLAGGED`
  - Visible to admins for review

## Testing
Run tests:
```bash
poetry run pytest --maxfail=1 --disable-warnings -q
```
- Unit tests: `tests/test_models.py`, `tests/test_services.py`
- API tests: `tests/test_api.py`

## CI/CD
Tests, linting, and type checks run via GitHub Actions in `.github/workflows/ci.yml`.

## Troubleshooting

### ALLOWED_HOSTS / DEBUG

If you see errors like `CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False` or `Invalid HTTP_HOST header`, ensure:

- DEBUG=True in your `.env`, or
- Add your host to `CORS_ALLOWED_ORIGINS` (e.g. `CORS_ALLOWED_ORIGINS=http://127.0.0.1:8000`), or
- Explicitly set `ALLOWED_HOSTS` in `.env` (e.g. `ALLOWED_HOSTS=127.0.0.1,localhost`).

### Missing database tables

If you encounter `no such table: loan_loanapplication` or similar, run:

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate --run-syncdb
```

### Redis connection issues

If you see `Error -3 connecting to redis`, caching will fallback to in-memory. Ensure your `REDIS_URL` is correct in `.env`. The cache is configured with `IGNORE_EXCEPTIONS=True` to prevent application failure.

### .env loading & virtual environment

Always run management commands from the project root so `.env` is loaded:

```bash
cp .env.example .env
source .venv/bin/activate  # if using venv
poetry install
poetry run python manage.py runserver
```

## License
MIT License