# Medidas Exactas para la Imagen de Portada

## Imagen Actual
**Archivo**: `bingo_app/static/images/bingo_login_background_v2.png`

## Problema Identificado
La imagen se ve alargada porque:
1. Se usa `background-size: cover` que puede distorsionar la imagen
2. En móvil se usa `background-size: 100% 100%` que fuerza la imagen a llenar todo el espacio (causa distorsión)

## Medidas Recomendadas

### Opción 1: Proporción 16:9 (Recomendada para Desktop y Tablet)
Esta es la proporción más común y funciona bien en la mayoría de dispositivos.

**Medidas exactas:**
- **1920 x 1080 píxeles** (Full HD)
- **3840 x 2160 píxeles** (4K Ultra HD - mejor calidad)
- **2560 x 1440 píxeles** (2K - buena calidad)

**Proporción**: 16:9 (1.777:1)

### Opción 2: Proporción 21:9 (Ultra Wide)
Para una imagen más panorámica:

**Medidas exactas:**
- **2560 x 1080 píxeles**
- **3440 x 1440 píxeles**

**Proporción**: 21:9 (2.333:1)

### Opción 3: Proporción 4:3 (Más cuadrada)
Para una imagen más cuadrada:

**Medidas exactas:**
- **1920 x 1440 píxeles**
- **1600 x 1200 píxeles**

**Proporción**: 4:3 (1.333:1)

## Recomendación Final

**Usa: 1920 x 1080 píxeles (16:9)**

Esta medida es:
- ✅ Estándar para web
- ✅ Funciona bien en desktop, tablet y móvil
- ✅ Tamaño de archivo razonable
- ✅ Buena calidad visual
- ✅ Compatible con la mayoría de dispositivos

## Especificaciones Técnicas

### Resolución
- **Ancho**: 1920 píxeles
- **Alto**: 1080 píxeles
- **Proporción**: 16:9

### Formato
- **Formato recomendado**: PNG (para transparencia si la necesitas) o JPG (para menor tamaño de archivo)
- **Calidad**: Alta (80-90% si es JPG)
- **Tamaño de archivo objetivo**: Menos de 500KB (para carga rápida)

### Área Segura
- **Zona central importante**: 1600 x 900 píxeles (centro de la imagen)
- Evita poner texto o elementos importantes en los bordes (primeros y últimos 160px de ancho, primeros y últimos 90px de alto)

## Cómo Crear la Imagen

1. **Abre tu editor de imágenes** (Photoshop, GIMP, Canva, etc.)
2. **Crea un nuevo documento** con estas medidas:
   - Ancho: 1920 píxeles
   - Alto: 1080 píxeles
   - Resolución: 72 DPI (para web) o 300 DPI (si quieres mejor calidad)
3. **Diseña tu imagen** manteniendo los elementos importantes en el centro
4. **Exporta como PNG o JPG** con buena calidad
5. **Reemplaza** el archivo `bingo_login_background_v2.png` en `bingo_app/static/images/`

## Nota Importante

He corregido el CSS para que la imagen NO se vea alargada. Ahora usa:
- `background-size: cover` (mantiene proporción)
- `background-position: center` (centra la imagen)
- `object-fit: cover` (para imágenes en elementos)

Con estas correcciones, cualquier imagen con proporción 16:9 se verá correctamente sin distorsión.

