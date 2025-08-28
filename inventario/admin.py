# inventario/admin.py
from django.contrib import admin
from django.db.models import Sum
from datetime import datetime, timedelta

# --- 1. IMPORTACIONES NECESARIAS ---
# Modelos de tu aplicación
from .models import Empresa, UserProfile, Pedido, Cliente, Producto, Retiro
# Modelos de Autenticación de Django (¡ESTA PARTE FALTABA!)
from django.contrib.auth.models import User, Group
# Paneles de Admin de Autenticación de Django (¡Y ESTA!)
from django.contrib.auth.admin import UserAdmin, GroupAdmin


# -----------------------------------------------------------------------------
# 2. Personalización de la vista de Empresas (Tus Clientes)
# -----------------------------------------------------------------------------
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'giro', 'dueño_de_la_cuenta', 'fecha_registro', 'total_ventas')
    search_fields = ('nombre', 'giro', 'userprofile__user__email')
    list_filter = ('giro',)

    def dueño_de_la_cuenta(self, obj):
        profile = UserProfile.objects.filter(empresa=obj).first()
        return profile.user.email if profile else "No asignado"
    
    def fecha_registro(self, obj):
        profile = UserProfile.objects.filter(empresa=obj).first()
        if profile:
            return profile.user.date_joined.strftime("%d/%m/%Y")
        return "N/A"

    def total_ventas(self, obj):
        total = Pedido.objects.filter(empresa=obj).aggregate(total_sum=Sum('total'))['total_sum']
        return f"${total or 0:,.2f}"

    dueño_de_la_cuenta.short_description = 'Email del Dueño'
    fecha_registro.short_description = 'Fecha de Registro'
    total_ventas.short_description = 'Ventas Totales'


# -----------------------------------------------------------------------------
# 3. Creación del Panel de Admin Personalizado con Métricas
# -----------------------------------------------------------------------------
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_mes = hoy.replace(day=1)

        total_empresas = Empresa.objects.count()
        nuevas_semana = Empresa.objects.filter(userprofile__user__date_joined__gte=inicio_semana).count()
        nuevas_mes = Empresa.objects.filter(userprofile__user__date_joined__gte=inicio_mes).count()
        total_pedidos = Pedido.objects.count()
        monto_total_vendido = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0

        stats = {
            'total_empresas': total_empresas,
            'nuevas_semana': nuevas_semana,
            'nuevas_mes': nuevas_mes,
            'total_pedidos': total_pedidos,
            'monto_total_vendido': f"${monto_total_vendido:,.2f}",
        }
        
        extra_context = extra_context or {}
        extra_context['growth_stats'] = stats
        
        return super().index(request, extra_context)

# Reemplaza el admin por defecto con nuestro admin personalizado
admin.site = MyAdminSite()


# -----------------------------------------------------------------------------
# 4. Registro de TODOS los modelos en el nuevo admin.site
# -----------------------------------------------------------------------------

# Registra los modelos de autenticación de Django para que aparezcan en tu panel.
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)

# Registra el modelo 'Empresa' usando la clase personalizada 'EmpresaAdmin'.
admin.site.register(Empresa, EmpresaAdmin)

# Registra los otros modelos de tu aplicación.
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(Retiro)
admin.site.register(UserProfile)