# inventario/admin.py
from django.contrib import admin
from .models import Producto, Pedido, PedidoItem, Cliente, Retiro, UserProfile, Empresa

# Register your models here.
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(PedidoItem)
admin.site.register(Retiro)
admin.site.register(UserProfile)
admin.site.register(Empresa)