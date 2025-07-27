"""
URL configuration for acat_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse

# Configurar títulos del admin
admin.site.site_header = "Sistema ACAT"
admin.site.site_title = "ACAT Admin"
admin.site.index_title = "Administración del Sistema ACAT"

def custom_logout_view(request):
    """Custom logout view that handles both GET and POST and redirects properly"""
    logout(request)
    return redirect('/admin/login/')

# Override admin logout URL directly
admin.site.logout_template = 'admin/logged_out.html'

urlpatterns = [
    # Custom logout handler BEFORE admin URLs
    path("admin/logout/", custom_logout_view, name='admin_logout'),
    path("admin/", admin.site.urls),
    # Backup logout URL in case admin doesn't work
    path("logout/", custom_logout_view, name='logout'),
    path("", TemplateView.as_view(template_name="base.html"), name="home"),
    path("denuncias/", include("apps.complaints.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("api/", include("apps.complaints.api_urls")),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
