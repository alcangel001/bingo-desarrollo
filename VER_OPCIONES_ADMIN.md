# 🔍 CÓMO VER LAS OPCIONES DE REFERIDOS Y PROMOCIONES EN EL ADMIN

## ⚠️ PROBLEMA IDENTIFICADO

Estás viendo solo la **PRIMERA PARTE** de la configuración. Las opciones de Referidos y Promociones están **MÁS ABAJO** en la misma página.

---

## 📋 LO QUE VES AHORA:

```
┌─────────────────────────────────────────────┐
│ Configuración de Porcentajes                │
├─────────────────────────────────────────────┤
│ 💰 Comisiones y Tarifas                     │
│   ✓ Activar Tarifa de Creación...          │
│   $ 1.00                                    │
│   ✓ Activar Comisión por Cartón             │
│   10.00%                                    │
│                                             │
│ 📣 Precios de Promoción                     │
│   $ 10.00 (Imagen)                          │
│   $ 15.00 (Video)                           │
│                                             │
│ Última actualización: 15 Oct 2025...       │
└─────────────────────────────────────────────┘
                    ↓
              ¡AQUÍ ESTÁS! 👆
```

---

## ✅ LO QUE NECESITAS HACER:

### 1️⃣ **HAZ SCROLL HACIA ABAJO** 📜

En esa misma página, **baja con la rueda del ratón** o con la barra de desplazamiento.

### 2️⃣ **VERÁS ESTA SECCIÓN:**

```
┌─────────────────────────────────────────────┐
│                                             │
│ 🎮 CONTROL DE FUNCIONALIDADES DEL USUARIO ⭐│
│                                             │
│ ⚠️ IMPORTANTE: Activa o desactiva           │
│ funcionalidades visibles para los usuarios  │
│ en el lobby. Si desactivas un sistema,      │
│ el enlace DESAPARECERÁ del menú.            │
│                                             │
│ ┌─────────────────────────────────────┐    │
│ │ ☑ Activar Compra de Créditos       │    │
│ │ ☑ Activar Retiro de Créditos       │    │
│ │ ☑ Activar Sistema de Referidos ⭐  │    │ ← AQUÍ
│ │ ☑ Activar Promociones y Bonos ⭐    │    │ ← AQUÍ
│ └─────────────────────────────────────┘    │
│                                             │
│ [ Guardar y continuar ]  [ Guardar ]       │
└─────────────────────────────────────────────┘
```

---

## 🎯 PASO A PASO:

### Opción A: Usando el Admin (después de actualizar)

1. **Cierra** la página del admin que tienes abierta
2. **Vuelve a abrir**: `/admin/bingo_app/percentagesettings/1/change/`
3. **Baja con la rueda del ratón**
4. **Verás** una sección con emojis: "🎮 CONTROL DE FUNCIONALIDADES DEL USUARIO ⭐"
5. **Ahí están** los checkboxes de Referidos y Promociones

### Opción B: Usando el Script (Más fácil)

```bash
python gestionar_sistemas.py
```

Verás:
```
[SISTEMA DE REFERIDOS]     [ACTIVO] o [DESACTIVADO]
[PROMOCIONES Y BONOS]      [ACTIVO] o [DESACTIVADO]

Selecciona opción:
3. Sistema de Referidos      ← Para cambiar Referidos
5. Promociones y Bonos        ← Para cambiar Promociones
```

---

## 🖥️ CAPTURAS VISUALES

### ANTES (lo que ves ahora):
```
╔═══════════════════════════════════════════╗
║ Configuración del Sistema                 ║
╠═══════════════════════════════════════════╣
║                                           ║
║ 💰 Comisiones y Tarifas                   ║
║ [Campos de tarifas]                       ║
║                                           ║
║ 📣 Precios de Promoción                   ║
║ [Campos de precios]                       ║
║                                           ║
║ ← TÚ ESTÁS AQUÍ, NECESITAS BAJAR         ║
╚═══════════════════════════════════════════╝
        ⬇️  ⬇️  ⬇️  ⬇️  ⬇️  ⬇️  ⬇️
```

### DESPUÉS (necesitas ver esto):
```
╔═══════════════════════════════════════════╗
║                                           ║
║ 🎮 CONTROL DE FUNCIONALIDADES ⭐          ║
║                                           ║
║ ☑ Activar Compra de Créditos             ║
║ ☑ Activar Retiro de Créditos             ║
║ ☑ Activar Sistema de Referidos    ⭐     ║
║ ☑ Activar Promociones y Bonos     ⭐     ║
║                                           ║
║ ← ¡AQUÍ ESTÁN LAS OPCIONES!              ║
╚═══════════════════════════════════════════╝
```

---

## 🚀 ACCIÓN INMEDIATA

### Si estás en el admin ahora mismo:

1. **En esa misma página que tienes abierta**
2. **Baja con la rueda del ratón** (scroll down)
3. **Mira debajo de "Precios de Promoción"**
4. **Encontrarás** "🎮 CONTROL DE FUNCIONALIDADES DEL USUARIO"

### Si no ves nada nuevo después de bajar:

**Actualiza la página del admin:**
1. Guarda los cambios que acabo de hacer
2. Ejecuta:
   ```bash
   python manage.py collectstatic --noinput
   ```
3. Recarga el admin (Ctrl+F5)
4. Vuelve a abrir "Configuración del Sistema"
5. Ahora la sección estará destacada con emojis ⭐

---

## ⚡ SOLUCIÓN RÁPIDA (SIN USAR ADMIN)

Si quieres evitar el admin completamente:

```bash
# Ver estado actual
python gestionar_sistemas.py
# Selecciona: 6

# Cambiar Referidos
python gestionar_sistemas.py
# Selecciona: 3

# Cambiar Promociones
python gestionar_sistemas.py
# Selecciona: 5
```

---

## 📊 VERIFICACIÓN

### ¿Cómo saber si encontraste la sección correcta?

Deberías ver **EXACTAMENTE esto** después de bajar:

```
🎮 CONTROL DE FUNCIONALIDADES DEL USUARIO ⭐

⚠️ IMPORTANTE: Activa o desactiva funcionalidades visibles...

☑ Activar Compra de Créditos
☑ Activar Retiro de Créditos
☑ Activar Sistema de Referidos        ← ¡AQUÍ!
☑ Activar Promociones y Bonos          ← ¡AQUÍ!
```

Si ves eso, **¡LO ENCONTRASTE!** 🎉

---

## 🆘 SI AÚN NO LO VES

1. **Cierra el navegador completamente**
2. **Ejecuta en la terminal:**
   ```bash
   python manage.py collectstatic --noinput
   ```
3. **Abre el admin de nuevo**
4. **Ve a "Configuración del Sistema"**
5. **Haz scroll hacia abajo**

O simplemente usa el script:
```bash
python gestionar_sistemas.py
```

---

**¡Las opciones ESTÁN AHÍ, solo necesitas hacer scroll hacia abajo!** 📜⬇️

