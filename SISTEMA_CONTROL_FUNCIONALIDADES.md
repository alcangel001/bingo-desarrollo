# 🎮 SISTEMA DE CONTROL DE FUNCIONALIDADES

## Control Total sobre qué pueden hacer los usuarios

Este sistema te permite **activar o desactivar** funcionalidades específicas del juego sin tocar código. Cuando una funcionalidad está desactivada, los usuarios **NO la verán** en el sitio.

---

## 🎯 FUNCIONALIDADES CONTROLABLES

### 1. 💰 **Compra de Créditos**
- **Activo**: Los usuarios pueden solicitar compra de créditos
- **Desactivado**: El botón/link de "Comprar Créditos" NO aparece

### 2. 💸 **Retiro de Créditos**
- **Activo**: Los usuarios pueden solicitar retiros
- **Desactivado**: El botón/link de "Retirar" NO aparece

### 3. 👥 **Sistema de Referidos**
- **Activo**: Los usuarios ven su código de referido y pueden compartirlo
- **Desactivado**: NO se muestran códigos, nuevos registros NO reciben bonos

### 4. 🎟️ **Sistema de Tickets**
- **Activo**: Los referidos reciben TICKETS de bingo gratuitos
- **Desactivado**: Los referidos reciben CRÉDITOS ($5)

### 5. 🎁 **Promociones y Bonos**
- **Activo**: Los usuarios pueden ver y reclamar promociones especiales
- **Desactivado**: La página de promociones NO es accesible

---

## 🚀 CÓMO USAR EL SISTEMA

### Opción 1: Script Interactivo (Más Fácil) ⭐

```bash
# Ejecutar el script
python gestionar_sistemas.py
```

El script te mostrará un menú interactivo:

```
============================================================
ESTADO ACTUAL DE LOS SISTEMAS
============================================================

[COMPRA DE CREDITOS]       [ACTIVO]
[RETIRO DE CREDITOS]       [ACTIVO]
[SISTEMA DE REFERIDOS]     [ACTIVO]
[SISTEMA DE TICKETS]       [DESACTIVADO]

============================================================

QUE SISTEMA DESEAS ACTIVAR/DESACTIVAR?

1. Compra de Creditos
2. Retiro de Creditos
3. Sistema de Referidos
4. Sistema de Tickets
5. Promociones y Bonos
6. Ver Estado Actual
0. Salir

Selecciona una opcion (0-6):
```

Simplemente selecciona el número del sistema que quieres cambiar.

### Opción 2: Desde el Admin de Django

1. Ir a: `https://tu-dominio.com/admin/`
2. Login como admin
3. Ir a **"Configuración del Sistema"** (PercentageSettings)
4. Cambiar los toggles:
   - ✅ Activar Compra de Créditos
   - ✅ Activar Retiro de Créditos
   - ✅ Activar Sistema de Referidos
5. Guardar

Para el sistema de tickets:
1. Ir a **"Configuración de Tickets"** (BingoTicketSettings)
2. Cambiar **"Activar/desactivar todo el sistema de tickets"**
3. Guardar

### Opción 3: Desde el Shell de Django

```python
python manage.py shell

# Desactivar compra de créditos
from bingo_app.models import PercentageSettings
settings = PercentageSettings.objects.first()
settings.credits_purchase_enabled = False
settings.save()
print("Compra de créditos desactivada")

# Desactivar retiro de créditos
settings.credits_withdrawal_enabled = False
settings.save()
print("Retiro desactivado")

# Desactivar referidos
settings.referral_system_enabled = False
settings.save()
print("Referidos desactivados")

# Activar sistema de tickets
from bingo_app.models import BingoTicketSettings
ticket_settings = BingoTicketSettings.get_settings()
ticket_settings.is_system_active = True
ticket_settings.save()
print("Sistema de tickets activado")
```

---

## 📋 CASOS DE USO COMUNES

### Caso 1: Mantenimiento de Pagos
**Situación**: Hay un problema con los pagos y necesitas pausar temporalmente.

**Acción**:
1. Desactivar "Compra de Créditos"
2. Desactivar "Retiro de Créditos"
3. Los usuarios NO verán estas opciones
4. Cuando se resuelva, vuelve a activarlas

### Caso 2: Lanzamiento Gradual
**Situación**: Quieres lanzar con funcionalidad limitada al principio.

**Acción**:
1. Desactivar "Retiro de Créditos" (hasta tener suficiente liquidez)
2. Activar "Compra de Créditos" (para generar ingresos)
3. Activar "Referidos" (para crecer)

### Caso 3: Cambiar de Créditos a Tickets
**Situación**: Quieres usar tickets en lugar de dar créditos por referidos.

**Acción**:
1. Activar "Sistema de Tickets"
2. Los nuevos referidos recibirán tickets
3. Debes configurar bingos diarios gratuitos

### Caso 4: Prevenir Abuso
**Situación**: Detectas abuso del sistema de referidos.

**Acción**:
1. Desactivar "Sistema de Referidos" temporalmente
2. Investigar
3. Reactivar cuando esté resuelto

---

## 🔍 COMPORTAMIENTO DETALLADO

### Cuando "Compra de Créditos" está DESACTIVADO:
- ❌ Botón "Comprar Créditos" NO aparece en el perfil
- ❌ Link directo `/request-credits/` redirige con mensaje de error
- ✅ Los admins AÚN pueden aprobar solicitudes pendientes
- ✅ Los créditos existentes NO se afectan

### Cuando "Retiro de Créditos" está DESACTIVADO:
- ❌ Botón "Retirar" NO aparece en el perfil
- ❌ Link directo `/request-withdrawal/` redirige con mensaje de error
- ✅ Los admins AÚN pueden procesar retiros pendientes
- ✅ El saldo de usuarios NO se afecta

### Cuando "Sistema de Referidos" está DESACTIVADO:
- ❌ Códigos de referido NO se muestran
- ❌ Página `/referral-system/` redirige con mensaje de error
- ❌ Nuevos registros con código NO reciben bono
- ✅ Los referidos anteriores se mantienen en el historial

### Cuando "Sistema de Tickets" está ACTIVADO:
- ✅ Nuevos referidos reciben TICKETS en lugar de créditos
- ⚠️ Requiere configurar bingos diarios para usar los tickets
- ✅ Se puede configurar cuántos tickets dar (por defecto: 1 cada uno)
- ✅ Los tickets expiran después de X días (configurable)

---

## ⚙️ CONFIGURACIÓN AVANZADA

### Modificar cantidad de créditos/tickets por referido

**Para Créditos** (cuando sistema de tickets está desactivado):

```python
# En views.py, línea ~104:
bonus_amount = 5.00  # Cambiar este valor

# O en el código del referido:
new_user.credit_balance += bonus_amount  # Ajustar
referrer.credit_balance += bonus_amount  # Ajustar
```

**Para Tickets** (cuando sistema de tickets está activo):

```python
python manage.py shell

from bingo_app.models import BingoTicketSettings

settings = BingoTicketSettings.get_settings()
settings.referral_ticket_bonus = 2  # Tickets para el referidor
settings.referred_ticket_bonus = 2  # Tickets para el referido
settings.ticket_expiration_days = 14  # Días de expiración
settings.save()

print("Configuración actualizada")
```

---

## 🛡️ SEGURIDAD

### Los usuarios NO pueden:
- ❌ Saltarse la verificación (está en el backend)
- ❌ Ver opciones desactivadas (no se renderizan)
- ❌ Acceder por URL directa (redirige con error)

### Los admins SÍ pueden:
- ✅ Ver todas las solicitudes pendientes
- ✅ Procesar solicitudes antiguas
- ✅ Cambiar configuración en cualquier momento
- ✅ Ver historial completo

---

## 📊 MONITOREO

### Ver estado actual desde terminal:

```bash
python gestionar_sistemas.py
# Selecciona opción 5: "Ver Estado Actual"
```

### Ver desde Django shell:

```python
python manage.py shell

from bingo_app.models import PercentageSettings, BingoTicketSettings

ps = PercentageSettings.objects.first()
ts = BingoTicketSettings.get_settings()

print(f"Compra de créditos: {ps.credits_purchase_enabled}")
print(f"Retiro de créditos: {ps.credits_withdrawal_enabled}")
print(f"Referidos: {ps.referral_system_enabled}")
print(f"Tickets: {ts.is_system_active}")
```

---

## 🔄 APLICAR EN PRODUCCIÓN (Railway)

### Método 1: Railway Shell

```bash
# En Railway Dashboard:
# 1. Ir a tu proyecto
# 2. Click en "Shell" o conectarte via Railway CLI
# 3. Ejecutar:

python manage.py shell

from bingo_app.models import PercentageSettings
settings = PercentageSettings.objects.first()
settings.credits_purchase_enabled = False  # o True
settings.save()
```

### Método 2: Admin de Django en Producción

1. Ir a `https://tu-dominio.railway.app/admin/`
2. Login como admin
3. Cambiar configuraciones
4. Guardar

### Método 3: Subir Script

1. Subir `gestionar_sistemas.py` al repositorio
2. Hacer commit y push
3. Conectar via Railway Shell
4. Ejecutar: `python gestionar_sistemas.py`

---

## ❓ PREGUNTAS FRECUENTES

### ¿Los cambios son inmediatos?
**Sí**. En cuanto cambies la configuración, los usuarios NO verán las opciones desactivadas.

### ¿Se pierden los datos al desactivar?
**No**. Los datos históricos (solicitudes, referidos, etc.) se mantienen intactos.

### ¿Puedo desactivar todo?
**Sí**, pero ten cuidado. Si desactivas todo, los usuarios solo podrán jugar con los créditos que ya tienen.

### ¿Afecta a los juegos en curso?
**No**. Los juegos activos NO se ven afectados. Solo afecta nuevas acciones.

### ¿Los admins se ven afectados?
**No**. Los admins siempre tienen acceso completo desde el admin panel.

---

## 🚨 RECOMENDACIONES

### Para Lanzamiento:
- ✅ Activar TODO al principio
- ⏳ Monitorear los primeros días
- 📊 Recopilar métricas
- 🔧 Ajustar según necesidad

### Para Mantenimiento:
- ⚠️ Avisar a usuarios antes de desactivar algo importante
- 📢 Usar anuncios para notificar cambios
- ⏱️ Desactivar durante horarios de baja actividad
- ✅ Reactivar lo antes posible

### Para Prevención de Fraude:
- 🔍 Monitorear sistema de referidos
- ⚠️ Desactivar temporalmente si detectas abuso
- 📊 Revisar logs de transacciones
- 🛡️ Ajustar configuraciones según patrones

---

## 📞 SOPORTE

Si tienes problemas o dudas:
1. Revisa la documentación completa en `AUDITORIA_LANZAMIENTO_2024.md`
2. Consulta `SOLUCION_PROBLEMAS_LANZAMIENTO.md`
3. Verifica logs en Railway Dashboard

---

**Última actualización**: 19 de Octubre, 2024  
**Versión**: 1.0  
**Sistema**: Django 5.2.7

