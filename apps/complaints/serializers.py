from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import EnvironmentalComplaint, ComplaintType, InfractionType
from apps.core.models import ProtectedArea, Sector


class ComplaintTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para tipos de denuncia
    """
    complaint_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ComplaintType
        fields = [
            'id', 'name', 'description', 'is_active', 
            'created_at', 'updated_at', 'complaint_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_complaint_count(self, obj):
        """Obtener cantidad de denuncias por tipo"""
        return obj.environmentalcomplaint_set.count()


class InfractionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para tipos de infracción
    """
    complaint_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InfractionType
        fields = [
            'id', 'name', 'description', 'is_active', 
            'created_at', 'updated_at', 'complaint_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_complaint_count(self, obj):
        """Obtener cantidad de denuncias por tipo de infracción"""
        return obj.environmentalcomplaint_set.count()


class EnvironmentalComplaintSerializer(serializers.ModelSerializer):
    """
    Serializer básico para denuncias ambientales
    """
    complaint_type_name = serializers.CharField(source='complaint_type.name', read_only=True)
    infraction_name_display = serializers.CharField(source='infraction_name.name', read_only=True)
    protected_area_name = serializers.CharField(source='protected_area.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EnvironmentalComplaint
        fields = [
            'id', 'sitada_number', 'accused_name', 'description',
            'complaint_type', 'complaint_type_name',
            'infraction_name', 'infraction_name_display',
            'protected_area', 'protected_area_name',
            'sector', 'sector_name',
            'location', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EnvironmentalComplaintGeoSerializer(GeoFeatureModelSerializer):
    """
    Serializer GeoJSON para denuncias ambientales con ubicación
    """
    complaint_type_name = serializers.CharField(source='complaint_type.name', read_only=True)
    protected_area_name = serializers.CharField(source='protected_area.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EnvironmentalComplaint
        geo_field = "location"
        fields = [
            'id', 'sitada_number', 'accused_name', 'description',
            'complaint_type_name', 'protected_area_name',
            'status', 'status_display', 'created_at'
        ]


# Serializers para referencias en las APIs
class ProtectedAreaSerializer(serializers.ModelSerializer):
    """Serializer para áreas protegidas"""
    class Meta:
        model = ProtectedArea
        fields = ['id', 'name', 'code', 'area_type']


class SectorSerializer(serializers.ModelSerializer):
    """Serializer para sectores"""
    protected_area_name = serializers.CharField(source='protected_area.name', read_only=True)
    
    class Meta:
        model = Sector
        fields = ['id', 'name', 'code', 'protected_area', 'protected_area_name']
