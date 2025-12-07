# 🏢 Propuesta: Sistema de Franquicias para Bingo

## 📋 Resumen Ejecutivo

Sistema que permite vender franquicias del bingo donde cada franquicia es completamente independiente, con su propio organizador/administrador que maneja todo su negocio sin acceso al código fuente.

---

## 🎯 Objetivos Principales

1. **Independencia Total**: Cada franquicia maneja su propio saldo y clientes
2. **Auto-gestión**: El franquiciado aprueba sus propios créditos y retiros
3. **Cuentas Bancarias Propias**: Cada franquicia configura sus métodos de pago
4. **Aislamiento**: Sin acceso a código ni a otras franquicias
5. **Suscripción**: Sistema de pago mensual/anual
6. **Personalización**: Nombre e imagen personalizables por franquicia

---

## 🏗️ Arquitectura Propuesta

### 1. **Nuevo Modelo: `Franchise`**

```python
class Franchise(models.Model):
    name = models.CharField(max_length=200)  # Nombre de la franquicia
    slug = models.SlugField(unique=True)  # URL única: franquicia1.bingo.com
    owner = models.OneToOneField(User, on_delete=models.CASCADE)  # Organizador dueño
    logo = models.ImageField(upload_to='franchises/logos/')  # Logo personalizado
    cover_image = models.ImageField(upload_to='franchises/covers/')  # Imagen de portada
    subscription_status = models.CharField(
        choices=[('active', 'Activa'), ('suspended', 'Suspendida'), ('expired', 'Expirada')],
        default='active'
    )
    subscription_start = models.DateTimeField()
    subscription_end = models.DateTimeField()
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Campos adicionales recomendados:**
- `custom_domain` (CharField): Dominio personalizado (ej: mibingo.com)
- `theme_color` (CharField): Color principal de la marca
- `contact_email` (EmailField): Email de contacto de la franquicia
- `contact_phone` (CharField): Teléfono de contacto
- `description` (TextField): Descripción de la franquicia
- `terms_and_conditions` (TextField): Términos propios de la franquicia

---

### 2. **Modificaciones al Modelo `User`**

```python
# Agregar al modelo User existente:
franchise = models.ForeignKey(
    'Franchise', 
    on_delete=models.SET_NULL, 
    null=True, 
    blank=True,
    related_name='users'
)
is_franchise_owner = models.BooleanField(default=False)
is_franchise_admin = models.BooleanField(default=False)  # Admin de su franquicia
```

**Lógica:**
- Si `is_franchise_owner=True`: Es dueño de una franquicia
- Si `is_franchise_admin=True`: Puede aprobar créditos/retiros de SU franquicia
- Si `franchise` está asignado: Usuario pertenece a esa franquicia

---

### 3. **Modificaciones a `CreditRequest` y `WithdrawalRequest`**

```python
# Agregar a ambos modelos:
franchise = models.ForeignKey(
    'Franchise',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='credit_requests'  # o 'withdrawal_requests'
)
processed_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='processed_credits'  # o 'processed_withdrawals'
)
```

**Lógica:**
- Cada solicitud se asocia a la franquicia del usuario
- Solo el dueño/admin de esa franquicia puede aprobarla
- El admin principal puede ver todas pero no aprobar (solo supervisar)

---

### 4. **Modificaciones a `BankAccount`**

```python
# Agregar al modelo BankAccount:
franchise = models.ForeignKey(
    'Franchise',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='bank_accounts'
)
is_global = models.BooleanField(
    default=False,
    help_text="Si es True, es cuenta del admin principal. Si es False, es de una franquicia."
)
```

**Lógica:**
- Si `franchise` está asignado: Solo visible para usuarios de esa franquicia
- Si `is_global=True`: Visible para todos (cuentas del admin principal)
- El franquiciado puede crear/editar solo sus propias cuentas

---

### 5. **Modificaciones a `Game` y `Raffle`**

```python
# Agregar a ambos modelos:
franchise = models.ForeignKey(
    'Franchise',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='games'  # o 'raffles'
)
```

**Lógica:**
- Cada juego/rifa pertenece a una franquicia
- Solo usuarios de esa franquicia pueden ver/participar
- El organizador solo puede crear juegos para su franquicia

---

## 🔐 Sistema de Permisos y Aislamiento

### Niveles de Usuario:

1. **Super Admin (Tú)**
   - Acceso total al código
   - Puede crear/editar franquicias
   - Puede cambiar nombre, logo, imagen de cada franquicia
   - Puede ver todas las franquicias (solo lectura)
   - NO puede aprobar créditos/retiros de franquicias (solo supervisar)

2. **Franchise Owner (Franquiciado)**
   - `is_franchise_owner=True`
   - `is_franchise_admin=True`
   - Solo ve SU franquicia
   - Aprueba créditos/retiros de SUS usuarios
   - Configura SUS cuentas bancarias
   - Crea juegos/rifas para SU franquicia
   - NO ve otras franquicias
   - NO tiene acceso al código

3. **Franchise User (Usuario de Franquicia)**
   - `franchise` asignado
   - Solo ve juegos/rifas de SU franquicia
   - Solo compra créditos usando cuentas de SU franquicia
   - Solo hace retiros que aprueba SU franquicia

---

## 💰 Sistema de Suscripción

### Opciones Recomendadas:

**Opción 1: Suscripción Mensual Fija**
- Pago mensual fijo (ej: $50/mes)
- Se renueva automáticamente
- Si no paga, se suspende la franquicia

**Opción 2: Suscripción + Comisión**
- Pago mensual base (ej: $30/mes)
- + Comisión por transacción (ej: 5% de cada compra de crédito)
- Más flexible para franquicias pequeñas

**Opción 3: Solo Comisión**
- Sin pago mensual
- Solo comisión por transacción (ej: 10%)
- Ideal para franquicias que empiezan

**Recomendación**: **Opción 2** (Suscripción + Comisión)
- Garantiza ingresos mínimos mensuales
- Permite escalar con el éxito de la franquicia
- Más atractivo para franquiciados

---

## 🎨 Sistema de Personalización

### Lo que el Admin Principal (Tú) puede cambiar por franquicia:

1. **Nombre de la Franquicia**
   - Campo editable desde panel de admin
   - Se refleja en toda la interfaz

2. **Logo**
   - Subir imagen (recomendado: 200x200px, PNG con fondo transparente)
   - Aparece en navbar, favicon, etc.

3. **Imagen de Portada**
   - Imagen de fondo del login/lobby
   - Recomendado: 1920x1080px

4. **Color Principal** (Opcional pero recomendado)
   - Color de marca personalizado
   - Se aplica a botones, acentos, etc.

5. **Dominio Personalizado** (Opcional, avanzado)
   - Cada franquicia puede tener su propio dominio
   - Requiere configuración DNS adicional

---

## 📊 Funcionalidades por Rol

### Para el Franchise Owner (Franquiciado):

**Dashboard Propio:**
- Ver estadísticas de SU franquicia
- Ver usuarios de SU franquicia
- Ver juegos/rifas de SU franquicia
- Ver ingresos/egresos de SU franquicia

**Gestión de Créditos:**
- Ver solicitudes de créditos de SUS usuarios
- Aprobar/Rechazar créditos
- Agregar créditos manualmente a SUS usuarios

**Gestión de Retiros:**
- Ver solicitudes de retiro de SUS usuarios
- Aprobar/Rechazar retiros
- Marcar retiros como completados

**Gestión de Cuentas Bancarias:**
- Crear/Editar/Eliminar SUS cuentas bancarias
- Activar/Desactivar cuentas
- Ordenar cuentas

**Gestión de Juegos:**
- Crear juegos (solo para SU franquicia)
- Editar SUS juegos
- Ver estadísticas de SUS juegos

**Gestión de Rifas:**
- Crear rifas (solo para SU franquicia)
- Ver estadísticas de SUS rifas

**NO puede:**
- Ver otras franquicias
- Aprobar créditos/retiros de otras franquicias
- Acceder al código fuente
- Cambiar configuración global del sistema

---

### Para el Super Admin (Tú):

**Gestión de Franquicias:**
- Crear nuevas franquicias
- Editar nombre, logo, imagen de cada franquicia
- Activar/Suspender franquicias
- Ver estadísticas de todas las franquicias
- Ver suscripciones y pagos

**Supervisión:**
- Ver todas las solicitudes de créditos/retiros (solo lectura)
- Ver transacciones de todas las franquicias
- Ver reportes consolidados

**Configuración Global:**
- Configurar comisiones por franquicia
- Configurar tarifas de suscripción
- Configurar límites y restricciones

---

## 🔄 Flujo de Trabajo

### 1. Crear una Nueva Franquicia:

1. Super Admin crea usuario para el franquiciado
2. Super Admin crea registro `Franchise`:
   - Asigna nombre
   - Sube logo e imagen
   - Configura suscripción
   - Asigna al usuario como `owner`
3. Sistema automáticamente:
   - Marca usuario como `is_franchise_owner=True`
   - Marca usuario como `is_franchise_admin=True`
   - Crea slug único para la franquicia

### 2. Usuario se Registra en una Franquicia:

1. Usuario se registra normalmente
2. Sistema detecta de qué franquicia viene (por URL o subdominio)
3. Asigna `franchise` al usuario
4. Usuario solo ve contenido de SU franquicia

### 3. Usuario Compra Créditos:

1. Usuario ve solo cuentas bancarias de SU franquicia
2. Hace transferencia y sube comprobante
3. Solicitud se crea con `franchise` asignado
4. Solo el `franchise_owner` de esa franquicia puede aprobar
5. Super Admin puede ver pero NO aprobar

### 4. Usuario Hace Retiro:

1. Usuario solicita retiro
2. Solicitud se crea con `franchise` asignado
3. Solo el `franchise_owner` de esa franquicia puede aprobar
4. El franquiciado transfiere desde SUS cuentas bancarias

---

## 🌐 Opciones de Implementación de URLs

### Opción 1: Subdominios (Recomendada)
```
franquicia1.bingo.com
franquicia2.bingo.com
mibingo.bingo.com
```

**Ventajas:**
- Aislamiento visual claro
- Fácil de implementar
- SEO mejorado

**Desventajas:**
- Requiere configuración DNS con wildcard
- Más complejo en Railway

### Opción 2: Rutas con Slug
```
bingo.com/franquicia1/
bingo.com/franquicia2/
bingo.com/mibingo/
```

**Ventajas:**
- Más fácil de implementar
- No requiere DNS especial
- Funciona en cualquier hosting

**Desventajas:**
- Menos "profesional"
- URLs más largas

**Recomendación**: **Opción 2** (Rutas con Slug) para empezar, luego migrar a subdominios si es necesario.

---

## 💳 Sistema de Pagos de Suscripción

### Opciones:

**Opción 1: Manual**
- Tú cobras manualmente
- Marcas como pagada en el sistema
- Simple pero requiere trabajo manual

**Opción 2: Integración con Stripe/PayPal**
- Pago automático mensual
- Renovación automática
- Suspensión automática si falla el pago
- Más profesional pero requiere integración

**Recomendación**: Empezar con **Opción 1** (Manual) y luego migrar a **Opción 2** cuando tengas varias franquicias.

---

## 📝 Modelo de Datos Completo

### Nuevos Modelos Necesarios:

```python
class Franchise(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='franchises/logos/')
    cover_image = models.ImageField(upload_to='franchises/covers/')
    theme_color = models.CharField(max_length=7, default='#2C3E50')
    subscription_status = models.CharField(max_length=20, choices=[...])
    subscription_start = models.DateTimeField()
    subscription_end = models.DateTimeField()
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    is_active = models.BooleanField(default=True)
    custom_domain = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FranchiseSubscription(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=100)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🛠️ Cambios Necesarios en el Código

### 1. **Middleware de Franquicia**
- Detectar qué franquicia está activa (por URL o subdominio)
- Filtrar todas las consultas por franquicia
- Asignar franquicia automáticamente a nuevos usuarios

### 2. **Filtros en Todas las Vistas**
- Modificar todas las vistas para filtrar por `franchise`
- Asegurar que cada usuario solo vea su franquicia

### 3. **Nuevas Vistas para Franchise Owner**
- Dashboard de franquicia
- Gestión de créditos de su franquicia
- Gestión de retiros de su franquicia
- Gestión de cuentas bancarias de su franquicia

### 4. **Panel de Admin para Super Admin**
- CRUD de franquicias
- Cambiar nombre, logo, imagen
- Ver estadísticas de todas las franquicias
- Gestionar suscripciones

### 5. **Sistema de Aislamiento**
- Middleware que bloquea acceso cruzado entre franquicias
- Validaciones en todas las operaciones críticas

---

## ⚠️ Consideraciones Importales

### Seguridad:
- **CRÍTICO**: Asegurar que ningún usuario pueda acceder a datos de otra franquicia
- Validar en cada vista que el usuario pertenece a la franquicia correcta
- Usar `select_related` y filtros en todas las consultas

### Escalabilidad:
- Cada franquicia puede tener miles de usuarios
- Considerar índices en `franchise` en todas las tablas
- Optimizar consultas para evitar N+1 queries

### Aislamiento de Datos:
- Cada franquicia debe ser completamente independiente
- No debe haber "fugas" de datos entre franquicias
- Logs separados por franquicia

---

## 📋 Checklist de Implementación

### Fase 1: Modelos y Base de Datos
- [ ] Crear modelo `Franchise`
- [ ] Crear modelo `FranchiseSubscription`
- [ ] Agregar campo `franchise` a `User`
- [ ] Agregar campo `franchise` a `CreditRequest`
- [ ] Agregar campo `franchise` a `WithdrawalRequest`
- [ ] Agregar campo `franchise` a `BankAccount`
- [ ] Agregar campo `franchise` a `Game`
- [ ] Agregar campo `franchise` a `Raffle`
- [ ] Crear migraciones

### Fase 2: Middleware y Filtros
- [ ] Crear middleware para detectar franquicia
- [ ] Modificar todas las vistas para filtrar por franquicia
- [ ] Agregar validaciones de seguridad

### Fase 3: Panel de Franchise Owner
- [ ] Dashboard de franquicia
- [ ] Gestión de créditos
- [ ] Gestión de retiros
- [ ] Gestión de cuentas bancarias
- [ ] Estadísticas de la franquicia

### Fase 4: Panel de Super Admin
- [ ] CRUD de franquicias
- [ ] Cambiar nombre, logo, imagen
- [ ] Ver estadísticas globales
- [ ] Gestionar suscripciones

### Fase 5: Sistema de URLs
- [ ] Implementar rutas con slug (`/franquicia1/`)
- [ ] Middleware para detectar franquicia desde URL
- [ ] Redirecciones automáticas

### Fase 6: Personalización
- [ ] Aplicar logo en toda la interfaz
- [ ] Aplicar imagen de portada
- [ ] Aplicar color de tema
- [ ] Cambiar nombre en toda la interfaz

---

## 💡 Recomendaciones Adicionales

### 1. **Sistema de Notificaciones por Franquicia**
- Cada franquicia tiene sus propias notificaciones
- No se mezclan entre franquicias

### 2. **Sistema de Reportes**
- Cada franquicia puede generar sus propios reportes
- Super Admin puede ver reportes consolidados

### 3. **Sistema de Límites**
- Límite de usuarios por franquicia (según plan)
- Límite de juegos simultáneos
- Límite de transacciones mensuales

### 4. **Sistema de Backup por Franquicia**
- Backups separados por franquicia
- Restauración independiente

### 5. **API para Franquicias** (Opcional, futuro)
- API REST para que franquicias integren con otros sistemas
- Útil para franquicias grandes

---

## 🎯 Opciones de Suscripción Recomendadas

### Plan Básico: $30/mes + 5% comisión
- Hasta 100 usuarios activos
- Hasta 10 juegos simultáneos
- Soporte por email

### Plan Estándar: $50/mes + 3% comisión
- Usuarios ilimitados
- Juegos ilimitados
- Dominio personalizado
- Soporte prioritario

### Plan Premium: $100/mes + 1% comisión
- Todo del Estándar
- API access
- White-label completo
- Soporte 24/7

---

## 📊 Resumen de Opciones Válidas

### ✅ Opciones Recomendadas:

1. **Sistema de Suscripción**: Mensual + Comisión (más flexible)
2. **URLs**: Rutas con slug para empezar (`/franquicia1/`)
3. **Pagos**: Manual al inicio, luego Stripe/PayPal
4. **Personalización**: Nombre, Logo, Imagen de Portada, Color
5. **Aislamiento**: Middleware + Filtros en todas las vistas
6. **Permisos**: 3 niveles (Super Admin, Franchise Owner, Franchise User)

---

## 🚀 Próximos Pasos

1. **Revisar esta propuesta** y decidir qué opciones prefieres
2. **Definir modelo de suscripción** (mensual, comisión, etc.)
3. **Definir estructura de URLs** (subdominios vs rutas)
4. **Crear plan de implementación** por fases
5. **Empezar con Fase 1** (modelos y base de datos)

---

¿Qué opciones prefieres? ¿Alguna modificación o pregunta antes de empezar a implementar?

