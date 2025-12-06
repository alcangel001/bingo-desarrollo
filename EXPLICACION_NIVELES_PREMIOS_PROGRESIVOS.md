# 🎯 EXPLICACIÓN: Opción "Añadir Niveles" en Crear Sala de Bingo

## 📋 **¿QUÉ ES LA OPCIÓN DE "AÑADIR NIVELES"?**

La opción de **"Añadir Niveles"** se refiere a los **Premios Progresivos**. Esta característica te permite aumentar automáticamente el premio del juego cuando se vendan ciertos números de cartones.

---

## 🎮 **¿CÓMO FUNCIONA?**

### **Concepto Básico:**

1. **Premio Base:** Es el premio inicial que defines al crear el juego (ej: 100 créditos)

2. **Niveles Progresivos:** Son aumentos adicionales al premio base que se activan cuando se alcanzan ciertos objetivos de cartones vendidos

3. **Ejemplo Visual:**
   ```
   Premio Base: 100 créditos
   
   Nivel 1: Cuando se vendan 10 cartones → +5 créditos
   Premio total: 105 créditos
   
   Nivel 2: Cuando se vendan 20 cartones → +10 créditos
   Premio total: 115 créditos
   
   Nivel 3: Cuando se vendan 30 cartones → +15 créditos
   Premio total: 130 créditos
   ```

---

## 🔧 **CÓMO CONFIGURAR LOS NIVELES**

### **Paso 1: Definir el Premio Base**

Al crear el juego, primero defines el **Premio Base**:
- Este es el premio mínimo que se pagará al ganador
- Ejemplo: 100 créditos

### **Paso 2: Añadir Niveles Progresivos**

En la sección **"Premios Progresivos"** del formulario:

1. **Nivel 1 (Obligatorio):**
   - **Cartones requeridos:** Número de cartones que deben venderse (ej: 10)
   - **Aumento de premio:** Créditos adicionales que se suman al premio base (ej: +5 créditos)

2. **Añadir Más Niveles:**
   - Haz clic en el botón **"Añadir otro nivel"**
   - Puedes crear tantos niveles como quieras
   - Ejemplo:
     - Nivel 2: 20 cartones → +10 créditos
     - Nivel 3: 30 cartones → +15 créditos
     - Nivel 4: 50 cartones → +25 créditos

---

## 📊 **EJEMPLO PRÁCTICO COMPLETO**

### **Configuración del Juego:**

```
Nombre: Bingo de Navidad
Premio Base: 100 créditos

Niveles Progresivos:
- Nivel 1: 10 cartones vendidos → +5 créditos
- Nivel 2: 20 cartones vendidos → +10 créditos
- Nivel 3: 30 cartones vendidos → +15 créditos
- Nivel 4: 50 cartones vendidos → +25 créditos
```

### **Cómo se Calcula el Premio:**

| Cartones Vendidos | Premio Base | Niveles Activados | Premio Total |
|-------------------|-------------|-------------------|--------------|
| 5 cartones | 100 | Ninguno | **100 créditos** |
| 10 cartones | 100 | Nivel 1 (+5) | **105 créditos** |
| 15 cartones | 100 | Nivel 1 (+5) | **105 créditos** |
| 20 cartones | 100 | Nivel 1, 2 (+15) | **115 créditos** |
| 25 cartones | 100 | Nivel 1, 2 (+15) | **115 créditos** |
| 30 cartones | 100 | Nivel 1, 2, 3 (+30) | **130 créditos** |
| 50 cartones | 100 | Todos los niveles (+55) | **155 créditos** |

---

## ⚙️ **CÓMO FUNCIONA EL CÓDIGO**

### **1. Almacenamiento de Niveles:**

Los niveles se guardan en la base de datos como un campo JSON:

```python
progressive_prizes = [
    {'target': 10, 'prize': 5},   # Nivel 1
    {'target': 20, 'prize': 10},  # Nivel 2
    {'target': 30, 'prize': 15},  # Nivel 3
    {'target': 50, 'prize': 25}   # Nivel 4
]
```

### **2. Cálculo del Premio Total:**

El sistema calcula el premio total sumando el premio base + todos los niveles alcanzados:

```python
def calculate_prize(self):
    total_prize = self.base_prize  # Premio base (ej: 100)
    
    # Sumar todos los niveles alcanzados
    if self.progressive_prizes:
        for prize in sorted(self.progressive_prizes, key=lambda x: x['target']):
            if self.max_cards_sold >= prize['target']:
                total_prize += Decimal(str(prize['prize']))
    
    return total_prize
```

### **3. Actualización en Tiempo Real:**

Cuando se vende un cartón:
1. Se actualiza el contador de cartones vendidos
2. Se verifica si se alcanzó algún nuevo nivel
3. Si se alcanzó, se actualiza el premio automáticamente
4. Se notifica a todos los jugadores en tiempo real (WebSocket)

---

## 💡 **VENTAJAS DE USAR NIVELES PROGRESIVOS**

### **1. Atrae Más Jugadores:**
- Los jugadores ven que el premio puede aumentar
- Motiva a más personas a comprar cartones

### **2. Aumenta las Ventas:**
- Los jugadores pueden compartir el juego para alcanzar los niveles
- Crea un efecto "bola de nieve" de participación

### **3. Premios Justos:**
- El premio crece según la participación
- Más jugadores = Premio más grande

### **4. Control de Costos:**
- Solo pagas los niveles que se alcancen
- Si no se venden suficientes cartones, solo pagas el premio base

---

## ⚠️ **IMPORTANTE: CONSIDERACIONES**

### **1. Orden de los Niveles:**
- Los niveles se ordenan automáticamente por número de cartones
- El primer nivel debe ser el que requiere menos cartones

### **2. Validación:**
- El primer nivel es **obligatorio**
- Los niveles adicionales son opcionales
- Cada nivel debe tener un número de cartones mayor que el anterior

### **3. Costos:**
- **NO se bloquean los créditos de los niveles progresivos**
- Solo se bloquea el premio base al crear el juego
- Los niveles se pagan cuando se alcanzan (de tu saldo disponible)

### **4. Ejemplo de Bloqueo de Créditos:**
```
Premio Base: 100 créditos → SE BLOQUEAN al crear el juego
Nivel 1: +5 créditos → NO se bloquean (se pagan cuando se alcanza)
Nivel 2: +10 créditos → NO se bloquean (se pagan cuando se alcanza)
```

---

## 🎯 **EJEMPLOS DE USO RECOMENDADOS**

### **Ejemplo 1: Juego Pequeño**
```
Premio Base: 50 créditos
- Nivel 1: 5 cartones → +2 créditos
- Nivel 2: 10 cartones → +5 créditos
- Nivel 3: 15 cartones → +10 créditos
```

### **Ejemplo 2: Juego Mediano**
```
Premio Base: 100 créditos
- Nivel 1: 10 cartones → +5 créditos
- Nivel 2: 20 cartones → +10 créditos
- Nivel 3: 30 cartones → +15 créditos
- Nivel 4: 50 cartones → +25 créditos
```

### **Ejemplo 3: Juego Grande**
```
Premio Base: 500 créditos
- Nivel 1: 20 cartones → +10 créditos
- Nivel 2: 50 cartones → +25 créditos
- Nivel 3: 100 cartones → +50 créditos
- Nivel 4: 200 cartones → +100 créditos
- Nivel 5: 500 cartones → +250 créditos
```

---

## 🔍 **CÓMO SE MUESTRA A LOS JUGADORES**

### **En el Lobby:**
- Los jugadores ven el premio actual del juego
- Pueden ver si hay niveles progresivos disponibles

### **En la Sala de Juego:**
- Se muestra el premio actual en tiempo real
- Se muestra un indicador de progreso hacia el siguiente nivel
- Cuando se alcanza un nivel, aparece una notificación

### **Ejemplo Visual:**
```
Premio Actual: 105 créditos
Próximo Nivel: 20 cartones (+10 créditos)
Progreso: 15/20 cartones (75%)
```

---

## 📝 **RESUMEN**

| Aspecto | Descripción |
|---------|-------------|
| **¿Qué es?** | Aumentos automáticos al premio base según cartones vendidos |
| **¿Cuántos niveles?** | Mínimo 1 (obligatorio), máximo ilimitado |
| **¿Se bloquean créditos?** | Solo el premio base se bloquea. Los niveles se pagan cuando se alcanzan |
| **¿Cuándo se activan?** | Automáticamente cuando se alcanza el número de cartones requerido |
| **¿Se puede editar?** | No después de crear el juego (para evitar confusión) |
| **¿Se muestra en tiempo real?** | Sí, todos los jugadores ven el premio actualizado |

---

## 🎮 **PASOS PARA CONFIGURAR**

1. **Crear el juego:**
   - Define el nombre y premio base

2. **Añadir Nivel 1:**
   - Cartones requeridos: Ej: 10
   - Aumento de premio: Ej: +5 créditos

3. **Añadir más niveles (opcional):**
   - Haz clic en "Añadir otro nivel"
   - Define cartones requeridos y aumento
   - Repite cuantas veces quieras

4. **Guardar:**
   - El sistema ordenará los niveles automáticamente
   - Los niveles se activarán según se vendan cartones

---

**Fecha de creación:** 13 de Noviembre de 2025  
**Sistema:** Bingo Online - Premios Progresivos  
**Versión:** 1.0








