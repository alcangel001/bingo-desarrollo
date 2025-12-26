# Guía para Verificar el Sistema de Múltiples Ganadores en Rifas

## 🎯 Resumen de Cambios Implementados

Se implementó un sistema completo de múltiples ganadores con premios escalonados en las rifas. Ahora puedes:

- Crear rifas con múltiples ganadores (1er, 2do, 3er lugar, etc.)
- Definir premios escalonados personalizados
- Ver todos los ganadores con sus posiciones y premios
- El sistema bloquea automáticamente el total de premios al crear la rifa

---

## 📋 Pasos para Verificar

### 1. Verificar que la Migración se Aplicó Correctamente

**En Railway:**
1. Ve a tu proyecto en Railway
2. Abre los logs del servicio
3. Busca el mensaje: `Applying bingo_app.0054_add_multiple_winners_to_raffle... OK`
4. Si ves "OK", la migración se aplicó correctamente

**O desde el Admin de Django:**
1. Ve a: `https://web-production-14f41.up.railway.app/admin/`
2. Entra a "Rifas" (Raffles)
3. Abre cualquier rifa existente
4. Deberías ver los nuevos campos:
   - ✅ "Habilitar múltiples ganadores"
   - ✅ "Estructura de premios"
   - ✅ "Ganadores"
   - ✅ "Números ganadores"

---

### 2. Crear una Rifa con Múltiples Ganadores

**Pasos:**

1. **Inicia sesión como organizador**
   - URL: `https://web-production-14f41.up.railway.app/`
   - Usa tu cuenta de organizador

2. **Ve a crear una nueva rifa**
   - URL: `https://web-production-14f41.up.railway.app/create_raffle/`
   - O desde el menú: "Crear Rifa"

3. **Llena los datos básicos:**
   - Título: "Rifa de Prueba - Múltiples Ganadores"
   - Descripción: (opcional)
   - Precio por ticket: Ej: 10 créditos
   - Premio: (este campo se usará si no activas múltiples ganadores)
   - Número inicial: 1
   - Número final: 100

4. **Activa Múltiples Ganadores:**
   - ✅ Marca el checkbox: **"Habilitar múltiples ganadores"**
   - Deberías ver aparecer una sección: **"Estructura de Premios Escalonados"**

5. **Define los Premios Escalonados:**
   - Haz clic en **"Agregar Premio"**
   - Configura los premios:
     - **1er Lugar:** 1000 créditos
     - **2do Lugar:** 500 créditos
     - **3er Lugar:** 100 créditos
   - Verifica que el **"Total de Premios"** sea correcto (1600 créditos en este ejemplo)

6. **Verifica tu saldo:**
   - Asegúrate de tener suficiente saldo para el total de premios
   - El sistema te mostrará un error si no tienes suficiente

7. **Crea la rifa:**
   - Haz clic en **"Crear Rifa"**
   - Deberías ver un mensaje de éxito

---

### 3. Verificar que los Créditos se Bloquearon Correctamente

**Pasos:**

1. **Ve a tu perfil:**
   - URL: `https://web-production-14f41.up.railway.app/profile/`
   - O desde el menú: "Mi Perfil"

2. **Verifica tu saldo bloqueado:**
   - Deberías ver que se descontó el total de premios de tu saldo disponible
   - Y se agregó a tu **"Saldo Bloqueado"**
   - Ejemplo: Si tenías 2000 créditos y creaste una rifa con 1600 en premios:
     - Saldo disponible: 400 créditos
     - Saldo bloqueado: 1600 créditos

3. **Verifica la transacción:**
   - En tu perfil, busca la sección de transacciones
   - Deberías ver una transacción que dice:
     - "Premios para rifa [nombre] (3 ganadores)"
     - Monto: -1600 créditos

---

### 4. Verificar la Estructura de Premios en la Rifa

**Pasos:**

1. **Ve a los detalles de la rifa que creaste:**
   - URL: `https://web-production-14f41.up.railway.app/raffle/[ID_DE_LA_RIFA]/`
   - O desde el lobby de rifas

2. **Verifica que se muestre la estructura de premios:**
   - Deberías ver una sección que muestra:
     - 1er Lugar: 1000 créditos
     - 2do Lugar: 500 créditos
     - 3er Lugar: 100 créditos
   - (Esto se mostrará antes del sorteo)

---

### 5. Realizar el Sorteo y Verificar Múltiples Ganadores

**Pasos:**

1. **Compra algunos tickets** (o pide a otros usuarios que compren):
   - Compra al menos 3 tickets diferentes
   - Asegúrate de que haya suficientes tickets vendidos

2. **Realiza el sorteo:**
   - Como organizador, ve a los detalles de la rifa
   - Haz clic en **"Realizar Sorteo"**
   - Confirma el sorteo

3. **Verifica los resultados:**
   - Deberías ver una sección: **"¡Tenemos múltiples ganadores!"**
   - Debería mostrar:
     - **1° Lugar:** [Usuario] - Ticket #[número] - 1000 créditos
     - **2° Lugar:** [Usuario] - Ticket #[número] - 500 créditos
     - **3° Lugar:** [Usuario] - Ticket #[número] - 100 créditos
   - **Total de Premios Distribuidos:** 1600 créditos

4. **Verifica que los tickets ganadores estén resaltados:**
   - En la grilla de números, los tickets ganadores deberían tener:
     - Fondo amarillo/dorado
     - Ícono de trofeo 🏆
     - Animación de pulso

5. **Verifica las notificaciones:**
   - Cada ganador debería recibir una notificación
   - Los ganadores deberían ver su premio en su saldo

---

### 6. Verificar que los Créditos se Desbloquearon Correctamente

**Pasos:**

1. **Ve a tu perfil como organizador:**
   - URL: `https://web-production-14f41.up.railway.app/profile/`

2. **Verifica tu saldo bloqueado:**
   - Después del sorteo, tu saldo bloqueado debería reducirse
   - Se deberían desbloquear 1600 créditos (el total de premios distribuidos)

3. **Verifica la transacción de desbloqueo:**
   - Deberías ver una transacción:
     - "Desbloqueo de créditos de premios de la rifa [nombre]"
     - Monto: +1600 créditos (o el total que se distribuyó)

---

### 7. Verificar Compatibilidad con Rifas Existentes

**Pasos:**

1. **Crea una rifa NORMAL (sin múltiples ganadores):**
   - No marques el checkbox de "Habilitar múltiples ganadores"
   - Solo define un premio único
   - Crea la rifa

2. **Verifica que funciona igual que antes:**
   - Debería funcionar exactamente como las rifas anteriores
   - Un solo ganador
   - Un solo premio

---

## 🔍 URLs Importantes

- **Crear Rifa:** `https://web-production-14f41.up.railway.app/create_raffle/`
- **Lobby de Rifas:** `https://web-production-14f41.up.railway.app/raffle_lobby/`
- **Detalles de Rifa:** `https://web-production-14f41.up.railway.app/raffle/[ID]/`
- **Mi Perfil:** `https://web-production-14f41.up.railway.app/profile/`
- **Admin Django:** `https://web-production-14f41.up.railway.app/admin/`

---

## ✅ Checklist de Verificación

- [ ] La migración se aplicó correctamente (sin errores en logs)
- [ ] Puedo crear una rifa con múltiples ganadores habilitado
- [ ] Puedo agregar/eliminar premios escalonados en el formulario
- [ ] El total de premios se calcula correctamente
- [ ] Los créditos se bloquean correctamente al crear la rifa
- [ ] La estructura de premios se muestra en los detalles de la rifa
- [ ] Puedo realizar el sorteo sin errores
- [ ] Se muestran múltiples ganadores después del sorteo
- [ ] Los tickets ganadores están resaltados en la grilla
- [ ] Los ganadores reciben sus premios correctamente
- [ ] Los créditos del organizador se desbloquean después del sorteo
- [ ] Las rifas normales (sin múltiples ganadores) siguen funcionando igual

---

## 🐛 Si Encuentras Problemas

1. **Error al crear rifa:**
   - Verifica que tienes suficiente saldo
   - Verifica que definiste al menos un premio si activaste múltiples ganadores

2. **Error al sortear:**
   - Verifica que hay suficientes tickets vendidos
   - Verifica que hay suficientes tickets únicos (sin repetir usuarios)

3. **No se muestran los ganadores:**
   - Refresca la página
   - Verifica en los logs de Railway si hubo algún error

4. **Los créditos no se desbloquean:**
   - Verifica en tu perfil las transacciones
   - Verifica que el sorteo se completó correctamente

---

## 📝 Notas Importantes

- **Un usuario solo puede ganar una vez:** Si un usuario tiene múltiples tickets ganadores, solo gana el premio más alto (1er lugar)
- **El total de premios puede ser diferente al premio base:** El sistema usa la suma de todos los premios escalonados
- **Compatibilidad:** Las rifas existentes sin múltiples ganadores siguen funcionando igual que antes

---

## 🎉 ¡Listo!

Si todos los pasos funcionan correctamente, el sistema de múltiples ganadores está completamente implementado y funcionando.




