# Action Items & Tasks

This outlines step-by-step actions for building and deploying a Django-based loan application backend with CI/CD, fraud detection, caching, testing, and robust error handling.

---

## 1. Project Initialization

- GitHub repo with `develop` and `main` branches
- Create and configure:
  - `.env.example`, `README.md`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`

---

## 2. Poetry Setup (`pyproject.toml`)

Includes Django, DRF, Redis, PostgreSQL, and dev tooling. Auth uses **token-based mechanism with refresh support** (e.g., Simple JWT or custom).

---

## 3. Docker & Compose

- Dockerize Django backend
- Include Redis and PostgreSQL containers
- Use `.env` for DB and Redis config
- Docker Compose manages all services locally

---

## 4. Django Configuration

- Use `django-environ` to load `.env`
- Setup DRF, CORS, logging, Swagger
- Add Redis cache settings

---

## 5. Data Models & Migrations

- `LoanApplication` and `FraudFlag` models with methods
- Signals to create flags
- Run migrations: `makemigrations` + `migrate`

---

## 6. API Endpoints

- Auth: register, login, logout with **refresh token support**
- Loan: create, list, retrieve
- Admin: approve, reject, flag

---

## 7. Fraud Detection Logic

- Trigger on loan creation
- Log reasons and status
- Rule-based flagging and caching

---

## 8. Caching Strategy

- Redis: fraud checks, loan lists, domain checks, OpenAPI schema
- Setup in settings with `django-redis`

---

## 9. CI/CD Pipeline

- GitHub Actions: build, test, lint, type-check
- Deploy `develop` to staging, `main` to production

---

## 10. Testing Strategy

- Unit tests, integration tests, edge case tests
- Run with `pytest --cov`
- Add test instructions to README

---

## 11. Logging & Error Handling

- Use Python `logging` module with proper levels
- Use DRF exception classes for HTTP handling
- Capture DB and Redis failures explicitly

---

## 12. README Submission Checklist

Ensure your `README.md` includes:

- ✅ Project summary
- ✅ Setup steps with Docker
- ✅ How to access app (`http://localhost:8000`)
- ✅ Example `.env` config
- ✅ Test instructions
- ✅ API documentation (e.g. Swagger URL)
- ✅ Auth guide (token + refresh usage)

---

*End of Tasks*
