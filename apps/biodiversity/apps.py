from django.apps import AppConfig


class BiodiversityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.biodiversity'
    verbose_name = 'Inventario de Biodiversidad'
    
    def ready(self):
        """Initialize signals and other app setup when Django starts."""
        pass
