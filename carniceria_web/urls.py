# carniceria_web/urls.py

from django.contrib import admin
from django.urls import path, include  # Importamos 'include'

urlpatterns = [
    path('admin/', admin.site.urls),          # Esta línea es para el panel de admin
    path('', include('inventario.urls')),   # Esta conecta con tu lista de productos
]