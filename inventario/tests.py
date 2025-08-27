from django.test import TestCase
from django.contrib.auth.models import User
from .models import Empresa, Producto, Pedido, PedidoItem, Cliente
from decimal import Decimal

class InventarioTestCase(TestCase):
    def setUp(self):
        # Crear datos básicos para las pruebas
        self.empresa = Empresa.objects.create(nombre="Carnicería de Prueba")
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.producto1 = Producto.objects.create(
            empresa=self.empresa,
            nombre="Arrachera",
            precio="250.00",
            costo="180.00",
            stock="50.000",
            unidad_medida='kg',
            requiere_stock=True
        )
        self.producto2 = Producto.objects.create(
            empresa=self.empresa,
            nombre="Refresco",
            precio="20.00",
            costo="12.00",
            stock="100.000",
            unidad_medida='unidad',
            requiere_stock=True
        )
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nombre="Cliente de Prueba",
            telefono="1234567890"
        )

    def test_creacion_producto(self):
        """Prueba que un producto se crea correctamente con sus valores."""
        arrachera = Producto.objects.get(nombre="Arrachera")
        self.assertEqual(arrachera.empresa.nombre, "Carnicería de Prueba")
        self.assertEqual(arrachera.precio, Decimal('250.00'))

    def test_finalizar_venta_simple(self):
        """Prueba que una venta simple actualiza el stock y crea el pedido."""
        # Estado inicial del stock
        stock_inicial = self.producto1.stock

        # Simular una venta
        pedido = Pedido.objects.create(
            empresa=self.empresa,
            cliente=self.cliente,
            total="500.00",
            metodo_pago='Efectivo'
        )
        PedidoItem.objects.create(
            pedido=pedido,
            producto=self.producto1,
            cantidad="2.000", # 2 kg
            precio_unitario="250.00"
        )

        # Actualizar stock (simulando la lógica de la vista)
        self.producto1.stock -= Decimal('2.000')
        self.producto1.save()

        # Refrescar el objeto desde la base de datos
        self.producto1.refresh_from_db()

        # Comprobar los resultados
        self.assertEqual(pedido.items.count(), 1)
        self.assertEqual(pedido.total, Decimal('500.00'))
        self.assertEqual(self.producto1.stock, stock_inicial - Decimal('2.000'))