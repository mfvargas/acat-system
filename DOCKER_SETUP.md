# ACAT System - Docker Setup Documentation

## 🐳 Configuración Docker Completada ✅

El sistema ACAT ahora está completamente dockerizado y funcionando con todos los servicios integrados.

## Servicios Activos

### 1. **Base de Datos PostgreSQL + PostGIS**
- **Imagen:** `postgis/postgis:15-3.3`
- **Puerto:** `5432`
- **Base de datos:** `acat_system_dev`
- **Usuario:** `acat_user`
- **Extensiones:** PostGIS, spatial_ref_sys

### 2. **Cache Redis**
- **Imagen:** `redis:7-alpine`
- **Puerto:** `6379`

### 3. **Aplicación Django Web**
- **Imagen:** Construida localmente con `Dockerfile`
- **Puerto:** `8000`
- **Framework:** Django 5.0 + GeoDjango
- **Configuración:** Desarrollo con live reload

## Comandos Principales

### Levantar todos los servicios:
```bash
sudo docker-compose up -d
```

### Ver el estado de los contenedores:
```bash
sudo docker-compose ps
```

### Ver logs de todos los servicios:
```bash
sudo docker-compose logs -f
```

### Ver logs específicos (web, db, redis):
```bash
sudo docker-compose logs -f web
sudo docker-compose logs -f db
sudo docker-compose logs -f redis
```

### Parar todos los servicios:
```bash
sudo docker-compose down
```

### Reconstruir la imagen web tras cambios:
```bash
sudo docker-compose build web
sudo docker-compose up -d web
```

## Acceso a la Aplicación

- **URL Principal:** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin/ (requiere superusuario)
- **API REST:** http://localhost:8000/api/

## Archivos de Configuración

### `docker-compose.yml`
Define los 3 servicios principales y sus configuraciones.

### `Dockerfile`
Imagen personalizada para Django con:
- Python 3.11-slim
- Dependencias del sistema (PostgreSQL client, GDAL, etc.)
- Dependencias Python del proyecto
- Script de inicio personalizado

### `entrypoint.sh`
Script de inicialización que:
- Espera a que PostgreSQL esté disponible
- Ejecuta migraciones automáticamente
- Recopila archivos estáticos (solo en producción)
- Inicia la aplicación Django

### `.env.docker`
Variables de entorno específicas para Docker:
```env
DB_HOST=db
DB_NAME=acat_system_dev
DB_USER=acat_user
DB_PASSWORD=dev_password
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web
```

### `scripts/init_db.sql`
Script SQL que se ejecuta al inicializar PostgreSQL:
- Crea la base de datos
- Habilita extensiones PostGIS
- Configura permisos del usuario

## Dependencias Python Instaladas

- Django==5.0.0
- psycopg2-binary==2.9.9
- python-decouple==3.8
- Pillow==10.1.0
- django-debug-toolbar==4.2.0
- django-extensions==3.2.3
- django-cors-headers==4.3.1
- djangorestframework==3.14.0
- django-filter==23.5
- djangorestframework-gis==1.0

## Volumenes Persistentes

- `postgres_data`: Datos de PostgreSQL persistentes
- `static_volume`: Archivos estáticos de Django
- `media_volume`: Archivos multimedia subidos

## Desarrollo

### Modificar código:
Los cambios en el código se reflejan automáticamente gracias al volumen montado y StatReloader de Django.

### Agregar dependencias:
1. Modificar `requirements.txt`
2. Reconstruir imagen: `sudo docker-compose build web`
3. Reiniciar servicio: `sudo docker-compose up -d web`

### Ejecutar comandos Django:
```bash
sudo docker-compose exec web python manage.py [comando]
```

Ejemplos:
```bash
# Crear superusuario
sudo docker-compose exec web python manage.py createsuperuser

# Shell de Django
sudo docker-compose exec web python manage.py shell

# Colectar archivos estáticos
sudo docker-compose exec web python manage.py collectstatic
```

## Solución de Problemas

### Si PostgreSQL no se conecta:
```bash
# Verificar logs de la base de datos
sudo docker-compose logs db

# Reiniciar servicio de base de datos
sudo docker-compose restart db
```

### Si el contenedor web falla:
```bash
# Ver logs detallados
sudo docker-compose logs web

# Reconstruir imagen
sudo docker-compose build --no-cache web
```

### Limpiar todo y empezar de nuevo:
```bash
sudo docker-compose down -v  # Incluye volúmenes
sudo docker system prune -f  # Limpia sistema Docker
sudo docker-compose up -d
```

## Estado Actual: ✅ FUNCIONANDO

Todos los servicios están operativos y la aplicación Django es accesible en http://localhost:8000 con:
- Base de datos PostgreSQL + PostGIS funcionando
- Migraciones aplicadas correctamente
- Servidor de desarrollo activo con live reload
- APIs REST operativas
- Archivos estáticos servidos correctamente

## Próximos Pasos Sugeridos

1. **Crear usuario administrador**: `sudo docker-compose exec web python manage.py createsuperuser`
2. **Probar funcionalidades**: Acceder a la interfaz web y APIs
3. **Configurar staging**: Preparar ambiente de staging similar
4. **CI/CD**: Integrar con GitHub Actions para despliegue automático
5. **Monitoring**: Agregar logs y monitoreo de contenedores
