from opensearchpy import OpenSearch
from django.conf import settings

def get_opensearch_client():
    """
    Devuelve un cliente de OpenSearch configurado según settings.OPENSEARCH.
    """
    host_list = settings.OPENSEARCH.get('HOST', ['http://localhost:9200'])
    verify_certs = settings.OPENSEARCH.get('VERIFY_CERTS', True)
    ssl_show_warn = settings.OPENSEARCH.get('SSL_SHOW_WARN', True)

    client = OpenSearch(
        hosts=host_list,
        verify_certs=verify_certs,
        ssl_show_warn=ssl_show_warn
    )
    return client



