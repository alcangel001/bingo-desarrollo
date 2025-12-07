# 💰 Propuesta: Sistema de Configuración de Precios de Paquetes

## 🎯 Concepto

Los paquetes vienen **preconfigurados** con la estructura que definimos, pero **tú puedes cambiar los precios** de cada uno desde un panel de administración.

---

## 📋 Estructura Preconfigurada (Valores por Defecto)

### 🎲 LÍNEA BINGO

#### **BÁSICO BINGO**
**Precio por Defecto:** $30/mes + 5% comisión

**Funcionalidades Preconfiguradas:**
- ✅ Sistema de Bingos
- ✅ Manual Personalizable
- ❌ Sistema de Rifas
- ❌ Video Llamadas (Bingos)
- ❌ Video Llamadas (Rifas)
- ❌ Cuentas por Cobrar
- ❌ Otras funcionalidades avanzadas

---

#### **PRO BINGO**
**Precio por Defecto:** $80/mes + 3% comisión

**Funcionalidades Preconfiguradas:**
- ✅ Sistema de Bingos
- ✅ Sistema de Rifas
- ✅ Manual Personalizable
- ✅ Video Llamadas (Bingos)
- ✅ Video Llamadas (Rifas)
- ✅ Cuentas por Cobrar
- ✅ Notificaciones Push
- ✅ Reportes Avanzados
- ✅ Promociones Avanzado
- ✅ Anuncios/Banners
- ✅ Todas las funcionalidades

---

### 🎫 LÍNEA RIFA

#### **BÁSICO RIFA**
**Precio por Defecto:** $30/mes + 5% comisión

**Funcionalidades Preconfiguradas:**
- ✅ Sistema de Rifas
- ✅ Manual Personalizable
- ❌ Sistema de Bingos
- ❌ Video Llamadas (Bingos)
- ❌ Video Llamadas (Rifas)
- ❌ Cuentas por Cobrar
- ❌ Otras funcionalidades avanzadas

---

#### **PRO RIFA**
**Precio por Defecto:** $80/mes + 3% comisión

**Funcionalidades Preconfiguradas:**
- ✅ Sistema de Rifas
- ✅ Sistema de Bingos
- ✅ Manual Personalizable
- ✅ Video Llamadas (Bingos)
- ✅ Video Llamadas (Rifas)
- ✅ Cuentas por Cobrar
- ✅ Notificaciones Push
- ✅ Reportes Avanzados
- ✅ Promociones Avanzado
- ✅ Anuncios/Banners
- ✅ Todas las funcionalidades

---

## 🏗️ Implementación Técnica

### 1. **Modelo: `PackageTemplate`** (Plantillas Preconfiguradas)

```python
class PackageTemplate(models.Model):
    """
    Plantillas preconfiguradas de paquetes
    No se pueden eliminar, solo editar precios
    """
    PACKAGE_TYPES = [
        ('BASIC_BINGO', 'Básico Bingo'),
        ('PRO_BINGO', 'PRO Bingo'),
        ('BASIC_RAFFLE', 'Básico Rifa'),
        ('PRO_RAFFLE', 'PRO Rifa'),
    ]
    
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, unique=True)
    name = models.CharField(max_length=100)  # "Básico Bingo", "PRO Bingo", etc.
    description = models.TextField(help_text="Descripción del paquete")
    
    # Precios (EDITABLES por ti)
    default_monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio mensual por defecto (puedes cambiarlo)"
    )
    current_monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio mensual actual (el que se usa)"
    )
    default_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Comisión por defecto (puedes cambiarla)"
    )
    current_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Comisión actual (la que se usa)"
    )
    
    # Funcionalidades (PRECONFIGURADAS, no editables desde aquí)
    bingos_enabled = models.BooleanField(default=False)
    raffles_enabled = models.BooleanField(default=False)
    accounts_receivable_enabled = models.BooleanField(default=False)
    video_calls_bingos_enabled = models.BooleanField(default=False)
    video_calls_raffles_enabled = models.BooleanField(default=False)
    custom_manual_enabled = models.BooleanField(default=True)
    notifications_push_enabled = models.BooleanField(default=False)
    advanced_reports_enabled = models.BooleanField(default=False)
    advanced_promotions_enabled = models.BooleanField(default=False)
    banners_enabled = models.BooleanField(default=False)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Paquete'
        verbose_name_plural = 'Plantillas de Paquetes'
        ordering = ['package_type']
    
    def __str__(self):
        return f"{self.name} - ${self.current_monthly_price}/mes + {self.current_commission_rate}%"
    
    def save(self, *args, **kwargs):
        # Si es la primera vez, copiar default a current
        if not self.pk:
            self.current_monthly_price = self.default_monthly_price
            self.current_commission_rate = self.default_commission_rate
        super().save(*args, **kwargs)
```

---

### 2. **Comando de Inicialización: `setup_package_templates`**

```python
# bingo_app/management/commands/setup_package_templates.py

from django.core.management.base import BaseCommand
from bingo_app.models import PackageTemplate

class Command(BaseCommand):
    help = 'Crea las plantillas preconfiguradas de paquetes'

    def handle(self, *args, **options):
        templates = [
            {
                'package_type': 'BASIC_BINGO',
                'name': 'Básico Bingo',
                'description': 'Paquete básico para organizadores que solo quieren bingos',
                'default_monthly_price': 30.00,
                'default_commission_rate': 5.00,
                'bingos_enabled': True,
                'custom_manual_enabled': True,
            },
            {
                'package_type': 'PRO_BINGO',
                'name': 'PRO Bingo',
                'description': 'Paquete completo para organizadores que quieren bingos + todo',
                'default_monthly_price': 80.00,
                'default_commission_rate': 3.00,
                'bingos_enabled': True,
                'raffles_enabled': True,
                'accounts_receivable_enabled': True,
                'video_calls_bingos_enabled': True,
                'video_calls_raffles_enabled': True,
                'custom_manual_enabled': True,
                'notifications_push_enabled': True,
                'advanced_reports_enabled': True,
                'advanced_promotions_enabled': True,
                'banners_enabled': True,
            },
            {
                'package_type': 'BASIC_RAFFLE',
                'name': 'Básico Rifa',
                'description': 'Paquete básico para organizadores que solo quieren rifas',
                'default_monthly_price': 30.00,
                'default_commission_rate': 5.00,
                'raffles_enabled': True,
                'custom_manual_enabled': True,
            },
            {
                'package_type': 'PRO_RAFFLE',
                'name': 'PRO Rifa',
                'description': 'Paquete completo para organizadores que quieren rifas + todo',
                'default_monthly_price': 80.00,
                'default_commission_rate': 3.00,
                'bingos_enabled': True,
                'raffles_enabled': True,
                'accounts_receivable_enabled': True,
                'video_calls_bingos_enabled': True,
                'video_calls_raffles_enabled': True,
                'custom_manual_enabled': True,
                'notifications_push_enabled': True,
                'advanced_reports_enabled': True,
                'advanced_promotions_enabled': True,
                'banners_enabled': True,
            },
        ]
        
        for template_data in templates:
            template, created = PackageTemplate.objects.get_or_create(
                package_type=template_data['package_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creada plantilla: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Plantilla ya existe: {template.name}')
                )
```

---

### 3. **Panel de Administración para Editar Precios**

**URL:** `/admin/package-templates/`

**Interfaz:**

```
╔══════════════════════════════════════════════════════════════╗
║        CONFIGURACIÓN DE PRECIOS DE PAQUETES                  ║
╚══════════════════════════════════════════════════════════════╝

🎲 BÁSICO BINGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precio Mensual:  [$30.00]  ← Puedes cambiar
Comisión:        [5.00%]   ← Puedes cambiar
Funcionalidades: (Preconfiguradas, no editables)
  ✅ Bingos
  ✅ Manual Personalizable
  ❌ Rifas
  ❌ Video Llamadas
  ❌ Cuentas por Cobrar
[Guardar Cambios]

🎲 PRO BINGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precio Mensual:  [$80.00]  ← Puedes cambiar
Comisión:        [3.00%]   ← Puedes cambiar
Funcionalidades: (Preconfiguradas, no editables)
  ✅ Bingos
  ✅ Rifas
  ✅ Manual Personalizable
  ✅ Video Llamadas (Bingos)
  ✅ Video Llamadas (Rifas)
  ✅ Cuentas por Cobrar
  ✅ Notificaciones Push
  ✅ Reportes Avanzados
  ✅ Promociones Avanzado
  ✅ Anuncios/Banners
[Guardar Cambios]

🎫 BÁSICO RIFA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precio Mensual:  [$30.00]  ← Puedes cambiar
Comisión:        [5.00%]   ← Puedes cambiar
Funcionalidades: (Preconfiguradas, no editables)
  ✅ Rifas
  ✅ Manual Personalizable
  ❌ Bingos
  ❌ Video Llamadas
  ❌ Cuentas por Cobrar
[Guardar Cambios]

🎫 PRO RIFA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precio Mensual:  [$80.00]  ← Puedes cambiar
Comisión:        [3.00%]   ← Puedes cambiar
Funcionalidades: (Preconfiguradas, no editables)
  ✅ Rifas
  ✅ Bingos
  ✅ Manual Personalizable
  ✅ Video Llamadas (Bingos)
  ✅ Video Llamadas (Rifas)
  ✅ Cuentas por Cobrar
  ✅ Notificaciones Push
  ✅ Reportes Avanzados
  ✅ Promociones Avanzado
  ✅ Anuncios/Banners
[Guardar Cambios]

[Restaurar Precios por Defecto]  ← Vuelve a los valores originales
```

---

### 4. **Vista de Edición de Precios**

```python
# bingo_app/views.py

@staff_member_required
def edit_package_prices(request):
    """
    Vista para editar precios de los paquetes preconfigurados
    """
    templates = PackageTemplate.objects.all().order_by('package_type')
    
    if request.method == 'POST':
        for template in templates:
            price_key = f'price_{template.package_type}'
            commission_key = f'commission_{template.package_type}'
            
            if price_key in request.POST:
                try:
                    new_price = Decimal(request.POST[price_key])
                    template.current_monthly_price = new_price
                except (ValueError, InvalidOperation):
                    messages.error(request, f'Precio inválido para {template.name}')
            
            if commission_key in request.POST:
                try:
                    new_commission = Decimal(request.POST[commission_key])
                    template.current_commission_rate = new_commission
                    template.save()
                except (ValueError, InvalidOperation):
                    messages.error(request, f'Comisión inválida para {template.name}')
        
        messages.success(request, 'Precios actualizados correctamente')
        return redirect('edit_package_prices')
    
    return render(request, 'bingo_app/admin/edit_package_prices.html', {
        'templates': templates
    })

@staff_member_required
@require_POST
def reset_package_prices(request):
    """
    Restaura los precios a los valores por defecto
    """
    templates = PackageTemplate.objects.all()
    for template in templates:
        template.current_monthly_price = template.default_monthly_price
        template.current_commission_rate = template.default_commission_rate
        template.save()
    
    messages.success(request, 'Precios restaurados a los valores por defecto')
    return redirect('edit_package_prices')
```

---

### 5. **Template HTML para Editar Precios**

```html
<!-- bingo_app/templates/bingo_app/admin/edit_package_prices.html -->

<h1>💰 Configuración de Precios de Paquetes</h1>

<form method="post">
    {% csrf_token %}
    
    {% for template in templates %}
    <div class="package-card">
        <h2>{{ template.name }}</h2>
        <p>{{ template.description }}</p>
        
        <div class="price-config">
            <label>Precio Mensual:</label>
            <input type="number" 
                   name="price_{{ template.package_type }}" 
                   value="{{ template.current_monthly_price }}" 
                   step="0.01" 
                   min="0">
            <small>Precio por defecto: ${{ template.default_monthly_price }}</small>
        </div>
        
        <div class="commission-config">
            <label>Comisión (%):</label>
            <input type="number" 
                   name="commission_{{ template.package_type }}" 
                   value="{{ template.current_commission_rate }}" 
                   step="0.01" 
                   min="0" 
                   max="100">
            <small>Comisión por defecto: {{ template.default_commission_rate }}%</small>
        </div>
        
        <div class="features-list">
            <h3>Funcionalidades (Preconfiguradas):</h3>
            <ul>
                <li>{% if template.bingos_enabled %}✅{% else %}❌{% endif %} Bingos</li>
                <li>{% if template.raffles_enabled %}✅{% else %}❌{% endif %} Rifas</li>
                <li>{% if template.accounts_receivable_enabled %}✅{% else %}❌{% endif %} Cuentas por Cobrar</li>
                <li>{% if template.video_calls_bingos_enabled %}✅{% else %}❌{% endif %} Video Llamadas (Bingos)</li>
                <li>{% if template.video_calls_raffles_enabled %}✅{% else %}❌{% endif %} Video Llamadas (Rifas)</li>
                <li>{% if template.custom_manual_enabled %}✅{% else %}❌{% endif %} Manual Personalizable</li>
                <!-- ... más funcionalidades ... -->
            </ul>
        </div>
    </div>
    {% endfor %}
    
    <button type="submit">💾 Guardar Cambios</button>
</form>

<form method="post" action="{% url 'reset_package_prices' %}">
    {% csrf_token %}
    <button type="submit" class="btn-reset">🔄 Restaurar Precios por Defecto</button>
</form>
```

---

## 🔄 Flujo de Trabajo

### 1. **Inicialización (Primera Vez)**
```bash
python manage.py setup_package_templates
```

Esto crea los 4 paquetes preconfigurados con:
- Básico Bingo: $30/mes + 5%
- PRO Bingo: $80/mes + 3%
- Básico Rifa: $30/mes + 5%
- PRO Rifa: $80/mes + 3%

---

### 2. **Editar Precios (Cuando Quieras)**

1. Vas a `/admin/package-templates/`
2. Ves los 4 paquetes con sus precios actuales
3. Cambias los precios que quieras
4. Guardas
5. Los nuevos precios se aplican a nuevas franquicias

---

### 3. **Crear Nueva Franquicia**

1. Seleccionas el paquete (Básico Bingo, PRO Bingo, etc.)
2. El sistema toma automáticamente:
   - Las funcionalidades preconfiguradas
   - El precio actual que configuraste
   - La comisión actual que configuraste

---

## 💡 Características del Sistema

### ✅ Ventajas:

1. **Preconfiguración Inteligente**
   - Los paquetes vienen listos con la estructura correcta
   - No tienes que configurar funcionalidades cada vez

2. **Precios Flexibles**
   - Puedes cambiar precios cuando quieras
   - Los cambios se aplican a nuevas franquicias
   - Las franquicias existentes mantienen su precio (o puedes actualizarlas)

3. **Fácil de Usar**
   - Panel simple para editar precios
   - Botón para restaurar valores por defecto
   - Vista clara de qué incluye cada paquete

4. **Historial de Cambios** (Opcional)
   - Puedes agregar un modelo para guardar historial de cambios de precios
   - Ver cuándo y cómo cambiaste los precios

---

## 📊 Ejemplo de Uso

### Escenario: Quieres aumentar precios

**Antes:**
- Básico Bingo: $30/mes
- PRO Bingo: $80/mes

**Acción:**
1. Vas al panel de precios
2. Cambias Básico Bingo a $35/mes
3. Cambias PRO Bingo a $90/mes
4. Guardas

**Después:**
- Nuevas franquicias: Precios nuevos ($35 y $90)
- Franquicias existentes: Mantienen precios antiguos (o puedes actualizarlas)

---

## 🎯 Resumen

### Lo que está Preconfigurado (No Editable):
- ✅ Funcionalidades de cada paquete
- ✅ Estructura de los 4 paquetes
- ✅ Qué incluye cada uno

### Lo que TÚ Puedes Editar:
- 💰 Precio mensual de cada paquete
- 💰 Comisión de cada paquete
- 🔄 Restaurar a valores por defecto

---

## 🚀 Implementación Sugerida

### Paso 1: Crear Modelo `PackageTemplate`
### Paso 2: Crear Comando `setup_package_templates`
### Paso 3: Crear Vista de Edición de Precios
### Paso 4: Crear Template HTML
### Paso 5: Agregar URLs
### Paso 6: Ejecutar comando de inicialización

---

¿Te parece bien esta estructura? ¿Quieres que agregue algo más al sistema de configuración de precios?

