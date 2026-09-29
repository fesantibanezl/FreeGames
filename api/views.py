from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from tienda.models import Categoria, Juego

from .permissions import EsAdministradorOConsulta
from .serializers import CategoriaSerializer, JuegoSerializer


@api_view(['GET', 'POST'])
@permission_classes([EsAdministradorOConsulta])
def categorias(request):
    if request.method == 'GET':
        registros = Categoria.objects.all()
        serializer = CategoriaSerializer(registros, many=True)
        return Response(serializer.data)

    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([EsAdministradorOConsulta])
def categoria_detalle(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    if request.method == 'GET':
        return Response(CategoriaSerializer(categoria).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = CategoriaSerializer(
            categoria,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        categoria.delete()
    except ProtectedError:
        return Response(
            {
                'detalle': (
                    'La categoría no puede eliminarse porque tiene juegos '
                    'asociados.'
                ),
            },
            status=status.HTTP_409_CONFLICT,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([EsAdministradorOConsulta])
def juegos(request):
    if request.method == 'GET':
        registros = Juego.objects.select_related('categoria').all()

        nombre = request.query_params.get('nombre', '').strip()
        categoria = request.query_params.get('categoria', '').strip()
        if nombre:
            registros = registros.filter(nombre__icontains=nombre)
        if categoria:
            registros = registros.filter(categoria__slug__iexact=categoria)

        for parametro in ('activo', 'gratis'):
            valor = request.query_params.get(parametro)
            if valor is None:
                continue
            booleanos = {
                'true': True,
                '1': True,
                'si': True,
                'sí': True,
                'false': False,
                '0': False,
                'no': False,
            }
            valor_normalizado = valor.strip().lower()
            if valor_normalizado not in booleanos:
                return Response(
                    {
                        parametro: (
                            'Use true o false para este parámetro.'
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seleccionado = booleanos[valor_normalizado]
            if parametro == 'activo':
                registros = registros.filter(activo=seleccionado)
            elif seleccionado:
                registros = registros.filter(precio=0)
            else:
                registros = registros.exclude(precio=0)

        serializer = JuegoSerializer(registros, many=True)
        return Response(serializer.data)

    serializer = JuegoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([EsAdministradorOConsulta])
def juego_detalle(request, juego_id):
    juego = get_object_or_404(
        Juego.objects.select_related('categoria'),
        pk=juego_id,
    )

    if request.method == 'GET':
        return Response(JuegoSerializer(juego).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = JuegoSerializer(
            juego,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        juego.delete()
    except ProtectedError:
        return Response(
            {
                'detalle': (
                    'El juego no puede eliminarse porque pertenece a un '
                    'pedido.'
                ),
            },
            status=status.HTTP_409_CONFLICT,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)
