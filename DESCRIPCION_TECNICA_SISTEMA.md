# 📋 DESCRIPCIÓN TÉCNICA DEL SISTEMA - BINGO ONLINE

## 1. MODELOS DE DATOS (Estructura)

### **Modelo Game (Bingo)**

El modelo `Game` representa un juego de bingo en el sistema. Tiene los siguientes campos principales:

#### **Campos Básicos:**
- `name` (CharField, max_length=100): Nombre del juego
- `organizer` (ForeignKey a User): **Relación con el organizador** - Cada juego pertenece a un organizador
- `password` (CharField, opcional): Contraseña para acceder al juego (si es privado)
- `is_active` (BooleanField): Si el juego está activo
- `created_at` (DateTimeField): Fecha de creación

#### **Configuración del Juego:**
- `entry_price` (PositiveIntegerField): Precio de entrada al juego (en créditos)
- `card_price` (DecimalField): Precio por cartón de bingo
- `winning_pattern` (CharField): Patrón ganador (HORIZONTAL, VERTICAL, DIAGONAL, FULL, CORNERS, CUSTOM)
- `custom_pattern` (JSONField): Patrón personalizado si es CUSTOM
- `max_cards_per_player` (PositiveIntegerField): Máximo de cartones por jugador
- `allows_printable_cards` (BooleanField): Si permite cartones imprimibles

#### **Estado del Juego:**
- `is_started` (BooleanField): Si el juego ha comenzado
- `is_finished` (BooleanField): Si el juego ha terminado
- `winner` (ForeignKey a User, opcional): Usuario ganador
- `current_number` (IntegerField): Último número llamado
- `called_numbers` (JSONField): Lista de números llamados

#### **Premios y Finanzas:**
- `base_prize` (DecimalField): Premio base del juego
- `progressive_prizes` (JSONField): Premios progresivos según cartones vendidos
- `prize` (DecimalField): Premio total calculado
- `held_balance` (DecimalField): Saldo bloqueado en escrow
- `total_cards_sold` (PositiveIntegerField): Total de cartones vendidos
- `max_cards_sold` (PositiveIntegerField): Máximo de cartones vendidos

#### **Configuración Automática:**
- `auto_call_interval` (PositiveIntegerField): Intervalo en segundos entre llamadas automáticas
- `is_auto_calling` (BooleanField): Si está en modo de llamada automática

### **Relación Game ↔ Organizador:**

```python
# En el modelo Game (línea 157):
organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_games')
```

**Explicación:**
- Cada `Game` tiene un campo `organizer` que es una **ForeignKey** (clave foránea) al modelo `User`
- Esto significa que **cada juego pertenece a un solo organizador**
- La relación es **uno a muchos**: Un organizador puede tener muchos juegos, pero cada juego tiene un solo organizador
- `related_name='organized_games'` permite acceder a todos los juegos de un organizador con: `user.organized_games.all()`
- `on_delete=models.CASCADE` significa que si se elimina el organizador, se eliminan todos sus juegos

**Ejemplo de uso:**
```python
# Obtener todos los juegos de un organizador
organizer = request.user
mis_juegos = organizer.organized_games.all()

# O desde el modelo Game
juegos = Game.objects.filter(organizer=organizer)
```

### **Tecnología de Base de Datos y Backend:**

- **Backend:** Python 3.x con Django (Framework web)
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción en Railway)
- **ORM:** Django ORM (Object-Relational Mapping)
- **Autenticación:** Django Authentication + django-allauth (para login social)
- **WebSockets:** Django Channels (para actualizaciones en tiempo real)
- **Servidor ASGI:** Daphne (para manejar WebSockets y HTTP)

---

## 2. AUTENTICACIÓN (Login)

### **Datos de Verificación del Login:**

El sistema usa **Django Authentication** que verifica:

1. **Usuario y Contraseña:**
   - `username`: Nombre de usuario
   - `password`: Contraseña (hasheada con PBKDF2)

2. **Login Social (Opcional):**
   - **Facebook Login:** Usa `django-allauth` con OAuth2
   - **Google Login:** Usa `django-allauth` con OAuth2

### **Proceso de Login:**

```python
# Vista de login (bingo_app/views.py, línea 198-216)
def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Obtiene el usuario
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('lobby')
```

**Pasos del proceso:**
1. El usuario envía `username` y `password` en el formulario
2. Django verifica las credenciales contra la base de datos
3. Si son válidas, se crea una **sesión** en el servidor
4. Se guarda el ID de sesión en una cookie en el navegador
5. El usuario queda autenticado

### **¿Qué pasa después del login exitoso?**

**NO se usa JWT (JSON Web Tokens).** En su lugar, Django usa **Sesiones**:

1. **Sesión del Servidor:**
   - Django crea una sesión en el servidor (almacenada en la base de datos o cache)
   - La sesión contiene el ID del usuario autenticado
   - Se genera un `session_id` único

2. **Cookie en el Navegador:**
   - Se envía una cookie `sessionid` al navegador
   - Esta cookie se envía automáticamente en cada petición
   - Django verifica la sesión en cada request

3. **Objeto `request.user`:**
   - En cada vista, `request.user` contiene el usuario autenticado
   - Si no está autenticado, `request.user` es `AnonymousUser`

**Código de configuración:**
```python
# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Login tradicional
    'allauth.account.auth_backends.AuthenticationBackend',  # Login social
]

LOGIN_URL = 'login'  # URL a la que redirige si no está autenticado
LOGIN_REDIRECT_URL = '/'  # URL a la que redirige después del login
```

**Seguridad:**
- Las contraseñas se almacenan hasheadas (nunca en texto plano)
- Las sesiones tienen expiración automática
- Protección CSRF en todos los formularios
- Cookies seguras en producción (`SESSION_COOKIE_SECURE = True`)

---

## 3. LÓGICA DE NEGOCIO (Listar Juegos del Organizador)

### **Cómo se Filtran los Juegos del Organizador:**

Cuando un organizador entra a su panel, el sistema filtra los juegos usando el campo `organizer`:

```python
# Código real del sistema (bingo_app/views.py, línea 3086)
def _get_organizer_dashboard_context_mejorado(request):
    organizer = request.user  # Usuario logueado
    
    # Filtrar juegos del organizador
    total_games = Game.objects.filter(organizer=organizer).count()
    
    # Juegos activos del organizador
    active_games = Game.objects.filter(
        organizer=organizer, 
        is_active=True, 
        is_finished=False
    ).count()
    
    # Juegos completados del organizador
    completed_games = Game.objects.filter(
        organizer=organizer,
        is_finished=True
    ).count()
```

### **Explicación Detallada:**

**1. Obtener el Organizador Logueado:**
```python
organizer = request.user
```
- `request.user` contiene el usuario autenticado (gracias a la sesión)
- Este es el organizador que inició sesión

**2. Filtrar Juegos:**
```python
Game.objects.filter(organizer=organizer)
```

**Traducción a SQL (conceptual):**
```sql
SELECT * FROM bingo_app_game 
WHERE organizer_id = [ID_DEL_ORGANIZADOR_LOGEADO];
```

**3. Filtros Adicionales:**
```python
# Solo juegos activos y no terminados
Game.objects.filter(
    organizer=organizer,      # Del organizador logueado
    is_active=True,           # Que estén activos
    is_finished=False         # Que no hayan terminado
)
```

**Traducción a SQL:**
```sql
SELECT * FROM bingo_app_game 
WHERE organizer_id = [ID_DEL_ORGANIZADOR]
  AND is_active = 1
  AND is_finished = 0;
```

### **Vista Completa del Dashboard:**

```python
# bingo_app/views.py, línea 3377-3381
@login_required  # Decorador que verifica que el usuario esté logueado
def organizer_dashboard(request):
    context = _get_organizer_dashboard_context_mejorado(request)
    return render(request, 'bingo_app/organizer_dashboard.html', context)
```

**Flujo completo:**
1. El organizador accede a `/organizer/dashboard/`
2. El decorador `@login_required` verifica que esté autenticado
3. Si no está autenticado, redirige a `/login/`
4. Si está autenticado, ejecuta la vista
5. La función obtiene `request.user` (el organizador logueado)
6. Filtra los juegos: `Game.objects.filter(organizer=request.user)`
7. Pasa los datos al template HTML
8. El template muestra solo los juegos del organizador

### **Seguridad:**

**¿Cómo se asegura que un organizador solo vea sus juegos?**

1. **Decorador `@login_required`:**
   - Verifica que el usuario esté autenticado
   - Si no, redirige al login

2. **Filtro por `organizer`:**
   - Siempre se filtra por `organizer=request.user`
   - Es imposible ver juegos de otros organizadores

3. **Validación en Vistas de Detalle:**
   ```python
   # Ejemplo de validación adicional
   game = get_object_or_404(Game, id=game_id)
   if game.organizer != request.user:
       return HttpResponseForbidden("No tienes permiso para ver este juego")
   ```

---

## 📊 RESUMEN TÉCNICO

| Aspecto | Tecnología/Implementación |
|---------|---------------------------|
| **Backend** | Python + Django |
| **Base de Datos** | SQLite (dev) / PostgreSQL (prod) |
| **ORM** | Django ORM |
| **Autenticación** | Django Sessions (no JWT) |
| **Login Social** | django-allauth (Facebook/Google) |
| **Relación Game-Organizador** | ForeignKey (uno a muchos) |
| **Filtrado de Juegos** | `Game.objects.filter(organizer=request.user)` |
| **WebSockets** | Django Channels |
| **Servidor** | Daphne (ASGI) |

---

## 🔍 EJEMPLOS DE CÓDIGO REAL

### **Crear un Juego (con organizador):**
```python
# Cuando un organizador crea un juego
game = Game.objects.create(
    name="Bingo de Navidad",
    organizer=request.user,  # El organizador logueado
    entry_price=10,
    card_price=0.50,
    base_prize=100.00
)
```

### **Listar Juegos del Organizador:**
```python
# En cualquier vista
organizer = request.user
mis_juegos = Game.objects.filter(organizer=organizer)

# Con filtros adicionales
juegos_activos = Game.objects.filter(
    organizer=organizer,
    is_active=True,
    is_finished=False
).order_by('-created_at')
```

### **Verificar Propiedad:**
```python
# Verificar si un juego pertenece al organizador
game = Game.objects.get(id=game_id)
if game.organizer == request.user:
    # El organizador puede editar este juego
    pass
else:
    # No tiene permiso
    return HttpResponseForbidden()
```

---

**Fecha de creación:** 13 de Noviembre de 2025  
**Sistema:** Bingo Online - Versión Mejorada  
**Framework:** Django 4.x








