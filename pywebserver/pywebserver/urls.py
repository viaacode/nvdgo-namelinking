"""pywebserver URL Configuration
see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from jsonrpc.backend.django import api

urlpatterns = [
    path('', RedirectView.as_view(url='/attestation/')),
    path('admin/', admin.site.urls),
    path('attestation/', include('attestation.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('api/jsonrpc', include(api.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
