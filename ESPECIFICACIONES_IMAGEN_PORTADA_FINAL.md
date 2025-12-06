# 📐 ESPECIFICACIONES EXACTAS PARA LA IMAGEN DE PORTADA

## ✅ DECISIÓN FINAL

Después de analizar el código y cómo se usa la imagen, estas son las **medidas exactas** que necesitas:

### 📏 MEDIDAS EXACTAS

**Ancho: 1920 píxeles**  
**Alto: 1080 píxeles**  
**Proporción: 16:9**

### 📁 ARCHIVO DONDE DEBE IR

**Ruta completa:**
```
bingo_app/static/images/bingo_login_background_v2.png
```

**Nombre del archivo:**
```
bingo_login_background_v2.png
```

### 🎯 ¿POR QUÉ ESTAS MEDIDAS?

1. **1920x1080 es el estándar Full HD** - funciona perfecto en la mayoría de pantallas
2. **Proporción 16:9** - es la más común en desktop, tablet y móvil
3. **Con `background-size: cover`** - la imagen se ajustará correctamente sin distorsión
4. **Tamaño de archivo razonable** - no será muy pesada para cargar

### 📋 ESPECIFICACIONES TÉCNICAS COMPLETAS

- **Formato**: PNG (recomendado) o JPG
- **Resolución**: 72 DPI (para web)
- **Tamaño de archivo objetivo**: Menos de 500KB (para carga rápida)
- **Modo de color**: RGB
- **Calidad**: Alta (80-90% si es JPG)

### 🎨 ZONA SEGURA (Área Importante)

Mantén los elementos importantes (texto, logos, etc.) dentro de:
- **Centro de la imagen**: 1600 x 900 píxeles
- **Evita los bordes**: No pongas nada importante en los primeros/últimos 160px de ancho y 90px de alto

### 📱 CÓMO SE VERÁ EN DIFERENTES DISPOSITIVOS

- **Desktop (1920x1080)**: Se verá completa y perfecta
- **Tablet (1024x768)**: Se recortará un poco pero mantendrá proporción
- **Móvil (375x667)**: Se recortará más pero se centrará correctamente

### ✅ PASOS PARA CREAR/REEMPLAZAR LA IMAGEN

1. Abre tu editor (Photoshop, GIMP, Canva, etc.)
2. Crea nuevo documento: **1920 x 1080 píxeles**
3. Diseña tu imagen (mantén lo importante en el centro)
4. Exporta como PNG o JPG (calidad alta)
5. Reemplaza el archivo: `bingo_app/static/images/bingo_login_background_v2.png`
6. ¡Listo! La imagen se verá perfecta sin distorsión

---

## 📝 RESUMEN RÁPIDO

**Medidas:** 1920 x 1080 píxeles  
**Archivo:** `bingo_app/static/images/bingo_login_background_v2.png`  
**Formato:** PNG o JPG  
**Tamaño máximo:** 500KB

