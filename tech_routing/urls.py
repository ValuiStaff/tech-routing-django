"""
URL configuration for tech_routing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import JsonResponse
from tech_routing import views

def admin_assign_view(request):
    """Admin assignment interface"""
    from core.admin import AssignmentAdminViews
    return AssignmentAdminViews.admin_assign_view(request)

def health_check(request):
    """Health check endpoint for deployment platforms"""
    return JsonResponse({'status': 'ok', 'service': 'tech-routing'})

# Note: Bulk upload URL is handled via core.urls

urlpatterns = [
    path("admin/core/assignment/assign/", admin_assign_view, name='admin_assign'),
    path("admin/", admin.site.urls),
    path("accounts/", include('accounts.urls', namespace='accounts')),
    path("core/", include('core.urls', namespace='core')),
    path("health/", health_check, name='health'),
    path("", views.home, name='home'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
