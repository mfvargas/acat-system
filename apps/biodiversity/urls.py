from django.urls import path
from . import views

app_name = 'biodiversity'

urlpatterns = [
    # Species views
    path('', views.SpeciesListView.as_view(), name='species_list'),
    path('especies/', views.SpeciesListView.as_view(), name='species_list_alt'),
    path('especies/<int:pk>/', views.SpeciesDetailView.as_view(), name='species_detail'),
    
    # Occurrence views
    path('registros/', views.OccurrenceListView.as_view(), name='occurrence_list'),
    path('registros/<int:pk>/', views.OccurrenceDetailView.as_view(), name='occurrence_detail'),
    
    # Map views
    path('mapa/', views.OccurrenceMapView.as_view(), name='occurrence_map'),
    path('especies/<int:pk>/mapa/', views.SpeciesMapView.as_view(), name='species_map'),
    
    # API endpoints for AJAX requests
    path('api/especies/', views.SpeciesListAPIView.as_view(), name='api_species_list'),
    path('api/registros/', views.OccurrenceListAPIView.as_view(), name='api_occurrence_list'),
    path('api/mapa-data/', views.MapDataAPIView.as_view(), name='api_map_data'),
    
    # Statistics and reports
    path('estadisticas/', views.StatisticsView.as_view(), name='statistics'),
    path('export/especies/', views.SpeciesExportView.as_view(), name='export_species'),
    path('export/registros/', views.OccurrenceExportView.as_view(), name='export_occurrences'),
]
