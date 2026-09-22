import re
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import transaction

from .models import PerfilUsuario, Rol


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
            reglas = (
                (r'[A-ZÁÉÍÓÚÜÑ]', 'Incluye al menos una letra mayúscula.'),
                (r'[a-záéíóúüñ]', 'Incluye al menos una letra minúscula.'),
                (r'\d', 'Incluye al menos un número.'),
                (
                    r'[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s]',
                    'Incluye al menos un carácter especial.',
                ),
            )
            if re.search(r'\s', clave):
                self.add_error('clave', 'La contraseña no puede contener espacios.')
            for patron, mensaje in reglas:
                if not re.search(patron, clave):
                    self.add_error('clave', mensaje)

            usuario_temporal = Usuario(
                username=datos.get('nombre_usuario', ''),
                email=datos.get('correo', ''),
            )
            try:
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
