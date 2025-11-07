from django.urls import path
from .views import DocumentDataView

urlpatterns = [
    path('new_document/', DocumentDataView.as_view(), name='data'),
    ]