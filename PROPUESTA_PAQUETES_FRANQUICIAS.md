# 📦 Propuesta: Sistema de Paquetes/Versiones para Franquicias

## 🎯 Resumen Ejecutivo

Sistema de paquetes que permite a cada franquicia elegir qué funcionalidades quiere activar, con dos versiones principales (Normal y PRO) y la posibilidad de activar funcionalidades individuales.

---

## 📋 Funcionalidades Disponibles

### 1. **Cuentas por Cobrar** 💰
- Organizador puede crear cuentas por cobrar a sus clientes
- Clientes pueden hacer pagos/abonos
- Seguimiento de deudas pendientes
- Historial de pagos

### 2. **Video Llamadas en Bingos** 📹
- Salas de video integradas en cada juego de bingo
- Públicas o privadas con contraseña
- Controles de cámara y micrófono
- Lista de participantes en tiempo real

### 3. **Video Llamadas en Rifas** 📹
- Salas de video integradas en cada rifa
- Mismas funcionalidades que en bingos
- Vinculadas a rifas específicas

### 4. **Sistema de Rifas** 🎫
- Crear rifas con tickets numerados
- Sorteos con ruleta visual
- Premios configurables
- Estadísticas de rifas

### 5. **Sistema de Bingos** 🎲
- Crear juegos de bingo
- Llamadas automáticas o manuales
- Premios progresivos
- Múltiples patrones de ganancia

### 6. **Manual Personalizable** 📖
- Cada organizador puede crear su propio manual/reglas
- Editor de texto enriquecido
- Secciones personalizables
- Visible para usuarios de su franquicia

---

## 📦 Paquetes Propuestos

### **VERSIÓN NORMAL (Básica)**

**Incluye:**
- ✅ Sistema de Bingos
- ✅ Manual Personalizable
- ❌ Cuentas por Cobrar
- ❌ Video Llamadas (Bingos)
- ❌ Video Llamadas (Rifas)
- ❌ Sistema de Rifas

**Precio Sugerido:** $30/mes + 5% comisión

---

### **VERSIÓN PRO (Completa)**

**Incluye:**
- ✅ Sistema de Bingos
- ✅ Sistema de Rifas
- ✅ Cuentas por Cobrar
- ✅ Video Llamadas en Bingos
- ✅ Video Llamadas en Rifas
- ✅ Manual Personalizable

**Precio Sugerido:** $80/mes + 3% comisión

---

## 🎛️ Sistema de Activación Individual (Opcional)

Además de los paquetes, permitir activar funcionalidades individuales:

### **Funcionalidades Individuales:**

1. **Cuentas por Cobrar**: +$15/mes
2. **Video Llamadas (Bingos)**: +$10/mes
3. **Video Llamadas (Rifas)**: +$10/mes
4. **Sistema de Rifas**: +$20/mes
5. **Manual Personalizable**: Incluido en ambas versiones

**Ejemplo:**
- Versión Normal ($30/mes)
- + Rifas (+$20/mes)
- + Video Llamadas Bingos (+$10/mes)
- **Total: $60/mes**

---

## 🔄 Lógica de Activación

### Escenario 1: Cliente quiere SOLO Rifas

**Opción A: Versión Normal + Rifas**
- Versión Normal: ✅ Bingos, ✅ Manual
- Activar Rifas: ✅ Rifas
- **Resultado:** Bingos + Rifas + Manual
- **Precio:** $30 + $20 = $50/mes

**Opción B: Versión PRO**
- Versión PRO: ✅ Todo incluido
- **Resultado:** Bingos + Rifas + Cuentas por Cobrar + Video Llamadas + Manual
- **Precio:** $80/mes

---

### Escenario 2: Cliente quiere Rifas + Video Llamadas

**Opción A: Versión Normal + Funcionalidades**
- Versión Normal: ✅ Bingos, ✅ Manual
- Activar Rifas: ✅ Rifas
- Activar Video Llamadas (Bingos): ✅ Video Bingos
- Activar Video Llamadas (Rifas): ✅ Video Rifas
- **Resultado:** Bingos + Rifas + Video Llamadas + Manual
- **Precio:** $30 + $20 + $10 + $10 = $70/mes

**Opción B: Versión PRO** (Mejor opción)
- Versión PRO: ✅ Todo incluido
- **Resultado:** Todo + Cuentas por Cobrar (bonus)
- **Precio:** $80/mes (más barato que sumar individual)

---

### Escenario 3: Cliente quiere Cuentas por Cobrar + Video Llamadas

**Opción A: Versión Normal + Funcionalidades**
- Versión Normal: ✅ Bingos, ✅ Manual
- Activar Cuentas por Cobrar: ✅ Cuentas por Cobrar
- Activar Video Llamadas (Bingos): ✅ Video Bingos
- Activar Video Llamadas (Rifas): ✅ Video Rifas
- **Resultado:** Bingos + Cuentas por Cobrar + Video Llamadas + Manual
- **Precio:** $30 + $15 + $10 + $10 = $65/mes

**Opción B: Versión PRO** (Mejor opción)
- Versión PRO: ✅ Todo incluido
- **Resultado:** Todo + Rifas (bonus)
- **Precio:** $80/mes

---

## 🏗️ Implementación Técnica

### 1. **Nuevo Modelo: `FranchisePackage`**

```python
class FranchisePackage(models.Model):
    PACKAGE_CHOICES = [
        ('NORMAL', 'Versión Normal'),
        ('PRO', 'Versión PRO'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    franchise = models.OneToOneField('Franchise', on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    
    # Funcionalidades individuales
    bingos_enabled = models.BooleanField(default=True)  # Siempre activo
    raffles_enabled = models.BooleanField(default=False)
    accounts_receivable_enabled = models.BooleanField(default=False)
    video_calls_bingos_enabled = models.BooleanField(default=False)
    video_calls_raffles_enabled = models.BooleanField(default=False)
    custom_manual_enabled = models.BooleanField(default=True)  # Siempre activo
    
    # Precios
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_features_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fechas
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
```

---

### 2. **Nuevo Modelo: `FranchiseManual`**

```python
class FranchiseManual(models.Model):
    franchise = models.OneToOneField('Franchise', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="Manual de Usuario")
    content = models.TextField(help_text="Contenido del manual en HTML")
    sections = models.JSONField(
        default=list,
        help_text="Secciones del manual: [{'title': 'Título', 'content': 'Contenido'}]"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Funcionalidades del Manual:**
- Editor WYSIWYG (What You See Is What You Get)
- Secciones personalizables
- Imágenes y videos
- Enlaces
- Formato de texto (negrita, cursiva, listas, etc.)
- Visible en: `/manual/` o `/reglas/`

---

### 3. **Modificaciones a `Franchise`**

```python
# Agregar al modelo Franchise:
package = models.OneToOneField(
    'FranchisePackage',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='franchise_package'
)
manual = models.OneToOneField(
    'FranchiseManual',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='franchise_manual'
)
```

---

## 🔐 Sistema de Validación

### En cada vista/función, verificar permisos:

```python
def check_franchise_feature(franchise, feature):
    """
    Verifica si una franquicia tiene una funcionalidad activa
    """
    if not franchise.package or not franchise.package.is_active:
        return False
    
    package = franchise.package
    
    feature_map = {
        'bingos': package.bingos_enabled,
        'raffles': package.raffles_enabled,
        'accounts_receivable': package.accounts_receivable_enabled,
        'video_calls_bingos': package.video_calls_bingos_enabled,
        'video_calls_raffles': package.video_calls_raffles_enabled,
        'custom_manual': package.custom_manual_enabled,
    }
    
    return feature_map.get(feature, False)
```

---

## 🎨 Interfaz de Usuario

### Para el Super Admin (Tú):

**Panel de Gestión de Paquetes:**
- Ver todas las franquicias y sus paquetes
- Cambiar paquete de una franquicia
- Activar/desactivar funcionalidades individuales
- Ver precios y facturación
- Editar manual de cada franquicia

**Vista de Paquetes:**
```
Franquicia: "Bingo Central"
Paquete: PRO
Estado: ✅ Activo
Funcionalidades:
  ✅ Bingos
  ✅ Rifas
  ✅ Cuentas por Cobrar
  ✅ Video Llamadas (Bingos)
  ✅ Video Llamadas (Rifas)
  ✅ Manual Personalizable
Precio: $80/mes + 3% comisión
```

---

### Para el Franchise Owner:

**Panel de Funcionalidades:**
- Ver qué funcionalidades tiene activas
- Ver qué funcionalidades puede activar (con precio)
- Solicitar activación de funcionalidades adicionales
- Editar su manual personalizado

**Editor de Manual:**
- Editor visual tipo Word
- Agregar secciones
- Formato de texto
- Imágenes
- Guardar y previsualizar

---

## 💡 Ideas Adicionales Recomendadas

### 1. **Sistema de Notificaciones Push** 📱
- Notificaciones cuando alguien compra créditos
- Notificaciones cuando alguien hace retiro
- Notificaciones de nuevos juegos/rifas
- **Precio:** +$5/mes o incluido en PRO

### 2. **Sistema de Reportes Avanzados** 📊
- Reportes de ventas detallados
- Reportes de usuarios
- Exportar a Excel/PDF
- Gráficos y estadísticas visuales
- **Precio:** +$10/mes o incluido en PRO

### 3. **Sistema de Promociones Avanzado** 🎁
- Crear promociones personalizadas
- Cupones de descuento
- Bonos por referidos personalizables
- Promociones por tiempo limitado
- **Precio:** +$8/mes o incluido en PRO

### 4. **Sistema de Anuncios/Banners** 📢
- Crear banners personalizados
- Anuncios en el lobby
- Carrusel de imágenes
- Videos promocionales
- **Precio:** +$5/mes o incluido en PRO

### 5. **Sistema de Tickets Avanzado** 🎫
- Tickets personalizados con logo
- Tickets con códigos QR
- Sistema de validación de tickets
- **Precio:** +$7/mes o incluido en PRO

### 6. **API REST para Integraciones** 🔌
- API para conectar con otros sistemas
- Webhooks para eventos
- Integración con sistemas de pago externos
- **Precio:** +$15/mes (solo PRO o add-on)

### 7. **Sistema de Multi-idioma** 🌍
- Soporte para múltiples idiomas
- Traducción de interfaz
- Contenido en diferentes idiomas
- **Precio:** +$10/mes o incluido en PRO

### 8. **Sistema de Afiliados/Comisiones** 💰
- Programa de afiliados para la franquicia
- Comisiones por referidos
- Tracking de conversiones
- **Precio:** +$12/mes o incluido en PRO

### 9. **Sistema de Chat Avanzado** 💬
- Chat en tiempo real mejorado
- Emojis y stickers
- Archivos adjuntos
- Moderación de chat
- **Precio:** +$8/mes o incluido en PRO

### 10. **Sistema de Backup Automático** 💾
- Backups diarios automáticos
- Restauración de datos
- Historial de backups
- **Precio:** +$5/mes o incluido en PRO

---

## 📊 Comparación de Paquetes (Actualizada)

### **VERSIÓN NORMAL**
| Funcionalidad | Incluido |
|--------------|----------|
| Sistema de Bingos | ✅ |
| Manual Personalizable | ✅ |
| Cuentas por Cobrar | ❌ (+$15) |
| Video Llamadas (Bingos) | ❌ (+$10) |
| Video Llamadas (Rifas) | ❌ (+$10) |
| Sistema de Rifas | ❌ (+$20) |
| Notificaciones Push | ❌ (+$5) |
| Reportes Avanzados | ❌ (+$10) |
| Promociones Avanzado | ❌ (+$8) |
| Anuncios/Banners | ❌ (+$5) |
| **Precio Base** | **$30/mes + 5%** |

---

### **VERSIÓN PRO**
| Funcionalidad | Incluido |
|--------------|----------|
| Sistema de Bingos | ✅ |
| Sistema de Rifas | ✅ |
| Cuentas por Cobrar | ✅ |
| Video Llamadas (Bingos) | ✅ |
| Video Llamadas (Rifas) | ✅ |
| Manual Personalizable | ✅ |
| Notificaciones Push | ✅ |
| Reportes Avanzados | ✅ |
| Promociones Avanzado | ✅ |
| Anuncios/Banners | ✅ |
| Tickets Avanzado | ✅ |
| Chat Avanzado | ✅ |
| Backup Automático | ✅ |
| **Precio** | **$80/mes + 3%** |

---

## 🎯 Recomendaciones Finales

### **Estructura de Paquetes Sugerida:**

**1. VERSIÓN BÁSICA** - $30/mes + 5%
- Bingos
- Manual Personalizable

**2. VERSIÓN ESTÁNDAR** - $50/mes + 4%
- Todo de Básica
- Rifas
- Video Llamadas (Bingos y Rifas)

**3. VERSIÓN PRO** - $80/mes + 3%
- Todo de Estándar
- Cuentas por Cobrar
- Notificaciones Push
- Reportes Avanzados
- Promociones Avanzado
- Anuncios/Banners
- Tickets Avanzado
- Chat Avanzado
- Backup Automático

**4. VERSIÓN ENTERPRISE** - $150/mes + 2%
- Todo de PRO
- API REST
- Multi-idioma
- Sistema de Afiliados
- Soporte prioritario 24/7
- Dominio personalizado

---

## 🔄 Flujo de Activación

### Cuando un cliente solicita una franquicia:

1. **Super Admin crea la franquicia**
2. **Asigna paquete inicial** (Normal o PRO)
3. **Sistema activa automáticamente** las funcionalidades del paquete
4. **Cliente puede solicitar** funcionalidades adicionales
5. **Super Admin aprueba** y se actualiza el precio

### Cuando un cliente quiere cambiar de paquete:

1. **Cliente solicita** cambio de paquete
2. **Super Admin evalúa** y aprueba
3. **Sistema actualiza** funcionalidades automáticamente
4. **Se ajusta el precio** según nuevo paquete
5. **Cliente mantiene** sus datos y usuarios

---

## 📝 Manual Personalizable - Detalles

### Características del Editor:

**Secciones Predefinidas (Opcionales):**
- Reglas del Juego
- Cómo Comprar Créditos
- Cómo Hacer Retiros
- Sistema de Referidos
- Términos y Condiciones
- Política de Privacidad
- Preguntas Frecuentes

**Editor Visual:**
- Tipo WYSIWYG (como WordPress)
- Formato de texto (negrita, cursiva, subrayado)
- Listas (numeradas y con viñetas)
- Enlaces
- Imágenes
- Videos (YouTube, Vimeo)
- Tablas
- Código de colores

**Vista para Usuarios:**
- Accesible desde menú: "Manual" o "Reglas"
- Diseño responsive (móvil y desktop)
- Búsqueda dentro del manual
- Índice navegable

---

## 🎨 Personalización Visual por Paquete

### Versión Normal:
- Logo personalizado
- Imagen de portada
- Color principal

### Versión PRO:
- Todo de Normal
- Múltiples colores personalizables
- Fuentes personalizadas
- Favicon personalizado
- CSS personalizado (avanzado)

---

## 💰 Modelo de Precios Recomendado

### Opción 1: Precios Fijos (Recomendada)
- **Normal:** $30/mes + 5% comisión
- **PRO:** $80/mes + 3% comisión
- **Funcionalidades individuales:** Precio adicional según lista

### Opción 2: Descuentos por Volumen
- 1-5 franquicias: Precio normal
- 6-10 franquicias: 10% descuento
- 11+ franquicias: 15% descuento

### Opción 3: Pago Anual con Descuento
- Pago mensual: Precio normal
- Pago anual: 15% descuento (pago único)

---

## 🚀 Plan de Implementación Sugerido

### Fase 1: Base (2-3 semanas)
- Modelo `FranchisePackage`
- Sistema de activación/desactivación
- Validaciones en vistas existentes
- Panel básico para Super Admin

### Fase 2: Manual Personalizable (1 semana)
- Modelo `FranchiseManual`
- Editor WYSIWYG
- Vista pública del manual
- Panel de edición para Franchise Owner

### Fase 3: Panel de Gestión (1 semana)
- Panel completo para Super Admin
- Panel de funcionalidades para Franchise Owner
- Sistema de solicitud de funcionalidades

### Fase 4: Testing y Ajustes (1 semana)
- Pruebas de todas las funcionalidades
- Ajustes de UI/UX
- Documentación

---

## ⚠️ Consideraciones Importantes

### Seguridad:
- Validar en cada vista que la franquicia tiene la funcionalidad activa
- No permitir acceso a funcionalidades no pagadas
- Logs de intentos de acceso no autorizados

### UX:
- Mostrar claramente qué funcionalidades están activas
- Indicar qué funcionalidades se pueden activar (con precio)
- Hacer fácil la solicitud de funcionalidades adicionales

### Facturación:
- Sistema de tracking de uso
- Alertas cuando se acerca el límite
- Reportes de facturación por franquicia

---

## 📋 Resumen de Opciones Válidas

### ✅ Recomendaciones Finales:

1. **3 Paquetes:** Básica, Estándar, PRO (más claro que 2)
2. **Funcionalidades Individuales:** Permitir activar por separado
3. **Manual Personalizable:** Incluido en todos los paquetes
4. **Precios:** Fijos con opción de pago anual con descuento
5. **Panel de Gestión:** Completo para Super Admin y Franchise Owner

---

## 🎯 Próximos Pasos

1. **Revisar esta propuesta**
2. **Decidir estructura de paquetes** (2 o 3 paquetes)
3. **Definir precios** exactos
4. **Decidir funcionalidades** adicionales a incluir
5. **Aprobar plan de implementación**

---

¿Qué estructura de paquetes prefieres? ¿Alguna modificación o pregunta?

