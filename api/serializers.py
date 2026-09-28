from rest_framework import serializers

from tienda.models import Categoria, Juego


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = (
            'id',
            'slug',
            'nombre',
            'icono',
            'clase_css',
            'resumen',
            'descripcion_meta',
            'imagen',
            'imagen_alt',
            'orden',
        )
        read_only_fields = ('id',)


class JuegoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True,
    )
    gratis = serializers.ReadOnlyField()

    class Meta:
        model = Juego
        fields = (
            'id',
            'categoria',
            'categoria_nombre',
            'slug',
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'activo',
            'imagen',
            'imagen_alt',
            'gratis',
            'creado_en',
            'actualizado_en',
        )
        read_only_fields = (
            'id',
            'categoria_nombre',
            'gratis',
            'creado_en',
            'actualizado_en',
        )
