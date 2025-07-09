from django.contrib import admin
from .models import ProtectedArea, Sector


@admin.register(ProtectedArea)
class ProtectedAreaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)
    list_editable = ('is_active',)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'protected_area', 'is_active', 'created_at')
    list_filter = ('protected_area', 'is_active', 'created_at')
    search_fields = ('name', 'protected_area__name')
    ordering = ('protected_area__name', 'name')
    list_editable = ('is_active',)
