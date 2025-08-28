# settings.py
"""
Django settings for carniceria_web project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv # Para leer el archivo .env

# --- 1. CONFIGURACIÓN DE RUTAS Y VARIABLES DE ENTORNO ---

# Construye rutas dentro del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables de entorno desde el archivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))


# --- 2. CONFIGURACIÓN DE SEGURIDAD Y DEPURACIÓN ---

# NUNCA subas tu SECRET_KEY a GitHub. Se lee desde el archivo .env.
SECRET_KEY = os.getenv('SECRET_KEY')

# El modo DEBUG debe ser FALSO en producción para mayor seguridad.
# Lo controlamos con una variable de entorno. Si no existe, es Falso.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# En producción, aquí debe ir el dominio de tu app (ej. 'kilos.onrender.com').
# Render lo configura automáticamente si usas una variable de entorno.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# --- 3. DEFINICIÓN DE APLICACIONES ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para servir archivos estáticos eficientemente
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_otp',
    'django_otp.plugins.otp_static',
    'widget_tweaks',
    'inventario',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise Middleware debe ir justo después de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # OTP Middleware DEBE ir después de AuthenticationMiddleware
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carniceria_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'carniceria_web.wsgi.application'


# --- 4. BASE DE DATOS ---

# Configuración flexible que usa la URL de Render en producción
# y tu base de datos local (sqlite) en desarrollo.
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}')
    )
}


# --- 5. VALIDACIÓN DE CONTRASEÑAS E INTERNACIONALIZACIÓN ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True


# --- 6. ARCHIVOS ESTÁTICOS (CSS, JAVASCRIPT) ---

STATIC_URL = 'static/'
# Directorio donde se recolectarán todos los archivos estáticos para producción.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Almacenamiento optimizado para producción con WhiteNoise.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- 7. CONFIGURACIONES ADICIONALES ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# --- 8. AJUSTES DE SEGURIDAD PARA PRODUCCIÓN ---
# Estos ajustes se activan automáticamente cuando DEBUG = False

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True