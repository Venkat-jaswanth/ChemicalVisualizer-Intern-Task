# backend/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# --- Make sure this import is here ---
from .views import DatasetViewSet, DatasetPDFDownloadView

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')

urlpatterns = [
    path('', include(router.urls)),
    
    path(
        'datasets/<int:pk>/download_pdf/', 
        DatasetPDFDownloadView.as_view(), 
        name='download-pdf'
    ),
]