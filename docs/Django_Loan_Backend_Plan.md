# Django Loan Backend Plan

This plan outlines the complete approach to designing and building a Django-based loan application backend with a focus on clean architecture, fraud detection, test coverage, robust error handling, security, and scalable practices.

---

## Assumptions

1. **Technology Stack**: Python ≥3.9, Django ≥4.0, Django REST Framework (DRF), PostgreSQL ≥14, Redis (for caching), Celery (for async tasks).
2. **Authentication**: Token-based authentication with refresh mechanism using DRF (e.g., Simple JWT).
3. **Deployment**: Dockerized environment; CI/CD via GitHub Actions.
4. **Environment**: `.env` file per environment (dev, staging, prod) using `django-environ`.
5. **Branching Strategy**: `develop` branch for staging, `main` branch for production.
6. **Standards**: Strict typing, PEP8, docstrings, structured logging, HTTP and DB error handling.

---

## Project Structure

```
loan-backend/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── README.md
├── Actions_n_Tasks.md
├── loan_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── loan/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── fraud/
│   ├── models.py
│   ├── services.py
│   ├── signals.py
│   └── serializers.py
├── tests/
│   ├── conftest.py
│   └── test_*.py
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Phase Highlights

- **Auth**: DRF token authentication with refresh mechanism.
- **Fraud Detection**: Rule-based flagging (e.g., high amount, duplicate domain usage).
- **Caching**: Redis-backed response and logic caching.
- **Testing**: Full coverage including edge/failure cases.
- **CI/CD**: GitHub Actions pipeline.
- **Error Handling**: Proper HTTP + DB + Redis error mapping with logging.

---

## Final Submission Requirements

Include a **README.md** file that describes:

- Project overview and tech stack
- Setup steps (`git clone`, `.env`, `docker-compose up`)
- Environment variable definitions (`.env.example`)
- How to access the API via `localhost:8000`
- How to run tests (`docker-compose exec web pytest`)
- Where to find API documentation (e.g., Swagger at `/swagger/`)
- Authentication instructions (how to obtain and refresh tokens)

---

*End of Plan*
