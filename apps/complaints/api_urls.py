from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'denuncias', api_views.EnvironmentalComplaintViewSet)
router.register(r'tipos-denuncia', api_views.ComplaintTypeViewSet)
router.register(r'tipos-infraccion', api_views.InfractionTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
