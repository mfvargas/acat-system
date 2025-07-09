#!/usr/bin/env python3
"""
Script básico para crear datos esenciales en la base de datos
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acat_system.settings.development')
django.setup()

from apps.complaints.models import ComplaintType, InfractionType, ProtectedArea, Sector

def create_basic_data():
    """Crear datos básicos necesarios para el sistema"""
    
    # Crear tipos de denuncia
    complaint_types = [
        'Tala ilegal',
        'Caza furtiva', 
        'Contaminación',
        'Construcción ilegal',
        'Extracción ilegal',
    ]
    
    print("Creando tipos de denuncia...")
    for ct_name in complaint_types:
        ct, created = ComplaintType.objects.get_or_create(
            name=ct_name,
            defaults={'description': f'Denuncia de {ct_name.lower()}'}
        )
        print(f"{'✓ Creado' if created else '- Existe'}: {ct_name}")
    
    # Crear tipos de infracción
    infraction_types = [
        ('Tala sin permiso', 'GRAVE'),
        ('Caza en veda', 'GRAVE'),
        ('Vertido de desechos', 'MODERADA'),
        ('Construcción en zona protegida', 'GRAVE'),
        ('Extracción de arena', 'MODERADA'),
    ]
    
    print("\nCreando tipos de infracción...")
    for it_name, it_severity in infraction_types:
        it, created = InfractionType.objects.get_or_create(
            name=it_name,
            defaults={'severity_level': it_severity}
        )
        print(f"{'✓ Creado' if created else '- Existe'}: {it_name} ({it_severity})")
    
    # Crear áreas protegidas básicas
    protected_areas = [
        ('Parque Nacional Manuel Antonio', 'PNMA'),
        ('Parque Nacional Corcovado', 'PNC'),
        ('Reserva Biológica Monteverde', 'RBM'),
        ('Parque Nacional Volcán Arenal', 'PNVA'),
        ('Área General', 'AG'),
    ]
    
    print("\nCreando áreas protegidas...")
    for pa_name, pa_code in protected_areas:
        pa, created = ProtectedArea.objects.get_or_create(
            name=pa_name,
            defaults={'code': pa_code, 'description': f'Descripción de {pa_name}'}
        )
        print(f"{'✓ Creado' if created else '- Existe'}: {pa_name} ({pa_code})")
    
    # Crear sectores básicos (asignar a la primera área protegida)
    area_general = ProtectedArea.objects.filter(name__contains='Área General').first()
    if area_general:
        sectors = [
            'Sector Norte',
            'Sector Sur', 
            'Sector Este',
            'Sector Oeste',
            'Sector Central',
        ]
        
        print("\nCreando sectores...")
        for s_name in sectors:
            s, created = Sector.objects.get_or_create(
                name=s_name,
                protected_area=area_general,
                defaults={'description': f'Área de {s_name.lower()}'}
            )
            print(f"{'✓ Creado' if created else '- Existe'}: {s_name}")
    else:
        print("\n⚠ No se pudo crear sectores: No se encontró área general")
    
    print(f"\n✅ Datos básicos creados exitosamente!")
    
    # Mostrar resumen
    print(f"\nResumen:")
    print(f"- Tipos de denuncia: {ComplaintType.objects.count()}")
    print(f"- Tipos de infracción: {InfractionType.objects.count()}")
    print(f"- Áreas protegidas: {ProtectedArea.objects.count()}")
    print(f"- Sectores: {Sector.objects.count()}")

if __name__ == '__main__':
    create_basic_data()
