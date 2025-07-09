# Sistema ACAT - Área de Conservación Arenal Tempisque

Sistema web para el manejo de datos del Área de Conservación Arenal Tempisque (ACAT), desarrollado con Django 5 + GeoDjango + Django Rest Framework + PostgreSQL/PostGIS.

## Características

- **Gestión de Denuncias Ambientales**: Registro, seguimiento y visualización de denuncias ambientales
- **Visualización Geoespacial**: Mapas interactivos con ubicaciones georreferenciadas
- **Dashboard Estadístico**: Gráficos y reportes de tendencias
- **API REST**: Endpoints para integración con otros sistemas
- **Administración Web**: Interface administrativa completa

## Módulos

### Implementados
- **Denuncias Ambientales**: Gestión completa de denuncias con geolocalización

### En Desarrollo
- **Biodiversidad**: Registro y monitoreo de especies
- **Otros módulos**: Planificados según necesidades del ACAT

## Tecnologías

- **Backend**: Django 5.0, Django REST Framework
- **Base de Datos**: PostgreSQL + PostGIS
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Mapas**: Leaflet.js
- **Gráficos**: Chart.js

## Estructura del Proyecto

```
acat-system/
├── apps/                   # Aplicaciones Django
│   ├── core/              # Modelos y funcionalidades compartidas
│   ├── complaints/        # Módulo de denuncias ambientales
│   └── dashboard/         # Panel principal y estadísticas
├── acat_system/           # Configuración principal
│   └── settings/          # Configuraciones por ambiente
├── static/                # Archivos estáticos
├── templates/             # Plantillas HTML
├── requirements/          # Dependencias por ambiente
└── scripts/              # Scripts de deployment
```

## Instalación

### Prerrequisitos

- Python 3.9+
- PostgreSQL 12+ con PostGIS
- GDAL/GEOS libraries

### Configuración Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/acatcr/acat-system.git
cd acat-system
```

2. **Crear ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements/development.txt
```

4. **Configurar base de datos**
```sql
CREATE DATABASE acat_system_dev;
CREATE USER acat_user WITH PASSWORD 'password';
ALTER ROLE acat_user SET client_encoding TO 'utf8';
ALTER ROLE acat_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE acat_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE acat_system_dev TO acat_user;

-- Habilitar PostGIS
\c acat_system_dev;
CREATE EXTENSION postgis;
```

5. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con los valores correctos
```

6. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

## Deployment

### Servidor de Staging
- URL: https://staging.acatcr.org
- Rama: `develop`
- Deploy automático vía GitHub Actions

### Servidor de Producción
- URL: https://acatcr.org
- Rama: `main`
- Deploy manual después de testing

### Variables de Entorno para Producción

```bash
# Django
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=acatcr.org,www.acatcr.org

# Database
DB_NAME=acat_system
DB_USER=acat_user
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## API Endpoints

### Denuncias Ambientales
- `GET /api/denuncias/` - Lista de denuncias
- `POST /api/denuncias/` - Crear nueva denuncia
- `GET /api/denuncias/{id}/` - Detalle de denuncia
- `PUT /api/denuncias/{id}/` - Actualizar denuncia
- `DELETE /api/denuncias/{id}/` - Eliminar denuncia

### Filtros Geoespaciales
- `GET /api/denuncias/?bbox=xmin,ymin,xmax,ymax` - Filtro por área
- `GET /api/denuncias/?area=area_id` - Filtro por área protegida

## Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Contacto

- **Organización**: ACAT Costa Rica
- **Repositorio**: https://github.com/acatcr/acat-system
- **Website**: https://acatcr.org
