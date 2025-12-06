# Guía: Instalación de la App Móvil (PWA)

## ✅ ¿Qué se implementó?

Se ha implementado una **Progressive Web App (PWA)** que permite instalar el sitio web como una aplicación móvil nativa.

## 📱 Características

- ✅ **Instalable en móviles**: Los usuarios pueden agregar la app a su pantalla de inicio
- ✅ **Funciona offline**: Cache básico para funcionar sin conexión
- ✅ **Icono personalizado**: La app aparece con su propio icono
- ✅ **Pantalla de inicio personalizada**: Sin barra del navegador cuando está instalada
- ✅ **Botón de instalación**: Aparece automáticamente cuando la app está lista para instalar

## 🎯 Cómo funciona

### Para usuarios en móviles:

1. **Android (Chrome)**:
   - Al visitar el sitio, aparecerá un banner o botón flotante "Instalar App"
   - También pueden ir al menú del navegador → "Agregar a pantalla de inicio"
   - La app se instalará y aparecerá como una app nativa

2. **iOS (Safari)**:
   - Ir al menú de Safari (botón de compartir)
   - Seleccionar "Agregar a pantalla de inicio"
   - La app se agregará con su icono personalizado

3. **Desktop (Chrome/Edge)**:
   - Aparecerá un icono de instalación en la barra de direcciones
   - O un banner sugiriendo instalar la app

## 📂 Archivos creados/modificados

### Archivos nuevos:
- `bingo_app/static/manifest.json` - Configuración de la PWA
- `bingo_app/static/js/service-worker.js` - Service Worker para funcionalidad offline
- `bingo_app/static/images/icon-*.png` - Iconos en diferentes tamaños (8 tamaños)
- `generar_iconos_pwa.py` - Script para generar iconos (ya ejecutado)

### Archivos modificados:
- `bingo_app/templates/bingo_app/base.html` - Agregado código PWA
- `bingo_app/views.py` - Vistas para servir manifest y service worker
- `bingo_app/urls.py` - URLs para manifest.json y service-worker.js

## 🔧 Configuración

### URLs agregadas:
- `/manifest.json` - Servir el manifest de la PWA
- `/service-worker.js` - Servir el service worker

### Meta tags agregados:
- `theme-color`: Color del tema (#2C3E50)
- `description`: Descripción de la app
- `manifest`: Enlace al manifest.json
- `apple-touch-icon`: Icono para iOS

## 🚀 Próximos pasos

### 1. Probar localmente:
```bash
python manage.py collectstatic
python manage.py runserver
```

Luego abrir en el navegador y verificar:
- Abrir DevTools (F12) → Application → Manifest (debe mostrar la info de la PWA)
- Application → Service Workers (debe estar registrado)
- En móvil, debería aparecer la opción de instalar

### 2. Personalizar iconos (opcional):
Los iconos actuales son básicos (con la letra "B"). Puedes reemplazarlos:
- Editar `generar_iconos_pwa.py` para cambiar el diseño
- O crear tus propios iconos y reemplazar los archivos en `bingo_app/static/images/icon-*.png`
- Tamaños necesarios: 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512

### 3. Deploy a producción:
- Asegurarse de que `collectstatic` se ejecute en el deploy
- Verificar que los archivos estáticos se sirvan correctamente
- Probar en un dispositivo móvil real

## 🐛 Troubleshooting

### El botón de instalación no aparece:
- Verificar que el sitio esté servido por HTTPS (requerido para PWA)
- Verificar que el manifest.json sea accesible: `https://tudominio.com/manifest.json`
- Verificar que el service-worker.js sea accesible: `https://tudominio.com/service-worker.js`
- Abrir DevTools → Application → Manifest para ver errores

### El service worker no se registra:
- Verificar la consola del navegador para errores
- Asegurarse de que el archivo service-worker.js esté en la ubicación correcta
- Verificar que la URL `/service-worker.js` funcione

### Los iconos no aparecen:
- Verificar que los archivos de iconos existan en `bingo_app/static/images/`
- Ejecutar `python manage.py collectstatic` para copiar los archivos a STATIC_ROOT
- Verificar las rutas en manifest.json

## 📝 Notas

- La PWA funciona mejor en HTTPS (requerido en producción)
- El service worker cachea recursos básicos para funcionar offline
- Los usuarios pueden desinstalar la app desde el menú de aplicaciones
- Cada vez que actualices el service worker, los usuarios recibirán la nueva versión automáticamente

## 🎨 Personalización

Para cambiar el nombre, colores, o descripción de la app, edita:
- `bingo_app/static/manifest.json` - Cambiar nombre, descripción, colores
- `bingo_app/templates/bingo_app/base.html` - Cambiar meta tags

---
**Fecha de implementación**: Noviembre 2025
**Estado**: ✅ Completado y listo para probar






