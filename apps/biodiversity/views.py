import json
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Max
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Species, Occurrence, ConservationStatus
from .serializers import SpeciesSerializer, OccurrenceSerializer


class SpeciesListView(ListView):
    """List view for species with filtering capabilities"""
    model = Species
    template_name = 'biodiversity/species_list.html'
    context_object_name = 'species_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Species.objects.select_related('conservation_status').prefetch_related('occurrences')
        
        # Apply filters
        kingdom = self.request.GET.get('kingdom')
        family = self.request.GET.get('family')
        genus = self.request.GET.get('genus')
        search = self.request.GET.get('search')
        conservation_filter = self.request.GET.get('conservation')
        
        if kingdom:
            queryset = queryset.filter(kingdom=kingdom)
        if family:
            queryset = queryset.filter(family=family)
        if genus:
            queryset = queryset.filter(genus=genus)
        if search:
            queryset = queryset.filter(
                Q(scientific_name__icontains=search) |
                Q(common_name__icontains=search) |
                Q(genus__icontains=search) |
                Q(species__icontains=search) |
                Q(family__icontains=search)
            )
        if conservation_filter == 'threatened':
            # Filter for species with any threatened status
            queryset = queryset.filter(
                Q(conservation_status__rlcvs_status__in=['PE', 'PRA']) |
                Q(conservation_status__cites_status__in=['AI', 'AII', 'AIII']) |
                Q(conservation_status__iucn_status__in=['CR', 'EN', 'VU', 'NT'])
            )
        elif conservation_filter == 'endemic':
            queryset = queryset.filter(conservation_status__endemic_to_acat=True)
        
        return queryset.annotate(occurrence_count=Count('occurrences')).order_by('family', 'genus', 'species')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['kingdoms'] = Species.objects.values_list('kingdom', flat=True).distinct().order_by('kingdom')
        context['families'] = Species.objects.values_list('family', flat=True).distinct().order_by('family')
        context['genera'] = Species.objects.values_list('genus', flat=True).distinct().order_by('genus')
        
        # Preserve current filters in context
        context['current_filters'] = {
            'kingdom': self.request.GET.get('kingdom', ''),
            'family': self.request.GET.get('family', ''),
            'genus': self.request.GET.get('genus', ''),
            'search': self.request.GET.get('search', ''),
            'conservation': self.request.GET.get('conservation', ''),
        }
        
        # Statistics
        context['total_species'] = Species.objects.count()
        context['total_occurrences'] = Occurrence.objects.count()
        context['threatened_species'] = Species.objects.filter(
            Q(conservation_status__rlcvs_status__in=['PE', 'PRA']) |
            Q(conservation_status__cites_status__in=['AI', 'AII', 'AIII']) |
            Q(conservation_status__iucn_status__in=['CR', 'EN', 'VU', 'NT'])
        ).count()
        
        return context


class SpeciesDetailView(DetailView):
    """Detail view for individual species"""
    model = Species
    template_name = 'biodiversity/species_detail.html'
    context_object_name = 'species'
    
    def get_queryset(self):
        return Species.objects.select_related('conservation_status').prefetch_related(
            'occurrences__species'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species = self.object
        
        # Get occurrences for this species
        occurrences = species.occurrences.all().order_by('-event_date')
        context['occurrences'] = occurrences[:10]  # Show first 10
        context['total_occurrences'] = occurrences.count()
        
        # Geographic distribution
        if occurrences.exists():
            context['has_occurrences'] = True
            # Get bounding box for map
            bounds = occurrences.aggregate(
                min_lat=Max('decimal_latitude'),
                max_lat=Max('decimal_latitude'),
                min_lon=Max('decimal_longitude'),
                max_lon=Max('decimal_longitude')
            )
            context['map_bounds'] = bounds
        else:
            context['has_occurrences'] = False
        
        # Temporal distribution
        yearly_counts = occurrences.filter(year__isnull=False).values('year').annotate(
            count=Count('id')
        ).order_by('year')
        context['yearly_distribution'] = list(yearly_counts)
        
        # Related species (same genus)
        context['related_species'] = Species.objects.filter(
            genus=species.genus
        ).exclude(id=species.id).annotate(
            occurrence_count=Count('occurrences')
        )[:5]
        
        return context


class OccurrenceListView(ListView):
    """List view for occurrence records"""
    model = Occurrence
    template_name = 'biodiversity/occurrence_list.html'
    context_object_name = 'occurrences'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Occurrence.objects.select_related('species').order_by('-event_date', '-created_at')
        
        # Apply filters
        species_id = self.request.GET.get('species')
        family = self.request.GET.get('family')
        year = self.request.GET.get('year')
        province = self.request.GET.get('province')
        search = self.request.GET.get('search')
        
        if species_id:
            queryset = queryset.filter(species_id=species_id)
        if family:
            queryset = queryset.filter(species__family=family)
        if year:
            queryset = queryset.filter(year=year)
        if province:
            queryset = queryset.filter(state_province__icontains=province)
        if search:
            queryset = queryset.filter(
                Q(species__scientific_name__icontains=search) |
                Q(locality__icontains=search) |
                Q(species__common_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter options
        context['families'] = Species.objects.values_list('family', flat=True).distinct().order_by('family')
        context['years'] = Occurrence.objects.filter(year__isnull=False).values_list('year', flat=True).distinct().order_by('-year')
        context['provinces'] = Occurrence.objects.filter(state_province__isnull=False).values_list('state_province', flat=True).distinct().order_by('state_province')
        
        # Current filters
        context['current_filters'] = {
            'species': self.request.GET.get('species', ''),
            'family': self.request.GET.get('family', ''),
            'year': self.request.GET.get('year', ''),
            'province': self.request.GET.get('province', ''),
            'search': self.request.GET.get('search', ''),
        }
        
        return context


class OccurrenceDetailView(DetailView):
    """Detail view for individual occurrence records"""
    model = Occurrence
    template_name = 'biodiversity/occurrence_detail.html'
    context_object_name = 'occurrence'
    
    def get_queryset(self):
        return Occurrence.objects.select_related('species')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        occurrence = self.object
        
        # Nearby occurrences (within 10km)
        if occurrence.location:
            nearby = Occurrence.objects.filter(
                location__distance_lte=(occurrence.location, 10000)  # 10km in meters
            ).exclude(id=occurrence.id).select_related('species')[:10]
            context['nearby_occurrences'] = nearby
        
        # Other occurrences of the same species
        context['species_occurrences'] = Occurrence.objects.filter(
            species=occurrence.species
        ).exclude(id=occurrence.id).order_by('-event_date')[:5]
        
        return context


class OccurrenceMapView(TemplateView):
    """Map view showing all occurrence records"""
    template_name = 'biodiversity/occurrence_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter options for map
        context['families'] = Species.objects.values_list('family', flat=True).distinct().order_by('family')
        context['years'] = Occurrence.objects.filter(year__isnull=False).values_list('year', flat=True).distinct().order_by('-year')
        
        return context


class SpeciesMapView(DetailView):
    """Map view for occurrences of a specific species"""
    model = Species
    template_name = 'biodiversity/species_map.html'
    context_object_name = 'species'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        species = self.object
        
        # Get all occurrences for this species
        occurrences = species.occurrences.all()
        context['occurrences'] = occurrences
        context['total_occurrences'] = occurrences.count()
        
        return context


class StatisticsView(TemplateView):
    """Statistics and summary view"""
    template_name = 'biodiversity/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # General statistics
        context['total_species'] = Species.objects.count()
        context['total_occurrences'] = Occurrence.objects.count()
        
        # Taxonomic breakdown
        context['kingdom_stats'] = Species.objects.values('kingdom').annotate(
            species_count=Count('id'),
            occurrence_count=Count('occurrences')
        ).order_by('-species_count')
        
        context['family_stats'] = Species.objects.values('family').annotate(
            species_count=Count('id'),
            occurrence_count=Count('occurrences')
        ).order_by('-species_count')[:20]  # Top 20 families
        
        # Conservation statistics
        context['conservation_stats'] = {
            'rlcvs_threatened': Species.objects.filter(conservation_status__rlcvs_status__in=['PE', 'PRA']).count(),
            'cites_listed': Species.objects.filter(conservation_status__cites_status__in=['AI', 'AII', 'AIII']).count(),
            'iucn_threatened': Species.objects.filter(conservation_status__iucn_status__in=['CR', 'EN', 'VU', 'NT']).count(),
            'endemic_acat': Species.objects.filter(conservation_status__endemic_to_acat=True).count(),
        }
        
        # Temporal statistics
        context['yearly_stats'] = Occurrence.objects.filter(year__isnull=False).values('year').annotate(
            occurrence_count=Count('id'),
            species_count=Count('species', distinct=True)
        ).order_by('year')
        
        # Recent activity
        context['recent_species'] = Species.objects.filter(last_gbif_update__isnull=False).order_by('-last_gbif_update')[:10]
        context['recent_occurrences'] = Occurrence.objects.order_by('-created_at')[:10]
        
        return context


# API Views for AJAX requests
class SpeciesListAPIView(APIView):
    """API endpoint for species list with filtering"""
    
    def get(self, request):
        queryset = Species.objects.all()
        
        # Apply filters
        family = request.GET.get('family')
        genus = request.GET.get('genus')
        search = request.GET.get('search')
        
        if family:
            queryset = queryset.filter(family=family)
        if genus:
            queryset = queryset.filter(genus=genus)
        if search:
            queryset = queryset.filter(scientific_name__icontains=search)
        
        serializer = SpeciesSerializer(queryset[:100], many=True)  # Limit to 100
        return Response(serializer.data)


class OccurrenceListAPIView(APIView):
    """API endpoint for occurrence list with filtering"""
    
    def get(self, request):
        queryset = Occurrence.objects.select_related('species')
        
        species_id = request.GET.get('species_id')
        if species_id:
            queryset = queryset.filter(species_id=species_id)
        
        serializer = OccurrenceSerializer(queryset[:1000], many=True)  # Limit to 1000
        return Response(serializer.data)


class MapDataAPIView(APIView):
    """API endpoint for map data (GeoJSON format)"""
    
    def get(self, request):
        queryset = Occurrence.objects.select_related('species')
        
        # Apply filters
        family = request.GET.get('family')
        species_id = request.GET.get('species_id')
        year = request.GET.get('year')
        bbox = request.GET.get('bbox')  # Format: "min_lon,min_lat,max_lon,max_lat"
        
        if family:
            queryset = queryset.filter(species__family=family)
        if species_id:
            queryset = queryset.filter(species_id=species_id)
        if year:
            queryset = queryset.filter(year=year)
        if bbox:
            try:
                min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                bbox_polygon = Polygon.from_bbox((min_lon, min_lat, max_lon, max_lat))
                queryset = queryset.filter(location__within=bbox_polygon)
            except (ValueError, TypeError):
                pass
        
        # Limit results for performance
        queryset = queryset[:5000]
        
        # Build GeoJSON
        features = []
        for occurrence in queryset:
            if occurrence.location:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [occurrence.location.x, occurrence.location.y]
                    },
                    "properties": {
                        "id": occurrence.id,
                        "species": occurrence.species.scientific_name,
                        "family": occurrence.species.family,
                        "locality": occurrence.locality,
                        "event_date": occurrence.event_date.isoformat() if occurrence.event_date else None,
                        "basis_of_record": occurrence.basis_of_record,
                    }
                }
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return Response(geojson)


# Export Views
class SpeciesExportView(ListView):
    """Export species data as CSV"""
    model = Species
    
    def get(self, request, *args, **kwargs):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="especies_acat.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Taxon Key', 'Reino', 'Filo', 'Clase', 'Orden', 'Familia', 
            'Género', 'Especie', 'Nombre Científico', 'Nombre Común',
            'Registros de Presencia', 'RLCVS', 'CITES', 'UICN', 'Endémica ACAT'
        ])
        
        species_list = Species.objects.select_related('conservation_status').annotate(
            occurrence_count=Count('occurrences')
        )
        
        for species in species_list:
            conservation = getattr(species, 'conservation_status', None)
            writer.writerow([
                species.taxon_key,
                species.kingdom,
                species.phylum,
                species.class_name,
                species.order,
                species.family,
                species.genus,
                species.species,
                species.scientific_name,
                species.common_name or '',
                species.occurrence_count,
                conservation.rlcvs_status if conservation else '',
                conservation.cites_status if conservation else '',
                conservation.iucn_status if conservation else '',
                'Sí' if conservation and conservation.endemic_to_acat else 'No',
            ])
        
        return response


class OccurrenceExportView(ListView):
    """Export occurrence data as CSV"""
    model = Occurrence
    
    def get(self, request, *args, **kwargs):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registros_presencia_acat.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'GBIF ID', 'Especie', 'Familia', 'Latitud', 'Longitud', 
            'Fecha', 'Año', 'Localidad', 'Provincia', 'Tipo de Registro'
        ])
        
        occurrences = Occurrence.objects.select_related('species')
        
        for occurrence in occurrences:
            writer.writerow([
                occurrence.gbif_id,
                occurrence.species.scientific_name,
                occurrence.species.family,
                occurrence.decimal_latitude,
                occurrence.decimal_longitude,
                occurrence.event_date.isoformat() if occurrence.event_date else '',
                occurrence.year or '',
                occurrence.locality,
                occurrence.state_province,
                occurrence.basis_of_record,
            ])
        
        return response
