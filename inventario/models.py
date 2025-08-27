from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Necesario para el futuro
from django.contrib.auth.models import User
from decimal import Decimal

# Se define PRIMERO, porque todos los demás modelos se conectarán a este.
class Empresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # --- NUEVOS CAMPOS ---
    UNIDAD_CHOICES = [
        ('kg', 'Kilogramo (kg)'),
        ('unidad', 'Unidad (u)'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Costo de adquisición del producto por unidad/kg.")
    
    # El stock ahora puede ser nulo para servicios que no lo requieren
    stock = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    
    precio_mayoreo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mayoreo_desde_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    
    # Define si se vende por peso o por pieza/servicio
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='kg')
    
    # Define si este producto debe descontar existencias
    requiere_stock = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) # <-- NUEVO: El cliente pertenece a una empresa
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20) # Ya no necesita ser 'unique' globalmente
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"

class Arqueo(models.Model): # <-- MOVIMOS ARQUEO ANTES DE PEDIDO Y RETIRO
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    ventas_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ventas_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    retiros = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    efectivo_esperado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_contado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    cerrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Arqueo del {self.fecha.strftime('%d/%m/%Y')} - {self.empresa.nombre}"

class Pedido(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    METODO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=10, choices=METODO_PAGO_CHOICES, default='Efectivo')
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cambio_entregado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # --- CAMBIO IMPORTANTE ---
    arqueo = models.ForeignKey(Arqueo, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')

    def __str__(self):
        return f"Pedido #{self.id} del {self.fecha.strftime('%d/%m/%Y')} - Total: ${self.total}"

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} kg de {self.producto.nombre}"

class Retiro(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)
    # --- CAMBIO IMPORTANTE ---
    arqueo = models.ForeignKey(Arqueo, on_delete=models.SET_NULL, null=True, blank=True, related_name='retiros_del_arqueo')


    def __str__(self):
        return f"Retiro de ${self.monto} el {self.fecha.strftime('%d/%m/%Y')} - {self.concepto}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Perfil de {self.user.username} en {self.empresa.nombre}"