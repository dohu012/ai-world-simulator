FROM python:3.12.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml .
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
RUN pip install --no-cache-dir .
USER 65532:65532
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=10.0.0.0/8"]
