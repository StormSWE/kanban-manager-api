# ========= Base Image =========
FROM python:3.12-slim

# ========= Work Directory =========
WORKDIR /app

# ========= Environment Variables =========
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ========= Install System Dependencies =========
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ========= Install Python Dependencies =========
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ========= Copy the Project =========
COPY . /app

# ========= Collect Static Files =========
RUN mkdir -p /app/static
RUN python manage.py collectstatic --noinput || true

# ========= Gunicorn Command =========
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
