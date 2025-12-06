# 📊 INFORME: Sistema de Toggles para Referidos y Promociones

## ✅ ESTADO ACTUAL DEL SISTEMA

### 🎯 LO QUE YA ESTÁ IMPLEMENTADO

El sistema **YA TIENE** los toggles para activar/desactivar:

1. **✅ Sistema de Referidos** 
   - Campo: `referral_system_enabled` en `PercentageSettings`
   - Control en: `/admin/` → "Configuración del Sistema"

2. **✅ Sistema de Promociones**
   - Campo: `promotions_enabled` en `PercentageSettings`
   - Control en: `/admin/` → "Configuración del Sistema"

3. **✅ Sistema de Tickets**
   - Campo: `is_system_active` en `BingoTicketSettings`
   - Control en: `/admin/` → "Configuración de Tickets"

### 📝 ARCHIVOS INVOLUCRADOS

#### 1. Modelos (bingo_app/models.py)
```python
class PercentageSettings(models.Model):
    # ... otros campos ...
    
    referral_system_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Sistema de Referidos"
    )
    
    promotions_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Promociones y Bonos"
    )
```

#### 2. Context Processor (bingo_app/context_processors.py)
```python
def system_settings_processor(request):
    percentage_settings = PercentageSettings.objects.first()
    ticket_settings = BingoTicketSettings.get_settings()
    
    return {
        'system_settings': {
            'referral_system_enabled': percentage_settings.referral_system_enabled,
            'promotions_enabled': percentage_settings.promotions_enabled,
            'ticket_system_enabled': ticket_settings.is_system_active,
        }
    }
```

#### 3. Template (bingo_app/templates/bingo_app/base.html)
```html
{% if system_settings.promotions_enabled %}
<li class="nav-item">
    <a class="nav-link" href="{% url 'launch_promotions' %}">
        <i class="fas fa-gift me-1"></i> Promociones
    </a>
</li>
{% endif %}

{% if system_settings.referral_system_enabled %}
<li class="nav-item">
    <a class="nav-link" href="{% url 'referral_system' %}">
        <i class="fas fa-users me-1"></i> Referidos
    </a>
</li>
{% endif %}
```

#### 4. Vistas (bingo_app/views.py)
```python
@login_required
def launch_promotions(request):
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.promotions_enabled:
        messages.error(request, 'El sistema de promociones está temporalmente deshabilitado.')
        return redirect('profile')
    # ... resto del código

@login_required
def referral_system(request):
    settings_obj = PercentageSettings.objects.first()
    if not settings_obj or not settings_obj.referral_system_enabled:
        messages.error(request, 'El sistema de referidos está temporalmente deshabilitado.')
        return redirect('profile')
    # ... resto del código
```

---

## 🎮 CÓMO USAR LOS TOGGLES

### Método 1: Admin de Django (Recomendado)

1. **Acceder al Admin**:
   ```
   https://tu-dominio.railway.app/admin/
   ```

2. **Configurar Referidos y Promociones**:
   - Busca: **"BINGO_APP"** → **"Configuración del Sistema"**
   - Verás una sección llamada: **"Control de Funcionalidades del Usuario"**
   - Checkboxes disponibles:
     - ☑ Activar Compra de Créditos
     - ☑ Activar Retiro de Créditos
     - ☑ **Activar Sistema de Referidos** ← AQUÍ
     - ☑ **Activar Promociones y Bonos** ← AQUÍ

3. **Configurar Sistema de Tickets**:
   - Busca: **"BINGO_APP"** → **"Configuración de Tickets"**
   - Checkbox: **"Activar/desactivar todo el sistema de tickets"**

4. **Guardar cambios**

### Método 2: Script de Gestión

Usa el script `gestionar_sistemas.py` que ya tienes:

```bash
python gestionar_sistemas.py
```

Te mostrará un menú:
```
=== GESTOR DE SISTEMAS ===
1. Compra de Creditos
2. Retiro de Creditos
3. Sistema de Referidos      ← OPCIÓN 3
4. Sistema de Tickets
5. Sistema de Promociones     ← NUEVA OPCIÓN QUE SE AGREGARÁ
```

---

## 🔧 QUÉ PASA CUANDO DESACTIVAS UN SISTEMA

### Cuando DESACTIVAS Referidos:
- ❌ El enlace "Referidos" desaparece del menú
- ❌ Si alguien intenta acceder por URL directa: `/referidos/`
  - Es redirigido al perfil
  - Ve mensaje: "El sistema de referidos está temporalmente deshabilitado"
- ✅ Los referidos existentes NO se pierden
- ✅ Los bonos ya otorgados NO se afectan

### Cuando DESACTIVAS Promociones:
- ❌ El enlace "Promociones" desaparece del menú
- ❌ Si alguien intenta acceder por URL directa: `/promociones/`
  - Es redirigido al perfil
  - Ve mensaje: "El sistema de promociones está temporalmente deshabilitado"
- ✅ Las promociones ya reclamadas NO se pierden
- ✅ Los bonos ya otorgados NO se afectan

### Cuando DESACTIVAS Tickets:
- ❌ Los enlaces "Mis Tickets" y "Bingos Diarios" desaparecen
- ❌ Los nuevos referidos reciben créditos en vez de tickets
- ✅ Los tickets existentes NO se pierden

---

## 🚨 PROBLEMA ACTUAL

Según tu descripción: **"yo no encuento las opciones"**

### Posibles causas:

1. **No estás viendo el menú correcto en el Admin**
   - Busca: "Configuración del Sistema" (PercentageSettings)
   - NO busques: "Percentage settings" o "Settings"

2. **Los toggles están activos, por eso ves los enlaces**
   - Si VES los enlaces de Referidos y Promociones = Están ACTIVOS
   - Verifica en el admin el estado actual

3. **Context processor no está cargando**
   - Verifica que en `settings.py` esté:
     ```python
     'bingo_app.context_processors.system_settings_processor',
     ```

---

## 🎯 VERIFICACIÓN RÁPIDA

### ¿Cómo saber si los toggles están funcionando?

1. **Ve al admin**: `/admin/`
2. **Busca**: "Configuración del Sistema"
3. **Mira los checkboxes**:
   - Si ✅ = Sistema activo → Enlaces VISIBLES en el lobby
   - Si ☐ = Sistema inactivo → Enlaces OCULTOS en el lobby

### Prueba práctica:

1. **Desactiva** "Activar Sistema de Referidos"
2. **Guarda**
3. **Recarga** el lobby (Ctrl+F5)
4. **Resultado esperado**: El enlace "Referidos" debe desaparecer

---

## 📌 RESUMEN EJECUTIVO

| Sistema | Toggle | Ubicación | Estado por Defecto |
|---------|--------|-----------|-------------------|
| Referidos | `referral_system_enabled` | PercentageSettings | ✅ Activo |
| Promociones | `promotions_enabled` | PercentageSettings | ✅ Activo |
| Tickets | `is_system_active` | BingoTicketSettings | ❌ Inactivo |

**TODO ESTÁ IMPLEMENTADO Y FUNCIONANDO** 🎉

Si no encuentras las opciones, es porque:
- Ya están activas (por eso ves los enlaces)
- O necesitas buscar "Configuración del Sistema" en el admin

---

## 🆘 SOLUCIÓN SI NO ENCUENTRAS LAS OPCIONES

### Opción A: Usar el script que te voy a crear

```bash
python gestionar_promociones_referidos.py
```

### Opción B: Admin de Django

1. Ve a: `https://tu-dominio/admin/bingo_app/percentagesettings/`
2. Click en el único registro que existe
3. Baja hasta la sección "Control de Funcionalidades del Usuario"
4. Marca/desmarca los checkboxes que quieras
5. Guarda

---

**¿Necesitas que cree un script más fácil de usar?** 
Puedo crear un archivo `toggle_referidos.py` y `toggle_promociones.py` que con un solo comando activen/desactiven cada sistema.

