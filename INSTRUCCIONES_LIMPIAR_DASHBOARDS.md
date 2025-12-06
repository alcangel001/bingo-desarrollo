# 🧹 Instrucciones para Limpiar Dashboards

## 📋 Descripción

El comando `limpiar_dashboards` elimina todos los datos históricos de los dashboards (juegos, transacciones, rifas, etc.) pero **conserva** usuarios y configuraciones del sistema.

---

## ⚠️ ADVERTENCIA IMPORTANTE

**Esta acción es IRREVERSIBLE.** Todos los datos históricos se eliminarán permanentemente.

**Se CONSERVARÁN:**
- ✅ Todos los usuarios registrados
- ✅ Configuraciones del sistema (comisiones, etc.)
- ✅ Métodos de pago (cuentas bancarias)
- ✅ Anuncios generales
- ✅ Promociones y referidos (configuración)
- ✅ Logros (configuración)

**Se ELIMINARÁN:**
- ❌ Todos los juegos creados
- ❌ Todas las transacciones históricas
- ❌ Todos los tickets/cartones comprados
- ❌ Todas las rifas
- ❌ Todos los mensajes de chat
- ❌ Todas las solicitudes de crédito/retiro
- ❌ Todos los cartones imprimibles

---

## 🚀 Uso del Comando

### 1. Vista Previa (Recomendado primero)

Ver qué se eliminaría sin ejecutar nada:

```bash
python manage.py limpiar_dashboards --solo-vista-previa
```

**Ejemplo de salida:**
```
🧹 LIMPIEZA DE DASHBOARDS
============================================================

📋 DATOS QUE SE CONSERVARÁN:
  ✅ Todos los usuarios registrados
  ✅ Configuraciones del sistema (comisiones, etc.)
  ...

📊 DATOS ACTUALES:
  • Juegos: 25
  • Transacciones: 500
  ...

⚠️  MODO VISTA PREVIA - No se ejecutará ninguna acción
```

---

### 2. Limpieza Completa (Recomendada para lanzamiento)

Limpia todos los datos históricos:

```bash
python manage.py limpiar_dashboards
```

El comando:
1. Mostrará un resumen de lo que se eliminará
2. Pedirá confirmación (escribir "SI" para confirmar)
3. Ejecutará la limpieza
4. Mostrará un resumen final

---

### 3. Limpieza Completa + Reset de Saldos

Limpia datos históricos Y resetea todos los saldos de usuarios a 0:

```bash
python manage.py limpiar_dashboards --reset-saldos
```

**Esta es la opción recomendada para un lanzamiento limpio.**

**Qué hace:**
- Elimina todos los juegos, transacciones, rifas, etc.
- Resetea `credit_balance` de todos los usuarios a 0
- Resetea `blocked_credits` de todos los usuarios a 0
- Resetea `total_completed_events` de todos los usuarios a 0

---

### 4. Limpieza sin Confirmación (Peligroso)

Solo para scripts automatizados. **NO recomendado para uso manual:**

```bash
python manage.py limpiar_dashboards --sin-confirmacion --reset-saldos
```

---

## 📊 Ejemplo de Ejecución Completa

```bash
$ python manage.py limpiar_dashboards --reset-saldos

============================================================
🧹 LIMPIEZA DE DASHBOARDS
============================================================

📋 DATOS QUE SE CONSERVARÁN:
  ✅ Todos los usuarios registrados
  ✅ Configuraciones del sistema (comisiones, etc.)
  ✅ Métodos de pago (cuentas bancarias)
  ✅ Anuncios generales
  ✅ Promociones y referidos (configuración)
  ✅ Logros (configuración)
  ✅ Historial de bloqueos

📊 DATOS ACTUALES:
  • Juegos: 25
  • Jugadores en juegos: 150
  • Transacciones: 500
  • Tickets (Bingo clásico): 200
  • BingoTickets (Bingo mejorado): 100
  • Rifas: 10
  • Mensajes de chat: 300
  • Mensajes privados: 50
  • Solicitudes de crédito: 5
  • Solicitudes de retiro: 3
  • Cartones imprimibles: 20
  • Grupos de videollamada: 25
  • Usuarios: 200 ✅ (SE CONSERVAN)
  • Saldo total de usuarios: $1500.00
  • Saldo bloqueado total: $500.00

🗑️  DATOS QUE SE ELIMINARÁN:
  ❌ 25 juegos
  ❌ 150 jugadores en juegos
  ❌ 500 transacciones
  ...
  ⚠️  Saldos de usuarios se resetearán a 0
     (Total a resetear: $2000.00)

⚠️  ADVERTENCIA: Esta acción es IRREVERSIBLE

¿Estás seguro de que quieres continuar? (escribe "SI" para confirmar): SI

🚀 Iniciando limpieza...

  ✅ Eliminados 300 mensajes de chat
  ✅ Eliminados 150 jugadores en juegos
  ✅ Eliminados 200 tickets (bingo clásico)
  ✅ Eliminados 100 bingotickets
  ✅ Eliminadas 450 transacciones relacionadas con juegos
  ✅ Eliminadas 8 transacciones de retiro
  ✅ Eliminadas 10 notificaciones de crédito
  ✅ Eliminadas 6 notificaciones de retiro
  ✅ Eliminadas 5 solicitudes de crédito
  ✅ Eliminadas 3 solicitudes de retiro
  ✅ Eliminados 20 cartones imprimibles
  ✅ Eliminados 25 grupos de videollamada
  ✅ Eliminados 50 mensajes privados
  ✅ Eliminadas 10 rifas
  ✅ Eliminados 25 juegos
  ✅ Saldos reseteados para 50 usuarios
  ✅ Contador de eventos completados reseteado
  ✅ Eliminadas 42 transacciones restantes

============================================================
✅ LIMPIEZA COMPLETADA EXITOSAMENTE
============================================================

📊 RESUMEN:
  • Total de registros eliminados: 1390

✅ Datos conservados:
  • Usuarios: 200
  • Configuraciones del sistema
  • Métodos de pago
  • Anuncios
  • Promociones y referidos
```

---

## ✅ Verificación Post-Limpieza

Después de ejecutar el comando, verifica que:

1. **Usuarios se conservaron:**
   ```bash
   python manage.py shell
   >>> from bingo_app.models import User
   >>> User.objects.count()
   200  # Debe ser el mismo número de antes
   ```

2. **Configuraciones se conservaron:**
   ```bash
   >>> from bingo_app.models import PercentageSettings
   >>> PercentageSettings.objects.exists()
   True
   ```

3. **Dashboards están vacíos:**
   - Ir al dashboard del administrador: Debe mostrar 0 juegos, $0 en todo
   - Ir al dashboard del organizador: Debe mostrar 0 juegos, $0 en todo

4. **Saldos reseteados (si usaste --reset-saldos):**
   ```bash
   >>> User.objects.aggregate(Sum('credit_balance'))
   {'credit_balance__sum': Decimal('0.00')}
   ```

---

## 🔧 Solución de Problemas

### Error: "No puedo eliminar porque hay Foreign Key constraints"

Si hay un error de Foreign Key, el comando maneja el orden correcto de eliminación. Si aún así falla:

1. El comando usa `transaction.atomic()` - si falla, se revierten todos los cambios
2. Verifica que no haya procesos ejecutándose (servidor web, tareas en background)
3. Verifica que la base de datos esté accesible

### Error: "Operación cancelada"

Es normal si cancelas la confirmación. El comando está funcionando correctamente.

---

## 💾 Backup Recomendado

**ANTES de ejecutar el comando, haz un backup:**

```bash
# SQLite (desarrollo)
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# PostgreSQL (producción)
pg_dump -U usuario -d nombre_db > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL (producción)
mysqldump -u usuario -p nombre_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 📝 Notas Finales

- El comando es **seguro**: usa transacciones atómicas (si falla, revierte todo)
- El comando es **completo**: elimina todos los datos históricos
- El comando es **conservador**: no toca usuarios ni configuraciones
- El comando es **informativo**: muestra resumen antes y después

---

## 🎯 Para un Lanzamiento Limpio

**Ejecuta:**

```bash
python manage.py limpiar_dashboards --reset-saldos
```

Esto dejará:
- ✅ Sistema funcionando
- ✅ Usuarios conservados
- ✅ Configuraciones activas
- ✅ Dashboards completamente vacíos (listos para comenzar)
- ✅ Todos los saldos en 0 (empiezan desde cero)

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo recuperar los datos después?**
R: No, la eliminación es permanente. Siempre haz backup antes.

**P: ¿Se eliminan las configuraciones?**
R: No, se conservan todas las configuraciones del sistema.

**P: ¿Los usuarios pueden seguir iniciando sesión?**
R: Sí, todos los usuarios se conservan con sus contraseñas.

**P: ¿Puedo ejecutar esto en producción?**
R: Sí, pero asegúrate de hacer backup primero y ejecutarlo en un horario de bajo tráfico.

**P: ¿Cuánto tiempo toma?**
R: Depende de la cantidad de datos. Para 1000 juegos puede tomar unos segundos.








