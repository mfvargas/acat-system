from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import ComplaintType, InfractionType, EnvironmentalComplaint


@admin.register(ComplaintType)
class ComplaintTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('is_active',)


@admin.register(InfractionType)
class InfractionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity_level', 'is_active', 'created_at')
    list_filter = ('severity_level', 'is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('is_active',)


@admin.register(EnvironmentalComplaint)
class EnvironmentalComplaintAdmin(GISModelAdmin):
    list_display = (
        'sitada_number', 
        'accused_name', 
        'infraction_date',
        'protected_area',
        'status',
        'created_at'
    )
    list_filter = (
        'status',
        'protected_area',
        'complaint_type',
        'infraction_name',
        'infraction_date',
        'created_at'
    )
    search_fields = (
        'sitada_number',
        'accused_name',
        'police_report_number'
    )
    ordering = ('-infraction_date', '-created_at')
    list_editable = ('status',)
    date_hierarchy = 'infraction_date'
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'sitada_number',
                'police_report_number',
                'status'
            )
        }),
        ('Ubicación', {
            'fields': (
                'location',
                'protected_area',
                'sector'
            )
        }),
        ('Detalles del Incidente', {
            'fields': (
                'infraction_date',
                'accused_name',
                'complaint_type',
                'infraction_name',
                'description'
            )
        }),
        ('Metadatos', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
