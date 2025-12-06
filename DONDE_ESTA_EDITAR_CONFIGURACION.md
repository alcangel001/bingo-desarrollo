# 📍 DÓNDE ESTÁ LA OPCIÓN "EDITAR CONFIGURACIÓN"

## 🎯 **UBICACIÓN EXACTA:**

### **Paso 1: Entra a tu Sala de Juego**
1. Ve al lobby
2. Haz clic en tu juego (el que creaste como organizador)
3. Esto te lleva a la sala del juego (`game_room`)

### **Paso 2: Busca el Botón de Controles del Organizador**
En la sala del juego, en la parte superior derecha, verás un botón con el icono de un **escudo** 🛡️:
- **Icono:** `fas fa-user-shield`
- **Tooltip:** "Controles del organizador"
- **Ubicación:** Parte superior derecha de la pantalla

### **Paso 3: Abre el Modal de Controles**
Haz clic en el botón del escudo. Se abrirá un modal (ventana emergente) que dice:
- **Título:** "Controles del organizador"

### **Paso 4: Busca el Botón "Editar Configuración"**
Dentro del modal, verás varios botones. Si el juego **NO ha iniciado** (`is_started = False`), verás:

```
┌─────────────────────────────────────────┐
│  Controles del organizador              │
├─────────────────────────────────────────┤
│                                         │
│  Ingresos por Ventas (Bloqueado)        │
│  $XX.XX                                 │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Editar Configuración            │   │ ← AQUÍ ESTÁ
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Iniciar Juego                   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## ⚠️ **CONDICIONES PARA QUE APAREZCA:**

El botón "Editar Configuración" **solo aparece** si:

1. ✅ Eres el **organizador** del juego (`request.user == game.organizer`)
2. ✅ El juego **NO ha iniciado** (`not game.is_started`)
3. ✅ El juego **NO ha terminado** (`not game.is_finished`)

Si el juego ya inició, **NO verás** el botón "Editar Configuración".

---

## 🔍 **SI NO LO VES, VERIFICA:**

### **1. ¿Eres el organizador?**
- Solo el creador del juego puede editar la configuración
- Si no eres el organizador, el botón no aparece

### **2. ¿El juego ya inició?**
- Una vez que inicias el juego (botón "Iniciar Juego"), ya no se puede editar
- El botón desaparece cuando `game.is_started = True`

### **3. ¿Estás en la sala correcta?**
- Debes estar en la página del juego (`/game/<game_id>/`)
- No en el lobby, no en otra página

---

## 📸 **REFERENCIA VISUAL:**

```
Sala de Juego (game_room.html)
┌──────────────────────────────────────────────┐
│  [🏠] [🔔] [🛡️] ← Botón del escudo aquí     │
├──────────────────────────────────────────────┤
│                                              │
│  Modal: Controles del organizador           │
│  ┌────────────────────────────────────┐     │
│  │ Ingresos: $XX.XX                   │     │
│  │                                    │     │
│  │ [Editar Configuración] ← AQUÍ     │     │
│  │ [Iniciar Juego]                   │     │
│  └────────────────────────────────────┘     │
└──────────────────────────────────────────────┘
```

---

## 🔧 **SI AÚN NO LO VES:**

### **Verificación en el Código:**
El botón está en la línea **2563** del archivo `game_room.html`:

```html
{% if not game.is_started %}
<a href="{% url 'edit_game_config' game.id %}" class="btn btn-outline-primary btn-lg">
    <i class="fas fa-edit me-2"></i>Editar Configuración
</a>
{% endif %}
```

### **Pruebas:**
1. Crea un juego nuevo (como organizador)
2. **NO lo inicies**
3. Entra a la sala del juego
4. Haz clic en el botón del escudo 🛡️
5. El botón "Editar Configuración" debe aparecer

---

## 💡 **ALTERNATIVA DIRECTA:**

Si necesitas acceder directamente, puedes usar esta URL:
```
/game/<game_id>/edit/
```

Reemplaza `<game_id>` con el ID de tu juego.

Ejemplo:
```
/game/1/edit/
```

---

## 🐛 **SI SIGUE SIN APARECER:**

Verifica:
1. ¿Los cambios se subieron correctamente a GitHub?
2. ¿Railway se actualizó con los últimos cambios?
3. ¿El servidor está corriendo la versión más reciente?
4. ¿El template `game_room.html` tiene los cambios?

---

**Última actualización:** 13 de Noviembre de 2025








