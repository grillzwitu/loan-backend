# Dockerfile for Loan Backend
# Base image using Python 3.12 slim variant for minimal footprint
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Ensure Python output is flushed immediately to the container logs
ENV PYTHONUNBUFFERED 1

# Copy dependency definitions for Poetry
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project dependencies (without dev dependencies)
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false --local && \
    poetry install --no-dev

# Copy application source code into the container
COPY . /app

# Expose port 8000 for serving the application
EXPOSE 8000

# Launch Gunicorn WSGI server to serve the Django app
CMD ["gunicorn", "loan_app.wsgi:application", "--bind", "0.0.0.0:8000"]