# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de tu aplicación
COPY . .

# Expone el puerto 8000
EXPOSE 8000

# Comando para correr la aplicación con Gunicorn
CMD gunicorn carniceria_web.config.wsgi:application --bind 0.0.0.0:8000