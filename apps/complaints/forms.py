from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from .models import EnvironmentalComplaint


class EnvironmentalComplaintForm(forms.ModelForm):
    """
    Formulario personalizado para denuncias ambientales con campos separados para latitud y longitud
    """
    
    # Campos adicionales para latitud y longitud (REQUERIDOS)
    latitude = forms.FloatField(
        label='Latitud',
        required=True,
        help_text='Coordenada Norte-Sur (valores positivos para Costa Rica: 8-12)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '10.5678',
            'step': 'any',
            'min': '8',
            'max': '12',
            'required': True
        })
    )
    
    longitude = forms.FloatField(
        label='Longitud',
        required=True,
        help_text='Coordenada Este-Oeste (valores negativos para Costa Rica: -82 a -87)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '-84.1234',
            'step': 'any',
            'min': '-87',
            'max': '-82',
            'required': True
        })
    )
    
    class Meta:
        model = EnvironmentalComplaint
        fields = [
            'sitada_number', 'accused_name', 'infraction_date', 'complaint_type', 
            'infraction_name', 'protected_area', 'sector', 
            'description', 'status'
        ]
        
        widgets = {
            'sitada_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: SITADA-2024-001'
            }),
            'accused_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del acusado'
            }),
            'infraction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'complaint_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'infraction_name': forms.Select(attrs={
                'class': 'form-select'
            }),
            'protected_area': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sector': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa detalladamente el incidente...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
        labels = {
            'sitada_number': 'Número SITADA',
            'accused_name': 'Nombre del Acusado',
            'infraction_date': 'Fecha de la Infracción',
            'complaint_type': 'Tipo de Denuncia',
            'infraction_name': 'Tipo de Infracción',
            'protected_area': 'Área Protegida',
            'sector': 'Sector',
            'description': 'Descripción',
            'status': 'Estado'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando una instancia existente, extraer lat/lng del Point
        if self.instance and self.instance.pk and self.instance.location:
            point = self.instance.location
            self.fields['longitude'].initial = point.x
            self.fields['latitude'].initial = point.y
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Verificar que ambos campos están presentes
        if latitude is None and longitude is None:
            raise ValidationError({
                'latitude': 'Las coordenadas son requeridas. Por favor proporciona latitud y longitud.',
                'longitude': 'Las coordenadas son requeridas. Por favor proporciona latitud y longitud.'
            })
        
        # Si solo se proporciona uno de los dos campos
        if latitude is None:
            raise ValidationError({'latitude': 'Este campo es requerido'})
        if longitude is None:
            raise ValidationError({'longitude': 'Este campo es requerido'})
        
        # Validar rangos para Costa Rica
        if not (8 <= latitude <= 12):
            raise ValidationError({
                'latitude': 'La latitud debe estar entre 8 y 12 para Costa Rica'
            })
        
        if not (-87 <= longitude <= -82):
            raise ValidationError({
                'longitude': 'La longitud debe estar entre -87 y -82 para Costa Rica'
            })
        
        # Crear el objeto Point
        try:
            cleaned_data['location'] = Point(longitude, latitude, srid=4326)
            print(f"Point creado exitosamente: POINT({longitude} {latitude})")
        except Exception as e:
            raise ValidationError(f'Error al crear las coordenadas: {e}')
        
        return cleaned_data
    
    def save(self, commit=True):
        """
        Sobrescribir save para asegurar que el location se guarde correctamente
        """
        instance = super().save(commit=False)
        
        # Asegurar que el campo location está asignado desde los cleaned_data
        if 'location' in self.cleaned_data:
            instance.location = self.cleaned_data['location']
            print(f"Asignando location a instancia: {instance.location}")
        else:
            print("WARNING: No se encontró 'location' en cleaned_data")
            
        if commit:
            instance.save()
            print(f"Instancia guardada con location: {instance.location}")
            
        return instance
