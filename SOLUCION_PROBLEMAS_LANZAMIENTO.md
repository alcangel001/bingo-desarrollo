# 🔧 SOLUCIÓN DE PROBLEMAS - LANZAMIENTO

**Guía rápida para resolver problemas comunes durante y después del lanzamiento**

---

## 📑 ÍNDICE RÁPIDO

1. [Problemas de Deployment](#problemas-de-deployment)
2. [Errores de Base de Datos](#errores-de-base-de-datos)
3. [Problemas con WebSockets](#problemas-con-websockets)
4. [Errores de Transacciones](#errores-de-transacciones)
5. [Problemas de Autenticación](#problemas-de-autenticación)
6. [Archivos Estáticos no Cargan](#archivos-estáticos-no-cargan)
7. [Problemas de Rendimiento](#problemas-de-rendimiento)
8. [Errores de Redis](#errores-de-redis)

---

## 🚨 PROBLEMAS DE DEPLOYMENT

### ❌ Error: "Application failed to start"

**Síntomas:**
- Railway muestra error al iniciar
- Logs muestran "Application error"

**Causas comunes:**
1. Variables de entorno faltantes
2. Error en migraciones
3. SECRET_KEY no configurado
4. Error en código

**Solución:**
```bash
# 1. Verificar logs en Railway
# Dashboard → Deployments → Ver logs

# 2. Verificar variables de entorno
# Dashboard → Variables → Verificar todas están configuradas

# 3. Si es error de migración:
# Conectar a Railway y ejecutar:
python manage.py migrate

# 4. Si persiste, hacer rollback:
# Dashboard → Deployments → Deployment anterior → Redeploy
```

---

### ❌ Error: "502 Bad Gateway"

**Síntomas:**
- Página muestra error 502
- No se puede acceder al sitio

**Solución:**
```bash
# 1. Verificar que Daphne esté corriendo
# En entrypoint.sh debe decir:
exec /opt/venv/bin/python -m daphne bingo_project.asgi:application -b 0.0.0.0 -p $PORT

# 2. Verificar PORT está configurado
# Railway lo configura automáticamente

# 3. Reiniciar deployment
# Dashboard → Settings → Restart
```

---

### ❌ Error: "Module not found"

**Síntomas:**
- Error al importar módulos
- "ModuleNotFoundError: No module named 'X'"

**Solución:**
```bash
# 1. Verificar requirements.txt tiene todas las dependencias
# 2. Forzar rebuild:
# Dashboard → Settings → Clear Build Cache → Redeploy

# 3. Si falta algo, agregar a requirements.txt y push:
git add requirements.txt
git commit -m "Fix dependencies"
git push origin main
```

---

## 💾 ERRORES DE BASE DE DATOS

### ❌ Error: "relation does not exist"

**Síntomas:**
- Error de tabla no existe
- `ProgrammingError: relation "bingo_app_X" does not exist`

**Solución:**
```bash
# En Railway CLI o shell:
python manage.py migrate

# Si persiste:
python manage.py fix_database_schema

# Si aún persiste:
python manage.py showmigrations
# Verificar que todas tengan [X]

# Último recurso (CUIDADO):
python manage.py migrate --run-syncdb
```

---

### ❌ Error: "column does not exist"

**Síntomas:**
- Error de columna faltante
- `ProgrammingError: column "blocked_credits" does not exist`

**Solución:**
```bash
# Ejecutar comando de fix:
python manage.py fix_database_schema

# Verificar migraciones:
python manage.py showmigrations

# Si falta una migración específica:
python manage.py migrate bingo_app 0040_bingoticketsettings_dailybingoschedule_bingoticket
```

---

### ❌ Error: "too many connections"

**Síntomas:**
- Error de conexiones agotadas
- "FATAL: sorry, too many clients already"

**Solución:**
```bash
# 1. En Railway, escalar la base de datos
# Dashboard → PostgreSQL → Settings → Scale

# 2. Reducir conexiones en settings.py:
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=60,  # Añadir esto
        conn_health_checks=True
    )
}

# 3. Reiniciar aplicación
```

---

## 🔌 PROBLEMAS CON WEBSOCKETS

### ❌ WebSockets no se conectan

**Síntomas:**
- Chat no funciona
- Notificaciones no llegan
- Console muestra "WebSocket connection failed"

**Verificación:**
```javascript
// En la consola del navegador:
console.log(window.location.protocol); // debe ser 'https:'

// Verificar URL del WebSocket
// Debe ser: wss://tu-dominio.railway.app/ws/...
// NO ws:// (sin SSL)
```

**Solución:**
```bash
# 1. Verificar REDIS_URL está configurado
# Railway Dashboard → Variables → REDIS_URL

# 2. Probar conexión a Redis:
python manage.py shell

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Si da error, problema con Redis

# 3. Verificar routing.py
# Asegurar que websocket_urlpatterns esté bien configurado

# 4. Reiniciar aplicación
```

---

### ❌ WebSocket se desconecta constantemente

**Síntomas:**
- Conexiones se caen cada pocos segundos
- "WebSocket is already in CLOSING or CLOSED state"

**Solución:**
```bash
# 1. Aumentar timeout en Railway:
# No hay configuración directa, pero verificar:
# - No hay loops infinitos en consumers
# - No hay errores en el código del consumer

# 2. Verificar logs para excepciones:
# Railway Dashboard → Logs → Buscar errores

# 3. Si es por carga, escalar Redis:
# Dashboard → Redis → Settings → Scale
```

---

## 💰 ERRORES DE TRANSACCIONES

### ❌ Créditos bloqueados negativos

**Síntomas:**
- User.blocked_credits < 0
- Error al finalizar juego

**Solución:**
```bash
# Ejecutar comando de fix:
python manage.py fix_negative_blocked_credits

# Verificar:
python manage.py debug_blocked_credits

# Si persiste, revisar manualmente:
python manage.py shell

from bingo_app.models import User
users = User.objects.filter(blocked_credits__lt=0)
for user in users:
    print(f"{user.username}: {user.blocked_credits}")
    user.blocked_credits = 0
    user.save()
```

---

### ❌ Premio no se distribuyó

**Síntomas:**
- Juego terminó pero ganador no recibió premio
- held_balance no se distribuyó

**Verificación:**
```bash
python manage.py shell

from bingo_app.models import Game, Transaction

# Verificar juego específico
game = Game.objects.get(id=GAME_ID)
print(f"Is finished: {game.is_finished}")
print(f"Winner: {game.winner}")
print(f"Prize: {game.prize}")
print(f"Held balance: {game.held_balance}")

# Verificar transacciones
transactions = Transaction.objects.filter(related_game=game)
for t in transactions:
    print(f"{t.user.username}: {t.amount} - {t.transaction_type}")
```

**Solución Manual (CUIDADO):**
```python
# Si realmente no se distribuyó:
from decimal import Decimal
from django.db import transaction
from bingo_app.models import Game, Transaction, User

with transaction.atomic():
    game = Game.objects.get(id=GAME_ID)
    winner = game.winner
    
    if winner:
        winner.credit_balance += game.prize
        winner.save()
        
        Transaction.objects.create(
            user=winner,
            amount=game.prize,
            transaction_type='PRIZE',
            description=f"Premio manual por {game.name}",
            related_game=game
        )
        
        print(f"Premio de {game.prize} acreditado a {winner.username}")
```

---

### ❌ Transacción duplicada

**Síntomas:**
- Usuario recibió créditos dos veces
- Premio se pagó múltiples veces

**Verificación:**
```bash
python manage.py check_transactions

# O manualmente:
python manage.py shell

from bingo_app.models import Transaction
from django.db.models import Count

# Buscar duplicados
duplicates = Transaction.objects.values(
    'user', 'amount', 'transaction_type', 'created_at'
).annotate(
    count=Count('id')
).filter(count__gt=1)

for dup in duplicates:
    print(dup)
```

**Solución:**
```python
# Contactar al usuario afectado
# Ajustar manualmente si es necesario
# NO hay solución automática - revisar caso por caso
```

---

## 🔐 PROBLEMAS DE AUTENTICACIÓN

### ❌ Login con Facebook/Google no funciona

**Síntomas:**
- Error al hacer login social
- Redirect loop
- "Configuration Error"

**Solución:**
```bash
# 1. Verificar variables de entorno:
FACEBOOK_CLIENT_ID=tu-id
FACEBOOK_SECRET=tu-secret
GOOGLE_CLIENT_ID=tu-id
GOOGLE_SECRET=tu-secret

# 2. Verificar URLs en Facebook/Google Console:
# Allowed redirect URIs debe incluir:
https://tu-dominio.railway.app/accounts/facebook/login/callback/
https://tu-dominio.railway.app/accounts/google/login/callback/

# 3. Verificar Site en Django:
python manage.py shell

from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'tu-dominio.railway.app'
site.name = 'Bingo JyM'
site.save()

# 4. Verificar SocialApp está creado:
from allauth.socialaccount.models import SocialApp
apps = SocialApp.objects.all()
for app in apps:
    print(f"{app.provider}: {app.client_id}")
```

---

### ❌ Usuario no puede hacer login

**Síntomas:**
- "Incorrect username or password"
- Usuario existe pero no puede entrar

**Verificación:**
```bash
python manage.py shell

from bingo_app.models import User

# Buscar usuario
user = User.objects.get(username='username')
print(f"Is active: {user.is_active}")
print(f"Is blocked: {user.is_blocked}")
print(f"Has password: {user.has_usable_password()}")
```

**Solución:**
```python
# Si está bloqueado:
user.is_blocked = False
user.blocked_until = None
user.save()

# Si no tiene password (login social):
# Debe usar login social

# Si necesita reset password:
from django.contrib.auth.tokens import default_token_generator
token = default_token_generator.make_token(user)
# Enviar email con link de reset
```

---

## 🎨 ARCHIVOS ESTÁTICOS NO CARGAN

### ❌ CSS/JS no se cargan

**Síntomas:**
- Página sin estilos
- JavaScript no funciona
- 404 en archivos estáticos

**Solución:**
```bash
# 1. Recolectar archivos estáticos:
python manage.py collectstatic --noinput

# 2. Verificar STATIC_ROOT y STATIC_URL:
python manage.py shell

from django.conf import settings
print(settings.STATIC_ROOT)
print(settings.STATIC_URL)

# 3. Verificar WhiteNoise está en middleware:
# settings.py debe tener:
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar aquí
    ...
]

# 4. Verificar STATICFILES_STORAGE:
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 5. Redeploy:
git commit --allow-empty -m "Force redeploy"
git push origin main
```

---

### ❌ Imágenes subidas no se muestran

**Síntomas:**
- Imágenes de perfil no cargan
- Comprobantes de pago no se ven

**Problema:**
Railway no es persistente para archivos media.

**Solución (Temporal):**
```bash
# Para producción, usar servicio externo:
# - AWS S3
# - Cloudinary
# - Railway Volumes (beta)

# Configurar django-storages:
pip install django-storages boto3

# settings.py:
if 'AWS_ACCESS_KEY_ID' in os.environ:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
```

---

## 🐌 PROBLEMAS DE RENDIMIENTO

### ❌ Sitio muy lento

**Síntomas:**
- Páginas tardan más de 5 segundos
- Timeouts frecuentes

**Diagnóstico:**
```bash
# 1. Revisar logs para queries lentas:
# Railway Dashboard → Logs

# 2. Activar query logging temporalmente:
# settings.py:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Solución:**
```bash
# 1. Agregar índices a la base de datos:
python manage.py shell

from django.db import connection
with connection.cursor() as cursor:
    # Ejemplo: índice para juegos activos
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_game_active_finished 
        ON bingo_app_game (is_active, is_finished);
    """)

# 2. Usar select_related y prefetch_related:
# En views.py, cambiar:
games = Game.objects.all()  # ❌ Lento

# Por:
games = Game.objects.select_related('organizer').all()  # ✅ Rápido

# 3. Implementar caché con Redis:
# settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# En views:
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache por 5 minutos
def lobby(request):
    ...

# 4. Escalar en Railway:
# Dashboard → Settings → Scale (más CPU/RAM)
```

---

## 🔴 ERRORES DE REDIS

### ❌ "Connection refused" error

**Síntomas:**
- `redis.exceptions.ConnectionError`
- WebSockets no funcionan

**Solución:**
```bash
# 1. Verificar REDIS_URL está configurado:
# Railway Dashboard → Variables → REDIS_URL

# 2. Formato correcto:
# redis://default:password@host:port

# 3. Si no existe Redis en Railway:
# Dashboard → New → Database → Redis

# 4. Reconectar y redeploy
```

---

### ❌ Redis "Out of Memory"

**Síntomas:**
- Error OOM
- Redis se reinicia constantemente

**Solución:**
```bash
# 1. Escalar Redis:
# Railway Dashboard → Redis → Settings → Scale

# 2. Reducir TTL de cache:
# settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
        'TIMEOUT': 300,  # 5 minutos en lugar de más
    }
}

# 3. Limpiar cache:
python manage.py shell

from django.core.cache import cache
cache.clear()
```

---

## 🆘 EMERGENCIA: ROLLBACK COMPLETO

Si nada funciona y necesitas volver a una versión anterior:

```bash
# Opción 1: Rollback en Railway (RECOMENDADO)
# 1. Railway Dashboard → Deployments
# 2. Encontrar último deployment que funcionaba
# 3. Click en los 3 puntos → Redeploy

# Opción 2: Rollback en Git
git log  # Ver commits anteriores
git checkout HASH_DEL_COMMIT_QUE_FUNCIONABA
git push origin main --force  # CUIDADO: Sobrescribe historial

# Opción 3: Restaurar backup de base de datos
# Railway Dashboard → PostgreSQL → Backups → Restore
```

---

## 📞 CHECKLIST DE DIAGNÓSTICO GENERAL

Cuando algo falla, sigue este orden:

1. **Verificar logs** (Railway Dashboard → Logs)
2. **Verificar variables de entorno** (Dashboard → Variables)
3. **Verificar estado de la base de datos** (`python manage.py dbshell`)
4. **Verificar Redis** (intentar conectar desde shell)
5. **Verificar migraciones** (`python manage.py showmigrations`)
6. **Buscar error en Sentry** (si está configurado)
7. **Probar en local** (descartar problema de código)
8. **Revisar este documento** (soluciones específicas)

---

## 🔍 COMANDOS ÚTILES DE DIAGNÓSTICO

```bash
# Ver estado del sistema
python manage.py check_system_status

# Verificar transacciones
python manage.py check_transactions

# Ver usuarios problemáticos
python manage.py shell
from bingo_app.models import User
User.objects.filter(credit_balance__lt=0)
User.objects.filter(blocked_credits__lt=0)
User.objects.filter(is_blocked=True)

# Ver juegos problemáticos
from bingo_app.models import Game
Game.objects.filter(is_finished=False, is_started=True, held_balance__gt=0)

# Ver ultimas transacciones
from bingo_app.models import Transaction
Transaction.objects.all().order_by('-created_at')[:10]

# Ver errores recientes
# Railway Dashboard → Logs → Filter by "ERROR"
```

---

## 📧 INFORMACIÓN DE CONTACTO DE EMERGENCIA

Si el problema persiste:

1. **Revisar documentación completa**: `AUDITORIA_LANZAMIENTO_2024.md`
2. **Ejecutar verificación**: `python check_launch_readiness.py`
3. **Consultar documentación específica**:
   - Facebook: `FACEBOOK_LOGIN_TROUBLESHOOTING.md`
   - Videollamadas: `VIDEOCALL_INSTRUCTIONS.md`
   - Backups: `BACKUP_RESTORATION_GUIDE.md`

---

**Última actualización**: 19 de Octubre, 2024
**Versión**: 1.0

