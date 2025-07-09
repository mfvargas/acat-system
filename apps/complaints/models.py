from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel, ProtectedArea, Sector


class ComplaintType(BaseModel):
    """
    Tipo de denuncia ambiental
    """
    name = models.CharField(_('Nombre'), max_length=200)
    description = models.TextField(_('Descripción'), blank=True)
    
    class Meta:
        verbose_name = _('Tipo de Denuncia')
        verbose_name_plural = _('Tipos de Denuncia')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InfractionType(BaseModel):
    """
    Tipo de infracción ambiental
    """
    name = models.CharField(_('Nombre'), max_length=200)
    description = models.TextField(_('Descripción'), blank=True)
    severity_level = models.CharField(
        _('Nivel de Severidad'),
        max_length=20,
        choices=[
            ('LEVE', _('Leve')),
            ('MODERADA', _('Moderada')),
            ('GRAVE', _('Grave')),
            ('MUY_GRAVE', _('Muy Grave')),
        ],
        default='MODERADA'
    )
    
    class Meta:
        verbose_name = _('Tipo de Infracción')
        verbose_name_plural = _('Tipos de Infracción')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class EnvironmentalComplaint(BaseModel):
    """
    Denuncia Ambiental
    """
    # Números de referencia
    sitada_number = models.CharField(
        _('Número en SITADA'), 
        max_length=100, 
        unique=True
    )
    police_report_number = models.CharField(
        _('Número de informe policial'), 
        max_length=100, 
        blank=True
    )
    
    # Ubicación geográfica
    location = models.PointField(
        _('Ubicación'), 
        srid=4326,
        help_text=_('Coordenadas geográficas del incidente')
    )
    protected_area = models.ForeignKey(
        ProtectedArea,
        on_delete=models.CASCADE,
        verbose_name=_('Área Silvestre Protegida'),
        related_name='complaints'
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        verbose_name=_('Sector'),
        related_name='complaints'
    )
    
    # Detalles del incidente
    infraction_date = models.DateField(_('Fecha de la infracción'))
    accused_name = models.CharField(_('Nombre del imputado'), max_length=200)
    complaint_type = models.ForeignKey(
        ComplaintType,
        on_delete=models.CASCADE,
        verbose_name=_('Tipo de denuncia'),
        related_name='complaints'
    )
    infraction_name = models.ForeignKey(
        InfractionType,
        on_delete=models.CASCADE,
        verbose_name=_('Nombre de infracción'),
        related_name='complaints'
    )
    
    # Información adicional
    description = models.TextField(
        _('Descripción detallada'), 
        blank=True,
        help_text=_('Descripción detallada del incidente')
    )
    evidence_photos = models.JSONField(
        _('Fotos de evidencia'),
        default=list,
        blank=True,
        help_text=_('URLs de las fotos de evidencia')
    )
    
    # Estado de la denuncia
    status = models.CharField(
        _('Estado'),
        max_length=20,
        choices=[
            ('pending', _('Pendiente')),
            ('in_progress', _('En Proceso')),
            ('resolved', _('Resuelto')),
            ('dismissed', _('Desestimado')),
        ],
        default='pending'
    )
    
    # Metadatos
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Creado por'),
        related_name='created_complaints'
    )
    
    # Propiedades calculadas
    @property
    def coordinates_x(self):
        """Coordenada X (Longitud)"""
        return self.location.x if self.location else None
    
    @property
    def coordinates_y(self):
        """Coordenada Y (Latitud)"""
        return self.location.y if self.location else None
    
    class Meta:
        verbose_name = _('Denuncia Ambiental')
        verbose_name_plural = _('Denuncias Ambientales')
        ordering = ['-infraction_date', '-created_at']
        indexes = [
            models.Index(fields=['sitada_number']),
            models.Index(fields=['infraction_date']),
            models.Index(fields=['status']),
            models.Index(fields=['protected_area', 'sector']),
        ]
    
    def __str__(self):
        return f"SITADA {self.sitada_number} - {self.accused_name}"
