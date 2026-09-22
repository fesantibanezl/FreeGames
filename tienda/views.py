from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as iniciar_sesion
from django.contrib.auth import logout as cerrar_sesion_django
from django.db import transaction
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .decorators import destino_por_rol, obtener_codigo_rol, rol_requerido
from .forms import (
    InicioSesionForm,
    JuegoForm,
    PerfilUsuarioForm,
    RegistroUsuarioForm,
    UsuarioAdministracionForm,
)
from .models import (
    Categoria,
    DetallePedido,
    Juego,
    Pedido,
    PerfilUsuario,
    Rol,
)


Usuario = get_user_model()
CLAVE_CARRITO = 'freegames_carrito'


def _es_administrador(usuario):
    return (
        usuario.is_authenticated
        and obtener_codigo_rol(usuario) == Rol.Codigos.ADMINISTRADOR
    )


def _carrito_sesion(request):
    carrito = request.session.get(CLAVE_CARRITO, {})
    if not isinstance(carrito, dict):
        carrito = {}
    return carrito


def _guardar_carrito(request, carrito):
    request.session[CLAVE_CARRITO] = carrito
    request.session.modified = True


def _items_carrito(request):
    carrito = _carrito_sesion(request)
    ids = []
    for identificador in carrito:
        try:
            ids.append(int(identificador))
        except (TypeError, ValueError):
            continue

    juegos = {
        str(juego.pk): juego
        for juego in Juego.objects.select_related('categoria').filter(
            pk__in=ids,
            activo=True,
        )
    }
    normalizado = {}
    items = []
    total = 0

    for identificador, valor in carrito.items():
        juego = juegos.get(str(identificador))
        try:
            cantidad = int(valor)
        except (TypeError, ValueError):
            continue
        if juego is None or cantidad < 1:
            continue

        normalizado[str(juego.pk)] = cantidad
        subtotal = juego.precio * cantidad
        total += subtotal
        items.append({
            'juego': juego,
            'cantidad': cantidad,
            'subtotal': subtotal,
            'subtotal_texto': (
                'Gratis'
                if subtotal == 0
                else f'${subtotal:,}'.replace(',', '.')
            ),
            'stock_suficiente': cantidad <= juego.stock,
        })

    if normalizado != carrito:
        _guardar_carrito(request, normalizado)
    return items, total


def _slug_juego_unico(nombre):
    base = slugify(nombre) or 'juego'
    candidato = base
    numero = 2
    while Juego.objects.filter(slug=candidato).exists():
        candidato = f'{base}-{numero}'
        numero += 1
    return candidato


def _entero_consulta(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise Http404('El identificador solicitado no es válido.')


def _contexto_administracion(
    request,
    *,
    juego_seleccionado=None,
    formulario_juego=None,
    usuario_seleccionado=None,
    formulario_usuario=None,
):
    juegos = Juego.objects.select_related('categoria').all()
    usuarios = Usuario.objects.filter(perfil__isnull=False).select_related(
        'perfil__rol',
    ).order_by('username')

    if formulario_juego is None:
        formulario_juego = JuegoForm(instance=juego_seleccionado)

    if usuario_seleccionado is None:
        usuario_seleccionado = usuarios.first()
    if formulario_usuario is None and usuario_seleccionado is not None:
        formulario_usuario = UsuarioAdministracionForm(
            usuario_objetivo=usuario_seleccionado,
            usuario_actual=request.user,
        )

    ventas = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
    clientes_activos = usuarios.filter(
        is_active=True,
        perfil__rol__codigo=Rol.Codigos.CLIENTE,
    ).count()

    return {
        'encabezado_compacto': True,
        'seccion_activa': 'administracion',
        'juegos': juegos,
        'usuarios': usuarios,
        'juego_seleccionado': juego_seleccionado,
        'formulario_juego': formulario_juego,
        'usuario_seleccionado': usuario_seleccionado,
        'formulario_usuario': formulario_usuario,
        'juegos_disponibles': juegos.filter(activo=True, stock__gt=0).count(),
        'juegos_no_disponibles': juegos.exclude(activo=True, stock__gt=0).count(),
        'clientes_activos': clientes_activos,
        'total_usuarios': usuarios.count(),
        'total_pedidos': Pedido.objects.count(),
        'total_ventas': ventas,
        'total_ventas_texto': (
            'Gratis' if ventas == 0 else f'${ventas:,}'.replace(',', '.')
        ),
    }


def inicio(request):
    """Muestra las categorías persistentes del catálogo."""
    if _es_administrador(request.user):
        return redirect('tienda:administracion')

    return render(request, 'tienda/index.html', {
        'categorias': Categoria.objects.all(),
        'seccion_activa': 'inicio',
    })


def categoria(request, slug):
    """Muestra los juegos publicados de una categoría."""
    if _es_administrador(request.user):
        return redirect('tienda:administracion')

    categoria_seleccionada = get_object_or_404(Categoria, slug=slug)
    return render(request, 'tienda/categoria.html', {
        'categoria': categoria_seleccionada,
        'juegos': categoria_seleccionada.juegos.filter(activo=True),
        'encabezado_compacto': True,
        'seccion_activa': slug,
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect(destino_por_rol(request.user))

    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = RegistroUsuarioForm(datos_formulario)
    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.save()
        iniciar_sesion(request, usuario)
        messages.success(
            request,
            'Cuenta creada correctamente. Ya puedes administrar tu perfil.',
        )
        return redirect('tienda:perfil')

    return render(request, 'tienda/registro.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'registro',
        'formulario': formulario,
    })


def login(request):
    if request.user.is_authenticated:
        return redirect(destino_por_rol(request.user))

    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = InicioSesionForm(datos_formulario, request=request)
    siguiente = request.POST.get('siguiente') or request.GET.get('next', '')

    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.usuario
        iniciar_sesion(request, usuario)

        if (
            obtener_codigo_rol(usuario) == Rol.Codigos.CLIENTE
            and siguiente
            and url_has_allowed_host_and_scheme(
                siguiente,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return redirect(siguiente)
        return redirect(destino_por_rol(usuario))

    return render(request, 'tienda/login.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'login',
        'formulario': formulario,
        'siguiente': siguiente,
    })


@require_POST
def logout(request):
    cerrar_sesion_django(request)
    return redirect('tienda:inicio')


def recuperar_clave(request):
    return render(request, 'tienda/recuperar_clave.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'recuperar_clave',
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def perfil(request):
    rol_predeterminado = Rol.objects.get(codigo=Rol.Codigos.CLIENTE)
    perfil_usuario, _ = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={'rol': rol_predeterminado},
    )
    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = PerfilUsuarioForm(
        datos_formulario,
        usuario=request.user,
        perfil=perfil_usuario,
    )
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(
            request,
            'Los datos del perfil se actualizaron correctamente.',
        )
        return redirect('tienda:perfil')

    return render(request, 'tienda/perfil.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'perfil',
        'formulario': formulario,
        'rol_nombre': perfil_usuario.rol.nombre,
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def carrito(request):
    items, total = _items_carrito(request)
    return render(request, 'tienda/carrito.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'carrito',
        'items_carrito': items,
        'carrito_valido': bool(items) and all(
            item['stock_suficiente'] for item in items
        ),
        'total_carrito': total,
        'total_carrito_texto': (
            'Gratis' if total == 0 else f'${total:,}'.replace(',', '.')
        ),
    })


@require_POST
@rol_requerido(Rol.Codigos.CLIENTE)
def agregar_carrito(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id, activo=True)
    carrito_actual = _carrito_sesion(request)
    clave = str(juego.pk)
    try:
        cantidad = int(carrito_actual.get(clave, 0))
    except (TypeError, ValueError):
        cantidad = 0

    if juego.stock < 1:
        messages.error(request, f'{juego.nombre} no tiene stock disponible.')
    elif cantidad >= juego.stock:
        messages.error(
            request,
            f'Ya agregaste todas las unidades disponibles de {juego.nombre}.',
        )
    else:
        carrito_actual[clave] = cantidad + 1
        _guardar_carrito(request, carrito_actual)
        messages.success(request, f'{juego.nombre} se agregó al carrito.')
    return redirect('tienda:categoria', slug=juego.categoria.slug)


@require_POST
@rol_requerido(Rol.Codigos.CLIENTE)
def actualizar_carrito(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id, activo=True)
    try:
        cantidad = int(request.POST.get('cantidad', '1'))
    except ValueError:
        cantidad = 0

    carrito_actual = _carrito_sesion(request)
    clave = str(juego.pk)
    if cantidad < 1:
        carrito_actual.pop(clave, None)
        messages.success(request, f'{juego.nombre} se quitó del carrito.')
    elif cantidad > juego.stock:
        messages.error(
            request,
            f'Solo hay {juego.stock} unidades disponibles de {juego.nombre}.',
        )
    else:
        carrito_actual[clave] = cantidad
        messages.success(request, 'La cantidad se actualizó correctamente.')
    _guardar_carrito(request, carrito_actual)
    return redirect('tienda:carrito')


@require_POST
@rol_requerido(Rol.Codigos.CLIENTE)
def quitar_carrito(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)
    carrito_actual = _carrito_sesion(request)
    carrito_actual.pop(str(juego.pk), None)
    _guardar_carrito(request, carrito_actual)
    messages.success(request, f'{juego.nombre} se quitó del carrito.')
    return redirect('tienda:carrito')


@require_POST
@rol_requerido(Rol.Codigos.CLIENTE)
def vaciar_carrito(request):
    _guardar_carrito(request, {})
    messages.success(request, 'El carrito quedó vacío.')
    return redirect('tienda:carrito')


@require_POST
@rol_requerido(Rol.Codigos.CLIENTE)
@transaction.atomic
def finalizar_compra(request):
    carrito_actual = _carrito_sesion(request)
    cantidades = {}
    for identificador, valor in carrito_actual.items():
        try:
            juego_id = int(identificador)
            cantidad = int(valor)
        except (TypeError, ValueError):
            continue
        if cantidad > 0:
            cantidades[juego_id] = cantidad

    if not cantidades:
        messages.error(request, 'Agrega al menos un juego antes de comprar.')
        return redirect('tienda:carrito')

    juegos = {
        juego.pk: juego
        for juego in Juego.objects.select_for_update().filter(
            pk__in=cantidades,
            activo=True,
        )
    }
    if len(juegos) != len(cantidades):
        messages.error(
            request,
            'Uno de los juegos ya no está publicado. Revisa el carrito.',
        )
        return redirect('tienda:carrito')

    for juego_id, cantidad in cantidades.items():
        juego = juegos[juego_id]
        if cantidad > juego.stock:
            messages.error(
                request,
                f'No hay stock suficiente de {juego.nombre}.',
            )
            return redirect('tienda:carrito')

    pedido = Pedido.objects.create(
        usuario=request.user,
        codigo=f'FG-{uuid4().hex[:12].upper()}',
    )
    total = 0
    for juego_id, cantidad in cantidades.items():
        juego = juegos[juego_id]
        DetallePedido.objects.create(
            pedido=pedido,
            juego=juego,
            nombre_juego=juego.nombre,
            precio_unitario=juego.precio,
            cantidad=cantidad,
        )
        total += juego.precio * cantidad
        juego.stock -= cantidad
        juego.save(update_fields=('stock', 'actualizado_en'))

    pedido.total = total
    pedido.save(update_fields=('total',))
    _guardar_carrito(request, {})
    return redirect(
        f"{reverse('tienda:compra_exitosa')}?pedido={pedido.pk}",
    )


@rol_requerido(Rol.Codigos.CLIENTE)
def compra_exitosa(request):
    pedido_id = request.GET.get('pedido')
    pedido = None
    if pedido_id:
        pedido = get_object_or_404(
            Pedido.objects.prefetch_related('detalles'),
            pk=_entero_consulta(pedido_id),
            usuario=request.user,
        )
    return render(request, 'tienda/compra_exitosa.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'compra_exitosa',
        'pedido': pedido,
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def mis_compras(request):
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related(
        'detalles',
    )
    return render(request, 'tienda/mis_compras.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'mis_compras',
        'pedidos': pedidos,
    })


@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def administracion(request):
    juego_seleccionado = None
    usuario_seleccionado = None
    if request.GET.get('juego'):
        juego_seleccionado = get_object_or_404(
            Juego,
            pk=_entero_consulta(request.GET['juego']),
        )
    if request.GET.get('usuario'):
        usuario_seleccionado = get_object_or_404(
            Usuario.objects.select_related('perfil__rol'),
            pk=_entero_consulta(request.GET['usuario']),
        )
    return render(
        request,
        'tienda/administracion.html',
        _contexto_administracion(
            request,
            juego_seleccionado=juego_seleccionado,
            usuario_seleccionado=usuario_seleccionado,
        ),
    )


@require_POST
@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def guardar_juego(request):
    juego_id = request.POST.get('juego_id')
    juego = get_object_or_404(Juego, pk=juego_id) if juego_id else None
    categoria_anterior_id = juego.categoria_id if juego else None
    formulario = JuegoForm(request.POST, instance=juego)

    if formulario.is_valid():
        juego_guardado = formulario.save(commit=False)
        if juego is None:
            juego_guardado.slug = _slug_juego_unico(juego_guardado.nombre)
        if juego is None or categoria_anterior_id != juego_guardado.categoria_id:
            juego_guardado.imagen = juego_guardado.categoria.imagen
            juego_guardado.imagen_alt = juego_guardado.categoria.imagen_alt
        juego_guardado.save()
        accion = 'registrado' if juego is None else 'actualizado'
        messages.success(
            request,
            f'{juego_guardado.nombre} fue {accion} correctamente.',
        )
        return redirect(
            f"{reverse('tienda:administracion')}?juego={juego_guardado.pk}#producto",
        )

    return render(
        request,
        'tienda/administracion.html',
        _contexto_administracion(
            request,
            juego_seleccionado=juego,
            formulario_juego=formulario,
        ),
    )


@require_POST
@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def cambiar_estado_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)
    juego.activo = not juego.activo
    juego.save(update_fields=('activo', 'actualizado_en'))
    messages.success(
        request,
        (
            f'{juego.nombre} volvió a publicarse.'
            if juego.activo
            else f'{juego.nombre} fue quitado del catálogo.'
        ),
    )
    return redirect(f"{reverse('tienda:administracion')}#inventario")


@require_POST
@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def eliminar_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)
    nombre = juego.nombre
    try:
        juego.delete()
        messages.success(request, f'{nombre} fue eliminado definitivamente.')
    except ProtectedError:
        juego.activo = False
        juego.save(update_fields=('activo', 'actualizado_en'))
        messages.error(
            request,
            f'{nombre} pertenece a un pedido y no puede eliminarse; quedó oculto.',
        )
    return redirect(f"{reverse('tienda:administracion')}#inventario")


@require_POST
@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def actualizar_usuario(request, usuario_id):
    usuario_objetivo = get_object_or_404(
        Usuario.objects.select_related('perfil__rol'),
        pk=usuario_id,
    )
    formulario = UsuarioAdministracionForm(
        request.POST,
        usuario_objetivo=usuario_objetivo,
        usuario_actual=request.user,
    )
    if formulario.is_valid():
        formulario.save()
        messages.success(
            request,
            f'La cuenta de {usuario_objetivo.username} fue actualizada.',
        )
        return redirect(
            f"{reverse('tienda:administracion')}?usuario={usuario_objetivo.pk}#usuario",
        )

    return render(
        request,
        'tienda/administracion.html',
        _contexto_administracion(
            request,
            usuario_seleccionado=usuario_objetivo,
            formulario_usuario=formulario,
        ),
    )
