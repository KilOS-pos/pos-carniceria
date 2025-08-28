# inventario/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Retiro, Producto, Cliente, Empresa

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

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Define tu contraseña'})
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirma tu contraseña'})
    )

    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': 'Email',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresa tu email'}),
        }


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya ha sido registrado. Por favor, elige otro.")
        # También asignaremos el email al username para evitar conflictos
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso como nombre de usuario.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        return cleaned_data

# --- NUEVO FORMULARIO: PASO 2 (Datos de la Empresa) ---
class EmpresaOnboardingForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'giro']
        labels = {
            'nombre': 'Nombre de tu Tienda o Negocio',
            'giro': '¿A qué se dedica tu negocio?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Abarrotes "La Esquinita"'}),
            'giro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Venta de abarrotes y cremería'}),
        }

class ProductoForm(forms.ModelForm):
    # --- NUEVO MÉTODO __init__ ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esta lógica se asegura de que el cambio solo aplique al crear un producto nuevo,
        # no al editar uno existente.
        if not self.instance.pk:
            self.fields['requiere_stock'].initial = False
    # --------------------------

    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'unidad_medida', 'requiere_stock', 'stock', 'precio_mayoreo', 'mayoreo_desde_kg']
        labels = {
            'nombre': 'Nombre del Producto o Servicio',
            'precio': 'Precio de Venta',
            'stock': 'Stock Inicial (si aplica)',
            'precio_mayoreo': 'Precio de Mayoreo (Opcional)',
            'mayoreo_desde_kg': 'Aplicar Mayoreo desde (Kg/u)',
            'unidad_medida': 'Se vende por',
            'requiere_stock': '¿Controlar inventario de este producto?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_mayoreo': forms.NumberInput(attrs={'class': 'form-control'}),
            'mayoreo_desde_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'requiere_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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

class ClienteDomicilioForm(forms.ModelForm):
    # La dirección ahora es obligatoria a nivel de formulario
    direccion = forms.CharField(label="Dirección (Obligatoria)", 
                                max_length=255, 
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. de la Tecnología #123'}))
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion']
        labels = {
            'nombre': 'Nombre del Cliente',
            'telefono': 'Teléfono',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 312123...'}),
        }