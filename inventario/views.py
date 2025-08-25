import json
import requests
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from .models import Producto, Pedido, PedidoItem, Cliente, Retiro, Empresa, UserProfile, Arqueo
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import RetiroForm, RegistroForm, ProductoForm, ClienteForm
from django.db.models.functions import TruncHour
from .models import Arqueo

# =================================================================================
# VISTAS DE AUTENTICACIÓN Y PÁGINA PRINCIPAL
# =================================================================================

@transaction.atomic
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('pagina-inicio')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            nueva_empresa = Empresa.objects.create(nombre=data['nombre_empresa'])
            nuevo_usuario = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            UserProfile.objects.create(user=nuevo_usuario, empresa=nueva_empresa)
            login(request, nuevo_usuario)
            return redirect('pagina-inicio')
    else:
        form = RegistroForm()
    return render(request, 'inventario/registro.html', {'form': form})

@login_required
def pagina_inicio(request):
    return render(request, 'inventario/pagina_inicio.html')

# =================================================================================
# VISTAS DEL PUNTO DE VENTA (POS)
# =================================================================================

@login_required
def lista_productos(request, tipo_venta):
    empresa_del_usuario = request.user.profile.empresa

    # 1. Lógica para seleccionar cliente automáticamente si viene de un registro
    cliente_id_param = request.GET.get('cliente_id')
    if cliente_id_param:
        try:
            cliente_a_seleccionar = Cliente.objects.get(id=cliente_id_param, empresa=empresa_del_usuario)
            request.session['cliente_id'] = cliente_a_seleccionar.id # <-- CORRECCIÓN
        except Cliente.DoesNotExist:
            pass

    # Lógica de búsqueda de cliente, si no hay uno seleccionado automáticamente
    busqueda_cliente = request.GET.get('buscar_cliente', '')
    clientes_encontrados = None
    if busqueda_cliente:
        clientes_encontrados = Cliente.objects.filter(
            empresa=empresa_del_usuario,
            nombre__icontains=busqueda_cliente
        ).order_by('nombre')
    
    productos = Producto.objects.filter(empresa=empresa_del_usuario).order_by('nombre')
    
    # 2. Obtener el cliente seleccionado para la plantilla
    cliente_seleccionado = None
    cliente_id_sesion = request.session.get('cliente_id') # <-- CORRECCIÓN
    if cliente_id_sesion:
        try:
            cliente_seleccionado = Cliente.objects.get(id=cliente_id_sesion, empresa=empresa_del_usuario)
        except Cliente.DoesNotExist:
            del request.session['cliente_id']

    carrito = request.session.get('carrito', {})
    items_del_carrito = []
    total_carrito = Decimal('0.00')

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=int(producto_id), empresa=empresa_del_usuario)
        
        # Lógica de precio al mayoreo
        precio_unitario = producto.precio
        if producto.precio_mayoreo and producto.mayoreo_desde_kg and Decimal(str(cantidad)) >= producto.mayoreo_desde_kg:
            precio_unitario = producto.precio_mayoreo

        subtotal = precio_unitario * Decimal(str(cantidad))
        total_carrito += subtotal
        items_del_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })

    # Guardar en la sesión para la finalización de la venta
    request.session['total_venta'] = str(total_carrito)

    contexto = {
        'productos': productos,
        'busqueda_cliente': busqueda_cliente,
        'clientes_encontrados': clientes_encontrados,
        'cliente_seleccionado': cliente_seleccionado,
        'tipo_venta': tipo_venta,
        'items_del_carrito': items_del_carrito,
        'total_carrito': total_carrito,
    }
    
    return render(request, 'inventario/lista_productos.html', contexto)
@login_required
def agregar_al_carrito(request, producto_id):
    empresa_del_usuario = request.user.profile.empresa
    producto = get_object_or_404(Producto, id=producto_id, empresa=empresa_del_usuario)
    carrito = request.session.get('carrito', {})
    cantidad = carrito.get(str(producto_id), 0) + 1
    carrito[str(producto_id)] = cantidad
    request.session['carrito'] = carrito
    tipo_venta = request.session.get('tipo_venta', 'mostrador')
    return redirect('lista-productos', tipo_venta=tipo_venta)

@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
    request.session['carrito'] = carrito
    tipo_venta = request.session.get('tipo_venta', 'mostrador')
    return redirect('lista-productos', tipo_venta=tipo_venta)

@login_required
def actualizar_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    if request.method == 'POST':
        cantidad_str = request.POST.get('cantidad', '0')
        try:
            cantidad = float(cantidad_str)
            if cantidad > 0:
                carrito[producto_id_str] = cantidad
            else:
                if producto_id_str in carrito:
                    del carrito[producto_id_str]
        except ValueError:
            pass
    request.session['carrito'] = carrito
    tipo_venta = request.session.get('tipo_venta', 'mostrador')
    return redirect('lista-productos', tipo_venta=tipo_venta)

@login_required
def seleccionar_cliente(request, cliente_id):
    empresa_del_usuario = request.user.profile.empresa
    cliente = get_object_or_404(Cliente, id=cliente_id, empresa=empresa_del_usuario)
    request.session['cliente_id'] = cliente.id
    tipo_venta = request.session.get('tipo_venta', 'mostrador')
    return redirect('lista-productos', tipo_venta=tipo_venta)

@login_required
def quitar_cliente(request):
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    tipo_venta = request.session.get('tipo_venta', 'mostrador')
    return redirect('lista-productos', tipo_venta=tipo_venta)

# inventario/views.py

# inventario/views.py

# Asegúrate de tener estas importaciones al inicio de tu archivo views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Producto, Pedido, PedidoItem, Cliente
from decimal import Decimal

# ... (el resto de tus vistas) ...

@login_required
@transaction.atomic
def finalizar_venta(request, metodo_pago):
    empresa_del_usuario = request.user.profile.empresa
    carrito = request.session.get('carrito', {})
    tipo_venta = request.session.get('tipo_venta', 'mostrador')

    if not carrito:
        messages.warning(request, 'El carrito está vacío.')
        return redirect('pagina-inicio')

    if tipo_venta == 'domicilio' and 'cliente_id' not in request.session:
        messages.error(request, 'Para ventas a domicilio, es obligatorio seleccionar un cliente.')
        return redirect('lista-productos', tipo_venta=tipo_venta)

    cliente = None
    if 'cliente_id' in request.session:
        cliente = get_object_or_404(Cliente, id=request.session['cliente_id'], empresa=empresa_del_usuario)

    total_final = Decimal('0.00')
    items_para_procesar = []
    
    # Validar stock y calcular totales antes de crear el pedido
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=int(producto_id), empresa=empresa_del_usuario)
        cantidad_decimal = Decimal(str(cantidad))
        
        if producto.stock < cantidad_decimal:
            messages.error(request, f'No hay suficiente stock para {producto.nombre}. Venta cancelada.')
            return redirect('lista-productos', tipo_venta=tipo_venta)
        
        precio_unitario_final = producto.precio
        if producto.precio_mayoreo and producto.mayoreo_desde_kg and cantidad_decimal >= producto.mayoreo_desde_kg:
            precio_unitario_final = producto.precio_mayoreo

        items_para_procesar.append({
            'producto': producto, 
            'cantidad': cantidad_decimal, 
            'precio_unitario': precio_unitario_final
        })
        total_final += precio_unitario_final * cantidad_decimal

    # Crear el pedido en la base de datos
    pedido = Pedido.objects.create(
        empresa=empresa_del_usuario, 
        total=total_final, 
        cliente=cliente, 
        metodo_pago=metodo_pago
    )

    # Crear los items del pedido y descontar el stock
    for item in items_para_procesar:
        PedidoItem.objects.create(
            pedido=pedido, 
            producto=item['producto'], 
            cantidad=item['cantidad'], 
            precio_unitario=item['precio_unitario']
        )
        # Actualizar stock del producto
        producto_a_actualizar = item['producto']
        producto_a_actualizar.stock -= item['cantidad']
        producto_a_actualizar.save()

    # --- CAMBIO PRINCIPAL ---
    # Se elimina por completo el bloque try/except que intentaba imprimir desde el servidor.
    # La impresión ahora es responsabilidad del cliente (navegador).
    
    # Limpiar la sesión
    del request.session['carrito']
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    if 'tipo_venta' in request.session:
        del request.session['tipo_venta']
        
    messages.success(request, f'Venta #{pedido.id} registrada con éxito.')

    # Redirigir a la nueva página de éxito que activará la impresión en el cliente.
    return redirect('venta-exitosa', pedido_id=pedido.id)



# =================================================================================
# VISTAS DE GESTIÓN DE INVENTARIO
# =================================================================================

@login_required
def gestion_inventario(request):
    empresa_del_usuario = request.user.profile.empresa
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.empresa = empresa_del_usuario
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" añadido correctamente.')
            return redirect('gestion-inventario')
    else:
        form = ProductoForm()
    productos_de_la_empresa = Producto.objects.filter(empresa=empresa_del_usuario).order_by('nombre')
    contexto = {'form': form, 'productos': productos_de_la_empresa}
    return render(request, 'inventario/gestion_inventario.html', contexto)

@login_required
def editar_producto(request, producto_id):
    empresa_del_usuario = request.user.profile.empresa
    producto = get_object_or_404(Producto, id=producto_id, empresa=empresa_del_usuario)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('gestion-inventario')
    else:
        form = ProductoForm(instance=producto)
    contexto = {'form': form, 'producto': producto}
    return render(request, 'inventario/editar_producto.html', contexto)

@login_required
def eliminar_producto(request, producto_id):
    empresa_del_usuario = request.user.profile.empresa
    producto = get_object_or_404(Producto, id=producto_id, empresa=empresa_del_usuario)
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado correctamente.')
        return redirect('gestion-inventario')
    contexto = {'producto': producto}
    return render(request, 'inventario/producto_confirm_delete.html', contexto)

# =================================================================================
# VISTAS DE REPORTES Y GRÁFICAS
# =================================================================================

@login_required
def reporte_ventas(request):
    empresa_del_usuario = request.user.profile.empresa
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    hoy = timezone.localtime(timezone.now()).date()

    if fecha_inicio_str and fecha_fin_str:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        pedidos = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date__range=[fecha_inicio, fecha_fin]).order_by('-fecha')
        titulo_reporte = f"Ventas del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    else:
        fecha_inicio = hoy
        fecha_fin = hoy
        pedidos = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy).order_by('-fecha')
        titulo_reporte = f"Ventas del Día ({hoy.strftime('%d/%m/%Y')})"

    total_vendido = sum(p.total for p in pedidos)
    contexto = {
        'pedidos': pedidos,
        'total_vendido': total_vendido,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'titulo_reporte': titulo_reporte,
    }
    return render(request, 'inventario/reporte_ventas.html', contexto)

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=request.user.profile.empresa)
    contexto = {'pedido': pedido}
    return render(request, 'inventario/detalle_pedido.html', contexto)

@login_required
def dashboard_ventas(request):
    empresa_del_usuario = request.user.profile.empresa
    periodo = request.GET.get('periodo', 'hoy')
    hoy = timezone.localtime(timezone.now()).date()
    
    if periodo == 'mes':
        fecha_inicio = hoy - timedelta(days=29)
        titulo = "Ventas de los Últimos 30 Días"
        dias_a_mostrar = 30
    elif periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=6)
        titulo = "Ventas de los Últimos 7 Días"
        dias_a_mostrar = 7
    else:
        fecha_inicio = hoy
        titulo = "Ventas del Día de Hoy (por hora)"
        dias_a_mostrar = 1

    etiquetas, datos = [], []
    if dias_a_mostrar > 1:
        ventas_agrupadas = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date__range=[fecha_inicio, hoy]).values('fecha__date').annotate(total=Sum('total')).order_by('fecha__date')
        ventas_dict = {item['fecha__date'].strftime('%d/%m'): item['total'] for item in ventas_agrupadas}
        for i in range(dias_a_mostrar):
            fecha = fecha_inicio + timedelta(days=i)
            fecha_str = fecha.strftime('%d/%m')
            etiquetas.append(fecha_str)
            datos.append(float(ventas_dict.get(fecha_str, 0)))
    else:
        ventas_agrupadas = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy).annotate(hora=TruncHour('fecha')).values('hora').annotate(total=Sum('total')).order_by('hora')
        ventas_dict = {item['hora'].strftime('%H:00'): item['total'] for item in ventas_agrupadas}
        for i in range(24):
            hora_str = f"{i:02d}:00"
            etiquetas.append(hora_str)
            datos.append(float(ventas_dict.get(hora_str, 0)))

    contexto = {
        'titulo': titulo,
        'etiquetas_json': json.dumps(etiquetas),
        'datos_json': json.dumps(datos),
        'tipo_grafica': 'line' if dias_a_mostrar == 1 else 'bar' 
    }
    return render(request, 'inventario/dashboard.html', contexto)

# =================================================================================
# VISTAS DE GESTIÓN DE CAJA
# =================================================================================

@login_required
def gestion_caja(request):
    empresa_del_usuario = request.user.profile.empresa
    
    if request.method == 'POST':
        form = RetiroForm(request.POST)
        if form.is_valid():
            retiro = form.save(commit=False)
            retiro.empresa = empresa_del_usuario
            retiro.save()
            
            messages.success(request, 'Retiro registrado con éxito.')
            # CORRECCIÓN: Esta línea debe estar DENTRO del bloque if.
            return redirect('retiro-exitoso', retiro_id=retiro.id)
    else:
        # CORRECCIÓN: Este else se alinea con "if request.method == 'POST'".
        form = RetiroForm()
    
    # Esta parte del código se ejecuta para las solicitudes GET 
    # o si el formulario POST no fue válido.
    hoy = timezone.localtime(timezone.now()).date()
    retiros_de_hoy = Retiro.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy).order_by('-fecha')
    
    contexto = {
        'form': form,
        'retiros': retiros_de_hoy,
    }
    return render(request, 'inventario/gestion_caja.html', contexto)

# inventario/views.py

@login_required
def arqueo_caja(request):
    empresa_del_usuario = request.user.profile.empresa
    hoy = timezone.localtime(timezone.now()).date()
    
    ventas_efectivo = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy, metodo_pago='Efectivo')
    total_efectivo = ventas_efectivo.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    
    ventas_tarjeta = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy, metodo_pago='Tarjeta')
    total_tarjeta = ventas_tarjeta.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    
    retiros_hoy = Retiro.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy)
    total_retiros = retiros_hoy.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
    
    efectivo_esperado = total_efectivo - total_retiros
    total_ventas = total_efectivo + total_tarjeta

    # Generamos un Arqueo "temporal" para la visualización del ticket.
    # No lo guardamos en la base de datos, es solo para pasar datos.
    arqueo_temporal = Arqueo(
        empresa=empresa_del_usuario,
        fecha=hoy,
        ventas_efectivo=total_efectivo,
        ventas_tarjeta=total_tarjeta,
        retiros=total_retiros,
        efectivo_esperado=efectivo_esperado,
        monto_contado=Decimal('0.00'), # No hay monto contado todavía
        diferencia=Decimal('0.00') # No hay diferencia todavía
    )
    
    texto_arqueo = _generar_texto_ticket_arqueo(arqueo_temporal)
    
    contexto = {
        'fecha': hoy,
        'total_efectivo': total_efectivo,
        'total_tarjeta': total_tarjeta,
        'total_ventas': total_ventas,
        'total_retiros': total_retiros,
        'efectivo_esperado': efectivo_esperado,
        'texto_arqueo_json': json.dumps(texto_arqueo),
    }
    return render(request, 'inventario/arqueo_caja.html', contexto)

# =================================================================================
# VISTAS SOLO PARA IMPRESIÓN
# =================================================================================

@login_required
def reimprimir_pedido(request, pedido_id):
    empresa_del_usuario = request.user.profile.empresa
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa_del_usuario)
    tipo_venta = 'domicilio' if pedido.cliente and pedido.cliente.direccion else 'mostrador'
    
    texto_del_ticket = _generar_texto_ticket_venta(pedido)
    enviar_a_puente_impresora(request, texto_del_ticket)
    return redirect('detalle-pedido', pedido_id=pedido.id)


# =================================================================================
# FUNCIONES AUXILIARES (NO SON VISTAS)
# =================================================================================

# inventario/views.py

def enviar_a_puente_impresora(request, texto_ticket):
    # --- CORRECCIÓN: La IP ahora es 127.0.0.1 ---
    puente_url = "http://127.0.0.1:5000/print"
    try:
        payload = {'ticket_text': texto_ticket}
        # Timeout de 3 segundos para no bloquear la app si el puente no responde
        response = requests.post(puente_url, json=payload, timeout=3)

        if response.status_code == 200:
            # No mostraremos un mensaje de éxito en cada impresión para no saturar la pantalla.
            # El usuario asumirá que funcionó si el ticket se imprime.
            return True
        else:
            messages.error(request, f"Error del puente de impresión: {response.json().get('message', 'Error desconocido')}")
            return False
    except requests.exceptions.RequestException:
        messages.error(request, "No se pudo conectar con el servicio de impresión. Asegúrate de que el programa puente esté en ejecución.")
        return False

def _generar_texto_ticket_venta(pedido):
    empresa = pedido.empresa
    cliente = pedido.cliente
    items = pedido.items.all()
    
    tipo_venta = 'domicilio' if cliente and cliente.direccion else 'mostrador'
    
    texto_ticket = f"{empresa.nombre.center(42)}\n"
    texto_ticket += "LA MEJOR CARNE DE COLIMA\n".center(42)
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += f"TICKET: #{pedido.id:06d}\n"
    texto_ticket += f"FECHA: {timezone.localtime(pedido.fecha).strftime('%d/%m/%Y %H:%M:%S')}\n"
    texto_ticket += f"TIPO: {tipo_venta.upper()}\n"
    texto_ticket += f"CLIENTE: {cliente.nombre if cliente else 'Mostrador'}\n"

    if tipo_venta == 'domicilio' and cliente:
        if cliente.telefono:
            texto_ticket += f"TEL: {cliente.telefono}\n"
        if cliente.direccion:
            texto_ticket += f"DIRECCIÓN: {cliente.direccion}\n"
    
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += "CANT  DESCRIPCION       TOTAL\n"
    texto_ticket += "-" * 42 + "\n"
    
    for item in items:
        producto_display = item.producto.nombre
        es_mayoreo_aplicado = (item.producto.precio_mayoreo is not None and 
                               item.producto.mayoreo_desde_kg is not None and 
                               item.cantidad >= item.producto.mayoreo_desde_kg)

        if es_mayoreo_aplicado:
            producto_display = (producto_display[:11] + ' (M)') if len(producto_display) > 14 else producto_display + " (M)"
        else:
            producto_display = producto_display[:15]

        cantidad_str = f"{item.cantidad}kg"
        subtotal_item = item.cantidad * item.precio_unitario
        total_item_str = f"${subtotal_item:.2f}"
        linea = f"{cantidad_str:<5} {producto_display:<18} {total_item_str:>15}\n"
        texto_ticket += linea
    
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += f"{'TOTAL:':>32} ${pedido.total:.2f}\n"
    texto_ticket += f"{'PAGO:':>32} {pedido.metodo_pago.upper()}\n"
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += "¡GRACIAS POR SU PREFERENCIA!\n".center(42)
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"

    
    return texto_ticket

def _generar_texto_ticket_retiro(retiro):
    empresa = retiro.empresa
    fecha = timezone.localtime(retiro.fecha).strftime('%d/%m/%Y %H:%M:%S')
    
    texto_ticket = f"{empresa.nombre.center(42)}\n"
    texto_ticket += "COMPROBANTE DE RETIRO\n".center(42)
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += f"RETIRO: #{retiro.id:06d}\n"
    texto_ticket += f"FECHA: {fecha}\n"
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += f"CONCEPTO: {retiro.concepto}\n"
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += f"{'MONTO RETIRADO:':>32} ${retiro.monto:.2f}\n"
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += "FIRMA: __________________\n".center(42)
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    
    return texto_ticket

def _generar_texto_ticket_arqueo(arqueo):
    empresa = arqueo.empresa
    fecha_str = arqueo.fecha.strftime('%d/%m/%Y')
    
    # Manejamos el caso de que no haya un usuario asignado
    cerrado_por_nombre = arqueo.cerrado_por.username if arqueo.cerrado_por else "No especificado"
    
    texto_ticket = f"{empresa.nombre.center(42)}\n"
    texto_ticket += "COMPROBANTE DE CIERRE DE CAJA\n".center(42)
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += f"FECHA: {fecha_str}\n"
    # Usamos la nueva variable 'cerrado_por_nombre'
    texto_ticket += f"CERRADO POR: {cerrado_por_nombre}\n"
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += f"{'VENTAS EN EFECTIVO:':>32} ${arqueo.ventas_efectivo:.2f}\n"
    texto_ticket += f"{'VENTAS CON TARJETA:':>32} ${arqueo.ventas_tarjeta:.2f}\n"
    texto_ticket += f"{'TOTAL DE VENTAS:':>32} ${arqueo.ventas_efectivo + arqueo.ventas_tarjeta:.2f}\n"
    texto_ticket += "-" * 42 + "\n"
    texto_ticket += f"{'TOTAL DE RETIROS:':>32} -${arqueo.retiros:.2f}\n"
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += f"{'EFECTIVO ESPERADO:':>32} ${arqueo.efectivo_esperado:.2f}\n"
    texto_ticket += f"{'MONTO CONTADO:':>32} ${arqueo.monto_contado:.2f}\n"
    
    texto_ticket += "-" * 42 + "\n"
    
    diferencia_signo = "+" if arqueo.diferencia >= 0 else ""
    texto_ticket += f"{'DIFERENCIA:':>32} {diferencia_signo}${arqueo.diferencia:.2f}\n"
    
    texto_ticket += "=" * 42 + "\n"
    texto_ticket += "FIRMA: __________________\n".center(42)
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    texto_ticket += "\n"
    
    return texto_ticket

@login_required
def venta_exitosa(request, pedido_id):
    empresa_del_usuario = request.user.profile.empresa
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa_del_usuario)

    # Generamos el texto del ticket aquí para pasarlo a la plantilla
    texto_del_ticket = _generar_texto_ticket_venta(pedido)

    contexto = {
        'pedido': pedido,
        'texto_del_ticket_json': json.dumps(texto_del_ticket),
    }
    return render(request, 'inventario/venta_exitosa.html', contexto)

@login_required
def retiro_exitoso(request, retiro_id):
    empresa_del_usuario = request.user.profile.empresa
    retiro = get_object_or_404(Retiro, id=retiro_id, empresa=empresa_del_usuario)

    # Generamos el texto del ticket para pasarlo a la plantilla
    texto_del_ticket = _generar_texto_ticket_retiro(retiro)

    contexto = {
        'retiro': retiro,
        'texto_del_ticket_json': json.dumps(texto_del_ticket),
    }
    return render(request, 'inventario/retiro_exitoso.html', contexto)

@login_required
@transaction.atomic
def cerrar_caja(request):
    empresa_del_usuario = request.user.profile.empresa
    hoy = timezone.localtime(timezone.now()).date()

    if request.method == 'POST':
        monto_contado_str = request.POST.get('monto_contado')
        try:
            monto_contado = Decimal(monto_contado_str)
        except (ValueError, TypeError):
            messages.error(request, "Monto inválido. Por favor, ingresa un número válido.")
            return redirect('arqueo-caja')

        ventas_efectivo_hoy = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy, metodo_pago='Efectivo')
        total_efectivo = ventas_efectivo_hoy.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        
        ventas_tarjeta_hoy = Pedido.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy, metodo_pago='Tarjeta')
        total_tarjeta = ventas_tarjeta_hoy.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        
        retiros_hoy = Retiro.objects.filter(empresa=empresa_del_usuario, fecha__date=hoy)
        total_retiros = retiros_hoy.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')

        efectivo_esperado = total_efectivo - total_retiros
        diferencia = monto_contado - efectivo_esperado

        # Guardar el arqueo del día en la base de datos
        arqueo = Arqueo.objects.create(
            empresa=empresa_del_usuario,
            fecha=hoy,
            ventas_efectivo=total_efectivo,
            ventas_tarjeta=total_tarjeta,
            retiros=total_retiros,
            efectivo_esperado=efectivo_esperado,
            monto_contado=monto_contado,
            diferencia=diferencia,
            cerrado_por=request.user 
        )

        # Eliminar las ventas y retiros del día
        ventas_tarjeta_hoy.delete()
        ventas_efectivo_hoy.delete()
        retiros_hoy.delete()
        
        messages.success(request, "Caja cerrada exitosamente. Se ha generado un comprobante de cierre.")

        # Redirigir a la nueva página de éxito que activará la impresión
        return redirect('cierre-caja-exitoso', arqueo_id=arqueo.id)

    return redirect('arqueo-caja')

@login_required
def cierre_caja_exitoso(request, arqueo_id):
    empresa_del_usuario = request.user.profile.empresa
    arqueo = get_object_or_404(Arqueo, id=arqueo_id, empresa=empresa_del_usuario)

    # Generamos el texto del ticket aquí para pasarlo a la plantilla
    texto_del_ticket = _generar_texto_ticket_arqueo(arqueo)

    contexto = {
        'arqueo': arqueo,
        'texto_arqueo_json': json.dumps(texto_del_ticket),
    }
    return render(request, 'inventario/cierre_caja_exitoso.html', contexto)

@login_required
def reporte_arqueos(request):
    empresa_del_usuario = request.user.profile.empresa
    arqueos = Arqueo.objects.filter(empresa=empresa_del_usuario).order_by('-fecha')
    
    contexto = {
        'arqueos': arqueos,
    }
    return render(request, 'inventario/reporte_arqueos.html', contexto)

@login_required
def gestion_clientes(request):
    empresa_del_usuario = request.user.profile.empresa
    clientes = Cliente.objects.filter(empresa=empresa_del_usuario).order_by('nombre')
    contexto = {'clientes': clientes}
    return render(request, 'inventario/gestion_clientes.html', contexto)


@login_required
def agregar_cliente(request):
    empresa_del_usuario = request.user.profile.empresa
    telefono_autocompletar = request.GET.get('telefono', '')
    # Obtener la URL a la que se debe redirigir después de guardar
    next_url = request.GET.get('next', 'gestion-clientes') 
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.empresa = empresa_del_usuario
            cliente.save()
            messages.success(request, f'Cliente "{cliente.nombre}" agregado correctamente.')

            # Redirigir a la URL de origen si existe, de lo contrario, a la gestión de clientes
            # La variable next_url contendrá la URL de la página de venta
            if next_url != 'gestion-clientes':
                return redirect(f'{next_url}?cliente_id={cliente.id}')
            
            return redirect(next_url)
    else:
        form = ClienteForm(initial={'telefono': telefono_autocompletar})
    
    contexto = {'form': form, 'titulo': 'Agregar Nuevo Cliente'}
    return render(request, 'inventario/agregar_editar_cliente.html', contexto)

@login_required
def editar_cliente(request, cliente_id):
    empresa_del_usuario = request.user.profile.empresa
    cliente = get_object_or_404(Cliente, id=cliente_id, empresa=empresa_del_usuario)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{cliente.nombre}" actualizado correctamente.')
            return redirect('gestion-clientes')
    else:
        form = ClienteForm(instance=cliente)
    contexto = {'form': form, 'cliente': cliente, 'titulo': 'Editar Cliente'}
    return render(request, 'inventario/agregar_editar_cliente.html', contexto)

@login_required
def eliminar_cliente(request, cliente_id):
    empresa_del_usuario = request.user.profile.empresa
    cliente = get_object_or_404(Cliente, id=cliente_id, empresa=empresa_del_usuario)
    if request.method == 'POST':
        nombre_cliente = cliente.nombre
        cliente.delete()
        messages.success(request, f'Cliente "{nombre_cliente}" eliminado correctamente.')
        return redirect('gestion-clientes')
    contexto = {'cliente': cliente}
    return render(request, 'inventario/cliente_confirm_delete.html', contexto)