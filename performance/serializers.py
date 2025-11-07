from rest_framework import serializers
from datetime import datetime

class RawDocDataSerializer(serializers.Serializer):
    producto = serializers.DictField()
    precio_lista = serializers.DecimalField(max_digits=10, decimal_places=2)
    moneda = serializers.CharField()

"""
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Convertir datetime a string en formato ISO
        if isinstance(ret.get('fecha_hora'), datetime):
            ret['fecha_hora'] = ret['fecha_hora'].isoformat()
        return ret

    def to_internal_value(self, data):
        if isinstance(data.get('fecha_hora'), str):
            try:
                # Intentar parsear la fecha si viene como string
                data['fecha_hora'] = datetime.fromisoformat(data['fecha_hora'])
            except (ValueError, TypeError):
                raise serializers.ValidationError({"fecha_hora": "Formato de fecha inválido. Use YYYY-MM-DDTHH:MM:SS"})
        return super().to_internal_value(data)

"""