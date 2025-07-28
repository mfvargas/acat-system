from rest_framework import serializers
from .models import Species, ConservationStatus, Occurrence, DataImportLog


class ConservationStatusSerializer(serializers.ModelSerializer):
    """Serializer for conservation status information"""
    
    class Meta:
        model = ConservationStatus
        fields = [
            'rlcvs_status',
            'cites_status', 
            'iucn_status',
            'endemic_to_acat',
            'is_threatened',
            'notes'
        ]


class SpeciesSerializer(serializers.ModelSerializer):
    """Serializer for species data"""
    conservation_status = ConservationStatusSerializer(read_only=True)
    occurrence_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Species
        fields = [
            'id',
            'taxon_key',
            'kingdom',
            'phylum',
            'class_name',
            'order',
            'family',
            'genus',
            'species',
            'scientific_name',
            'common_name',
            'conservation_status',
            'occurrence_count',
            'created_at',
            'updated_at',
            'last_gbif_update'
        ]
    
    def get_occurrence_count(self, obj):
        """Get count of occurrence records for this species"""
        return obj.occurrences.count()


class SpeciesBasicSerializer(serializers.ModelSerializer):
    """Basic serializer for species (for dropdown lists, etc.)"""
    
    class Meta:
        model = Species
        fields = [
            'id',
            'taxon_key',
            'scientific_name',
            'family',
            'genus',
            'species'
        ]


class OccurrenceSerializer(serializers.ModelSerializer):
    """Serializer for occurrence data"""
    species = SpeciesBasicSerializer(read_only=True)
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Occurrence
        fields = [
            'id',
            'gbif_id',
            'species',
            'coordinates',
            'decimal_longitude',
            'decimal_latitude',
            'locality',
            'state_province',
            'country_code',
            'event_date',
            'year',
            'month',
            'day',
            'basis_of_record',
            'institution_code',
            'collection_code',
            'created_at',
            'updated_at'
        ]
    
    def get_coordinates(self, obj):
        """Get coordinates as [longitude, latitude] array for mapping"""
        if obj.location:
            return [obj.location.x, obj.location.y]
        return None


class OccurrenceGeoJSONSerializer(serializers.ModelSerializer):
    """GeoJSON serializer for occurrence data"""
    species_name = serializers.CharField(source='species.scientific_name', read_only=True)
    family = serializers.CharField(source='species.family', read_only=True)
    
    class Meta:
        model = Occurrence
        fields = [
            'id',
            'gbif_id',
            'species_name',
            'family',
            'decimal_longitude',
            'decimal_latitude',
            'locality',
            'event_date',
            'basis_of_record'
        ]


class DataImportLogSerializer(serializers.ModelSerializer):
    """Serializer for data import logs"""
    success_rate = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DataImportLog
        fields = [
            'id',
            'import_type',
            'status',
            'records_processed',
            'records_created',
            'records_updated',
            'records_errors',
            'success_rate',
            'source_file',
            'started_at',
            'completed_at',
            'duration_seconds',
            'duration_display'
        ]
    
    def get_success_rate(self, obj):
        """Get success rate as percentage"""
        return obj.success_rate
    
    def get_duration_display(self, obj):
        """Get formatted duration"""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f'{obj.duration_seconds:.1f}s'
            elif obj.duration_seconds < 3600:
                return f'{obj.duration_seconds/60:.1f}m'
            else:
                return f'{obj.duration_seconds/3600:.1f}h'
        return None


class StatisticsSerializer(serializers.Serializer):
    """Serializer for biodiversity statistics"""
    total_species = serializers.IntegerField()
    total_occurrences = serializers.IntegerField()
    kingdom_breakdown = serializers.ListField()
    family_breakdown = serializers.ListField()
    conservation_summary = serializers.DictField()
    temporal_distribution = serializers.ListField()
