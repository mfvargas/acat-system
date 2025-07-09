import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acat_system.settings.local')
django.setup()

from apps.core.models import ProtectedArea, Sector
from apps.complaints.models import ComplaintType, InfractionType

# Crear tipos de denuncia
ComplaintType.objects.get_or_create(name="Tala ilegal", defaults={'description': 'Corte no autorizado de árboles'})
ComplaintType.objects.get_or_create(name="Caza furtiva", defaults={'description': 'Caza ilegal de animales'})
ComplaintType.objects.get_or_create(name="Contaminación", defaults={'description': 'Contaminación ambiental'})

# Crear tipos de infracción
InfractionType.objects.get_or_create(name="Tala de árboles", defaults={'description': 'Corte de árboles', 'severity_level': 'GRAVE'})
InfractionType.objects.get_or_create(name="Caza ilegal", defaults={'description': 'Caza no autorizada', 'severity_level': 'GRAVE'})
InfractionType.objects.get_or_create(name="Vertido contaminante", defaults={'description': 'Contaminación de agua', 'severity_level': 'MUY_GRAVE'})

# Crear área protegida
area, created = ProtectedArea.objects.get_or_create(
    name="Parque Nacional Volcán Arenal",
    defaults={
        'code': 'PNVA',
        'area_type': 'PARQUE_NACIONAL',
        'description': 'Parque Nacional Volcán Arenal'
    }
)

# Crear sector
Sector.objects.get_or_create(
    name="Sector Norte", 
    protected_area=area,
    defaults={
        'code': 'PNVA-N',
        'description': 'Sector Norte del parque'
    }
)

print("✅ Datos creados exitosamente!")
