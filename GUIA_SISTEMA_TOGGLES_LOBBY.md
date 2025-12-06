# 📋 Guía del Sistema de Toggles del Lobby

## 🎯 Resumen

Se ha implementado exitosamente el sistema de activación/desactivación de funcionalidades en el lobby. Ahora puedes controlar qué opciones son visibles para los usuarios desde el panel de administración de Django.

---

## 🔧 Funcionalidades Controlables

### 1. **Sistema de Referidos** 🤝
- **Toggle:** `referral_system_enabled`
- **Ubicación en menú:** "Referidos"
- **Descripción:** Permite a los usuarios invitar amigos y obtener bonificaciones

### 2. **Sistema de Promociones** 🎁
- **Toggle:** `promotions_enabled`
- **Ubicación en menú:** "Promociones"
- **Descripción:** Muestra promociones especiales, bonos de bienvenida y ofertas

### 3. **Sistema de Tickets de Bingo Diarios** 🎫
- **Toggle:** `ticket_system_enabled` (en BingoTicketSettings)
- **Ubicaciones en menú:**
  - "Mis Tickets"
  - "Bingos Diarios"
- **Descripción:** Sistema de tickets gratuitos para bingos diarios programados

### 4. **Compra de Créditos** 💰
- **Toggle:** `credits_purchase_enabled`
- **Descripción:** Permite a los usuarios solicitar compras de créditos

### 5. **Retiro de Créditos** 💸
- **Toggle:** `credits_withdrawal_enabled`
- **Descripción:** Permite a los usuarios solicitar retiros de fondos

---

## 🎮 Cómo Activar/Desactivar Funcionalidades

### Paso 1: Acceder al Panel de Administración
1. Ve a tu sitio web y agrega `/admin` al final de la URL
   - Ejemplo: `https://tusitio.com/admin`
2. Inicia sesión con tus credenciales de administrador

### Paso 2: Configurar Sistemas de Usuario

#### Para Referidos, Promociones, Compra/Retiro de Créditos:

1. En el panel de administración, busca la sección **"BINGO_APP"**
2. Haz clic en **"Configuración del Sistema"** (PercentageSettings)
3. Verás una pantalla organizada en secciones:

   **Sección: "Control de Funcionalidades del Usuario"**
   - ✅ **Activar Sistema de Referidos:** Marca/desmarca para mostrar/ocultar el sistema de referidos
   - ✅ **Activar Promociones y Bonos:** Marca/desmarca para mostrar/ocultar promociones
   - ✅ **Activar Compra de Créditos:** Marca/desmarca para permitir/bloquear compra de créditos
   - ✅ **Activar Retiro de Créditos:** Marca/desmarca para permitir/bloquear retiros

4. Haz clic en **"Guardar"** en la parte inferior

#### Para Sistema de Tickets de Bingo Diarios:

1. En el panel de administración, busca **"Configuración de Tickets"** (BingoTicketSettings)
2. Verás un campo llamado **"Activar/desactivar todo el sistema de tickets"** (`is_system_active`)
3. Marca/desmarca este campo para activar/desactivar el sistema completo
4. Haz clic en **"Guardar"**

---

## ✨ Qué Sucede Cuando Desactivas un Sistema

### En el Menú de Navegación:
- ❌ **El enlace desaparece completamente** del menú superior
- Los usuarios no verán la opción en absoluto

### Si un Usuario Intenta Acceder Directamente (por URL):
- 🚫 **Será redirigido** a su perfil
- ⚠️ **Verá un mensaje de error** informándole que el sistema está deshabilitado
- Ejemplos de mensajes:
  - "El sistema de referidos está temporalmente deshabilitado."
  - "El sistema de tickets de bingo está temporalmente deshabilitado."
  - "El sistema de promociones está temporalmente deshabilitado."

---

## 📊 Vista Rápida de Toggles en el Admin

Cuando entres a **"Configuración del Sistema"**, verás esta estructura:

```
┌─────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DEL SISTEMA                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  📊 Comisiones y Tarifas                            │
│  ├─ Comisión de plataforma: 10.00%                 │
│  ├─ ☑ Activar Comisión por Cartón                  │
│  ├─ Tarifa de Creación de Juego: 1.00              │
│  └─ ☑ Activar Tarifa de Creación                   │
│                                                      │
│  💰 Precios de Promoción                            │
│  ├─ Precio Promoción con Imagen: 10.00             │
│  └─ Precio Promoción con Video: 15.00              │
│                                                      │
│  🎮 Control de Funcionalidades del Usuario          │
│  ├─ ☑ Activar Compra de Créditos                   │
│  ├─ ☑ Activar Retiro de Créditos                   │
│  ├─ ☑ Activar Sistema de Referidos                 │
│  └─ ☑ Activar Promociones y Bonos                  │
│                                                      │
│  ℹ️ Información                                      │
│  └─ Última actualización: ...                       │
│                                                      │
│  [Guardar y continuar editando] [Guardar] [Eliminar]│
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Cómo Probar los Toggles

### Test 1: Desactivar Sistema de Referidos
1. Ve al admin → "Configuración del Sistema"
2. **Desmarca** "Activar Sistema de Referidos"
3. Guarda los cambios
4. Abre el sitio en una ventana de incógnito
5. Inicia sesión como usuario normal
6. ✅ **Resultado esperado:** El enlace "Referidos" NO aparece en el menú

### Test 2: Desactivar Sistema de Tickets
1. Ve al admin → "Configuración de Tickets"
2. **Desmarca** "Activar/desactivar todo el sistema de tickets"
3. Guarda los cambios
4. Recarga la página del lobby
5. ✅ **Resultado esperado:** Los enlaces "Mis Tickets" y "Bingos Diarios" NO aparecen

### Test 3: Intentar Acceder por URL Directa
1. Desactiva el sistema de promociones
2. Como usuario normal, intenta acceder a: `https://tusitio.com/promociones/`
3. ✅ **Resultado esperado:** 
   - Serás redirigido a tu perfil
   - Verás mensaje: "El sistema de promociones está temporalmente deshabilitado."

---

## 🔍 Archivos Modificados

Los siguientes archivos fueron actualizados para implementar esta funcionalidad:

1. **`bingo_app/templates/bingo_app/base.html`**
   - Se agregaron condiciones `{% if system_settings.TOGGLE %}` alrededor de los enlaces del menú

2. **`bingo_app/views.py`**
   - Se agregaron validaciones en las vistas:
     - `my_bingo_tickets()` - Verifica `ticket_system_enabled`
     - `daily_bingo_schedule()` - Verifica `ticket_system_enabled`
     - `launch_promotions()` - Verifica `promotions_enabled` (ya existía)
     - `referral_system()` - Verifica `referral_system_enabled` (ya existía)

3. **`bingo_app/admin.py`**
   - Se mejoró `PercentageSettingsAdmin` para mostrar todos los toggles de forma organizada
   - Se agregaron fieldsets para mejor organización visual

4. **`bingo_app/context_processors.py`**
   - Ya contenía el `system_settings_processor` que expone los toggles globalmente

---

## 📝 Notas Importantes

### ⚡ Cambios en Tiempo Real
- Los cambios en los toggles se aplican **inmediatamente**
- No es necesario reiniciar el servidor
- Los usuarios necesitarán **recargar la página** para ver los cambios

### 🔒 Seguridad
- Incluso si un usuario conoce la URL directa, no podrá acceder a sistemas desactivados
- Todas las vistas tienen validación en el backend

### 👥 Usuarios Afectados
- Todos los usuarios ven los mismos toggles
- Los toggles afectan a **todos los usuarios** por igual
- Los administradores también están sujetos a los toggles

### 💾 Base de Datos
- Los toggles se guardan en la base de datos
- Solo hay **una instancia** de configuración por sitio
- No se puede eliminar la configuración (está protegida)

---

## 🎉 Estado Final

✅ **Sistema de Referidos:** Controlable con toggle  
✅ **Sistema de Promociones:** Controlable con toggle  
✅ **Mis Tickets de Bingo:** Controlable con toggle  
✅ **Bingos Diarios:** Controlable con toggle  
✅ **Compra de Créditos:** Controlable con toggle (en profile)  
✅ **Retiro de Créditos:** Controlable con toggle (en profile)  

**Todo está funcionando correctamente y listo para usar! 🚀**

---

## 🆘 Soporte

Si necesitas ayuda adicional o encuentras algún problema:
1. Verifica que los toggles estén guardados correctamente
2. Recarga la página del navegador (Ctrl+F5)
3. Verifica que el usuario tenga una sesión activa
4. Revisa los logs de Django para errores

---

*Última actualización: Octubre 2024*

