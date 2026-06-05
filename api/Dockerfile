# Stage 1 : builder 
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2 : runtime 
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copie les dépendances installées depuis le builder
COPY --from=builder /install /usr/local

# Copie uniquement le code source
COPY api/ ./api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]