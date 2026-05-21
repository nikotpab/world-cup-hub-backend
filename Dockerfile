# ---- Etapa 1: Builder ----
FROM python:3.11-alpine AS builder
WORKDIR /install

# Instalar dependencias del SO necesarias para compilar (ej: psycopg2, gevent)
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---- Etapa 2: Runner ----
FROM python:3.11-alpine
WORKDIR /app

# Instalar solo dependencias runtime (libpq para postgres)
RUN apk add --no-cache libpq

# Copiar paquetes compilados desde el builder
COPY --from=builder /install /usr/local
COPY . .

# Seguridad: Ejecutar como usuario no root
RUN adduser -D nonrootuser
USER nonrootuser

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gevent", "-w", "4", "--timeout", "120", "run:app"]
