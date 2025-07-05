FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false --local && \
    poetry install --no-dev
COPY . /app
EXPOSE 8000
CMD ["gunicorn", "loan_app.wsgi:application", "--bind", "0.0.0.0:8000"]