# 1. Partimos de una imagen oficial con Python 3.12 ya instalado.
FROM python:3.12-slim

# 2. Carpeta de trabajo dentro del contenedor.
WORKDIR /app

# 3. Instalamos las librerías (Flask, gunicorn y las de Google Cloud).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos el código: el módulo de facturación y la aplicación web.
COPY src ./src
COPY app ./app
ENV PYTHONPATH=/app/src:/app/app

# 5. Cloud Run nos dice en qué puerto escuchar con la variable PORT.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
