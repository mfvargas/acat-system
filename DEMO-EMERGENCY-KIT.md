# 🚨 DEMO EMERGENCY KIT - ACAT System

## ⚡ URLs de Respaldo (En orden de preferencia)
1. **Principal**: https://staging.acatcr.org
2. **HTTP Fallback**: http://staging.acatcr.org  
3. **IP Directa**: http://159.65.122.13
4. **IP + HTTPS**: https://159.65.122.13 (ignorar warning de certificado)

## 🔧 Comandos de Emergencia Rápidos
```bash
# Si el sitio no responde - Reinicio rápido
ssh -i ~/.ssh/acat root@staging.acatcr.org "cd /opt/acat-system && docker-compose -f docker-compose.production.yml restart nginx web"

# Verificar que todo esté UP
ssh -i ~/.ssh/acat root@staging.acatcr.org "cd /opt/acat-system && docker-compose -f docker-compose.production.yml ps"
```

## 🎭 Frases para Problemas Técnicos
- **Si hay lentitud**: "Como ven, estamos en un entorno staging, en producción sería aún más rápido"
- **Si algo no funciona**: "Esto es una demostración del entorno de desarrollo, permítanme mostrarles la arquitectura mientras se actualiza"
- **Internet lento**: "Aprovecho para explicarles la robusta arquitectura que tenemos por detrás"

## 📱 Backup Content (Si todo falla)
- Tener screenshots de las funcionalidades principales
- Preparar explicación de la arquitectura técnica
- Mostrar el código en GitHub/repositorio
