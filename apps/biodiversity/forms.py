from django import forms
from django.db.models import Q
from .models import Species, ConservationStatus, Occurrence


class SpeciesFilterForm(forms.Form):
    """Form for filtering species list"""
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre científico, común, género, familia...',
        }),
        label='Búsqueda'
    )
    
    kingdom = forms.ChoiceField(
        choices=[('', 'Todos los reinos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Reino'
    )
    
    family = forms.ChoiceField(
        choices=[('', 'Todas las familias')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Familia'
    )
    
    genus = forms.ChoiceField(
        choices=[('', 'Todos los géneros')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Género'
    )
    
    conservation = forms.ChoiceField(
        choices=[
            ('', 'Todos los estados'),
            ('threatened', 'Especies amenazadas'),
            ('endemic', 'Endémicas del ACAT'),
            ('cites', 'Listadas en CITES'),
            ('rlcvs', 'Listadas en RLCVS'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado de Conservación'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate kingdom choices
        kingdoms = Species.objects.values_list('kingdom', flat=True).distinct().order_by('kingdom')
        self.fields['kingdom'].choices += [(k, k) for k in kingdoms if k]
        
        # Dynamically populate family choices (limit to 100 for performance)
        families = Species.objects.values_list('family', flat=True).distinct().order_by('family')[:100]
        self.fields['family'].choices += [(f, f) for f in families if f]
        
        # Dynamically populate genus choices (limit to 100 for performance)
        genera = Species.objects.values_list('genus', flat=True).distinct().order_by('genus')[:100]
        self.fields['genus'].choices += [(g, g) for g in genera if g]


class OccurrenceFilterForm(forms.Form):
    """Form for filtering occurrence records"""
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por especie, localidad...',
        }),
        label='Búsqueda'
    )
    
    species = forms.ModelChoiceField(
        queryset=Species.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especie',
        empty_label='Todas las especies'
    )
    
    family = forms.ChoiceField(
        choices=[('', 'Todas las familias')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Familia'
    )
    
    year = forms.ChoiceField(
        choices=[('', 'Todos los años')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Año'
    )
    
    province = forms.ChoiceField(
        choices=[('', 'Todas las provincias')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Provincia'
    )
    
    basis_of_record = forms.ChoiceField(
        choices=[('', 'Todos los tipos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Registro'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Desde'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Hasta'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically populate species choices (limit for performance)
        self.fields['species'].queryset = Species.objects.select_related().order_by('scientific_name')[:200]
        
        # Dynamically populate family choices
        families = Species.objects.values_list('family', flat=True).distinct().order_by('family')
        self.fields['family'].choices += [(f, f) for f in families if f]
        
        # Dynamically populate year choices
        years = Occurrence.objects.filter(year__isnull=False).values_list('year', flat=True).distinct().order_by('-year')
        self.fields['year'].choices += [(y, str(y)) for y in years if y]
        
        # Dynamically populate province choices
        provinces = Occurrence.objects.filter(state_province__isnull=False).values_list('state_province', flat=True).distinct().order_by('state_province')
        self.fields['province'].choices += [(p, p) for p in provinces if p][:50]  # Limit for performance
        
        # Dynamically populate basis of record choices
        basis_records = Occurrence.objects.filter(basis_of_record__isnull=False).values_list('basis_of_record', flat=True).distinct().order_by('basis_of_record')
        self.fields['basis_of_record'].choices += [(b, b) for b in basis_records if b]


class ConservationStatusForm(forms.ModelForm):
    """Form for editing conservation status"""
    
    class Meta:
        model = ConservationStatus
        fields = [
            'species',
            'rlcvs_status',
            'cites_status',
            'iucn_status',
            'endemic_to_acat',
            'notes'
        ]
        widgets = {
            'species': forms.Select(attrs={'class': 'form-control'}),
            'rlcvs_status': forms.Select(attrs={'class': 'form-control'}),
            'cites_status': forms.Select(attrs={'class': 'form-control'}),
            'iucn_status': forms.Select(attrs={'class': 'form-control'}),
            'endemic_to_acat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas adicionales sobre el estado de conservación...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make species field use autocomplete
        self.fields['species'].queryset = Species.objects.order_by('scientific_name')
        self.fields['species'].widget.attrs.update({
            'class': 'form-control species-autocomplete'
        })


class SpeciesForm(forms.ModelForm):
    """Form for editing species information"""
    
    class Meta:
        model = Species
        fields = [
            'common_name',
        ]
        widgets = {
            'common_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre común de la especie'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all Darwin Core fields read-only since they come from GBIF
        if self.instance and self.instance.pk:
            darwin_core_fields = [
                'taxon_key', 'kingdom', 'phylum', 'class_name', 'order',
                'family', 'genus', 'species', 'scientific_name'
            ]
            for field_name in darwin_core_fields:
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs['readonly'] = True


class MapFilterForm(forms.Form):
    """Form for filtering map data"""
    
    family = forms.ChoiceField(
        choices=[('', 'Todas las familias')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Familia'
    )
    
    genus = forms.ChoiceField(
        choices=[('', 'Todos los géneros')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        label='Género'
    )
    
    year_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Desde año'
        }),
        label='Desde'
    )
    
    year_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Hasta año'
        }),
        label='Hasta'
    )
    
    conservation_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo especies amenazadas'
    )
    
    endemic_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo especies endémicas'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate family choices
        families = Species.objects.values_list('family', flat=True).distinct().order_by('family')[:50]
        self.fields['family'].choices += [(f, f) for f in families if f]
        
        # Populate genus choices
        genera = Species.objects.values_list('genus', flat=True).distinct().order_by('genus')[:50]
        self.fields['genus'].choices += [(g, g) for g in genera if g]


class ExportForm(forms.Form):
    """Form for data export options"""
    
    EXPORT_FORMATS = [
        ('csv', 'CSV (Comma Separated Values)'),
        ('excel', 'Excel (.xlsx)'),
        ('geojson', 'GeoJSON (solo registros con coordenadas)'),
    ]
    
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Formato de Exportación'
    )
    
    include_conservation = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir información de conservación'
    )
    
    include_occurrences = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir todos los registros de presencia'
    )
    
    date_range = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Filtrar por rango de fechas'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Desde'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Hasta'
    )


class ImportDataForm(forms.Form):
    """Form for importing Darwin Core data"""
    
    IMPORT_TYPES = [
        ('species', 'Solo especies (especies.csv)'),
        ('occurrences', 'Solo registros de presencia (registros-presencia.gpkg)'),
        ('full', 'Importación completa (ambos archivos)'),
    ]
    
    import_type = forms.ChoiceField(
        choices=IMPORT_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Tipo de Importación'
    )
    
    species_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        label='Archivo de Especies (CSV)',
        help_text='Archivo CSV con estructura Darwin Core para especies'
    )
    
    occurrences_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.gpkg'
        }),
        label='Archivo de Registros (GeoPackage)',
        help_text='Archivo GeoPackage con registros de presencia'
    )
    
    backup_before_import = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Crear respaldo antes de importar'
    )
    
    dry_run = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Simulación (no realizar cambios reales)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        import_type = cleaned_data.get('import_type')
        species_file = cleaned_data.get('species_file')
        occurrences_file = cleaned_data.get('occurrences_file')
        
        if import_type in ['species', 'full'] and not species_file:
            raise forms.ValidationError(
                'Se requiere el archivo de especies para este tipo de importación.'
            )
        
        if import_type in ['occurrences', 'full'] and not occurrences_file:
            raise forms.ValidationError(
                'Se requiere el archivo de registros para este tipo de importación.'
            )
        
        return cleaned_data
