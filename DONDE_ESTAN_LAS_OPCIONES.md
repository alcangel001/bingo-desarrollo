# 🎯 ¿DÓNDE ESTÁN LAS OPCIONES? - Guía Visual

## ❗ RESPUESTA RÁPIDA

**"no encuento las opciones"**

Las opciones están en **2 lugares**:

---

## 🚀 OPCIÓN 1: SCRIPT (MÁS FÁCIL)

### Paso 1: Abre la terminal en tu proyecto

```bash
cd C:\Users\DELL VOSTRO 7500\bingo-mejorado
```

### Paso 2: Ejecuta el script

```bash
python gestionar_sistemas.py
```

### Paso 3: Verás este menú

```
============================================================
ESTADO ACTUAL DE LOS SISTEMAS
============================================================

[COMPRA DE CREDITOS]       [ACTIVO]
[RETIRO DE CREDITOS]       [ACTIVO]
[SISTEMA DE REFERIDOS]     [ACTIVO]        ← AQUÍ ESTÁ
[PROMOCIONES Y BONOS]      [ACTIVO]        ← AQUÍ ESTÁ
[SISTEMA DE TICKETS]       [DESACTIVADO]

============================================================

QUE SISTEMA DESEAS ACTIVAR/DESACTIVAR?

1. Compra de Creditos
2. Retiro de Creditos
3. Sistema de Referidos      ← OPCIÓN 3
4. Sistema de Tickets
5. Promociones y Bonos        ← OPCIÓN 5
6. Ver Estado Actual
0. Salir

Selecciona una opcion (0-6): _
```

### Paso 4: Selecciona el número

- Para **REFERIDOS**: Escribe `3` y presiona ENTER
- Para **PROMOCIONES**: Escribe `5` y presiona ENTER

✅ **¡LISTO!** El sistema cambia de estado automáticamente.

---

## 🌐 OPCIÓN 2: ADMIN DE DJANGO

### Paso 1: Abre el admin

```
https://tu-dominio.railway.app/admin/
```

O si estás en local:
```
http://localhost:8000/admin/
```

### Paso 2: Inicia sesión

Usa tus credenciales de administrador.

### Paso 3: Busca "Configuración del Sistema"

En la página principal del admin verás una lista de modelos agrupados:

```
BINGO_APP
├── Anuncios y Promociones
├── Bank accounts
├── Bingo ticket settingses
├── Chat messages
├── Configuración de Tickets
├── Configuración del Sistema       ← AQUÍ ⭐
├── Credit request notifications
├── Credit requests
├── Daily bingo schedules
├── Flash messages
├── Games
├── Messages
├── Players
├── Printable cards
├── Raffles
├── Transactions
├── Users
├── Video call groups
└── Withdrawal requests
```

**Haz click en:** "Configuración del Sistema"

### Paso 4: Edita la configuración

Verás una página como esta:

```
┌─────────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DEL SISTEMA                              │
│                                                          │
│  Change percentage settings                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Comisiones y Tarifas                                   │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Platform commission: [10.00]                      │ │
│  │ ☑ Platform commission enabled                     │ │
│  │ Game creation fee: [1.00]                         │ │
│  │ ☑ Game creation fee enabled                       │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  Precios de Promoción                                   │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Image promotion price: [10.00]                    │ │
│  │ Video promotion price: [15.00]                    │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  Control de Funcionalidades del Usuario ← AQUÍ ⭐       │
│  ┌───────────────────────────────────────────────────┐ │
│  │ ☑ Credits purchase enabled                        │ │
│  │ ☑ Credits withdrawal enabled                      │ │
│  │ ☑ Referral system enabled           ← REFERIDOS  │ │
│  │ ☑ Promotions enabled                ← PROMOCIONES│ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
│  [ Guardar y continuar editando ]  [ Guardar ]          │
└─────────────────────────────────────────────────────────┘
```

### Paso 5: Marca/desmarca los checkboxes

- **Para ACTIVAR**: Marca el checkbox ☑
- **Para DESACTIVAR**: Desmarca el checkbox ☐

### Paso 6: Guarda los cambios

Click en el botón **"Guardar"** en la parte inferior.

---

## 🎯 PRUEBA RÁPIDA

### Para verificar que funciona:

**1. Desactiva el sistema de REFERIDOS:**

```bash
python gestionar_sistemas.py
# Selecciona: 3
```

**2. Abre el sitio en modo incógnito**

**3. Ve al lobby**

**4. Verifica:**
- ✅ El enlace "Referidos" NO debe aparecer en el menú
- ✅ Si intentas ir a `/referidos/` te redirige con error

**5. Vuelve a activarlo:**

```bash
python gestionar_sistemas.py
# Selecciona: 3 de nuevo
```

**6. Recarga la página**

**7. Verifica:**
- ✅ El enlace "Referidos" ahora SÍ aparece en el menú

---

## 📊 COMPARACIÓN CON SISTEMA DE TICKETS

**Ya conoces el sistema de tickets, ¿verdad?**

```bash
python activar_sistema_tickets.py
# o
python desactivar_sistema_tickets.py
```

**Pues REFERIDOS y PROMOCIONES funcionan IGUAL:**

| Sistema | Script | Opción |
|---------|--------|--------|
| Tickets | `activar_sistema_tickets.py` | - |
| Referidos | `gestionar_sistemas.py` | Opción 3 |
| Promociones | `gestionar_sistemas.py` | Opción 5 |

**Mismo comportamiento:**
- ✅ Activas → Aparece en el lobby
- ❌ Desactivas → Desaparece del lobby
- ⚡ Cambio inmediato
- 💾 Datos se conservan

---

## 🔍 ESTADO ACTUAL

### ¿Quieres saber el estado actual SIN cambiar nada?

**Método 1:**
```bash
python gestionar_sistemas.py
# Selecciona: 6 (Ver Estado Actual)
```

**Método 2:**
```bash
python gestionar_promociones_referidos.py status
```

**Método 3:**
- Ve al admin
- Abre "Configuración del Sistema"
- Mira los checkboxes:
  - ☑ = ACTIVO
  - ☐ = DESACTIVADO

---

## ❓ PREGUNTAS COMUNES

### "¿Por qué veo los enlaces de Referidos y Promociones?"

**Respuesta:** Porque están ACTIVOS por defecto.

Si no quieres que los usuarios los vean, desactívalos:
```bash
python gestionar_sistemas.py
# Opción 3 para Referidos
# Opción 5 para Promociones
```

### "¿Dónde dice que están activos/desactivados?"

**En el script:**
```
[SISTEMA DE REFERIDOS]     [ACTIVO]    o    [DESACTIVADO]
[PROMOCIONES Y BONOS]      [ACTIVO]    o    [DESACTIVADO]
```

**En el admin:**
```
☑ Referral system enabled   (checkmark = activo)
☐ Referral system enabled   (sin checkmark = desactivado)
```

### "¿Cómo sé si funcionó?"

**Después de cambiar el toggle:**
1. Abre el sitio en modo incógnito (Ctrl+Shift+N)
2. Inicia sesión
3. Ve al lobby
4. Mira el menú de navegación:
   - Si el sistema está ACTIVO → Ves el enlace
   - Si el sistema está DESACTIVADO → NO ves el enlace

---

## 🎉 RESUMEN VISUAL

```
QUIERO CAMBIAR REFERIDOS/PROMOCIONES
           │
           ├─── Método 1 (FÁCIL) ────────────────┐
           │                                      │
           │    1. python gestionar_sistemas.py  │
           │    2. Selecciona 3 o 5              │
           │    3. ¡LISTO!                       │
           │                                      │
           └─── Método 2 (ADMIN) ────────────────┘
                                                  │
                1. /admin/                        │
                2. "Configuración del Sistema"    │
                3. Marca/desmarca checkbox        │
                4. Guardar                        │
                5. ¡LISTO!                        │
```

---

## 🚀 ACCIÓN INMEDIATA

**AHORA MISMO, haz esto:**

1. Abre la terminal
2. Copia y pega:
   ```bash
   cd "C:\Users\DELL VOSTRO 7500\bingo-mejorado"
   python gestionar_sistemas.py
   ```
3. Selecciona opción `6` para ver el estado actual
4. Ahí verás si Referidos y Promociones están activos o no

**¡Eso es todo!** 🎯

---

**¿Sigues sin encontrar las opciones?**
- Verifica que estés en la carpeta correcta del proyecto
- Asegúrate de que el archivo `gestionar_sistemas.py` existe
- Si estás en Railway, usa el admin web en su lugar

**Las opciones ESTÁN AHÍ, solo necesitas saber dónde mirar** 👀

