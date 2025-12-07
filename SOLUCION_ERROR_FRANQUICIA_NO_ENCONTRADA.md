# 🔧 SOLUCIÓN: "Franquicia no encontrada o inactiva"

## 📋 PASO 1: Verificar el Slug Exacto de tu Franquicia

1. **Entra como super admin** a: `https://web-production-14f41.up.railway.app/admin/`
2. Ve a **"Franchises"** en el menú izquierdo
3. Haz clic en la franquicia que creaste
4. **Busca el campo "Slug"** - ese es el código exacto que debes usar
5. **Copia ese slug exactamente** (puede tener guiones, minúsculas, etc.)

**Ejemplo:** Si el slug es `mi-franquicia-2024`, ese es el que debes usar.

---

## 📋 PASO 2: Verificar que la Franquicia Esté Activa

En la misma página de detalles de la franquicia:

1. **Busca el campo "Is active"** (o "Activa")
2. **Debe estar marcado/activado** ✅
3. Si NO está activada:
   - Márcala como activa
   - Guarda los cambios

---

## 📋 PASO 3: Obtener el Enlace Correcto

### Opción A: Desde el Panel de Franquicia (Recomendado)

1. **Entra con el usuario "jenirecano"**
2. Ve al **Panel de Franquicia**: `https://web-production-14f41.up.railway.app/franchise/dashboard/`
3. En la sección **"Enlace de Registro para tus Clientes"** verás:
   - El enlace completo (ya copiado y listo)
   - El slug exacto de tu franquicia

### Opción B: Construir el Enlace Manualmente

Si el slug de tu franquicia es, por ejemplo: `mi-franquicia`

El enlace sería:
```
https://web-production-14f41.up.railway.app/franchise/mi-franquicia/
```

**⚠️ IMPORTANTE:**
- El slug debe ser **exactamente igual** al que está en la base de datos
- No debe tener espacios
- Debe tener el `/` al final
- Es case-sensitive (mayúsculas/minúsculas importan)

---

## 📋 PASO 4: Probar el Enlace

1. **Copia el enlace completo** del Panel de Franquicia
2. **Pégalo en una nueva pestaña** del navegador
3. **Deberías ver:**
   - ✅ La imagen de fondo de tu franquicia
   - ✅ El logo (si lo subiste)
   - ✅ El nombre de tu franquicia
   - ✅ Botones para registrarse

**Si ves el error "Franquicia no encontrada":**
- Verifica que el slug sea exactamente igual
- Verifica que la franquicia esté activa
- Prueba con el enlace directo al registro: `https://web-production-14f41.up.railway.app/register/?franchise=TU-SLUG`

---

## 📋 PASO 5: Verificar en el Admin

Si sigues teniendo problemas:

1. Ve al admin: `https://web-production-14f41.up.railway.app/admin/`
2. Ve a **"Franchises"**
3. Abre tu franquicia
4. **Verifica estos campos:**
   - ✅ **Slug:** Debe tener un valor (ej: `mi-franquicia`)
   - ✅ **Is active:** Debe estar marcado
   - ✅ **Owner:** Debe ser "jenirecano"
   - ✅ **Name:** Debe tener un nombre

5. **Si el slug está vacío o tiene espacios:**
   - Edítalo para que sea algo como: `mi-franquicia` (sin espacios, solo letras, números y guiones)
   - Guarda los cambios

---

## 🔍 DIAGNÓSTICO RÁPIDO

**Preguntas para verificar:**

1. ¿Cuál es el slug exacto de tu franquicia? (Dímelo y te ayudo a construir el enlace)
2. ¿La franquicia está marcada como "Activa" en el admin?
3. ¿Qué enlace exacto estás usando? (Cópialo y pégalo aquí)

---

## ✅ SOLUCIÓN RÁPIDA

Si quieres una solución inmediata:

1. Ve al admin
2. Abre tu franquicia
3. **Copia el slug exacto**
4. Construye el enlace así: `https://web-production-14f41.up.railway.app/franchise/[TU-SLUG-AQUI]/`
5. Reemplaza `[TU-SLUG-AQUI]` con el slug exacto

**Ejemplo:**
- Si el slug es: `franquicia-jenire`
- El enlace es: `https://web-production-14f41.up.railway.app/franchise/franquicia-jenire/`

---

## 🆘 SI NADA FUNCIONA

1. **Dime el slug exacto** de tu franquicia (cópialo del admin)
2. **Dime si está activa** (sí o no)
3. **Prueba este enlace directo al registro** (reemplaza TU-SLUG):
   ```
   https://web-production-14f41.up.railway.app/register/?franchise=TU-SLUG
   ```

Este enlace directo al registro debería funcionar aunque la landing no funcione.

