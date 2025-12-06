# 💰 ANÁLISIS: Ajustar Premio Base Después de Ver Ventas

## 📋 **TU PROPUESTA:**

**Escenario:**
- Premio base bloqueado: 30 créditos
- Ventas: 100 cartones a 1 crédito = 100 créditos recaudados
- Quieres: Aumentar premio a 70 créditos
- Los otros 30 créditos para el organizador
- Descontar del premio ya bloqueado

---

## 🔍 **CÓMO FUNCIONA ACTUALMENTE:**

### **Al Crear el Juego:**
1. Organizador bloquea: 30 créditos (premio base)
2. Se guarda en: `organizer.blocked_credits = 30`
3. Se descuenta de: `organizer.credit_balance -= 30`

### **Durante las Ventas:**
1. Cada cartón vendido se acumula en: `game.held_balance`
2. Ejemplo: 100 cartones × 1 crédito = `held_balance = 100`

### **Al Terminar el Juego:**
1. Se paga el premio: 30 créditos (premio base)
2. Se desbloquea: 30 créditos de `blocked_credits`
3. Se distribuye `held_balance` (100 créditos):
   - Organizador: 90 créditos (100 - 10% comisión)
   - Plataforma: 10 créditos (comisión)

---

## 💡 **OPCIONES PARA AJUSTAR EL PREMIO:**

### **OPCIÓN 1: Ajustar Premio Base (Tu Propuesta)**

**Concepto:**
- Aumentar el premio base de 30 a 70 créditos
- Los 40 créditos adicionales se toman del premio bloqueado
- Si no hay suficiente bloqueado, se bloquea más

**Ejemplo:**
```
Premio base original: 30 créditos (bloqueados)
Ventas: 100 cartones = 100 créditos recaudados
Nuevo premio base: 70 créditos

Ajuste:
- Premio bloqueado actual: 30
- Necesitas: 70
- Diferencia: +40 créditos
- Se bloquean 40 créditos adicionales del saldo del organizador
```

**Implementación:**
```python
# Si aumentas de 30 a 70:
diferencia = 70 - 30 = 40 créditos
if organizer.credit_balance >= diferencia:
    organizer.blocked_credits += diferencia
    organizer.credit_balance -= diferencia
    game.base_prize = 70
    game.prize = 70  # Actualizar premio total
```

**Pros:**
- ✅ Flexibilidad total
- ✅ Puedes aumentar el premio según ventas
- ✅ Atractivo para jugadores

**Contras:**
- ⚠️ Requiere más créditos bloqueados
- ⚠️ Si aumentas mucho, necesitas más saldo
- ⚠️ Puede ser confuso para organizadores

---

### **OPCIÓN 2: Premio Basado en Porcentaje de Ventas**

**Concepto:**
- Premio = Porcentaje de lo recaudado
- Mínimo = Premio base (si las ventas lo permiten)
- Máximo = Límite configurado

**Ejemplo:**
```
Premio base: 30 créditos (mínimo garantizado)
Ventas: 100 cartones = 100 créditos
Configuración: 70% de ventas = premio

Cálculo:
- 70% de 100 = 70 créditos (premio)
- Mínimo garantizado: 30 créditos
- Premio final: 70 créditos (mayor que mínimo)
```

**Implementación:**
```python
# Configurar porcentaje al crear juego
game.prize_percentage = 70  # 70% de ventas

# Al calcular premio:
recaudado = game.held_balance
premio_calculado = recaudado * (game.prize_percentage / 100)
premio_final = max(premio_calculado, game.base_prize)  # Mínimo garantizado
```

**Pros:**
- ✅ Automático según ventas
- ✅ No requiere ajustes manuales
- ✅ Justo para todos

**Contras:**
- ⚠️ Premio variable (puede decepcionar jugadores)
- ⚠️ Más complejo de explicar

---

### **OPCIÓN 3: Ajustar Premio desde lo Recaudado (Tu Idea Mejorada)**

**Concepto:**
- Usar parte de lo recaudado para aumentar el premio
- Descontar del premio base bloqueado si reduces
- Añadir al premio base bloqueado si aumentas

**Ejemplo:**
```
Premio base bloqueado: 30 créditos
Ventas: 100 cartones = 100 créditos recaudados

Ajuste:
- Nuevo premio: 70 créditos
- Diferencia: +40 créditos
- Opción A: Bloquear 40 créditos adicionales
- Opción B: Usar 40 créditos de lo recaudado (held_balance)
```

**Implementación:**
```python
# Opción A: Bloquear más créditos
if nuevo_premio > base_prize:
    diferencia = nuevo_premio - base_prize
    if organizer.credit_balance >= diferencia:
        organizer.blocked_credits += diferencia
        organizer.credit_balance -= diferencia
        game.base_prize = nuevo_premio

# Opción B: Usar de lo recaudado (más inteligente)
if nuevo_premio > base_prize:
    diferencia = nuevo_premio - base_prize
    if game.held_balance >= diferencia:
        # Usar de lo recaudado
        game.held_balance -= diferencia
        game.base_prize = nuevo_premio
        # No necesitas bloquear más, ya está en held_balance
```

**Pros:**
- ✅ Usa el dinero ya recaudado
- ✅ No requiere más créditos del organizador
- ✅ Más justo y lógico

**Contras:**
- ⚠️ Reduce los ingresos del organizador
- ⚠️ Puede ser confuso calcular

---

### **OPCIÓN 4: Sistema Híbrido (Recomendada)**

**Concepto:**
- Premio base mínimo: 30 créditos (garantizado)
- Premio ajustable: Hasta un máximo basado en ventas
- Ajuste automático o manual

**Ejemplo:**
```
Premio base: 30 créditos (bloqueados)
Ventas: 100 cartones = 100 créditos

Opciones:
1. Mantener premio base: 30 créditos
2. Aumentar a: 70 créditos (usando 40 de lo recaudado)
3. Máximo permitido: 80% de ventas = 80 créditos

Si eliges 70:
- Premio: 70 créditos
- Se usan: 40 créditos de held_balance
- Organizador recibe: 60 créditos (100 - 40 - comisión)
```

**Implementación:**
```python
# Al ajustar premio:
nuevo_premio = 70
diferencia = nuevo_premio - game.base_prize  # 40 créditos

if diferencia > 0:  # Aumentar
    if game.held_balance >= diferencia:
        # Usar de lo recaudado
        game.held_balance -= diferencia
        game.base_prize = nuevo_premio
        game.prize = nuevo_premio
    else:
        # No hay suficiente recaudado, bloquear más
        falta = diferencia - game.held_balance
        organizer.blocked_credits += falta
        organizer.credit_balance -= falta
        game.base_prize = nuevo_premio
        game.prize = nuevo_premio
elif diferencia < 0:  # Reducir
    # Desbloquear créditos
    organizer.blocked_credits += diferencia  # diferencia es negativo
    organizer.credit_balance -= diferencia  # se suma porque diferencia es negativo
    game.base_prize = nuevo_premio
    game.prize = nuevo_premio
```

**Pros:**
- ✅ Máxima flexibilidad
- ✅ Usa lo recaudado primero
- ✅ Permite aumentar o reducir
- ✅ Protege al organizador

**Contras:**
- ⚠️ Más complejo de implementar
- ⚠️ Requiere validaciones

---

## 📊 **COMPARACIÓN DE OPCIONES:**

| Opción | Complejidad | Usa Recaudado | Requiere Más Bloqueo | Flexibilidad |
|--------|-------------|---------------|----------------------|--------------|
| **1. Ajustar Premio Base** | Media | ❌ | ✅ | Alta |
| **2. Porcentaje Automático** | Baja | ✅ | ❌ | Media |
| **3. Ajustar desde Recaudado** | Media | ✅ | ⚠️ | Alta |
| **4. Sistema Híbrido** | Alta | ✅ | ⚠️ | Muy Alta |

---

## 🎯 **MI RECOMENDACIÓN:**

### **Opción 3 Mejorada: Ajustar Premio desde lo Recaudado**

**Por qué:**
1. ✅ Usa el dinero ya recaudado (más lógico)
2. ✅ No requiere bloquear más créditos del organizador
3. ✅ Justo: Si vendes más, puedes dar más premio
4. ✅ Protege: No puedes aumentar más de lo recaudado

**Implementación sugerida:**
```python
# En la vista de editar configuración
def adjust_base_prize(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if game.is_started:
        return error("No se puede ajustar después de iniciar")
    
    nuevo_premio = Decimal(request.POST['new_base_prize'])
    diferencia = nuevo_premio - game.base_prize
    
    if diferencia > 0:  # Aumentar premio
        # Verificar que hay suficiente recaudado
        if game.held_balance >= diferencia:
            game.held_balance -= diferencia
            game.base_prize = nuevo_premio
            game.prize = nuevo_premio
        else:
            # No hay suficiente, necesitas bloquear más
            falta = diferencia - game.held_balance
            if request.user.credit_balance >= falta:
                request.user.blocked_credits += falta
                request.user.credit_balance -= falta
                game.base_prize = nuevo_premio
                game.prize = nuevo_premio
            else:
                return error("No tienes suficiente saldo")
    
    elif diferencia < 0:  # Reducir premio
        # Desbloquear créditos
        request.user.blocked_credits += diferencia  # negativo
        request.user.credit_balance -= diferencia  # positivo
        game.base_prize = nuevo_premio
        game.prize = nuevo_premio
    
    game.save()
    request.user.save()
```

---

## ⚠️ **CONSIDERACIONES IMPORTANTES:**

### **1. Validaciones Necesarias:**
- ✅ No permitir ajustar después de iniciar
- ✅ No permitir aumentar más de lo recaudado + saldo disponible
- ✅ No permitir reducir si ya hay jugadores (puede decepcionar)
- ✅ Mostrar advertencia si reduces el premio

### **2. Transparencia:**
- Mostrar al organizador:
  - Premio actual: 30 créditos
  - Recaudado: 100 créditos
  - Máximo posible: 100 créditos (o % configurado)
  - Nuevo premio propuesto: 70 créditos
  - Impacto: -40 créditos de tus ingresos

### **3. Notificaciones:**
- Si aumentas el premio: Notificar a todos los jugadores
- Si reduces: Advertir al organizador del impacto

---

## 💡 **EJEMPLO PRÁCTICO COMPLETO:**

### **Escenario:**
```
Premio base: 30 créditos (bloqueados)
Ventas: 100 cartones × 1 crédito = 100 créditos recaudados
```

### **Opción A: Aumentar a 70 créditos**
```
Ajuste:
- Nuevo premio: 70 créditos
- Diferencia: +40 créditos
- Se usan: 40 créditos de held_balance
- held_balance restante: 60 créditos
- Al terminar:
  - Premio pagado: 70 créditos
  - Organizador recibe: 54 créditos (60 - 10% comisión)
  - Total ingresos organizador: 54 créditos
  - Créditos bloqueados desbloqueados: 30 créditos
```

### **Opción B: Mantener en 30 créditos**
```
Sin ajuste:
- Premio: 30 créditos
- held_balance: 100 créditos
- Al terminar:
  - Premio pagado: 30 créditos
  - Organizador recibe: 90 créditos (100 - 10% comisión)
  - Total ingresos organizador: 90 créditos
  - Créditos bloqueados desbloqueados: 30 créditos
```

---

## 🎯 **PROPUESTA FINAL:**

### **Sistema de Ajuste de Premio Base:**

1. **En la página de editar configuración:**
   - Mostrar premio base actual
   - Mostrar ventas actuales (held_balance)
   - Permitir ajustar premio base
   - Mostrar impacto en ingresos

2. **Validaciones:**
   - Máximo: held_balance + saldo disponible
   - Mínimo: 0 (o un mínimo configurado)
   - Solo antes de iniciar

3. **Cálculo:**
   - Si aumentas: Usar de held_balance primero, luego bloquear más si es necesario
   - Si reduces: Desbloquear créditos proporcionalmente

4. **Transparencia:**
   - Mostrar cálculo completo
   - Mostrar impacto en ingresos
   - Confirmar antes de guardar

---

## ❓ **PREGUNTAS PARA DECIDIR:**

1. **¿Quieres poder REDUCIR el premio también?**
   - Si reduces de 30 a 20, desbloqueas 10 créditos
   - Pero puede decepcionar a jugadores que ya compraron

2. **¿Límite máximo?**
   - ¿Puedes aumentar hasta el 100% de lo recaudado?
   - ¿O un porcentaje máximo (ej: 80%)?

3. **¿Cuándo permitir ajustar?**
   - Solo antes de iniciar (recomendado)
   - O también después de iniciar (más riesgoso)

4. **¿Notificar a jugadores?**
   - Si aumentas el premio, ¿notificar automáticamente?
   - Si reduces, ¿advertir antes?

---

**Fecha de análisis:** 13 de Noviembre de 2025  
**Estado:** Propuesta para análisis - Sin implementar








