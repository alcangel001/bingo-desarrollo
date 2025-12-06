# Opciones para Limpiar Dashboards (Conservando Usuarios)

## 📊 Datos que se CONSERVARÁN

✅ **Usuarios** (`User`) - Todos los usuarios registrados
✅ **Configuraciones del Sistema** (`PercentageSettings`) - Configuración de comisiones
✅ **Cuentas Bancarias** (`BankAccount`) - Métodos de pago configurados
✅ **Anuncios** (`Announcement`) - Anuncios generales del sistema
✅ **Promociones** (`LaunchPromotion`, `UserPromotion`) - Sistema de promociones
✅ **Referidos** (`ReferralProgram`) - Configuración de referidos
✅ **Logros** (`LaunchAchievement`, `UserAchievement`) - Sistema de logros
✅ **Configuración de Cartones** (`BingoTicketSettings`, `DailyBingoSchedule`) - Configuraciones
✅ **Historial de Bloqueos** (`UserBlockHistory`) - Historial administrativo

---

## 🗑️ Datos que se ELIMINARÁN (Dashboard)

### Opción 1: Limpieza COMPLETA (Recomendada para lanzamiento)
Elimina todo el historial de juegos y actividades:

- ❌ **Juegos** (`Game`) - Todos los juegos creados
- ❌ **Jugadores en juegos** (`Player`) - Participaciones en juegos
- ❌ **Transacciones** (`Transaction`) - Todas las transacciones históricas
- ❌ **Tickets/BingoTickets** (`Ticket`, `BingoTicket`) - Todos los cartones comprados
- ❌ **Rifas** (`Raffle`) - Todas las rifas creadas
- ❌ **Mensajes de Chat** (`ChatMessage`) - Mensajes en salas de juego
- ❌ **Mensajes entre usuarios** (`Message`) - Mensajes privados
- ❌ **Solicitudes de crédito** (`CreditRequest`) - Solicitudes pendientes/completadas
- ❌ **Notificaciones de crédito** (`CreditRequestNotification`) - Notificaciones históricas
- ❌ **Solicitudes de retiro** (`WithdrawalRequest`) - Todas las solicitudes de retiro
- ❌ **Notificaciones de retiro** (`WithdrawalRequestNotification`) - Notificaciones históricas
- ❌ **Cartones imprimibles** (`PrintableCard`) - Cartones físicos asignados
- ❌ **Grupos de videollamada** (`VideoCallGroup`) - Grupos de juegos

### Opción 2: Limpieza SELECTIVA (Solo historial, mantiene configuraciones)
Elimina solo el historial pero conserva configuraciones:

- ❌ **Juegos finalizados** (`Game` donde `is_finished=True`)
- ❌ **Rifas finalizadas** (`Raffle` donde `status='FINISHED'`)
- ❌ **Transacciones antiguas** (`Transaction` de más de X días)
- ❌ **Tickets de juegos finalizados** (`Ticket`, `BingoTicket` de juegos eliminados)
- ❌ **Chat de juegos finalizados** (`ChatMessage` de juegos eliminados)
- ✅ **Conserva**: Juegos activos/no iniciados, solicitudes pendientes, cartones imprimibles

### Opción 3: Reset de Saldos (Mantiene estructura, limpia dinero)
Limpia saldos pero conserva juegos y transacciones:

- ❌ **Resetear saldos** (`User.credit_balance = 0`)
- ❌ **Resetear bloqueados** (`User.blocked_credits = 0`)
- ❌ **Resetear contadores** (`User.total_completed_events = 0`)
- ✅ **Conserva**: Juegos, transacciones, tickets (historial completo)

---

## 🔧 OPCIONES DE IMPLEMENTACIÓN

### **Opción A: Comando Django de Gestión** ⭐ RECOMENDADA

Crear un comando: `python manage.py limpiar_dashboards --opcion=1`

**Ventajas:**
- ✅ Seguro y controlado
- ✅ Puede hacer backup automático antes
- ✅ Muestra resumen de lo que se eliminará
- ✅ Fácil de ejecutar y repetir
- ✅ Puede tener confirmación interactiva

**Ejemplo de uso:**
```bash
# Limpieza completa
python manage.py limpiar_dashboards --completo

# Limpieza selectiva (solo finalizados)
python manage.py limpiar_dashboards --selectivo

# Solo resetear saldos
python manage.py limpiar_dashboards --saldos
```

---

### **Opción B: Script SQL Directo**

Ejecutar SQL directamente en la base de datos.

**Ventajas:**
- ✅ Rápido
- ✅ Control total
- ❌ Requiere acceso directo a BD
- ❌ Más riesgoso si hay errores

**Ejemplo SQL:**
```sql
-- Limpiar juegos y todo lo relacionado
DELETE FROM bingo_app_chatmessage;
DELETE FROM bingo_app_player;
DELETE FROM bingo_app_ticket;
DELETE FROM bingo_app_bingoticket;
DELETE FROM bingo_app_transaction WHERE related_game_id IS NOT NULL;
DELETE FROM bingo_app_game;
-- ... etc
```

---

### **Opción C: Script Python Independiente**

Script `.py` que se ejecuta directamente (sin Django shell).

**Ventajas:**
- ✅ Fácil de entender
- ✅ Puede incluir confirmaciones
- ❌ Requiere configuración de Django

**Ejemplo:**
```python
# limpiar_dashboards.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import Game, Player, Transaction, ...
# ... lógica de limpieza
```

---

### **Opción D: Interfaz Web (Admin Django)**

Panel en el admin de Django para limpiar dashboards.

**Ventajas:**
- ✅ Interfaz visual
- ✅ Fácil de usar
- ❌ Requiere desarrollo adicional
- ❌ Menos seguro (acceso web)

---

## 📋 RECOMENDACIÓN FINAL

**Para tu caso (lanzamiento con usuarios conservados):**

**Opción 1A (Limpieza Completa + Comando Django):**

1. ✅ Crear comando `limpiar_dashboards`
2. ✅ Hacer backup automático antes de limpiar
3. ✅ Mostrar resumen de lo que se eliminará
4. ✅ Pedir confirmación antes de ejecutar
5. ✅ Resetear saldos de usuarios a 0
6. ✅ Resetear contadores (`total_completed_events`)
7. ✅ Conservar usuarios y configuraciones

**Flujo sugerido:**
```
1. Hacer backup completo
2. Ejecutar: python manage.py limpiar_dashboards --completo --confirmar
3. Verificar que usuarios se mantuvieron
4. Verificar que configuraciones se mantuvieron
5. Resetear saldos de todos los usuarios a 0
```

---

## ⚠️ ADVERTENCIAS

1. **Saldos de Usuarios**: Después de limpiar, los saldos pueden quedar inconsistentes. Considera:
   - Resetear todos los saldos a 0
   - O conservar solo saldos de recargas administrativas

2. **Relaciones Foreign Key**: Al eliminar juegos, las transacciones relacionadas pueden quedar huérfanas. El comando debe manejar esto.

3. **Backup**: SIEMPRE hacer backup antes de limpiar.

4. **Pruebas**: Probar primero en entorno de desarrollo.

---

## ❓ PREGUNTAS PARA DECIDIR

1. ¿Quieres conservar los saldos actuales de los usuarios o resetearlos a 0?
2. ¿Quieres conservar juegos que no han iniciado?
3. ¿Quieres conservar solicitudes de crédito/retiro pendientes?
4. ¿Quieres hacer backup automático antes de limpiar?

---

## 🎯 ORDEN DE EJECUCIÓN RECOMENDADO

Si eliges la Opción 1A, el comando ejecutará en este orden:

1. Mostrar resumen de datos a eliminar
2. Pedir confirmación
3. Hacer backup (opcional)
4. Eliminar en orden (respetando Foreign Keys):
   - `ChatMessage`
   - `Player`
   - `Ticket` / `BingoTicket`
   - `Transaction` (relacionadas a juegos)
   - `Game`
   - `Raffle`
   - `Message` (mensajes privados)
   - `CreditRequest` / `WithdrawalRequest`
   - Notificaciones
5. Resetear saldos y contadores (si se solicita)
6. Mostrar resumen final








