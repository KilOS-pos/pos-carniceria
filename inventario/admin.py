# inventario/admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import Empresa, UserProfile, Pedido, Cliente, Producto, Retiro
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. Personalización de la vista de Empresas (Tus Clientes)
# -----------------------------------------------------------------------------
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """
    Esta clase personaliza cómo ves la lista de tus clientes (las empresas).
    """
    list_display = ('nombre', 'giro', 'dueño_de_la_cuenta', 'fecha_registro', 'total_ventas')
    search_fields = ('nombre', 'giro', 'userprofile__user__email')
    list_filter = ('giro',)

    def dueño_de_la_cuenta(self, obj):
        # Busca el perfil de usuario asociado a esta empresa y devuelve su email.
        profile = UserProfile.objects.filter(empresa=obj).first()
        return profile.user.email if profile else "No asignado"
    
    def fecha_registro(self, obj):
        # Muestra la fecha en que el dueño se registró.
        profile = UserProfile.objects.filter(empresa=obj).first()
        if profile:
            return profile.user.date_joined.strftime("%d/%m/%Y")
        return "N/A"

    def total_ventas(self, obj):
        # Calcula y muestra el total vendido por esta empresa.
        total = Pedido.objects.filter(empresa=obj).aggregate(total_sum=Sum('total'))['total_sum']
        return f"${total or 0:,.2f}"

    # Añade un encabezado a la columna calculada.
    dueño_de_la_cuenta.short_description = 'Email del Dueño'
    fecha_registro.short_description = 'Fecha de Registro'
    total_ventas.short_description = 'Ventas Totales'


# -----------------------------------------------------------------------------
# 2. Añadir métricas de crecimiento al panel principal del admin
# -----------------------------------------------------------------------------
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        """
        Sobrescribimos la página principal del admin para inyectar nuestras estadísticas.
        """
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_mes = hoy.replace(day=1)

        # Conteo total de empresas (tus clientes)
        total_empresas = Empresa.objects.count()
        
        # Nuevas empresas esta semana y este mes
        nuevas_semana = Empresa.objects.filter(userprofile__user__date_joined__gte=inicio_semana).count()
        nuevas_mes = Empresa.objects.filter(userprofile__user__date_joined__gte=inicio_mes).count()
        
        # Conteo total de ventas y monto total
        total_pedidos = Pedido.objects.count()
        monto_total_vendido = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0

        # Prepara el contexto para la plantilla
        stats = {
            'total_empresas': total_empresas,
            'nuevas_semana': nuevas_semana,
            'nuevas_mes': nuevas_mes,
            'total_pedidos': total_pedidos,
            'monto_total_vendido': f"${monto_total_vendido:,.2f}",
        }
        
        if extra_context is None:
            extra_context = {}
        extra_context['growth_stats'] = stats
        
        return super().index(request, extra_context)

# Reemplaza el admin por defecto con nuestro admin personalizado
admin.site = MyAdminSite()

# Registra los otros modelos para que puedas verlos en el admin (opcional)
# Puedes descomentar los que quieras gestionar desde tu panel.
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(Retiro)
admin.site.register(UserProfile)