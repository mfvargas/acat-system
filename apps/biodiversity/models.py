from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.urls import reverse


class Species(models.Model):
    """
    Darwin Core Species model - taxonomic data from GBIF
    Based on especies.csv structure with additional conservation fields
    """
    # Darwin Core fields (from especies.csv)
    taxon_key = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name="Taxon Key (GBIF)",
        help_text="Unique identifier from GBIF"
    )
    kingdom = models.CharField(max_length=100, verbose_name="Reino")
    phylum = models.CharField(max_length=100, verbose_name="Filo")
    class_name = models.CharField(max_length=100, db_column='class', verbose_name="Clase")
    order = models.CharField(max_length=100, verbose_name="Orden")
    family = models.CharField(max_length=100, verbose_name="Familia", db_index=True)
    genus = models.CharField(max_length=100, verbose_name="Género", db_index=True)
    species = models.CharField(max_length=200, verbose_name="Especie")
    
    # Additional metadata fields
    scientific_name = models.CharField(
        max_length=300, 
        verbose_name="Nombre Científico",
        help_text="Generated from genus + species"
    )
    common_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Nombre Común"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_gbif_update = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Última actualización GBIF"
    )
    
    class Meta:
        db_table = 'biodiversity_species'
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ['family', 'genus', 'species']
        indexes = [
            models.Index(fields=['family', 'genus']),
            models.Index(fields=['kingdom', 'phylum', 'class_name']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate scientific name
        if self.genus and self.species:
            self.scientific_name = f"{self.genus} {self.species}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.scientific_name or f"{self.genus} {self.species}"
    
    def get_absolute_url(self):
        return reverse('biodiversity:species_detail', kwargs={'pk': self.pk})
    
    @property
    def occurrence_count(self):
        """Count of occurrence records for this species"""
        return self.occurrences.count()


class ConservationStatus(models.Model):
    """
    Conservation status for species - separate model to persist through GBIF updates
    """
    # RLCVS (Reglamento a la Ley de Conservación de la Vida Silvestre)
    class RLCVSChoices(models.TextChoices):
        PE = 'PE', 'En peligro de extinción'
        PRA = 'PRA', 'Población reducida o amenazada'
        NR = 'NR', 'No registrada en lista'
    
    # CITES
    class CITESChoices(models.TextChoices):
        AI = 'AI', 'Apéndice I'
        AII = 'AII', 'Apéndice II'
        AIII = 'AIII', 'Apéndice III'
        NONE = 'NONE', 'No listada en CITES'
    
    # UICN Lista Roja
    class IUCNChoices(models.TextChoices):
        CR = 'CR', 'En peligro crítico'
        EN = 'EN', 'En peligro'
        VU = 'VU', 'Vulnerable'
        NT = 'NT', 'Casi amenazada'
        LC = 'LC', 'Preocupación menor'
        DD = 'DD', 'Datos insuficientes'
        NE = 'NE', 'No evaluada'
    
    species = models.OneToOneField(
        Species,
        on_delete=models.CASCADE,
        related_name='conservation_status',
        verbose_name="Especie"
    )
    
    # Conservation classifications
    rlcvs_status = models.CharField(
        max_length=3,
        choices=RLCVSChoices.choices,
        default=RLCVSChoices.NR,
        verbose_name="Estado RLCVS"
    )
    cites_status = models.CharField(
        max_length=4,
        choices=CITESChoices.choices,
        default=CITESChoices.NONE,
        verbose_name="Estado CITES"
    )
    iucn_status = models.CharField(
        max_length=2,
        choices=IUCNChoices.choices,
        default=IUCNChoices.NE,
        verbose_name="Estado UICN"
    )
    
    # Additional fields
    endemic_to_acat = models.BooleanField(
        default=False,
        verbose_name="Endémica del ACAT"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas adicionales"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'biodiversity_conservation_status'
        verbose_name = "Estado de Conservación"
        verbose_name_plural = "Estados de Conservación"
    
    def __str__(self):
        return f"{self.species.scientific_name} - RLCVS: {self.rlcvs_status}, CITES: {self.cites_status}, UICN: {self.iucn_status}"
    
    @property
    def is_threatened(self):
        """Check if species has any threatened status"""
        threatened_rlcvs = ['PE', 'PRA']
        threatened_cites = ['AI', 'AII', 'AIII']
        threatened_iucn = ['CR', 'EN', 'VU', 'NT']
        
        return (
            self.rlcvs_status in threatened_rlcvs or
            self.cites_status in threatened_cites or
            self.iucn_status in threatened_iucn
        )


class Occurrence(models.Model):
    """
    Darwin Core Occurrence model - presence records from GBIF
    Based on registros-presencia.gpkg structure
    """
    # Darwin Core fields (from registros-presencia.gpkg)
    gbif_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name="GBIF ID",
        help_text="Unique occurrence identifier from GBIF"
    )
    dataset_key = models.CharField(
        max_length=100,
        verbose_name="Dataset Key"
    )
    occurrence_id = models.CharField(
        max_length=200,
        verbose_name="Occurrence ID"
    )
    
    # Link to species
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name='occurrences',
        verbose_name="Especie"
    )
    
    # Geographic data (PostGIS)
    location = models.PointField(
        srid=4326,  # WGS84
        verbose_name="Ubicación",
        help_text="Coordinates in WGS84 (EPSG:4326)"
    )
    decimal_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Longitud Decimal"
    )
    decimal_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="Latitud Decimal"
    )
    
    # Additional Darwin Core fields
    scientific_name = models.CharField(
        max_length=300,
        verbose_name="Nombre Científico"
    )
    taxon_rank = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Rango Taxonómico"
    )
    country_code = models.CharField(
        max_length=2,
        default='CR',
        verbose_name="Código de País"
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Provincia"
    )
    locality = models.TextField(
        blank=True,
        verbose_name="Localidad"
    )
    
    # Collection/observation metadata
    basis_of_record = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de Registro"
    )
    institution_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Código de Institución"
    )
    collection_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Código de Colección"
    )
    
    # Date information
    event_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha del Evento"
    )
    year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Año"
    )
    month = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mes"
    )
    day = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Día"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_gbif_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última actualización GBIF"
    )
    
    class Meta:
        db_table = 'biodiversity_occurrence'
        verbose_name = "Registro de Presencia"
        verbose_name_plural = "Registros de Presencia"
        ordering = ['-event_date', '-created_at']
        indexes = [
            models.Index(fields=['species', 'event_date']),
            models.Index(fields=['country_code', 'state_province']),
            models.Index(fields=['year', 'month']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-create Point from lat/lon
        if self.decimal_longitude and self.decimal_latitude:
            self.location = Point(
                float(self.decimal_longitude),
                float(self.decimal_latitude),
                srid=4326
            )
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validate coordinates are within Costa Rica bounds approximately
        if self.decimal_latitude and self.decimal_longitude:
            if not (8.0 <= float(self.decimal_latitude) <= 11.5):
                raise ValidationError("Latitude should be within Costa Rica bounds")
            if not (-87.0 <= float(self.decimal_longitude) <= -82.5):
                raise ValidationError("Longitude should be within Costa Rica bounds")
    
    def __str__(self):
        return f"{self.species.scientific_name} - {self.locality or 'Sin localidad'} ({self.event_date or 'Sin fecha'})"
    
    def get_absolute_url(self):
        return reverse('biodiversity:occurrence_detail', kwargs={'pk': self.pk})


class DataImportLog(models.Model):
    """
    Log of data import operations from Darwin Core files
    """
    class StatusChoices(models.TextChoices):
        STARTED = 'STARTED', 'Iniciado'
        SUCCESS = 'SUCCESS', 'Exitoso'
        ERROR = 'ERROR', 'Error'
        PARTIAL = 'PARTIAL', 'Parcial'
    
    import_type = models.CharField(
        max_length=20,
        choices=[
            ('species', 'Importación de Especies'),
            ('occurrences', 'Importación de Registros'),
            ('full', 'Importación Completa')
        ],
        verbose_name="Tipo de Importación"
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.STARTED,
        verbose_name="Estado"
    )
    
    # Counters
    records_processed = models.IntegerField(default=0, verbose_name="Registros Procesados")
    records_created = models.IntegerField(default=0, verbose_name="Registros Creados")
    records_updated = models.IntegerField(default=0, verbose_name="Registros Actualizados")
    records_errors = models.IntegerField(default=0, verbose_name="Errores")
    
    # Files and metadata
    source_file = models.CharField(max_length=500, verbose_name="Archivo Fuente")
    file_size = models.BigIntegerField(null=True, verbose_name="Tamaño del Archivo")
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Iniciado")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completado")
    duration_seconds = models.IntegerField(null=True, verbose_name="Duración (segundos)")
    
    # Log messages
    log_messages = models.TextField(blank=True, verbose_name="Mensajes de Log")
    error_details = models.TextField(blank=True, verbose_name="Detalles de Errores")
    
    class Meta:
        db_table = 'biodiversity_data_import_log'
        verbose_name = "Log de Importación"
        verbose_name_plural = "Logs de Importación"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_import_type_display()} - {self.get_status_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.records_processed == 0:
            return 0
        return ((self.records_processed - self.records_errors) / self.records_processed) * 100
