from django.db import models

# Create your models here.
class DocumentData(models.Model):
    id_op_search_document = models.CharField(max_length=255, unique=True)
    index_name = models.CharField(max_length=255, default='default_document')
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()
    id_document = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.title} - {self.id_op_search_document} - {self.received_at}"
    