# inventario/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Retiro, Producto, Cliente

class RetiroForm(forms.ModelForm):
    class Meta:
        model = Retiro
        fields = ['monto', 'concepto']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 500.00'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pago a proveedor de refrescos'}),
        }
        labels = {
            'monto': 'Monto a Retirar',
            'concepto': 'Concepto del Retiro',
        }

class RegistroForm(forms.Form):
    nombre_empresa = forms.CharField(label="Nombre de tu Carnicería", max_length=100)
    username = forms.CharField(label="Nombre de Usuario (para iniciar sesión)", max_length=100)
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput)

    # --- Funciones de Validación ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")

        return cleaned_data

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Excluimos 'empresa' porque la asignaremos automáticamente
        fields = ['nombre', 'precio', 'stock', 'precio_mayoreo', 'mayoreo_desde_kg']
        labels = {
            'nombre': 'Nombre del Producto',
            'precio': 'Precio de Venta por Kg',
            'stock': 'Stock Inicial (Kg)',
            'precio_mayoreo': 'Precio de Mayoreo (Opcional)',
            'mayoreo_desde_kg': 'Aplicar Mayoreo desde (Kg)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_mayoreo': forms.NumberInput(attrs={'class': 'form-control'}),
            'mayoreo_desde_kg': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion']
        labels = {
            'nombre': 'Nombre del Cliente',
            'telefono': 'Teléfono',
            'direccion': 'Dirección (opcional)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3121234567'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej. Calle 123, Colonia Centro, Ciudad, Estado'}),
        }