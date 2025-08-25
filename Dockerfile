# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo a /app
WORKDIR /app

# Copia los archivos de requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu aplicación
COPY . .

# Establece el directorio de trabajo a la subcarpeta de tu proyecto Django
WORKDIR /app/carniceria_web

# Expone el puerto 8000
EXPOSE 8000

# Comando para correr la aplicación con Gunicorn
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000