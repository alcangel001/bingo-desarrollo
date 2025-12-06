# Corrección de la Imagen de Portada

## Problema
La imagen de portada se veía alargada porque:
1. En móvil se usaba `background-size: 100% 100%` que fuerza la imagen a llenar todo el espacio causando distorsión
2. La proporción de la imagen no coincidía con la del viewport

## Solución Implementada

### Cambios en CSS
Se corrigió `bingo_app/templates/bingo_app/login.html`:
- **Antes**: `background-size: 100% 100%` (en móvil) - causaba distorsión
- **Ahora**: `background-size: cover` - mantiene la proporción de la imagen

### Medidas Recomendadas para la Imagen
**1920 x 1080 píxeles (proporción 16:9)**

Esta medida es ideal porque:
- ✅ Es el estándar para web
- ✅ Funciona bien en todos los dispositivos
- ✅ No se verá alargada con el CSS corregido
- ✅ Tamaño de archivo razonable

## Instrucciones para Reemplazar la Imagen

1. Crea o edita tu imagen con estas medidas exactas:
   - **Ancho**: 1920 píxeles
   - **Alto**: 1080 píxeles
   - **Proporción**: 16:9

2. Guarda la imagen como PNG o JPG con buena calidad

3. Reemplaza el archivo:
   ```
   bingo_app/static/images/bingo_login_background_v2.png
   ```

4. La imagen se verá correctamente sin distorsión en todos los dispositivos

## Verificación

Después de reemplazar la imagen:
- ✅ Desktop: Se verá centrada y sin distorsión
- ✅ Tablet: Se verá centrada y sin distorsión  
- ✅ Móvil: Se verá centrada y sin distorsión (ya no se estirará)

