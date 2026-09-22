import re
from datetime import date

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import transaction

from .models import Juego, PerfilUsuario, Rol


Usuario = get_user_model()

VALIDAR_NOMBRE = RegexValidator(
    regex=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '\-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$",
    message='Usa solamente letras, espacios, apóstrofes o guiones.',
)
VALIDAR_USUARIO = RegexValidator(
    regex=r'^[A-Za-z0-9._-]+$',
    message='Usa letras, números, puntos, guiones o guion bajo, sin espacios.',
)


def separar_nombre(nombre_completo):
    partes = nombre_completo.strip().split(maxsplit=1)
    return partes[0], partes[1] if len(partes) > 1 else ''


def validar_fecha_nacimiento(fecha_nacimiento):
    hoy = date.today()
    if fecha_nacimiento > hoy:
        raise ValidationError('La fecha de nacimiento no puede ser futura.')

    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    ):
        edad -= 1

    if edad < 13:
        raise ValidationError('Debes tener al menos 13 años.')


def validar_formato_clave(clave):
    errores = []
    reglas = (
        (r'[A-ZÁÉÍÓÚÜÑ]', 'Incluye al menos una letra mayúscula.'),
        (r'[a-záéíóúüñ]', 'Incluye al menos una letra minúscula.'),
        (r'\d', 'Incluye al menos un número.'),
        (
            r'[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s]',
            'Incluye al menos un carácter especial.',
        ),
    )
    if len(clave) > 18:
        errores.append('La contraseña no puede superar los 18 caracteres.')
    if re.search(r'\s', clave):
        errores.append('La contraseña no puede contener espacios.')
    for patron, mensaje in reglas:
        if not re.search(patron, clave):
            errores.append(mensaje)
    if errores:
        raise ValidationError(errores)


class InicioSesionForm(forms.Form):
    acceso = forms.CharField(max_length=100)
    clave = forms.CharField(max_length=128)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.usuario = None
        super().__init__(*args, **kwargs)

    def clean(self):
        datos = super().clean()
        acceso = datos.get('acceso', '').strip()
        clave = datos.get('clave')
        if not acceso or not clave:
            return datos

        usuario = Usuario.objects.filter(username__iexact=acceso).first()
        if usuario is None:
            usuario = Usuario.objects.filter(email__iexact=acceso).first()

        if usuario is not None and not usuario.is_active:
            raise ValidationError(
                'La cuenta está desactivada. Contacta al administrador.',
            )

        if usuario is not None:
            self.usuario = authenticate(
                self.request,
                username=usuario.username,
                password=clave,
            )

        if self.usuario is None:
            raise ValidationError(
                'No fue posible iniciar sesión. Revisa tus credenciales.',
            )

        return datos


class DatosUsuarioForm(forms.Form):
    nombre_completo = forms.CharField(
        min_length=3,
        max_length=60,
        validators=(VALIDAR_NOMBRE,),
    )
    nombre_usuario = forms.CharField(
        min_length=4,
        max_length=16,
        validators=(VALIDAR_USUARIO,),
    )
    correo = forms.EmailField(max_length=100)
    fecha_nacimiento = forms.DateField()
    direccion = forms.CharField(
        required=False,
        min_length=10,
        max_length=160,
    )

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data['nombre_usuario'].strip()
        usuarios = Usuario.objects.filter(username__iexact=nombre_usuario)
        usuario_actual = getattr(self, 'usuario', None)
        if usuario_actual is not None:
            usuarios = usuarios.exclude(pk=usuario_actual.pk)
        if usuarios.exists():
            raise ValidationError('Ese nombre de usuario ya está registrado.')
        return nombre_usuario

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        usuarios = Usuario.objects.filter(email__iexact=correo)
        usuario_actual = getattr(self, 'usuario', None)
        if usuario_actual is not None:
            usuarios = usuarios.exclude(pk=usuario_actual.pk)
        if usuarios.exists():
            raise ValidationError('Ese correo electrónico ya está registrado.')
        return correo

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        validar_fecha_nacimiento(fecha_nacimiento)
        return fecha_nacimiento

    def clean_direccion(self):
        return self.cleaned_data['direccion'].strip()


class RegistroUsuarioForm(DatosUsuarioForm):
    clave = forms.CharField(min_length=8, max_length=18)
    repetir_clave = forms.CharField(min_length=8, max_length=18)

    def clean(self):
        datos = super().clean()
        clave = datos.get('clave')
        repetir_clave = datos.get('repetir_clave')

        if clave and repetir_clave and clave != repetir_clave:
            self.add_error('repetir_clave', 'Las contraseñas no coinciden.')

        if clave:
            usuario_temporal = Usuario(
                username=datos.get('nombre_usuario', ''),
                email=datos.get('correo', ''),
            )
            try:
                validar_formato_clave(clave)
                validate_password(clave, usuario_temporal)
            except ValidationError as error:
                self.add_error('clave', error)

        return datos

    @transaction.atomic
    def save(self):
        nombre, apellido = separar_nombre(self.cleaned_data['nombre_completo'])
        usuario = Usuario(
            username=self.cleaned_data['nombre_usuario'],
            first_name=nombre,
            last_name=apellido,
            email=self.cleaned_data['correo'],
        )
        usuario.set_password(self.cleaned_data['clave'])
        usuario.save()

        rol_cliente = Rol.objects.get(codigo=Rol.Codigos.CLIENTE)
        PerfilUsuario.objects.create(
            usuario=usuario,
            rol=rol_cliente,
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            direccion=self.cleaned_data['direccion'],
        )
        return usuario


class PerfilUsuarioForm(DatosUsuarioForm):
    def __init__(self, *args, usuario, perfil, **kwargs):
        self.usuario = usuario
        self.perfil = perfil
        datos = args[0] if args else kwargs.get('data')
        if datos is None:
            kwargs.setdefault(
                'initial',
                {
                    'nombre_completo': usuario.get_full_name(),
                    'nombre_usuario': usuario.username,
                    'correo': usuario.email,
                    'fecha_nacimiento': (
                        perfil.fecha_nacimiento.isoformat()
                        if perfil.fecha_nacimiento
                        else ''
                    ),
                    'direccion': perfil.direccion,
                },
            )
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self):
        nombre, apellido = separar_nombre(self.cleaned_data['nombre_completo'])
        self.usuario.first_name = nombre
        self.usuario.last_name = apellido
        self.usuario.username = self.cleaned_data['nombre_usuario']
        self.usuario.email = self.cleaned_data['correo']
        self.usuario.save(
            update_fields=('first_name', 'last_name', 'username', 'email'),
        )

        self.perfil.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        self.perfil.direccion = self.cleaned_data['direccion']
        self.perfil.save(update_fields=('fecha_nacimiento', 'direccion', 'actualizado_en'))
        return self.usuario


class JuegoForm(forms.ModelForm):
    class Meta:
        model = Juego
        fields = (
            'nombre',
            'categoria',
            'descripcion',
            'precio',
            'stock',
            'activo',
        )
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'admin-product-name',
                'placeholder': 'Ejemplo: Hollow Knight',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'admin-product-category',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'admin-product-description',
                'rows': 4,
                'placeholder': 'Describe brevemente el juego',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'admin-product-price',
                'min': 0,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'admin-product-stock',
                'min': 0,
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'admin-product-active',
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        juegos = Juego.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            juegos = juegos.exclude(pk=self.instance.pk)
        if juegos.exists():
            raise ValidationError('Ya existe un juego registrado con ese nombre.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion'].strip()
        if len(descripcion) < 10:
            raise ValidationError('La descripción debe tener al menos 10 caracteres.')
        return descripcion


class UsuarioCrearForm(RegistroUsuarioForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.none(),
        to_field_name='codigo',
        empty_label=None,
    )
    activo = forms.ChoiceField(
        choices=(('true', 'Cuenta activa'), ('false', 'Cuenta inactiva')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        atributos = {
            'nombre_completo': {'class': 'form-control', 'id': 'admin-new-name'},
            'nombre_usuario': {'class': 'form-control', 'id': 'admin-new-username'},
            'correo': {'class': 'form-control', 'id': 'admin-new-email'},
            'clave': {'class': 'form-control', 'id': 'admin-new-password'},
            'repetir_clave': {'class': 'form-control', 'id': 'admin-new-password-repeat'},
            'fecha_nacimiento': {
                'class': 'form-control',
                'id': 'admin-new-birthdate',
                'type': 'date',
            },
            'direccion': {'class': 'form-control', 'id': 'admin-new-address'},
            'rol': {'class': 'form-select', 'id': 'admin-new-role'},
            'activo': {'class': 'form-select', 'id': 'admin-new-active'},
        }
        for nombre, attrs in atributos.items():
            self.fields[nombre].widget.attrs.update(attrs)

    @transaction.atomic
    def save(self):
        usuario = super().save()
        rol = self.cleaned_data['rol']
        usuario.perfil.rol = rol
        usuario.perfil.save(update_fields=('rol', 'actualizado_en'))
        usuario.is_active = self.cleaned_data['activo'] == 'true'
        usuario.is_staff = rol.codigo == Rol.Codigos.ADMINISTRADOR
        usuario.is_superuser = False
        usuario.save(update_fields=('is_active', 'is_staff', 'is_superuser'))
        return usuario


class UsuarioAdministracionForm(DatosUsuarioForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.none(),
        to_field_name='codigo',
        empty_label=None,
    )
    activo = forms.ChoiceField(
        choices=(('true', 'Cuenta activa'), ('false', 'Cuenta inactiva')),
    )

    def __init__(self, *args, usuario_objetivo, usuario_actual, **kwargs):
        self.usuario_objetivo = usuario_objetivo
        self.usuario_actual = usuario_actual
        self.usuario = usuario_objetivo
        datos = args[0] if args else kwargs.get('data')
        if datos is None:
            kwargs.setdefault(
                'initial',
                {
                    'nombre_completo': usuario_objetivo.get_full_name(),
                    'nombre_usuario': usuario_objetivo.username,
                    'correo': usuario_objetivo.email,
                    'fecha_nacimiento': (
                        usuario_objetivo.perfil.fecha_nacimiento.isoformat()
                        if usuario_objetivo.perfil.fecha_nacimiento
                        else ''
                    ),
                    'direccion': usuario_objetivo.perfil.direccion,
                },
            )
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        self.fields['rol'].widget.attrs.update({
            'class': 'form-select',
            'id': 'admin-user-role',
        })
        self.fields['activo'].widget.attrs.update({
            'class': 'form-select',
            'id': 'admin-user-active',
        })
        atributos = {
            'nombre_completo': {'class': 'form-control', 'id': 'admin-user-name'},
            'nombre_usuario': {'class': 'form-control', 'id': 'admin-user-username'},
            'correo': {'class': 'form-control', 'id': 'admin-user-email'},
            'fecha_nacimiento': {
                'class': 'form-control',
                'id': 'admin-user-birthdate',
                'type': 'date',
            },
            'direccion': {'class': 'form-control', 'id': 'admin-user-address'},
        }
        for nombre, attrs in atributos.items():
            self.fields[nombre].widget.attrs.update(attrs)

        if not self.is_bound:
            self.initial.update({
                'rol': usuario_objetivo.perfil.rol.codigo,
                'activo': str(usuario_objetivo.is_active).lower(),
            })

    def clean(self):
        datos = super().clean()
        rol = datos.get('rol')
        activo = datos.get('activo') == 'true'

        cambia_rol_propio = (
            rol is not None
            and rol.codigo != Rol.Codigos.ADMINISTRADOR
        )
        if (
            self.usuario_objetivo == self.usuario_actual
            and (cambia_rol_propio or not activo)
        ):
            raise ValidationError(
                'No puedes cambiar tu propio rol ni desactivar tu cuenta.',
            )
        return datos

    @transaction.atomic
    def save(self):
        rol = self.cleaned_data['rol']
        activo = self.cleaned_data['activo'] == 'true'
        perfil = self.usuario_objetivo.perfil
        nombre, apellido = separar_nombre(self.cleaned_data['nombre_completo'])

        self.usuario_objetivo.first_name = nombre
        self.usuario_objetivo.last_name = apellido
        self.usuario_objetivo.username = self.cleaned_data['nombre_usuario']
        self.usuario_objetivo.email = self.cleaned_data['correo']
        perfil.rol = rol
        perfil.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        perfil.direccion = self.cleaned_data['direccion']
        perfil.save(
            update_fields=(
                'rol',
                'fecha_nacimiento',
                'direccion',
                'actualizado_en',
            ),
        )

        self.usuario_objetivo.is_active = activo
        self.usuario_objetivo.is_staff = (
            rol.codigo == Rol.Codigos.ADMINISTRADOR
        )
        if rol.codigo != Rol.Codigos.ADMINISTRADOR:
            self.usuario_objetivo.is_superuser = False
        self.usuario_objetivo.save(
            update_fields=(
                'first_name',
                'last_name',
                'username',
                'email',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        )
        return self.usuario_objetivo


class RecuperacionClaveForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'correo-recuperacion',
            'autocomplete': 'email',
            'placeholder': 'nombre@correo.cl',
        })


class DefinirClaveForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
            'maxlength': 18,
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
            'maxlength': 18,
        })

    def clean_new_password1(self):
        clave = self.cleaned_data['new_password1']
        validar_formato_clave(clave)
        return clave
