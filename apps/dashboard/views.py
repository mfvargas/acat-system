from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q
from apps.complaints.models import EnvironmentalComplaint, ComplaintType
from apps.core.models import ProtectedArea
from django.utils import timezone
from datetime import timedelta


class DashboardView(TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas
        context['total_complaints'] = EnvironmentalComplaint.objects.count()
        context['total_protected_areas'] = ProtectedArea.objects.count()
        
        # Denuncias por estado
        context['complaints_by_status'] = EnvironmentalComplaint.objects.values(
            'status'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Denuncias recientes (últimos 30 días)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['recent_complaints'] = EnvironmentalComplaint.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        # Denuncias por tipo
        context['complaints_by_type'] = EnvironmentalComplaint.objects.values(
            'complaint_type__name'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        # Últimas denuncias
        context['latest_complaints'] = EnvironmentalComplaint.objects.select_related(
            'protected_area', 'complaint_type'
        ).order_by('-created_at')[:5]
        
        return context


class StatsView(TemplateView):
    template_name = 'dashboard/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas detalladas por mes
        context['monthly_stats'] = self.get_monthly_stats()
        context['complaint_types'] = ComplaintType.objects.annotate(
            complaint_count=Count('environmentalcomplaint')
        ).order_by('-complaint_count')
        
        return context
    
    def get_monthly_stats(self):
        # Obtener estadísticas de los últimos 12 meses
        from django.db.models.functions import TruncMonth
        
        return EnvironmentalComplaint.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')


class MapView(TemplateView):
    template_name = 'dashboard/map.html'
    
    def get_context_data(self, **kwargs):
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        context = super().get_context_data(**kwargs)
        
        # Obtener denuncias con coordenadas para el mapa
        complaints_queryset = EnvironmentalComplaint.objects.filter(
            location__isnull=False
        ).select_related('protected_area', 'complaint_type')
        
        # Convertir a lista de diccionarios para JSON
        complaints_data = []
        for complaint in complaints_queryset:
            complaints_data.append({
                'id': complaint.id,
                'sitada': complaint.sitada_number or 'Sin SITADA',
                'accused': complaint.accused_name,
                'type': complaint.complaint_type.name if complaint.complaint_type else 'Sin tipo',
                'area': complaint.protected_area.name if complaint.protected_area else 'Sin área',
                'status': complaint.status,
                'date': complaint.created_at.strftime('%d/%m/%Y'),
                'description': complaint.description[:100] if complaint.description else '',
                'location': str(complaint.location)  # Convert to string
            })
        
        # Serializar a JSON para usar en JavaScript
        context['complaints_json'] = json.dumps(complaints_data, cls=DjangoJSONEncoder)
        context['complaints_with_location'] = complaints_data  # Para el contador
        context['protected_areas'] = ProtectedArea.objects.all()
        
        return context
