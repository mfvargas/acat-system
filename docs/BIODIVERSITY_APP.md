# 🌿 **Aplicación Biodiversity - Inventario de Biodiversidad ACAT**

## 📋 **Resumen**

La aplicación `biodiversity` es un módulo completo del sistema ACAT diseñado para gestionar el inventario de especies y registros de presencia del Área de Conservación Arenal Tempisque (ACAT), basado en datos Darwin Core obtenidos de GBIF.

## 🏗️ **Arquitectura**

### **Modelos de Datos**

#### **1. Species**
- **Propósito**: Almacena información taxonómica de especies según estándar Darwin Core
- **Campos principales**:
  - `taxon_key`: Identificador único de GBIF
  - Taxonomía completa: `kingdom`, `phylum`, `class_name`, `order`, `family`, `genus`, `species`
  - `scientific_name`: Generado automáticamente
  - `common_name`: Nombre común (editable)
  - Metadatos de sincronización con GBIF

#### **2. ConservationStatus**
- **Propósito**: Estado de conservación de especies (persiste ante actualizaciones GBIF)
- **Clasificaciones**:
  - **RLCVS**: PE (Peligro extinción), PRA (Población reducida), NR (No registrada)
  - **CITES**: AI, AII, AIII (Apéndices I-III)
  - **UICN**: CR, EN, VU, NT, LC, DD, NE
  - `endemic_to_acat`: Booleano para especies endémicas

#### **3. Occurrence**
- **Propósito**: Registros de presencia espaciales Darwin Core
- **Campos principales**:
  - `gbif_id`: Identificador único del registro
  - Coordenadas: `decimal_latitude`, `decimal_longitude`, `location` (PostGIS Point)
  - Información temporal: `event_date`, `year`, `month`, `day`
  - Metadatos de colección: `locality`, `institution_code`, `basis_of_record`

#### **4. DataImportLog**
- **Propósito**: Auditoría de importaciones Darwin Core
- **Métricas**: Records procesados, creados, actualizados, errores, tasa de éxito

### **Componentes Principales**

#### **Management Command: `import_darwin_core`**
```bash
# Importación completa
python manage.py import_darwin_core --import-type=full

# Solo especies
python manage.py import_darwin_core --import-type=species

# Solo registros de presencia
python manage.py import_darwin_core --import-type=occurrences

# Modo simulación
python manage.py import_darwin_core --dry-run
```

**Características**:
- Procesamiento por lotes (batch processing)
- Manejo de errores robusto
- Logging detallado
- Soporte para archivos CSV (especies) y GeoPackage (registros)
- Validación de coordenadas dentro de Costa Rica

#### **Vistas Principales**

1. **SpeciesListView**: Lista filtrable de especies
   - Filtros: familia, género, reino, estado conservación
   - Paginación y búsqueda
   - Vista de tarjetas y tabla

2. **SpeciesDetailView**: Detalle completo de especie
   - Información taxonómica
   - Estado de conservación
   - Registros de presencia
   - Distribución temporal
   - Especies relacionadas

3. **OccurrenceMapView**: Mapa interactivo
   - Clustering de marcadores
   - Mapa de calor
   - Filtros dinámicos
   - Exportación de datos

4. **API Endpoints**:
   - `/api/especies/`: Lista de especies (JSON)
   - `/api/registros/`: Lista de registros (JSON)
   - `/api/mapa-data/`: Datos geográficos (GeoJSON)

#### **Admin Interface**
- **SpeciesAdmin**: Gestión de especies con filtros avanzados
- **ConservationStatusAdmin**: Edición de estados de conservación
- **OccurrenceAdmin**: Interface GIS para registros espaciales
- **DataImportLogAdmin**: Monitoreo de importaciones

## 📊 **Funcionalidades**

### **Para Usuarios Finales**
- ✅ **Exploración de especies** con filtros taxonómicos
- ✅ **Visualización en mapas** interactivos con clustering
- ✅ **Búsqueda avanzada** por nombre científico/común
- ✅ **Información de conservación** (RLCVS, CITES, UICN)
- ✅ **Exportación de datos** (CSV, GeoJSON, KML)
- ✅ **Estadísticas** taxonómicas y temporales

### **Para Administradores**
- ✅ **Importación automatizada** desde archivos Darwin Core
- ✅ **Gestión de estados de conservación**
- ✅ **Monitoreo de importaciones** con logs detallados
- ✅ **Interface GIS** para edición espacial
- ✅ **Validación de datos** automática

## 🔧 **Archivos de Datos**

### **Estructura Esperada**

#### **especies.csv** (Darwin Core)
```csv
taxonKey,kingdom,phylum,class,order,family,genus,species
8365367,Plantae,Tracheophyta,Magnoliopsida,Laurales,Monimiaceae,Mollinedia,Mollinedia viridiflora
```

#### **registros-presencia.gpkg** (GeoPackage)
- Campos requeridos: `gbifID`, `taxonKey`, `decimalLatitude`, `decimalLongitude`
- Campos opcionales: `eventDate`, `locality`, `basisOfRecord`, etc.

### **Ubicación de Archivos**
```
data/
└── biodiversity/
    ├── raw/                    ← Archivos originales Darwin Core
    │   ├── especies.csv
    │   └── registros-presencia.gpkg
    └── processed/              ← Archivos procesados (futuro uso)
```

## 🌐 **URLs de la Aplicación**

```
/biodiversidad/                          # Lista de especies
/biodiversidad/especies/<id>/            # Detalle de especie
/biodiversidad/registros/                # Lista de registros
/biodiversidad/mapa/                     # Mapa interactivo
/biodiversidad/estadisticas/             # Dashboard estadísticas
/biodiversidad/export/especies/          # Exportar especies
/biodiversidad/api/especies/             # API especies
/biodiversidad/api/mapa-data/            # API datos geográficos
```

## 🎨 **Interface de Usuario**

### **Características del Frontend**
- **Responsive design** con Bootstrap 5
- **Mapas interactivos** con Leaflet.js
- **Filtros dinámicos** con AJAX
- **Clustering inteligente** de marcadores
- **Gráficos temporales** con Chart.js
- **Exportación flexible** en múltiples formatos

### **Navegación**
```
Biodiversidad/
├── 📋 Especies           # Lista y filtros
├── 📍 Registros          # Lista de presencias
├── 🗺️ Mapa              # Visualización espacial
└── 📊 Estadísticas       # Dashboard analítico
```

## 🧪 **Testing**

### **Tests Implementados**
- ✅ **Modelos**: Creación, validación, propiedades
- ✅ **Vistas**: Respuestas HTTP, contenido, filtros
- ✅ **Management Commands**: Existencia y funcionalidad
- ✅ **Admin**: Interface de administración

### **Ejecutar Tests**
```bash
# Todos los tests de biodiversity
python manage.py test apps.biodiversity

# Tests específicos
python manage.py test apps.biodiversity.tests.SpeciesModelTest
```

## 🔄 **Workflow de Actualización**

### **Proceso Recomendado**
1. **Obtener datos actualizados** de GBIF
2. **Copiar archivos** a `data/biodiversity/raw/`
3. **Ejecutar importación**:
   ```bash
   python manage.py import_darwin_core --import-type=full
   ```
4. **Verificar logs** en Django Admin
5. **Actualizar estados de conservación** si es necesario

### **Monitoreo**
- **DataImportLog**: Revisa éxito/errores de importaciones
- **Admin interface**: Verifica conteos de especies/registros
- **Dashboard estadísticas**: Valida coherencia de datos

## 🚀 **Deployment**

### **Consideraciones de Producción**
- ✅ **PostGIS** requerido para datos espaciales
- ✅ **Nginx** configurado para archivos estáticos/media
- ✅ **Redis** para cacheo (opcional)
- ✅ **Celery** para importaciones asíncronas (futuro)

### **Variables de Entorno**
Las mismas del sistema base ACAT - no requiere configuración adicional.

## 📈 **Rendimiento**

### **Optimizaciones Implementadas**
- **Índices de base de datos** en campos clave
- **Select/prefetch related** en vistas
- **Paginación** en listados largos
- **Clustering de marcadores** en mapas
- **Lazy loading** de componentes pesados

### **Métricas Esperadas**
- **5,687 especies** (dato actual)
- **65,035 registros** (dato actual)
- **Tiempo de importación**: ~2-3 minutos para dataset completo

## 🛠️ **Mantenimiento**

### **Tareas Regulares**
- **Actualización mensual** de datos GBIF
- **Backup** de estados de conservación antes de importar
- **Revisión de logs** de importación
- **Actualización de nombres comunes**

### **Troubleshooting**
- **Errores de importación**: Revisar `DataImportLog`
- **Problemas de mapa**: Verificar archivos JavaScript
- **Performance**: Revisar índices de base de datos

---

## 📚 **Documentación Técnica Adicional**

- `models.py`: Documentación inline de modelos
- `admin.py`: Configuración de interface administrativa  
- `views.py`: Documentación de vistas y API endpoints
- `management/commands/`: Comandos de importación
- `tests.py`: Casos de prueba y ejemplos de uso

**La aplicación Biodiversity está lista para uso en producción.** 🌿
