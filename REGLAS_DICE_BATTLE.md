# 🎲 REGLAS DEL JUEGO "DICE BATTLE" (BATALLA DE DADOS)

## 📋 CONCEPTOS BÁSICOS

### Jugadores
- **Cantidad**: Siempre **3 jugadores** por partida
- **Vidas iniciales**: Cada jugador comienza con **3 vidas**
- **Objetivo**: Ser el último jugador en pie (el que no pierda todas sus vidas)

---

## 🎮 CÓMO FUNCIONA EL JUEGO

### 1. Inicio de la Partida
- Se reúnen 3 jugadores en la cola de matchmaking
- Cada jugador paga el precio de entrada (ej: $0.10)
- Se crea una partida automáticamente
- Se determina un multiplicador aleatorio (ej: 2x, 3x, 5x) que define el premio final

### 2. Desarrollo de las Rondas

Cada ronda sigue estos pasos:

#### Paso 1: Lanzamiento de Dados
- **Todos los jugadores** lanzan **2 dados** simultáneamente
- Cada dado muestra un número del **1 al 6**
- Se calcula el **total** sumando ambos dados (rango: 2 a 12)

#### Paso 2: Comparación de Resultados
- Se comparan los **totales** de los 3 jugadores
- El jugador con el **total MÁS BAJO** es el perdedor de la ronda

#### Paso 3: Pérdida de Vida
- El perdedor **pierde 1 vida**
- Si un jugador llega a **0 vidas**, queda **eliminado** del juego

#### Paso 4: Continuación
- Si quedan **2 o más jugadores activos**, se inicia una nueva ronda
- Si solo queda **1 jugador**, ese jugador es el **ganador** y recibe el premio

---

## 📊 EJEMPLO DE PARTIDA

### Ronda 1
- **Jugador A**: Dado 1 = 3, Dado 2 = 4 → **Total = 7**
- **Jugador B**: Dado 1 = 1, Dado 2 = 2 → **Total = 3** ⚠️ (MÁS BAJO)
- **Jugador C**: Dado 1 = 5, Dado 2 = 6 → **Total = 11**

**Resultado**: Jugador B pierde 1 vida (quedan 2 vidas)

### Ronda 2
- **Jugador A**: Dado 1 = 2, Dado 2 = 3 → **Total = 5** ⚠️ (MÁS BAJO)
- **Jugador B**: Dado 1 = 4, Dado 2 = 4 → **Total = 8**
- **Jugador C**: Dado 1 = 3, Dado 2 = 3 → **Total = 6**

**Resultado**: Jugador A pierde 1 vida (quedan 2 vidas)

### Ronda 3
- **Jugador A**: Dado 1 = 1, Dado 2 = 1 → **Total = 2** ⚠️ (MÁS BAJO)
- **Jugador B**: Dado 1 = 3, Dado 2 = 3 → **Total = 6**
- **Jugador C**: Dado 1 = 4, Dado 2 = 4 → **Total = 8**

**Resultado**: Jugador A pierde 1 vida (queda 1 vida)

### Ronda 4
- **Jugador A**: Dado 1 = 1, Dado 2 = 1 → **Total = 2** ⚠️ (MÁS BAJO)
- **Jugador B**: Dado 1 = 2, Dado 2 = 2 → **Total = 4**
- **Jugador C**: Dado 1 = 3, Dado 2 = 3 → **Total = 6**

**Resultado**: Jugador A pierde 1 vida (queda 0 vidas) → **ELIMINADO** ❌

### Ronda 5 (Solo quedan 2 jugadores)
- **Jugador B**: Dado 1 = 2, Dado 2 = 1 → **Total = 3** ⚠️ (MÁS BAJO)
- **Jugador C**: Dado 1 = 4, Dado 2 = 3 → **Total = 7**

**Resultado**: Jugador B pierde 1 vida (quedan 2 vidas)

### Ronda 6
- **Jugador B**: Dado 1 = 1, Dado 2 = 1 → **Total = 2** ⚠️ (MÁS BAJO)
- **Jugador C**: Dado 1 = 3, Dado 2 = 2 → **Total = 5**

**Resultado**: Jugador B pierde 1 vida (queda 1 vida)

### Ronda 7
- **Jugador B**: Dado 1 = 1, Dado 2 = 1 → **Total = 2** ⚠️ (MÁS BAJO)
- **Jugador C**: Dado 1 = 2, Dado 2 = 2 → **Total = 4**

**Resultado**: Jugador B pierde 1 vida (queda 0 vidas) → **ELIMINADO** ❌

### 🏆 GANADOR
**Jugador C** es el ganador y recibe el premio final (precio de entrada × multiplicador × 3 jugadores)

---

## 🎯 PUNTOS IMPORTANTES

### Sobre los Cuadros de Resultados
- **SIEMPRE deben mostrarse 3 cuadros**, uno para cada jugador
- Cada cuadro muestra el **total** de los dados de ese jugador en la ronda actual
- Si un jugador aún no ha lanzado, su cuadro muestra "-"
- Si un jugador está eliminado, su cuadro puede seguir mostrando su último resultado

### Sobre las Vidas
- Cada jugador comienza con **3 vidas**
- Cuando un jugador pierde una vida, se muestra visualmente (ej: 3 → 2 → 1 → 0)
- Al llegar a 0 vidas, el jugador queda **eliminado permanentemente**

### Sobre el Premio
- El premio se calcula como: **Precio de entrada × Multiplicador × 3 jugadores**
- Ejemplo: $0.10 × 2x × 3 = $0.60
- El multiplicador se determina aleatoriamente al inicio de la partida

### Sobre las Rondas
- No hay límite de rondas
- El juego continúa hasta que solo quede 1 jugador
- Cada ronda es independiente (los resultados anteriores no afectan la siguiente)

---

## 🔧 CORRECCIONES REALIZADAS

Se corrigió el código para asegurar que:
1. **Siempre se muestren los 3 cuadros de resultados** (uno por cada jugador)
2. **Todos los jugadores estén incluidos en los resultados** enviados desde el servidor
3. **El mapeo de jugadores a asientos sea correcto** para mostrar los resultados en el lugar correcto

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Qué pasa si dos jugadores tienen el mismo total?**
R: Si hay empate en el total más bajo, ambos pierden una vida.

**P: ¿Puedo ver los resultados de los otros jugadores mientras juego?**
R: Sí, todos los jugadores ven los resultados de todos en tiempo real.

**P: ¿Cuánto tiempo tengo para lanzar los dados?**
R: Debes lanzar cuando sea tu turno. El juego espera a que todos los jugadores lancen antes de procesar la ronda.

**P: ¿Qué pasa si me desconecto durante el juego?**
R: Si te desconectas, puedes reconectarte y volver a la partida. Si no vuelves, puedes ser eliminado automáticamente.

---

**Última actualización**: 24 de Diciembre, 2025

