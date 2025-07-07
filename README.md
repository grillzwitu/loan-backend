# Django Loan Backend

**A Django-based backend service for managing loan applications with fraud detection and admin workflows.**

## Table of Contents
- [Technologies & Dependencies](#technologies--dependencies)
- [Project Structure](#project-structure)
- [Assumptions & Endpoint Behavior](#assumptions--endpoint-behavior)
- [Fraud Detection Rules](#fraud-detection-rules)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Setup & Running](#setup--running)

## Technologies & Dependencies

### Main Dependencies
- Django 5.2
- Django REST Framework
- Simple JWT authentication ([`djangorestframework-simplejwt`](https://pypi.org/project/djangorestframework-simplejwt/))
- Swagger/OpenAPI docs ([`drf-yasg`](https://pypi.org/project/drf-yasg/))
- CORS handling ([`django-cors-headers`](https://pypi.org/project/django-cors-headers/))
- Redis caching ([`django-redis`](https://pypi.org/project/django-redis/)) with locmem fallback
- PostgreSQL adapter ([`psycopg2`](https://pypi.org/project/psycopg2/)) and SQLite
- 12-factor configuration ([`django-environ`](https://pypi.org/project/django-environ/))
- Gunicorn WSGI HTTP server ([`gunicorn`](https://pypi.org/project/gunicorn/))  
- WhiteNoise static file serving ([`whitenoise`](https://pypi.org/project/whitenoise/))

### Development Dependencies
- pytest, pytest-django
- flake8
- mypy, django-stubs
- Black, isort

## Project Structure

```
.
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── loan_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── apps.py
│   ├── urls.py
│   └── views.py
├── loan/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   └── views.py
├── fraud/
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   └── services.py
├── tests/
│   ├── unit/           # Unit tests (models, services, settings, caching, logging, permission, fraud)
│   │   └── ...         # Organized into subfolders by category
│   ├── integration/    # Integration tests (API flows, admin actions, fraud scenarios)
│   │   └── ...         # Organized into subfolders: api, admin, fraud
│   └── conftest.py     # Global pytest fixtures and configuration
└── README.md
```

**Directory Descriptions:**
- `loan_app/`: Core Django project settings and configuration ([`loan_app/settings.py`](loan_app/settings.py:18)).
- `users/`: Handles user registration and JWT token endpoints ([`users/views.py`](users/views.py:1)).
- `loan/`: Manages the `LoanApplication` model and related API logic ([`loan/models.py`](loan/models.py:10), [`loan/views.py`](loan/views.py:173)).
- `fraud/`: Implements fraud detection rules and manual flagging services ([`fraud/services.py`](fraud/services.py:26)).
- `tests/`: Unit and integration tests covering all functionality.

## Assumptions & Endpoint Behavior

**Registration & Authentication:**
- `POST /register/`: Create new user, returns JWT tokens.
- `POST /api/token/`: Obtain access and refresh tokens.
- `POST /api/token/refresh/`: Refresh access token.
- `POST /logout/`: Invalidate refresh tokens.

**Loan Application Workflow:**
1. **Creation** (`POST /loans/`):
    - New `LoanApplication` is created with `status = "PENDING"` and includes a `purpose` (string describing the loan purpose).
    - Fraud checks triggered in [`fraud/services.py`](fraud/services.py:26).
2. **Auto-Approval**:  
   - If no fraud flags **and** `amount ≤ 1_000_000`, loan is auto-set to `APPROVED`.  
3. **High-Value Review**:  
   - If no fraud flags but `amount > 1_000_000`, loan remains `PENDING` for admin review.  
4. **Flagging**:  
   - If any fraud rule fails, `status = "FLAGGED"`.  
   - Flags stored in `FraudFlag` and a mock notification is sent.  
5. **User Withdrawal** (`POST /loans/{id}/withdraw/`):  
   - Only the original user can withdraw their `PENDING` loan; returns `204 NO CONTENT`.  
   - Withdrawn loans cannot be modified thereafter.  
6. **Admin Actions** (`/approve/`, `/reject/`, `/flag/`):  
   - Admins can approve, reject, or flag loans in `PENDING` or `FLAGGED` states.  
   - HTTP `403 FORBIDDEN` if loan is in any other state (e.g., `WITHDRAWN`).

## Fraud Detection Rules
- **Overuse**: More than 3 loans in the past 24 hours.  
- **High Amount**: `amount > 5_000_000`.  
- **Email Domain**: More than 10 users share the same email domain.  

See the full implementation in [`fraud/services.py`](fraud/services.py:26).

## Testing
- **Unit Tests**: run with `pytest tests/unit`
- **Integration Tests**: run with `pytest tests/integration`
- **All Tests**: run full suite with `pytest --maxfail=1 --disable-warnings -q`

## API Documentation
- **Swagger UI**: `GET /swagger/`  
- **Redoc**: `GET /redoc/`  
- **OpenAPI JSON**: `GET /swagger.json`

## Setup & Running

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/loan-backend.git
   ```
2. Navigate into the project directory:
   ```bash
   cd loan-backend
   ```
3. Copy `.env.example` to `.env` and configure environment variables:
   ```bash
   cp .env.example .env
   ```
4. Install dependencies:
   ```bash
   poetry install
   ```
5. Apply database migrations:
   ```bash
   poetry run python manage.py migrate
   ```
6. Start the development server:
   ```bash
   poetry run python manage.py runserver
   ```

### Docker
1. Update the Poetry lock file:  
   ```bash
   poetry lock
   ```  
2. Build and start containers:
   ```
   docker-compose up --build
   ```  
3. The API will be available at `http://localhost:8000/`.
4. Stop services with:
   ```
   docker-compose down
   ```

Enjoy developing and testing with the Loan Backend service!