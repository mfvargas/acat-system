from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import EnvironmentalComplaint, ComplaintType, InfractionType
from .serializers import (
    EnvironmentalComplaintSerializer, 
    ComplaintTypeSerializer, 
    InfractionTypeSerializer
)


class ComplaintTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tipos de denuncia
    """
    queryset = ComplaintType.objects.all()
    serializer_class = ComplaintTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class InfractionTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tipos de infracción
    """
    queryset = InfractionType.objects.all()
    serializer_class = InfractionTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class EnvironmentalComplaintViewSet(viewsets.ModelViewSet):
    """
    ViewSet para denuncias ambientales
    """
    queryset = EnvironmentalComplaint.objects.all()
    serializer_class = EnvironmentalComplaintSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros
    filterset_fields = {
        'status': ['exact', 'in'],
        'complaint_type': ['exact'],
        'infraction_name': ['exact'],
        'protected_area': ['exact'],
        'sector': ['exact'],
        'created_at': ['gte', 'lte', 'range'],
    }
    
    # Búsqueda
    search_fields = [
        'sitada_number', 
        'accused_name', 
        'description',
        'complaint_type__name',
        'protected_area__name'
    ]
    
    # Ordenamiento
    ordering_fields = [
        'created_at', 'updated_at', 'sitada_number', 
        'accused_name', 'status'
    ]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimizar consultas con select_related
        """
        return super().get_queryset().select_related(
            'complaint_type', 
            'infraction_name', 
            'protected_area', 
            'sector'
        )
