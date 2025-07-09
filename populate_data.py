#!/usr/bin/env python
"""
Script para poblar la base de datos con datos básicos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acat_system.settings.local')
django.setup()

from apps.core.models import ProtectedArea, Sector
from apps.complaints.models import ComplaintType, InfractionType

def create_basic_data():
    print("🌟 Creando datos básicos para el sistema ACAT...")
    
    # Crear tipos de denuncia
    complaint_types = [
        "Tala ilegal",
        "Caza furtiva", 
        "Contaminación de ríos",
        "Construcción ilegal",
        "Extracción de arena",
        "Pesca ilegal",
        "Invasión de terrenos",
        "Quema no autorizada"
    ]
    
    print("📋 Creando tipos de denuncia...")
    for name in complaint_types:
        obj, created = ComplaintType.objects.get_or_create(
            name=name,
            defaults={'description': f'Denuncia por {name.lower()}'}
        )
        if created:
            print(f"  ✅ {name}")
    
    # Crear tipos de infracción
    infraction_types = [
        ("Tala de árboles", "GRAVE"),
        ("Caza de animales protegidos", "MUY_GRAVE"),
        ("Vertido de contaminantes", "GRAVE"),
        ("Construcción sin permisos", "MODERADA"),
        ("Extracción de recursos", "MODERADA"),
        ("Pesca en zona vedada", "GRAVE"),
        ("Ocupación ilegal", "MODERADA"),
        ("Incendio provocado", "MUY_GRAVE")
    ]
    
    print("⚖️ Creando tipos de infracción...")
    for name, severity in infraction_types:
        obj, created = InfractionType.objects.get_or_create(
            name=name,
            defaults={
                'description': f'Infracción: {name.lower()}',
                'severity_level': severity
            }
        )
        if created:
            print(f"  ✅ {name} ({severity})")
    
    # Crear áreas protegidas
    protected_areas = [
        ("Parque Nacional Volcán Arenal", "PN", "PARQUE_NACIONAL"),
        ("Refugio Nacional de Vida Silvestre Caño Negro", "RNVS", "REFUGIO"),
        ("Reserva Biológica Alberto Brenes", "RB", "RESERVA_BIOLOGICA"),
        ("Parque Nacional Tenorio", "PN", "PARQUE_NACIONAL"),
        ("Zona Protectora Arenal", "ZP", "ZONA_PROTECTORA")
    ]
    
    print("🏞️ Creando áreas protegidas...")
    for name, code, area_type in protected_areas:
        obj, created = ProtectedArea.objects.get_or_create(
            name=name,
            defaults={
                'code': code,
                'area_type': area_type,
                'description': f'Área protegida: {name}'
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # Crear sectores para cada área
    print("📍 Creando sectores...")
    for area in ProtectedArea.objects.all():
        sectors = [
            f"Sector Norte - {area.name[:20]}",
            f"Sector Sur - {area.name[:20]}",
            f"Sector Este - {area.name[:20]}"
        ]
        
        for sector_name in sectors:
            obj, created = Sector.objects.get_or_create(
                name=sector_name,
                protected_area=area,
                defaults={
                    'code': f"{area.code}-{sector_name.split()[1][0]}",
                    'description': f'Sector de {area.name}'
                }
            )
            if created:
                print(f"  ✅ {sector_name}")
    
    print("\n🎉 ¡Datos básicos creados exitosamente!")
    print("📊 Resumen:")
    print(f"  - Tipos de denuncia: {ComplaintType.objects.count()}")
    print(f"  - Tipos de infracción: {InfractionType.objects.count()}")
    print(f"  - Áreas protegidas: {ProtectedArea.objects.count()}")
    print(f"  - Sectores: {Sector.objects.count()}")

if __name__ == "__main__":
    create_basic_data()
