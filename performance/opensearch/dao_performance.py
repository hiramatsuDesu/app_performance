from opensearchpy import NotFoundError
from .open_search_client import get_opensearch_client
from prometheus_client import Summary, Gauge
import time
import json
import os
from opensearchpy import NotFoundError
from .open_search_client import get_opensearch_client

INDEX_NAME = 'documents'

# get_by_id_document query duration
opensearch_get_duration = Summary(
    'opensearch_get_by_id_seconds',
    'Time in seconds taken by the get_by_id_document function'
)

# search query duration
opensearch_search_duration = Summary(
    'opensearch_search_seconds',
    'Time in seconds taken by the search function'
)

# search template query duration
opensearch_template_duration = Summary(
    'opensearch_template_seconds',
    'Time in seconds taken by the search_with_template function'
)

# number of documents returned
opensearch_search_results = Gauge(
    'opensearch_search_result_count',
    'Number of results returned in the last search'
)

class Dao_performance():
    def __init__(self):
        self.client = get_opensearch_client()
        self.index_name = INDEX_NAME
        self.tempaltes_dir = os.path.join(os.path.dirname(__file__), "template_mustache")

    def index_document(self, document, doc_id=None):
        """Insert a new document"""
        return self.client.index(index=self.index_name, body=document, id=doc_id, refresh=True)

    @opensearch_get_duration.time()
    def get_by_id_document(self, doc_id):
        """Get the document by the _id"""
        try:
            resp = self.client.get(index=self.index_name, id=doc_id)
            return resp["_source"]
        except NotFoundError:
            return None

    @opensearch_search_duration.time()
    def search(self, must=None, must_not=None, should=None, filters=None, size=10):
        """
        Generic search with parameters bool.
        must/must_not/should are lists of dicts
        """
        query = {"bool": {}}
        if must:
            query["bool"]["must"] = must
        if must_not:
            query["bool"]["must_not"] = must_not
        if should:
            query["bool"]["should"] = should
        if filters:
            query["bool"]["filters"] = filters


        body = {"query": query, "size": size}
        return self.client.search(index=self.index_name, body=body)

    def list_all(self, size=100):
        """list all the documents"""
        query = {"match_all": {}}
        body = {"query": query, "size": size}
        return self.client.search(index=self.index_name, body=body)
    
    def delete_by_id(self, id_doc):
        """delete a document"""
        try:
            return self.client.delete(index=self.index_document, id=id_doc)
        except NotFoundError:
            return None


    # ---------- NUEVO: TEMPLATES MUSTACHE ----------
    def load_template_mustache(self, template_name: str):
        """
            upload mustache template
        """
        path = os.path.join(self.tempaltes_dir, f"{template_name}.mustache")

        with open(path, "r", encoding="utf-8") as f:
            template_source = json.loads(f.read())
        return template_source


    def register_template(self, template_name: str):
        """
        Register the mustache template here
        """
        source = self.load_template_mustache(template_name)
        payload = {
            "script": {
                "lang": "mustache",
                "source": json.dumps(source)
            }
        }
        resp = self.client.transport.perform_request(
            "POST", f"/_scripts/{template_name}", body=payload
        )
        return resp

    @opensearch_template_duration.time()
    def search_with_template(self, template_name:str, params:dict):
        """
            Execute a mustache template in opensearch
        """

        body = {"id": template_name, "params": params}
        resp = self.client.transport.perform_request(
            "POST", f"/_search/template", body=body
        )
        hits = resp.get("hits", {}).get("hits", [])
        opensearch_search_results.set(len(hits))
        return hits
