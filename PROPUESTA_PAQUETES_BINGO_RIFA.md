# 📦 Propuesta: Sistema de Paquetes Separados (Bingo y Rifa)

## 🎯 Concepto Principal

Dos líneas de paquetes independientes: una para Bingo y otra para Rifa, donde cada versión PRO incluye todo lo del otro más funcionalidades avanzadas.

---

## 📋 Estructura de Paquetes

### 🎲 LÍNEA BINGO

#### **BÁSICO BINGO** - $30/mes + 5% comisión
**Para clientes que SOLO quieren bingos:**

✅ **Incluye:**
- Sistema de Bingos (completo)
- Manual Personalizable
- Crear juegos de bingo
- Llamadas automáticas/manuales
- Premios progresivos
- Múltiples patrones de ganancia

❌ **NO incluye:**
- Sistema de Rifas
- Video Llamadas (Bingos)
- Video Llamadas (Rifas)
- Cuentas por Cobrar

---

#### **PRO BINGO** - $80/mes + 3% comisión
**Para clientes que quieren bingos + todo lo demás:**

✅ **Incluye TODO de Básico Bingo:**
- Sistema de Bingos (completo)
- Manual Personalizable

✅ **PLUS - Todo lo que le falta:**
- ✅ Sistema de Rifas (completo)
- ✅ Video Llamadas en Bingos
- ✅ Video Llamadas en Rifas
- ✅ Cuentas por Cobrar
- ✅ Notificaciones Push
- ✅ Reportes Avanzados
- ✅ Promociones Avanzado
- ✅ Anuncios/Banners

**Resultado:** Tiene TODO (bingos + rifas + todas las funcionalidades)

---

### 🎫 LÍNEA RIFA

#### **BÁSICO RIFA** - $30/mes + 5% comisión
**Para clientes que SOLO quieren rifas:**

✅ **Incluye:**
- Sistema de Rifas (completo)
- Manual Personalizable
- Crear rifas con tickets
- Sorteos con ruleta visual
- Premios configurables
- Estadísticas de rifas

❌ **NO incluye:**
- Sistema de Bingos
- Video Llamadas (Bingos)
- Video Llamadas (Rifas)
- Cuentas por Cobrar

---

#### **PRO RIFA** - $80/mes + 3% comisión
**Para clientes que quieren rifas + todo lo demás:**

✅ **Incluye TODO de Básico Rifa:**
- Sistema de Rifas (completo)
- Manual Personalizable

✅ **PLUS - Todo lo que le falta:**
- ✅ Sistema de Bingos (completo)
- ✅ Video Llamadas en Bingos
- ✅ Video Llamadas en Rifas
- ✅ Cuentas por Cobrar
- ✅ Notificaciones Push
- ✅ Reportes Avanzados
- ✅ Promociones Avanzado
- ✅ Anuncios/Banners

**Resultado:** Tiene TODO (rifas + bingos + todas las funcionalidades)

---

## 📊 Comparación Visual

### BÁSICO BINGO vs BÁSICO RIFA

| Funcionalidad | Básico Bingo | Básico Rifa |
|--------------|-------------|-------------|
| Sistema de Bingos | ✅ | ❌ |
| Sistema de Rifas | ❌ | ✅ |
| Manual Personalizable | ✅ | ✅ |
| Video Llamadas (Bingos) | ❌ | ❌ |
| Video Llamadas (Rifas) | ❌ | ❌ |
| Cuentas por Cobrar | ❌ | ❌ |
| **Precio** | **$30/mes + 5%** | **$30/mes + 5%** |

---

### PRO BINGO vs PRO RIFA

| Funcionalidad | PRO Bingo | PRO Rifa |
|--------------|----------|----------|
| Sistema de Bingos | ✅ | ✅ |
| Sistema de Rifas | ✅ | ✅ |
| Manual Personalizable | ✅ | ✅ |
| Video Llamadas (Bingos) | ✅ | ✅ |
| Video Llamadas (Rifas) | ✅ | ✅ |
| Cuentas por Cobrar | ✅ | ✅ |
| Notificaciones Push | ✅ | ✅ |
| Reportes Avanzados | ✅ | ✅ |
| Promociones Avanzado | ✅ | ✅ |
| Anuncios/Banners | ✅ | ✅ |
| **Precio** | **$80/mes + 3%** | **$80/mes + 3%** |

**Nota:** Ambos PRO tienen EXACTAMENTE lo mismo, solo cambia el nombre según qué quiera el cliente principalmente.

---

## 🎯 Lógica de Ventas

### Escenario 1: Cliente quiere SOLO Bingos
**Vende:** BÁSICO BINGO ($30/mes)
- Tiene bingos
- No tiene rifas (no las necesita)
- Puede actualizar a PRO BINGO si después quiere rifas

### Escenario 2: Cliente quiere SOLO Rifas
**Vende:** BÁSICO RIFA ($30/mes)
- Tiene rifas
- No tiene bingos (no los necesita)
- Puede actualizar a PRO RIFA si después quiere bingos

### Escenario 3: Cliente quiere Bingos + Rifas + Todo
**Vende:** PRO BINGO o PRO RIFA ($80/mes)
- Ambos tienen lo mismo
- El nombre depende de qué es lo principal que quiere
- Si su negocio principal es bingo → PRO BINGO
- Si su negocio principal es rifa → PRO RIFA

---

## 💡 Ventajas de esta Estructura

### ✅ Para el Cliente:
1. **Paga solo por lo que necesita**
   - Si solo quiere bingos, no paga por rifas
   - Si solo quiere rifas, no paga por bingos

2. **Fácil de entender**
   - "Básico Bingo" = solo bingos
   - "Básico Rifa" = solo rifas
   - "PRO" = todo incluido

3. **Flexibilidad**
   - Puede empezar con básico y actualizar a PRO cuando necesite más

### ✅ Para Ti:
1. **Más opciones de venta**
   - Puedes vender a clientes que solo quieren bingos
   - Puedes vender a clientes que solo quieren rifas
   - No pierdes ventas por falta de opciones

2. **Upsell fácil**
   - Cliente con Básico Bingo puede actualizar a PRO BINGO cuando quiera rifas
   - Cliente con Básico Rifa puede actualizar a PRO RIFA cuando quiera bingos

3. **Precios claros**
   - Básico: $30/mes (simple y accesible)
   - PRO: $80/mes (completo y premium)

---

## 🏗️ Implementación Técnica

### Modelo `FranchisePackage`:

```python
class FranchisePackage(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('BASIC_BINGO', 'Básico Bingo'),
        ('PRO_BINGO', 'PRO Bingo'),
        ('BASIC_RAFFLE', 'Básico Rifa'),
        ('PRO_RAFFLE', 'PRO Rifa'),
    ]
    
    franchise = models.OneToOneField('Franchise', on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    
    # Funcionalidades base
    bingos_enabled = models.BooleanField(default=False)
    raffles_enabled = models.BooleanField(default=False)
    custom_manual_enabled = models.BooleanField(default=True)  # Siempre activo
    
    # Funcionalidades avanzadas
    accounts_receivable_enabled = models.BooleanField(default=False)
    video_calls_bingos_enabled = models.BooleanField(default=False)
    video_calls_raffles_enabled = models.BooleanField(default=False)
    notifications_push_enabled = models.BooleanField(default=False)
    advanced_reports_enabled = models.BooleanField(default=False)
    advanced_promotions_enabled = models.BooleanField(default=False)
    banners_enabled = models.BooleanField(default=False)
    
    # Precios
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

### Lógica de Activación Automática:

```python
def activate_package_features(package):
    """
    Activa automáticamente las funcionalidades según el tipo de paquete
    """
    if package.package_type == 'BASIC_BINGO':
        package.bingos_enabled = True
        package.raffles_enabled = False
        package.accounts_receivable_enabled = False
        package.video_calls_bingos_enabled = False
        package.video_calls_raffles_enabled = False
        # ... otras funcionalidades en False
        
    elif package.package_type == 'PRO_BINGO':
        # PRO Bingo tiene TODO
        package.bingos_enabled = True
        package.raffles_enabled = True  # ✅ Incluye rifas
        package.accounts_receivable_enabled = True
        package.video_calls_bingos_enabled = True
        package.video_calls_raffles_enabled = True
        package.notifications_push_enabled = True
        # ... todas las funcionalidades en True
        
    elif package.package_type == 'BASIC_RAFFLE':
        package.bingos_enabled = False
        package.raffles_enabled = True
        package.accounts_receivable_enabled = False
        package.video_calls_bingos_enabled = False
        package.video_calls_raffles_enabled = False
        # ... otras funcionalidades en False
        
    elif package.package_type == 'PRO_RAFFLE':
        # PRO Rifa tiene TODO
        package.bingos_enabled = True  # ✅ Incluye bingos
        package.raffles_enabled = True
        package.accounts_receivable_enabled = True
        package.video_calls_bingos_enabled = True
        package.video_calls_raffles_enabled = True
        package.notifications_push_enabled = True
        # ... todas las funcionalidades en True
```

---

## 📋 Tabla Comparativa Completa

| Funcionalidad | Básico Bingo | PRO Bingo | Básico Rifa | PRO Rifa |
|--------------|-------------|-----------|-------------|----------|
| **Sistema de Bingos** | ✅ | ✅ | ❌ | ✅ |
| **Sistema de Rifas** | ❌ | ✅ | ✅ | ✅ |
| **Manual Personalizable** | ✅ | ✅ | ✅ | ✅ |
| **Video Llamadas (Bingos)** | ❌ | ✅ | ❌ | ✅ |
| **Video Llamadas (Rifas)** | ❌ | ✅ | ❌ | ✅ |
| **Cuentas por Cobrar** | ❌ | ✅ | ❌ | ✅ |
| **Notificaciones Push** | ❌ | ✅ | ❌ | ✅ |
| **Reportes Avanzados** | ❌ | ✅ | ❌ | ✅ |
| **Promociones Avanzado** | ❌ | ✅ | ❌ | ✅ |
| **Anuncios/Banners** | ❌ | ✅ | ❌ | ✅ |
| **Precio** | $30/mes + 5% | $80/mes + 3% | $30/mes + 5% | $80/mes + 3% |

---

## 🎯 Casos de Uso

### Caso 1: Cliente solo quiere Bingos
**Solución:** BÁSICO BINGO
- Paga $30/mes
- Tiene bingos completos
- No paga por rifas que no usará
- Si después quiere rifas, actualiza a PRO BINGO

### Caso 2: Cliente solo quiere Rifas
**Solución:** BÁSICO RIFA
- Paga $30/mes
- Tiene rifas completas
- No paga por bingos que no usará
- Si después quiere bingos, actualiza a PRO RIFA

### Caso 3: Cliente quiere Bingos + Rifas + Todo
**Solución:** PRO BINGO o PRO RIFA
- Paga $80/mes
- Tiene TODO
- El nombre depende de qué es su negocio principal

---

## 💰 Estrategia de Precios

### Precios Sugeridos:

**BÁSICO BINGO:** $30/mes + 5% comisión
- Accesible para empezar
- Solo paga por bingos

**PRO BINGO:** $80/mes + 3% comisión
- Incluye todo
- Comisión más baja (incentivo)

**BÁSICO RIFA:** $30/mes + 5% comisión
- Accesible para empezar
- Solo paga por rifas

**PRO RIFA:** $80/mes + 3% comisión
- Incluye todo
- Comisión más baja (incentivo)

---

## 🔄 Actualización de Paquetes

### De Básico a PRO:

**Básico Bingo → PRO Bingo:**
- Cliente paga diferencia: $80 - $30 = $50 adicional
- Se activan automáticamente: Rifas + Video Llamadas + Cuentas por Cobrar + etc.
- Sin pérdida de datos

**Básico Rifa → PRO Rifa:**
- Cliente paga diferencia: $80 - $30 = $50 adicional
- Se activan automáticamente: Bingos + Video Llamadas + Cuentas por Cobrar + etc.
- Sin pérdida de datos

---

## 🎨 Diferenciación Visual

### En el Panel de Admin:

**Paquetes Bingo:**
- 🎲 Icono de bingo
- Color: Azul
- "Básico Bingo" / "PRO Bingo"

**Paquetes Rifa:**
- 🎫 Icono de rifa
- Color: Verde
- "Básico Rifa" / "PRO Rifa"

---

## 📊 Resumen Ejecutivo

### ✅ Ventajas de esta Estructura:

1. **Flexibilidad Total**
   - Clientes que solo quieren bingos → Básico Bingo
   - Clientes que solo quieren rifas → Básico Rifa
   - Clientes que quieren todo → PRO (cualquiera de los dos)

2. **Precios Justos**
   - Básico: $30/mes (accesible)
   - PRO: $80/mes (completo)
   - Cliente paga solo por lo que necesita

3. **Fácil de Vender**
   - "¿Solo quieres bingos? → Básico Bingo"
   - "¿Solo quieres rifas? → Básico Rifa"
   - "¿Quieres todo? → PRO"

4. **Upsell Natural**
   - Cliente con Básico puede actualizar a PRO cuando necesite más
   - Proceso simple y claro

---

## 🎯 Recomendación Final

**Estructura de 4 Paquetes:**
1. **Básico Bingo** - $30/mes + 5%
2. **PRO Bingo** - $80/mes + 3%
3. **Básico Rifa** - $30/mes + 5%
4. **PRO Rifa** - $80/mes + 3%

**Lógica:**
- Básico = Solo su especialidad (bingo o rifa)
- PRO = Todo incluido (bingo + rifa + funcionalidades avanzadas)
- Ambos PRO son idénticos en funcionalidades, solo cambia el nombre

---

¿Te parece bien esta estructura? ¿Alguna modificación o pregunta?

