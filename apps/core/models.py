from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models
    """
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Fecha de actualización'), auto_now=True)
    is_active = models.BooleanField(_('Activo'), default=True)
    
    class Meta:
        abstract = True


class ProtectedArea(BaseModel):
    """
    Área Silvestre Protegida
    """
    name = models.CharField(_('Nombre'), max_length=200)
    code = models.CharField(_('Código'), max_length=50, unique=True)
    description = models.TextField(_('Descripción'), blank=True)
    
    class Meta:
        verbose_name = _('Área Silvestre Protegida')
        verbose_name_plural = _('Áreas Silvestres Protegidas')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Sector(BaseModel):
    """
    Sector dentro de un Área Silvestre Protegida
    """
    name = models.CharField(_('Nombre'), max_length=200)
    protected_area = models.ForeignKey(
        ProtectedArea, 
        on_delete=models.CASCADE,
        related_name='sectors',
        verbose_name=_('Área Silvestre Protegida')
    )
    description = models.TextField(_('Descripción'), blank=True)
    
    class Meta:
        verbose_name = _('Sector')
        verbose_name_plural = _('Sectores')
        ordering = ['protected_area__name', 'name']
        unique_together = ['name', 'protected_area']
    
    def __str__(self):
        return f"{self.protected_area.code} - {self.name}"
