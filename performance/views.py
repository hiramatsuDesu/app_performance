from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .serializers import RawDocDataSerializer
from .models import DocumentData
from .opensearch.dao_performance import Dao_performance
import uuid
import datetime

# Create your views here.

class DocumentDataView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dao = Dao_performance()

    def post(self, request, format=None):
        serializer = RawDocDataSerializer(data=request.data)
        id_document = str(uuid.uuid4())
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir los datos validados a un diccionario con valores serializables
        payload = {
            'id_document': id_document,
            'fecha_hora': datetime.datetime.now().isoformat(),
            'producto': serializer.validated_data['producto'],
            'precio_lista': str(serializer.validated_data['precio_lista']),
            'moneda': serializer.validated_data['moneda']
        }
            
        # Validate and process the data
        try:
            precio_lista = Decimal(request.data['precio_lista'])
        except (TypeError, InvalidOperation):
            return Response({"error": 'precio_lista is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            
        iva = Decimal('21.7')
        ingresos_brutos = Decimal('3.5')
        ganancias = Decimal('35.0')

        total_impuestos = (precio_lista * (iva + ingresos_brutos + ganancias)) / Decimal('100.0')
        precio_final = precio_lista + total_impuestos

        impuestos = {
            'iva': float((precio_lista * iva) / Decimal('100.0')),
            'ingresos_brutos': float((precio_lista * ingresos_brutos) / Decimal('100.0')),
            'ganancias': float((precio_lista * ganancias) / Decimal('100.0')),
            'total_impuestos': float(total_impuestos)
        }

        payload['impuestos'] = impuestos
        payload['precio_final'] = float(precio_final)

        try:
            resp =self.dao.index_document(payload)
        except Exception as e:
            return Response({"error": 'error indexing in opensearch', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        opensearch_id = resp.get('_id', None) or resp.get('id', None)

        meta_data = DocumentData.objects.create(
            id_op_search_document=opensearch_id,
            payload=payload,
            id_document = id_document
        )

        return Response({
            "status": "Document indexed successfully",
            "id": opensearch_id,
            "id_document": id_document,
            "meta_id": meta_data.id
        }, status=status.HTTP_201_CREATED)
    
    def get(self, request, format=None):
        codigo = request.query_params.get("codigo")
        id_document = request.query_params.get("id_document")
        _id_os = request.query_params.get("_id")

        if not codigo or not id_document or not _id_os:
            return Response({"error": "You must fill the fields codigo, id_document and _id"}, status=status.HTTP_400_BAD_REQUEST)

        must = [
            {"term": {"id_document.keyword": id_document}},
            {"term": {"producto.codigo.keyword": codigo}}
        ]

        try:
            response = {}

            result_layers_search = self.dao.search(must=must)
            result_layers_hits = result_layers_search.get("hits", {}).get("hits", [])
            response['result_layers'] = result_layers_hits

            result = self.dao.get_by_id_document(_id_os)
            response['result_by_id'] = result

            #search by template
            self.dao.register_template("search_by_code")
            result_template_search = self.dao.search_with_template(
                template_name="search_by_code",
                params={
                    "id_document": id_document,
                    "codigo": codigo
                }
            )
            response["with template"] = result_template_search

            if not result_layers_hits and not result:
                return Response({"message": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Internal server error", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
