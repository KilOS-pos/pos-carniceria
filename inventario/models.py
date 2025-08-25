from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Necesario para el futuro
from django.contrib.auth.models import User

# Se define PRIMERO, porque todos los demás modelos se conectarán a este.
class Empresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) # <-- NUEVO: El producto pertenece a una empresa
    nombre = models.CharField(max_length=100) # Ya no necesita ser 'unique' globalmente
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.DecimalField(max_digits=10, decimal_places=3)
    precio_mayoreo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mayoreo_desde_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) # <-- NUEVO: El cliente pertenece a una empresa
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20) # Ya no necesita ser 'unique' globalmente
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"

class Pedido(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) # <-- NUEVO: El pedido pertenece a una empresa
    METODO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=10, choices=METODO_PAGO_CHOICES, default='Efectivo')

    def __str__(self):
        return f"Pedido #{self.id} del {self.fecha.strftime('%d/%m/%Y')} - Total: ${self.total}"

class PedidoItem(models.Model):
    # Este modelo no necesita el campo 'empresa' porque lo hereda a través del 'pedido'
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} kg de {self.producto.nombre}"

class Retiro(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) # <-- NUEVO: El retiro pertenece a una empresa
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)

    def __str__(self):
        return f"Retiro de ${self.monto} el {self.fecha.strftime('%d/%m/%Y')} - {self.concepto}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Perfil de {self.user.username} en {self.empresa.nombre}"