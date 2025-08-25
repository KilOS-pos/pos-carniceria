# inventario/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URL Principal
    path('', views.pagina_inicio, name='pagina-inicio'),

    # Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='inventario/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Punto de Venta (POS)
    path('pos/<str:tipo_venta>/', views.lista_productos, name='lista-productos'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar-al-carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar-del-carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar-cantidad'),
    path('cliente/seleccionar/<int:cliente_id>/', views.seleccionar_cliente, name='seleccionar-cliente'),
    path('cliente/quitar/', views.quitar_cliente, name='quitar-cliente'),
    path('venta/finalizar/<str:metodo_pago>/', views.finalizar_venta, name='finalizar-venta'),

    # Gestión de Inventario
    path('inventario/', views.gestion_inventario, name='gestion-inventario'),
    path('inventario/editar/<int:producto_id>/', views.editar_producto, name='editar-producto'),
    path('inventario/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar-producto'),

    # Reportes y Gráficas
    path('reportes/', views.reporte_ventas, name='reporte-ventas'),
    path('reportes/pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle-pedido'),
    path('reportes/pedido/<int:pedido_id>/reimprimir/', views.reimprimir_pedido, name='reimprimir-pedido'),
    path('dashboard/', views.dashboard_ventas, name='dashboard'),

    # Gestión de Caja
    path('caja/', views.gestion_caja, name='gestion-caja'),
    path('arqueo/', views.arqueo_caja, name='arqueo-caja'),
    path('arqueo/imprimir/', views.imprimir_arqueo_caja, name='imprimir-arqueo-caja'),
]