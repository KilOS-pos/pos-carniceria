# Usa una imagen base de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo a /app
WORKDIR /app

# Copia los archivos de requerimientos e instálalos
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia todo el código del proyecto al contenedor
COPY . .

# Establece el directorio de trabajo a la subcarpeta de tu proyecto Django
WORKDIR /app/carniceria_web

# Expone el puerto 8000 (el que usará Gunicorn)
EXPOSE 8000

# Comando para correr la aplicación con Gunicorn
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000