from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('estadisticas/', views.StatsView.as_view(), name='stats'),
    path('mapa/', views.MapView.as_view(), name='map'),
    path('test-map/', TemplateView.as_view(template_name='test_map.html'), name='test_map'),
]
