#!/usr/bin/env python
"""
Test script para validar funcionalidades del Sistema ACAT
"""

import os
import django
from django.contrib.gis.geos import Point
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acat_system.settings.development')
django.setup()

from apps.complaints.models import EnvironmentalComplaint, ComplaintType, InfractionType
from apps.core.models import ProtectedArea, Sector
from django.contrib.auth.models import User

def test_database_connection():
    """Test básico de conexión a la base de datos"""
    print("🔍 Testing database connection...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL conectado: {version[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_postgis_extensions():
    """Test de extensiones PostGIS"""
    print("\n🗺️  Testing PostGIS extensions...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT PostGIS_Version()")
        postgis_version = cursor.fetchone()[0]
        print(f"✅ PostGIS funcionando: {postgis_version}")
        
        # Test funcionalidad geoespacial
        test_point = Point(-84.2, 10.1)  # Coordenadas Costa Rica
        print(f"✅ Creación de puntos geoespaciales: {test_point}")
        return True
    except Exception as e:
        print(f"❌ Error PostGIS: {e}")
        return False

def test_models():
    """Test de modelos principales"""
    print("\n📋 Testing models...")
    try:
        # Test User model
        user_count = User.objects.count()
        print(f"✅ Usuarios en sistema: {user_count}")
        
        # Test complaint model
        complaint_count = EnvironmentalComplaint.objects.count()
        print(f"✅ Denuncias en sistema: {complaint_count}")
        
        # Test geographic models
        protected_area_count = ProtectedArea.objects.count()
        sector_count = Sector.objects.count()  
        complaint_type_count = ComplaintType.objects.count()
        infraction_type_count = InfractionType.objects.count()
        
        print(f"✅ Áreas Protegidas: {protected_area_count}")
        print(f"✅ Sectores: {sector_count}")
        print(f"✅ Tipos de Denuncia: {complaint_type_count}")
        print(f"✅ Tipos de Infracción: {infraction_type_count}")
        
        return True
    except Exception as e:
        print(f"❌ Error en modelos: {e}")
        return False

def create_test_data():
    """Crear datos de prueba"""
    print("\n🎯 Creating test data...")
    try:
        # Crear área protegida de prueba
        protected_area, created = ProtectedArea.objects.get_or_create(
            code="ACG-001",
            defaults={
                "name": "Área de Conservación Arenal Tempisque",
                "description": "Área de conservación de prueba para testing"
            }
        )
        if created:
            print("✅ Área Protegida creada")
        else:
            print("ℹ️  Área Protegida ya existe")
        
        # Crear sector de prueba
        sector, created = Sector.objects.get_or_create(
            name="Sector Tempisque",
            protected_area=protected_area,
            defaults={
                "description": "Sector de prueba en el área del Tempisque"
            }
        )
        if created:
            print("✅ Sector creado")
        else:
            print("ℹ️  Sector ya existe")
            
        # Crear tipo de denuncia
        complaint_type, created = ComplaintType.objects.get_or_create(
            name="Contaminación de Agua",
            defaults={
                "description": "Denuncias relacionadas con contaminación de cuerpos de agua"
            }
        )
        if created:
            print("✅ Tipo de denuncia creado")
        else:
            print("ℹ️  Tipo de denuncia ya existe")
            
        # Crear tipo de infracción
        infraction_type, created = InfractionType.objects.get_or_create(
            name="Vertido de aguas residuales",
            defaults={
                "description": "Vertido no autorizado de aguas residuales",
                "severity_level": "GRAVE"
            }
        )
        if created:
            print("✅ Tipo de infracción creado")
        else:
            print("ℹ️  Tipo de infracción ya existe")
        
        # Crear usuario para la denuncia
        user, created = User.objects.get_or_create(
            username="test_user",
            defaults={
                "email": "test@acat.local",
                "first_name": "Usuario",
                "last_name": "Prueba"
            }
        )
        if created:
            print("✅ Usuario de prueba creado")
        else:
            print("ℹ️  Usuario de prueba ya existe")
        
        # Crear denuncia de prueba con geolocalización
        location = Point(-84.7, 10.4)  # Área de Arenal Tempisque
        
        from datetime import date
        complaint, created = EnvironmentalComplaint.objects.get_or_create(
            sitada_number="TEST-2025-001",
            defaults={
                "location": location,
                "protected_area": protected_area,
                "sector": sector,
                "infraction_date": date.today(),
                "accused_name": "Juan Pérez (Prueba)",
                "complaint_type": complaint_type,
                "infraction_name": infraction_type,
                "description": "Denuncia de prueba: Vertido de aguas residuales al río Tempisque cerca del puente.",
                "status": "pending",
                "created_by": user
            }
        )
        
        if created:
            print("✅ Denuncia de prueba creada con geolocalización")
            print(f"   📍 Ubicación: {complaint.location}")
            print(f"   🏛️  Área: {complaint.protected_area.name}")
        else:
            print("ℹ️  Denuncia de prueba ya existe")
            
        return True
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False

def test_api_functionality():
    """Test básico de funcionalidad API"""
    print("\n🌐 Testing API functionality...")
    try:
        from apps.complaints.serializers import EnvironmentalComplaintSerializer
        
        # Test serializer
        complaints = EnvironmentalComplaint.objects.all()
        if complaints:
            complaint = complaints.first()
            serializer = EnvironmentalComplaintSerializer(complaint)
            print(f"✅ Serialización de denuncia: {len(serializer.data)} campos")
            print(f"   Título: {serializer.data.get('title', 'N/A')}")
        else:
            print("ℹ️  No hay denuncias para serializar")
            
        return True
    except Exception as e:
        print(f"❌ Error en API: {e}")
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TESTS DEL SISTEMA ACAT")
    print("=" * 50)
    
    results = []
    
    # Database tests
    results.append(test_database_connection())
    results.append(test_postgis_extensions())
    results.append(test_models())
    results.append(create_test_data())
    results.append(test_api_functionality())
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 TODOS LOS TESTS PASARON: {passed}/{total}")
        print("✅ Sistema ACAT completamente funcional")
    else:
        print(f"⚠️  TESTS PASADOS: {passed}/{total}")
        print("❌ Hay problemas que requieren atención")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
