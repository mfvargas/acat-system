#!/usr/bin/env python3
"""
Script para depurar el problema del mapa
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acat_system.settings.development')
django.setup()

from apps.complaints.models import EnvironmentalComplaint

def debug_coordinates():
    """Depurar las coordenadas de las denuncias"""
    
    complaints = EnvironmentalComplaint.objects.filter(location__isnull=False)
    
    print(f"Denuncias con coordenadas: {complaints.count()}")
    
    for complaint in complaints:
        print(f"\n--- Denuncia ID {complaint.id} ---")
        print(f"Acusado: {complaint.accused_name}")
        print(f"Location (objeto): {complaint.location}")
        print(f"Location (string): {str(complaint.location)}")
        print(f"Location (repr): {repr(complaint.location)}")
        
        # Intentar extraer coordenadas
        try:
            if hasattr(complaint.location, 'x') and hasattr(complaint.location, 'y'):
                print(f"Coordenadas X,Y: {complaint.location.x}, {complaint.location.y}")
                print(f"Coordenadas lon,lat: {complaint.location.x}, {complaint.location.y}")
            
            # Verificar si las coordenadas están en rango válido para Costa Rica
            if hasattr(complaint.location, 'y') and hasattr(complaint.location, 'x'):
                lat, lon = complaint.location.y, complaint.location.x
                if 8 <= lat <= 12 and -87 <= lon <= -82:
                    print("✅ Coordenadas válidas para Costa Rica")
                else:
                    print("❌ Coordenadas fuera del rango de Costa Rica")
                    print(f"   Rango esperado: lat 8-12, lon -87 a -82")
                    print(f"   Valores actuales: lat {lat}, lon {lon}")
        except Exception as e:
            print(f"Error al extraer coordenadas: {e}")

if __name__ == '__main__':
    debug_coordinates()
