# 📋 GUÍA: Cómo Asignar 300 Cartones a un Cliente

## 🎯 Objetivo
Asignar 300 cartones imprimibles a un cliente específico de forma rápida y eficiente.

---

## 📝 PASO A PASO

### **PASO 1: Verificar que tienes suficientes cartones disponibles**

1. **Accede a la gestión de cartones:**
   ```
   https://web-production-14f41.up.railway.app/admin-panel/printable-cards/
   ```

2. **Verifica cuántos cartones sin asignar tienes:**
   - Busca en la lista los cartones que tienen "Sin asignar" en la columna "Propietario"
   - Si tienes menos de 300 cartones sin asignar, necesitas generar más

---

### **PASO 2: Generar cartones (si no tienes suficientes)**

1. **Desde la página de gestión de cartones, haz clic en "Generar Cartones"** o ve directamente a:
   ```
   https://web-production-14f41.up.railway.app/admin-panel/printable-cards/generate/
   ```

2. **En el formulario:**
   - **Cantidad:** Ingresa `300` (o más si quieres tener extras)
   - Haz clic en **"Generar Cartones"**

3. **Espera a que se generen:**
   - Verás un mensaje de éxito cuando se completen
   - Los cartones aparecerán en la lista con "Sin asignar"

---

### **PASO 3: Asignar los cartones en masa al cliente**

1. **Ve a la página de asignación en masa:**
   ```
   https://web-production-14f41.up.railway.app/admin-panel/bulk-assign-cards/
   ```

2. **Selecciona el cliente:**
   - En el dropdown **"Seleccionar Usuario"**, busca y selecciona el cliente
   - Si no aparece, verifica que el usuario existe y no es staff/admin

3. **Selecciona los 300 cartones:**
   - Verás una lista de cartones disponibles (sin asignar)
   - **Marca los checkboxes** de los 300 cartones que quieres asignar
   - 💡 **TIP:** Puedes usar "Seleccionar todo" si tu navegador lo permite (Ctrl+A en algunos casos)
   - Si hay muchos cartones, puedes usar la búsqueda del navegador (Ctrl+F) para encontrar rangos específicos

4. **Confirma la asignación:**
   - Haz clic en el botón **"Asignar Cartones"**
   - Verás un mensaje de éxito indicando cuántos cartones se asignaron

---

### **PASO 4: Verificar la asignación**

1. **Vuelve a la página de gestión de cartones:**
   ```
   https://web-production-14f41.up.railway.app/admin-panel/printable-cards/
   ```

2. **Filtra por el cliente:**
   - Busca en la lista los cartones que ahora tienen el nombre del cliente en "Propietario"
   - Deberías ver 300 cartones asignados a ese cliente

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

### **Problema 1: No tengo suficientes cartones sin asignar**
**Solución:** 
- Genera más cartones usando el paso 2
- Puedes generar hasta 1000 cartones a la vez

### **Problema 2: El cliente no aparece en la lista**
**Solución:**
- Verifica que el usuario existe
- Verifica que el usuario NO es staff ni superuser (solo usuarios normales aparecen)
- Si es necesario, crea el usuario primero

### **Problema 3: No puedo seleccionar 300 cartones fácilmente**
**Solución:**
- Selecciona los cartones en grupos (ej: 50 a la vez)
- O genera exactamente 300 cartones nuevos y asígnalos todos de una vez

### **Problema 4: Error al asignar**
**Solución:**
- Verifica que seleccionaste un usuario
- Verifica que seleccionaste al menos un cartón
- Asegúrate de que los cartones no estén ya asignados a otro usuario

---

## 🎯 MÉTODO RÁPIDO (Recomendado)

Si quieres hacerlo más rápido:

1. **Genera exactamente 300 cartones nuevos:**
   - Ve a: `https://web-production-14f41.up.railway.app/admin-panel/printable-cards/generate/`
   - Genera 300 cartones

2. **Asigna todos de una vez:**
   - Ve a: `https://web-production-14f41.up.railway.app/admin-panel/bulk-assign-cards/`
   - Selecciona el cliente
   - Selecciona TODOS los cartones recién generados (deberían estar al inicio de la lista)
   - Asigna

---

## 📊 VERIFICACIÓN FINAL

Para confirmar que todo está correcto:

1. **Cuenta los cartones asignados:**
   - Ve a la gestión de cartones
   - Busca los cartones del cliente
   - Deberías ver exactamente 300 cartones

2. **Verifica desde el perfil del cliente (opcional):**
   - Si el cliente tiene acceso, puede ver sus cartones en su perfil
   - Los cartones aparecerán como "Disponibles" para usar en juegos

---

## 🔗 LINKS RÁPIDOS

- **Gestión de Cartones:** `https://web-production-14f41.up.railway.app/admin-panel/printable-cards/`
- **Generar Cartones:** `https://web-production-14f41.up.railway.app/admin-panel/printable-cards/generate/`
- **Asignar en Masa:** `https://web-production-14f41.up.railway.app/admin-panel/bulk-assign-cards/`

---

## 💡 CONSEJOS ADICIONALES

1. **Genera más cartones de los que necesitas:**
   - Si necesitas 300, genera 350 para tener extras
   - Esto te permite tener cartones de respaldo

2. **Organiza los cartones:**
   - Los cartones tienen IDs únicos (ej: `P-ABC12345`)
   - Puedes anotar los IDs asignados si necesitas hacer seguimiento

3. **Asignación por lotes:**
   - Si necesitas asignar a múltiples clientes, hazlo por lotes
   - Ejemplo: 100 cartones a cada uno de 3 clientes

---

**Última actualización:** Diciembre 2025




