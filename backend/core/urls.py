# backend/core/urls.py

from django.contrib import admin
from django.urls import path, include # Make sure 'include' is still imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This is our API
    path('api/', include('api.urls')),
    
    # --- ADD THIS LINE ---
    # This provides the login/logout views for the browseable API
    path('api-auth/', include('rest_framework.urls')),
    # ---------------------
]