from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Species, ConservationStatus, Occurrence, DataImportLog


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = [
        'scientific_name',
        'family',
        'genus',
        'kingdom',
        'occurrence_count_display',
        'conservation_status_display',
        'last_gbif_update',
    ]
    list_filter = [
        'kingdom',
        'phylum',
        'class_name',
        'order',
        'family',
        'last_gbif_update',
    ]
    search_fields = [
        'scientific_name',
        'genus',
        'species',
        'family',
        'common_name',
    ]
    readonly_fields = [
        'taxon_key',
        'scientific_name',
        'created_at',
        'updated_at',
        'last_gbif_update',
        'occurrence_count_display',
    ]
    fieldsets = (
        ('Información Taxonómica', {
            'fields': (
                'taxon_key',
                'scientific_name',
                ('kingdom', 'phylum'),
                ('class_name', 'order'),
                ('family', 'genus', 'species'),
            )
        }),
        ('Información Adicional', {
            'fields': (
                'common_name',
                'occurrence_count_display',
            )
        }),
        ('Metadatos', {
            'fields': (
                'created_at',
                'updated_at',
                'last_gbif_update',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'conservation_status'
        ).prefetch_related('occurrences')
    
    def occurrence_count_display(self, obj):
        count = obj.occurrence_count
        if count > 0:
            url = reverse('admin:biodiversity_occurrence_changelist') + f'?species__id__exact={obj.id}'
            return format_html(
                '<a href="{}">{} registros</a>',
                url,
                count
            )
        return '0 registros'
    occurrence_count_display.short_description = 'Registros de Presencia'
    
    def conservation_status_display(self, obj):
        try:
            status = obj.conservation_status
            badges = []
            
            if status.rlcvs_status != 'NR':
                badges.append(f'<span class="badge badge-warning">RLCVS: {status.rlcvs_status}</span>')
            
            if status.cites_status != 'NONE':
                badges.append(f'<span class="badge badge-danger">CITES: {status.cites_status}</span>')
            
            if status.iucn_status not in ['LC', 'NE']:
                badges.append(f'<span class="badge badge-info">UICN: {status.iucn_status}</span>')
            
            if status.endemic_to_acat:
                badges.append('<span class="badge badge-success">Endémica ACAT</span>')
            
            if badges:
                return mark_safe(' '.join(badges))
            return '-'
        except ConservationStatus.DoesNotExist:
            return mark_safe('<span class="badge badge-secondary">Sin estado</span>')
    conservation_status_display.short_description = 'Estado de Conservación'


@admin.register(ConservationStatus)
class ConservationStatusAdmin(admin.ModelAdmin):
    list_display = [
        'species',
        'rlcvs_status',
        'cites_status',
        'iucn_status',
        'endemic_to_acat',
        'is_threatened',
        'updated_at',
    ]
    list_filter = [
        'rlcvs_status',
        'cites_status',
        'iucn_status',
        'endemic_to_acat',
        'updated_at',
    ]
    search_fields = [
        'species__scientific_name',
        'species__genus',
        'species__family',
        'notes',
    ]
    autocomplete_fields = ['species']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Especie', {
            'fields': ('species',)
        }),
        ('Estados de Conservación', {
            'fields': (
                ('rlcvs_status', 'cites_status', 'iucn_status'),
                'endemic_to_acat',
            )
        }),
        ('Información Adicional', {
            'fields': ('notes',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_threatened(self, obj):
        return obj.is_threatened
    is_threatened.boolean = True
    is_threatened.short_description = 'Amenazada'


@admin.register(Occurrence)
class OccurrenceAdmin(gis_admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {'default_zoom': 8, 'default_lon': -84.0, 'default_lat': 10.0}
    }
    
    list_display = [
        'species',
        'gbif_id',
        'locality_short',
        'decimal_latitude',
        'decimal_longitude',
        'event_date',
        'basis_of_record',
    ]
    list_filter = [
        'species__kingdom',
        'species__family',
        'basis_of_record',
        'country_code',
        'state_province',
        'event_date',
        'year',
        'last_gbif_update',
    ]
    search_fields = [
        'species__scientific_name',
        'species__genus',
        'species__family',
        'locality',
        'gbif_id',
        'occurrence_id',
    ]
    readonly_fields = [
        'gbif_id',
        'dataset_key',
        'occurrence_id',
        'scientific_name',
        'location',
        'created_at',
        'updated_at',
        'last_gbif_update',
    ]
    autocomplete_fields = ['species']
    
    fieldsets = (
        ('Información de la Especie', {
            'fields': (
                'species',
                'scientific_name',
                'taxon_rank',
            )
        }),
        ('Identificadores GBIF', {
            'fields': (
                'gbif_id',
                'dataset_key', 
                'occurrence_id',
            )
        }),
        ('Ubicación Geográfica', {
            'fields': (
                ('decimal_latitude', 'decimal_longitude'),
                'location',
                'country_code',
                'state_province',
                'locality',
            )
        }),
        ('Información Temporal', {
            'fields': (
                'event_date',
                ('year', 'month', 'day'),
            )
        }),
        ('Metadatos de Colección', {
            'fields': (
                'basis_of_record',
                'institution_code',
                'collection_code',
            )
        }),
        ('Metadatos del Sistema', {
            'fields': (
                'created_at',
                'updated_at',
                'last_gbif_update',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def locality_short(self, obj):
        if obj.locality:
            return obj.locality[:50] + ('...' if len(obj.locality) > 50 else '')
        return obj.state_province or '-'
    locality_short.short_description = 'Localidad'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('species')


@admin.register(DataImportLog)
class DataImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'import_type',
        'status',
        'records_processed',
        'success_rate_display',
        'duration_display',
        'started_at',
    ]
    list_filter = [
        'import_type',
        'status',
        'started_at',
    ]
    readonly_fields = [
        'import_type',
        'status',
        'records_processed',
        'records_created',
        'records_updated',
        'records_errors',
        'source_file',
        'file_size',
        'started_at',
        'completed_at',
        'duration_seconds',
        'success_rate_display',
    ]
    
    fieldsets = (
        ('Información de la Importación', {
            'fields': (
                'import_type',
                'status',
                'source_file',
                'file_size',
            )
        }),
        ('Estadísticas', {
            'fields': (
                ('records_processed', 'records_created'),
                ('records_updated', 'records_errors'),
                'success_rate_display',
            )
        }),
        ('Tiempos', {
            'fields': (
                'started_at',
                'completed_at',
                'duration_seconds',
            )
        }),
        ('Logs y Errores', {
            'fields': (
                'log_messages',
                'error_details',
            )
        }),
    )
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 95:
            color = 'green'
        elif rate >= 80:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Tasa de Éxito'
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f'{obj.duration_seconds:.1f}s'
            elif obj.duration_seconds < 3600:
                return f'{obj.duration_seconds/60:.1f}m'
            else:
                return f'{obj.duration_seconds/3600:.1f}h'
        return '-'
    duration_display.short_description = 'Duration'
    
    def has_add_permission(self, request):
        # Import logs are created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Import logs are read-only
        return False


# Custom admin site customization
admin.site.site_header = "ACAT - Administración de Biodiversidad"
admin.site.site_title = "ACAT Biodiversity Admin"
admin.site.index_title = "Gestión del Inventario de Biodiversidad"
