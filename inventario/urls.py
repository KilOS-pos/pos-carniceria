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
    path('venta/exitosa/<int:pedido_id>/', views.venta_exitosa, name='venta-exitosa'),
    path('caja/retiro/exitoso/<int:retiro_id>/', views.retiro_exitoso, name='retiro-exitoso'),
    path('caja/cerrar/', views.cerrar_caja, name='cerrar-caja'),
    path('caja/cierre/exitoso/<int:arqueo_id>/', views.cierre_caja_exitoso, name='cierre-caja-exitoso'),
    path('reportes/arqueos/', views.reporte_arqueos, name='reporte-arqueos'),
    path('clientes/', views.gestion_clientes, name='gestion-clientes'),
    path('clientes/agregar/', views.agregar_cliente, name='agregar-cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar-cliente'),
    path('clientes/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar-cliente'),
]