# 🧪 GUÍA DE PRUEBA - SISTEMA DE FRANQUICIAS

## ✅ PASO 1: Verificar que el Deploy se Completó

1. Ve a Railway: https://railway.app
2. Entra a tu proyecto "bingo-desarrollo"
3. Ve a la pestaña "Deployments"
4. Verifica que el último deploy esté en estado "Success" (verde)
5. Si está en "Building" o "Deploying", espera a que termine

---

## ✅ PASO 2: Verificar Personalización Visual

### 2.1 Entrar con Usuario Propietario de Franquicia

1. Ve a: `https://web-production-14f41.up.railway.app`
2. Inicia sesión con el usuario que es **propietario de una franquicia**
   - Este es el usuario que asignaste como "owner" cuando creaste la franquicia

### 2.2 Verificar que se Muestra la Información de la Franquicia

**Lo que DEBES ver:**
- ✅ En el navbar (arriba), debe aparecer el **nombre de tu franquicia** en lugar de "Bingo y Rifa JyM"
- ✅ Si subiste un logo, debe aparecer el **logo de la franquicia** en el navbar
- ✅ Si subiste una imagen de fondo, debe aparecer esa **imagen como fondo** de la página
- ✅ En la pestaña del navegador, debe aparecer el **nombre de la franquicia** como título

**Si NO ves esto:**
- Verifica que el usuario tenga una franquicia asignada
- Ve al panel de admin y verifica que la franquicia esté activa

---

## ✅ PASO 3: Verificar Panel de Franquicia

### 3.1 Acceder al Panel

1. En el menú de navegación, busca la opción **"Panel Franquicia"**
2. Haz clic en ella
3. Deberías ver: `https://web-production-14f41.up.railway.app/franchise/dashboard/`

### 3.2 Verificar Estadísticas

**Lo que DEBES ver:**
- ✅ Total de Juegos (y cuántos están activos)
- ✅ Total de Rifas (y cuántas están activas)
- ✅ Total de Usuarios
- ✅ Total de Créditos (suma de saldos de todos los usuarios de la franquicia)

**Si NO ves esto:**
- Verifica que tengas juegos/rifas/usuarios asignados a tu franquicia

---

## ✅ PASO 4: Verificar Filtrado Automático

### 4.1 Verificar Lobby

1. Ve al **Lobby** (página principal)
2. **Lo que DEBES ver:**
   - ✅ Solo juegos de bingo que pertenecen a TU franquicia
   - ✅ Solo rifas que pertenecen a TU franquicia
   - ❌ NO deberías ver juegos/rifas de otras franquicias
   - ❌ NO deberías ver juegos/rifas sin franquicia asignada (a menos que seas super admin)

### 4.2 Crear un Juego Nuevo

1. Ve a "Crear Sala" o "Crear Juego"
2. Llena el formulario y crea un juego
3. **Lo que DEBES verificar:**
   - ✅ El juego se crea correctamente
   - ✅ El juego aparece en el lobby
   - ✅ El juego está asignado automáticamente a tu franquicia

**Cómo verificar que está asignado a tu franquicia:**
- Ve al panel de admin (si eres super admin)
- O verifica en el código que el juego tenga `franchise = tu_franquicia`

### 4.3 Crear una Rifa Nueva

1. Ve a "Crear Rifa"
2. Llena el formulario y crea una rifa
3. **Lo que DEBES verificar:**
   - ✅ La rifa se crea correctamente
   - ✅ La rifa aparece en el lobby de rifas
   - ✅ La rifa está asignada automáticamente a tu franquicia

---

## ✅ PASO 5: Verificar Sistema de Solicitudes

### 5.1 Preparar un Usuario de Prueba

1. Crea un usuario nuevo (o usa uno existente)
2. **IMPORTANTE:** Asigna este usuario a tu franquicia:
   - Ve al panel de admin
   - Edita el usuario
   - En el campo "Franchise", selecciona tu franquicia
   - Guarda

### 5.2 Hacer una Solicitud de Crédito

1. **Cierra sesión** y entra con el usuario de prueba
2. Ve a tu perfil
3. Haz una solicitud de crédito (por ejemplo, $10)
4. Sube un comprobante (puede ser cualquier imagen)
5. Envía la solicitud

### 5.3 Verificar que la Solicitud Llegue al Panel del Franquiciado

1. **Cierra sesión** y entra con el usuario propietario de la franquicia
2. Ve al **Panel Franquicia** (`/franchise/dashboard/`)
3. **Lo que DEBES ver:**
   - ✅ En "Solicitudes de Crédito Pendientes", debe aparecer la solicitud que acabas de hacer
   - ✅ Debe mostrar el nombre del usuario, el monto y la fecha

4. Haz clic en "Ver" o "Procesar"
5. **Lo que DEBES ver:**
   - ✅ Los detalles de la solicitud
   - ✅ El comprobante que subió el usuario
   - ✅ Botones para "Aprobar" o "Rechazar"

### 5.4 Aprobar una Solicitud de Crédito

1. En la página de procesar solicitud, haz clic en **"Aprobar Solicitud"**
2. **Lo que DEBES verificar:**
   - ✅ Mensaje de éxito
   - ✅ La solicitud desaparece de "Pendientes"
   - ✅ El usuario ahora tiene los créditos en su cuenta

**Para verificar que el usuario tiene los créditos:**
- Entra con el usuario de prueba
- Ve a su perfil
- Verifica que su saldo aumentó

### 5.5 Hacer una Solicitud de Retiro

1. Entra con el usuario de prueba
2. Asegúrate de que tenga saldo suficiente (por ejemplo, $20)
3. Ve a "Retiros" en el menú
4. Haz una solicitud de retiro (por ejemplo, $15)
5. Llena los datos bancarios
6. Envía la solicitud

### 5.6 Verificar y Aprobar Solicitud de Retiro

1. Entra con el usuario propietario de la franquicia
2. Ve al **Panel Franquicia**
3. **Lo que DEBES ver:**
   - ✅ En "Solicitudes de Retiro Pendientes", debe aparecer la solicitud

4. Haz clic en "Ver" o "Procesar"
5. **Lo que DEBES ver:**
   - ✅ Los detalles de la solicitud
   - ✅ Los datos bancarios
   - ✅ El saldo actual del usuario
   - ✅ Botones para "Aprobar" o "Rechazar"

6. Haz clic en **"Aprobar y Procesar Retiro"**
7. **Lo que DEBES verificar:**
   - ✅ Mensaje de éxito
   - ✅ La solicitud desaparece de "Pendientes"
   - ✅ El saldo del usuario se descontó

---

## ✅ PASO 6: Verificar Aislamiento de Datos

### 6.1 Crear Otra Franquicia (si eres super admin)

1. Ve al panel de admin
2. Crea otra franquicia con otro propietario
3. Crea algunos juegos/rifas para esa franquicia

### 6.2 Verificar que NO Ves Datos de Otra Franquicia

1. Entra con el usuario propietario de la PRIMERA franquicia
2. **Lo que DEBES verificar:**
   - ✅ En el lobby, NO ves juegos/rifas de la segunda franquicia
   - ✅ En el panel de franquicia, NO ves usuarios de la segunda franquicia
   - ✅ En solicitudes, NO ves solicitudes de usuarios de la segunda franquicia

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### Problema: No veo el nombre de la franquicia en el navbar
**Solución:**
- Verifica que el usuario tenga una franquicia asignada
- Verifica que la franquicia esté activa
- Limpia la caché del navegador (Ctrl+F5)

### Problema: No veo el panel de franquicia en el menú
**Solución:**
- Verifica que el usuario sea propietario de una franquicia (`owned_franchise`)
- Verifica que el usuario tenga `is_organizer = True`

### Problema: Veo juegos de otras franquicias
**Solución:**
- Verifica que el middleware esté activo en `settings.py`
- Verifica que los juegos tengan `franchise` asignado
- Si eres super admin, es normal que veas todo

### Problema: Las solicitudes no aparecen en el panel del franquiciado
**Solución:**
- Verifica que el usuario que hizo la solicitud tenga `franchise` asignado
- Verifica que la franquicia del usuario sea la misma que la del propietario
- Verifica que la solicitud tenga `franchise` asignado en la base de datos

### Problema: Error al aprobar solicitud
**Solución:**
- Verifica que el usuario tenga suficiente saldo (para retiros)
- Verifica los logs de Railway para ver el error específico
- Verifica que la transacción se complete correctamente

---

## ✅ CHECKLIST FINAL

Antes de considerar que todo funciona, verifica:

- [ ] El nombre de la franquicia aparece en el navbar
- [ ] El logo aparece (si lo subiste)
- [ ] La imagen de fondo aparece (si la subiste)
- [ ] El panel de franquicia es accesible
- [ ] Las estadísticas se muestran correctamente
- [ ] Solo ves juegos/rifas de tu franquicia en el lobby
- [ ] Los juegos nuevos se asignan automáticamente a tu franquicia
- [ ] Las rifas nuevas se asignan automáticamente a tu franquicia
- [ ] Las solicitudes de crédito aparecen en el panel del franquiciado
- [ ] Puedes aprobar solicitudes de crédito
- [ ] Las solicitudes de retiro aparecen en el panel del franquiciado
- [ ] Puedes aprobar solicitudes de retiro
- [ ] NO ves datos de otras franquicias
- [ ] Los usuarios de tu franquicia solo ven datos de tu franquicia

---

## 📞 ¿NECESITAS AYUDA?

Si encuentras algún problema:
1. Revisa los logs de Railway
2. Revisa la consola del navegador (F12)
3. Verifica que todos los pasos anteriores se hayan completado
4. Documenta el error específico que estás viendo




