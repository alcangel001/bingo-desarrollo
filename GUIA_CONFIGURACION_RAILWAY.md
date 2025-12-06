# 🚀 GUÍA COMPLETA: CONFIGURACIÓN DE RAILWAY PARA LANZAMIENTO

## 📊 ESTADO ACTUAL (Según verificación local)

Actualmente en tu entorno local **FALTAN** estas variables:

### 🔴 OBLIGATORIAS (4):
- ❌ DATABASE_URL
- ❌ REDIS_URL
- ❌ SECRET_KEY
- ❌ ALLOWED_HOSTS

### 🟡 IMPORTANTES (3):
- ❌ SENDGRID_API_KEY
- ❌ EMAIL_HOST_PASSWORD
- ❌ DEFAULT_FROM_EMAIL

### 🟢 OPCIONALES (11):
- ❌ GOOGLE_CLIENT_ID, GOOGLE_SECRET
- ❌ FACEBOOK_CLIENT_ID, FACEBOOK_SECRET
- ❌ AGORA_APP_ID, AGORA_APP_CERTIFICATE
- ❌ SENTRY_DSN
- ❌ Otras...

**NOTA:** Railway automáticamente crea DATABASE_URL, REDIS_URL y RAILWAY_PUBLIC_DOMAIN.

---

## 🎯 CONFIGURACIÓN PASO A PASO

### PASO 1: Variables que Railway crea automáticamente

Cuando creas un proyecto en Railway, estas se crean solas:

```bash
# Railway las crea automáticamente:
DATABASE_URL="postgresql://..."          # ✅ Auto
RAILWAY_PUBLIC_DOMAIN="xxxx.railway.app" # ✅ Auto
RAILWAY_ENVIRONMENT="production"         # ✅ Auto
```

**NO necesitas configurarlas manualmente** ✅

---

### PASO 2: Agregar servicio Redis

Railway necesita Redis para los WebSockets:

**En el dashboard de Railway:**
1. Click en tu proyecto
2. Click en **"New"** → **"Database"** → **"Add Redis"**
3. Railway automáticamente:
   - Crea el servicio Redis
   - Configura REDIS_URL
   - Lo vincula a tu aplicación

**Resultado:**
```bash
REDIS_URL="redis://default:password@host:port" # ✅ Auto configurada
```

---

### PASO 3: Configurar SECRET_KEY (OBLIGATORIO)

**Genera una clave segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Resultado ejemplo:**
```
8kJ2nH5mP9qR3tY7vZ1xC4bN6aS8dF0gH2jK4lM7nP9qR3tY5vZ1xC3
```

**Configúrala en Railway:**
```bash
railway variables set SECRET_KEY="8kJ2nH5mP9qR3tY7vZ1xC4bN6aS8dF0gH2jK4lM7nP9qR3tY5vZ1xC3"
```

O desde el dashboard:
1. Ve a tu proyecto en Railway
2. Click en **"Variables"**
3. Click en **"New Variable"**
4. **Name:** `SECRET_KEY`
5. **Value:** [pega la clave generada]
6. Click **"Add"**

---

### PASO 4: Configurar ALLOWED_HOSTS (OBLIGATORIO)

**Valor recomendado:**
```bash
railway variables set ALLOWED_HOSTS="tudominio.railway.app,www.tudominio.com"
```

**Si solo usas el dominio de Railway:**
```bash
railway variables set ALLOWED_HOSTS="web-production-2d504.up.railway.app"
```

**Reemplaza** `web-production-2d504.up.railway.app` con tu dominio real de Railway.

**Encontrar tu dominio:**
1. Ve a tu proyecto en Railway
2. Click en tu servicio web
3. Mira en **"Settings"** → **"Domains"**
4. Copia el dominio que termina en `.railway.app`

---

### PASO 5: Configurar CSRF_TRUSTED_ORIGINS (IMPORTANTE)

Debe coincidir con tu dominio:

```bash
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app"
```

**Si tienes dominio personalizado:**
```bash
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app,https://www.tudominio.com"
```

---

### PASO 6: Configurar EMAIL (Para funcionalidad completa)

#### Opción A: SendGrid (Recomendado)

1. **Crear cuenta en SendGrid:** https://sendgrid.com/
2. **Crear API Key:**
   - Ve a Settings → API Keys
   - Click "Create API Key"
   - Nombre: "Bingo App"
   - Permisos: "Full Access"
   - Copia la clave generada

3. **Configurar en Railway:**
```bash
railway variables set SENDGRID_API_KEY="SG.xxxxxxxxxxxxxxxxxxxxxxxx"
railway variables set EMAIL_HOST_PASSWORD="SG.xxxxxxxxxxxxxxxxxxxxxxxx"
railway variables set DEFAULT_FROM_EMAIL="noreply@tudominio.com"
```

**NOTA:** `EMAIL_HOST_PASSWORD` es un alias de `SENDGRID_API_KEY` (tu código usa el primero).

---

### PASO 7: Login Social (OPCIONAL)

#### Google OAuth (Si quieres login con Google):

1. **Ir a:** https://console.cloud.google.com/
2. **Crear proyecto** o seleccionar existente
3. **APIs & Services** → **Credentials**
4. **Create Credentials** → **OAuth 2.0 Client ID**
5. **Authorized redirect URIs:** 
   ```
   https://tudominio.railway.app/accounts/google/login/callback/
   ```
6. **Copiar Client ID y Client Secret**

**Configurar en Railway:**
```bash
railway variables set GOOGLE_CLIENT_ID="tu-client-id.apps.googleusercontent.com"
railway variables set GOOGLE_SECRET="tu-client-secret"
```

#### Facebook OAuth (Si quieres login con Facebook):

1. **Ir a:** https://developers.facebook.com/
2. **Crear App** → **Consumer**
3. **Add Product** → **Facebook Login**
4. **Settings** → **Basic**
5. **Copiar App ID y App Secret**
6. **Valid OAuth Redirect URIs:**
   ```
   https://tudominio.railway.app/accounts/facebook/login/callback/
   ```

**Configurar en Railway:**
```bash
railway variables set FACEBOOK_CLIENT_ID="tu-app-id"
railway variables set FACEBOOK_SECRET="tu-app-secret"
```

---

### PASO 8: Videollamadas con Agora (OPCIONAL)

#### Si quieres funcionalidad de videollamadas:

1. **Crear cuenta en Agora:** https://www.agora.io/
2. **Crear proyecto** en el dashboard
3. **Copiar App ID y Certificate**

**Configurar en Railway:**
```bash
railway variables set AGORA_APP_ID="tu-app-id"
railway variables set AGORA_APP_CERTIFICATE="tu-certificate"
```

---

### PASO 9: Monitoreo con Sentry (OPCIONAL pero RECOMENDADO)

#### Para detectar errores en producción:

1. **Crear cuenta en Sentry:** https://sentry.io/
2. **Crear nuevo proyecto** → Django
3. **Copiar DSN**

**Configurar en Railway:**
```bash
railway variables set SENTRY_DSN="https://xxx@xxx.ingest.sentry.io/xxx"
```

---

## 📋 CHECKLIST COMPLETO DE CONFIGURACIÓN

### ✅ Variables Obligatorias:

- [ ] **DATABASE_URL** → Railway lo crea automáticamente ✅
- [ ] **REDIS_URL** → Agregar servicio Redis en Railway
- [ ] **SECRET_KEY** → Generar y configurar manualmente
- [ ] **ALLOWED_HOSTS** → Tu dominio de Railway

### ⏳ Variables Importantes:

- [ ] **SENDGRID_API_KEY** → Para emails (alta prioridad)
- [ ] **EMAIL_HOST_PASSWORD** → Mismo valor que SENDGRID_API_KEY
- [ ] **DEFAULT_FROM_EMAIL** → Email remitente
- [ ] **CSRF_TRUSTED_ORIGINS** → Tu dominio con https://

### 🎁 Variables Opcionales (según necesites):

- [ ] **GOOGLE_CLIENT_ID, GOOGLE_SECRET** → Login con Google
- [ ] **FACEBOOK_CLIENT_ID, FACEBOOK_SECRET** → Login con Facebook
- [ ] **AGORA_APP_ID, AGORA_APP_CERTIFICATE** → Videollamadas
- [ ] **SENTRY_DSN** → Monitoreo de errores (recomendado)

---

## 🛠️ CONFIGURACIÓN RÁPIDA MÍNIMA

Si quieres lanzar **LO MÁS RÁPIDO POSIBLE**, configura solo esto:

```bash
# 1. Agregar Redis en Railway dashboard
# (Click en New → Database → Redis)

# 2. Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# 3. Configurar las 3 variables esenciales:
railway variables set SECRET_KEY="[clave-generada]"
railway variables set ALLOWED_HOSTS="tu-app.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app"

# 4. Deploy!
git push railway main
```

**Con esto funcionará:**
- ✅ Juegos de bingo
- ✅ Rifas
- ✅ Compra/venta de cartones
- ✅ Sistema de créditos
- ✅ WebSockets (notificaciones en tiempo real)

**NO funcionará (hasta configurar emails):**
- ❌ Notificaciones por email
- ❌ Recuperación de contraseña

---

## 📝 SCRIPT COMPLETO DE CONFIGURACIÓN

### Copia y pega esto (reemplaza los valores):

```bash
# ============================================
# CONFIGURACIÓN COMPLETA DE RAILWAY
# ============================================

# 1. SECRET_KEY (Generar nueva)
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copiar resultado y:
railway variables set SECRET_KEY="[pegar-aqui]"

# 2. HOSTS
railway variables set ALLOWED_HOSTS="tu-app.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app"

# 3. EMAIL (SendGrid)
railway variables set SENDGRID_API_KEY="SG.xxxxx"
railway variables set EMAIL_HOST_PASSWORD="SG.xxxxx"
railway variables set DEFAULT_FROM_EMAIL="noreply@tudominio.com"

# 4. GOOGLE LOGIN (Opcional)
railway variables set GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
railway variables set GOOGLE_SECRET="xxx"

# 5. FACEBOOK LOGIN (Opcional)
railway variables set FACEBOOK_CLIENT_ID="xxx"
railway variables set FACEBOOK_SECRET="xxx"

# 6. VIDEOLLAMADAS (Opcional)
railway variables set AGORA_APP_ID="xxx"
railway variables set AGORA_APP_CERTIFICATE="xxx"

# 7. MONITOREO (Opcional pero recomendado)
railway variables set SENTRY_DSN="https://xxx@xxx.ingest.sentry.io/xxx"

# 8. DEBUG (Asegurar que esté en False)
railway variables set DEBUG="False"
```

---

## 🔍 VERIFICAR CONFIGURACIÓN ACTUAL EN RAILWAY

### Opción 1: Desde CLI

```bash
# Instalar Railway CLI si no lo tienes:
# npm install -g @railway/cli

# Login
railway login

# Ver variables actuales
railway variables

# Ver una variable específica
railway variables get SECRET_KEY
```

### Opción 2: Desde Dashboard

1. Ve a https://railway.app/
2. Login
3. Selecciona tu proyecto
4. Click en **"Variables"** (ícono de engranaje)
5. Verás todas las variables configuradas

---

## ⚙️ CONFIGURACIÓN SEGÚN FUNCIONALIDAD

### 🎮 Solo Bingo Básico:
```bash
✅ DATABASE_URL (auto)
✅ REDIS_URL (agregar Redis)
✅ SECRET_KEY (configurar)
✅ ALLOWED_HOSTS (configurar)
```

### 📧 Bingo + Emails:
```bash
✅ Todo lo anterior +
✅ SENDGRID_API_KEY
✅ EMAIL_HOST_PASSWORD
✅ DEFAULT_FROM_EMAIL
```

### 👥 Bingo + Login Social:
```bash
✅ Todo lo anterior +
✅ GOOGLE_CLIENT_ID, GOOGLE_SECRET
✅ FACEBOOK_CLIENT_ID, FACEBOOK_SECRET
```

### 📹 Bingo Completo (Todo):
```bash
✅ Todo lo anterior +
✅ AGORA_APP_ID, AGORA_APP_CERTIFICATE
✅ SENTRY_DSN
```

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "Application failed to respond"

**Causa:** DATABASE_URL o REDIS_URL no configuradas

**Solución:**
```bash
# Verificar que Redis esté agregado
railway services
# Si no está, agregarlo desde el dashboard

# Verificar variables
railway variables list
```

---

### Problema 2: "SECRET_KEY is not configured"

**Causa:** SECRET_KEY no está en variables de entorno

**Solución:**
```bash
# Generar nueva
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Configurar
railway variables set SECRET_KEY="[valor-generado]"

# Verificar
railway variables get SECRET_KEY
```

---

### Problema 3: "Invalid HTTP_HOST header"

**Causa:** ALLOWED_HOSTS no incluye el dominio actual

**Solución:**
```bash
# Ver tu dominio actual
railway domain

# Configurar
railway variables set ALLOWED_HOSTS="tu-dominio.railway.app"
```

---

### Problema 4: Emails no se envían

**Causa:** SENDGRID_API_KEY no configurada o inválida

**Solución:**
1. Verificar que la API Key de SendGrid sea válida
2. Verificar que DEFAULT_FROM_EMAIL esté configurado
3. Verificar que EMAIL_HOST_PASSWORD tenga el mismo valor que SENDGRID_API_KEY

---

## 📊 CONFIGURACIÓN MÍNIMA vs COMPLETA

### CONFIGURACIÓN MÍNIMA (Para empezar):

**Tiempo:** 10 minutos  
**Funcionalidades:** 70%

```bash
# Desde Railway Dashboard:
1. Agregar servicio Redis
2. Configurar SECRET_KEY
3. Configurar ALLOWED_HOSTS

# Desde CLI:
railway variables set SECRET_KEY="[generar-nueva]"
railway variables set ALLOWED_HOSTS="tudominio.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app"
```

**Funciona:**
- ✅ Bingo completo
- ✅ Rifas
- ✅ Compra/venta
- ✅ WebSockets
- ❌ Emails (usar admin manual)
- ❌ Login social

---

### CONFIGURACIÓN COMPLETA (Recomendado):

**Tiempo:** 30-60 minutos  
**Funcionalidades:** 100%

```bash
# Todo lo de mínima +
railway variables set SENDGRID_API_KEY="SG.xxx"
railway variables set EMAIL_HOST_PASSWORD="SG.xxx"
railway variables set DEFAULT_FROM_EMAIL="noreply@tudominio.com"
railway variables set GOOGLE_CLIENT_ID="xxx"
railway variables set GOOGLE_SECRET="xxx"
railway variables set FACEBOOK_CLIENT_ID="xxx"
railway variables set FACEBOOK_SECRET="xxx"
railway variables set AGORA_APP_ID="xxx"
railway variables set AGORA_APP_CERTIFICATE="xxx"
railway variables set SENTRY_DSN="https://xxx"
```

**Funciona:**
- ✅ Todo
- ✅ Emails automáticos
- ✅ Login con Google/Facebook
- ✅ Videollamadas
- ✅ Monitoreo de errores

---

## 🎯 PLAN RECOMENDADO

### DÍA 1: Configuración Básica

```bash
# 1. Agregar Redis (desde dashboard)
# 2. Configurar variables mínimas:
railway variables set SECRET_KEY="[nueva]"
railway variables set ALLOWED_HOSTS="tudominio.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app"

# 3. Deploy
git push railway main

# 4. Probar que funcione
```

---

### DÍA 2: Agregar Emails

```bash
# 1. Crear cuenta SendGrid
# 2. Generar API Key
# 3. Configurar:
railway variables set SENDGRID_API_KEY="SG.xxx"
railway variables set EMAIL_HOST_PASSWORD="SG.xxx"
railway variables set DEFAULT_FROM_EMAIL="noreply@tudominio.com"

# 4. Probar envío de emails
```

---

### DÍA 3: Funcionalidades Opcionales

```bash
# Solo si las necesitas:
# - Login social (Google/Facebook)
# - Videollamadas (Agora)
# - Monitoreo (Sentry)
```

---

## 🔧 COMANDOS ÚTILES DE RAILWAY

```bash
# Ver todas las variables
railway variables

# Listar servicios
railway services

# Ver logs en tiempo real
railway logs

# Ver dominio
railway domain

# Reiniciar aplicación
railway up --detach

# Conectar a shell de producción
railway run bash

# Ejecutar comando en producción
railway run python manage.py createsuperuser

# Ver estado del deployment
railway status
```

---

## 📝 TEMPLATE DE CONFIGURACIÓN

Guarda esto y completa los valores:

```bash
# ==========================================
# CONFIGURACIÓN RAILWAY - BINGO JYM
# Fecha: [completar]
# ==========================================

# === OBLIGATORIAS ===
DATABASE_URL=[Railway lo crea auto]
REDIS_URL=[Railway lo crea auto al agregar Redis]
SECRET_KEY=[generar con: python -c "import secrets; print(secrets.token_urlsafe(50))"]
ALLOWED_HOSTS=[tu-dominio].railway.app
CSRF_TRUSTED_ORIGINS=https://[tu-dominio].railway.app

# === IMPORTANTES ===
SENDGRID_API_KEY=SG.[completar]
EMAIL_HOST_PASSWORD=SG.[mismo valor que arriba]
DEFAULT_FROM_EMAIL=noreply@[tu-dominio].com

# === OPCIONALES ===
GOOGLE_CLIENT_ID=[completar si quieres]
GOOGLE_SECRET=[completar si quieres]
FACEBOOK_CLIENT_ID=[completar si quieres]
FACEBOOK_SECRET=[completar si quieres]
AGORA_APP_ID=[completar si quieres videollamadas]
AGORA_APP_CERTIFICATE=[completar si quieres videollamadas]
SENTRY_DSN=[completar si quieres monitoreo]

# === AUTOMÁTICAS (Railway las crea) ===
RAILWAY_PUBLIC_DOMAIN=[auto]
RAILWAY_ENVIRONMENT=production [auto]
PORT=[auto]
```

---

## ⚡ LANZAMIENTO RÁPIDO (15 MINUTOS)

Si quieres lanzar **HOY** con lo esencial:

```bash
# 1. Agregar Redis (desde dashboard Railway)
# Click en: New → Database → Add Redis

# 2. Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# 3. Configurar (reemplaza los valores)
railway variables set SECRET_KEY="[valor-generado-paso-2]"
railway variables set ALLOWED_HOSTS="tu-app.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app"

# 4. Deploy
git push railway main

# 5. Ver logs
railway logs

# ✅ LISTO! Tu app está en línea
```

**Funcionalidad:** 70% (suficiente para empezar)

---

## 🎉 DESPUÉS DE CONFIGURAR

### Verificar que todo funcione:

1. **Abrir tu app:** https://tu-dominio.railway.app/
2. **Crear cuenta** de usuario
3. **Login** exitoso
4. **Ver lobby** de juegos
5. **Probar compra** de créditos (manual desde admin)
6. **Crear juego** y probar

---

## 📞 SOPORTE

**Si algo no funciona:**

```bash
# Ver logs en tiempo real
railway logs --follow

# Ver últimas 100 líneas
railway logs --tail 100

# Verificar estado
railway status

# Ver variables configuradas
railway variables
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `verificar_railway.py` - Script para ver qué falta
- `env_example.txt` - Ejemplo de variables
- `CHECKLIST_LANZAMIENTO_RAPIDO.md` - Checklist general

---

## ✅ RESUMEN

**TIENES que configurar:**
1. Agregar Redis (click en dashboard)
2. SECRET_KEY (generar y configurar)
3. ALLOWED_HOSTS (tu dominio)
4. CSRF_TRUSTED_ORIGINS (tu dominio con https)

**OPCIONAL (para después):**
5. SendGrid (emails)
6. Google/Facebook (login social)
7. Agora (videollamadas)
8. Sentry (monitoreo)

**Tiempo mínimo:** 10-15 minutos  
**Tiempo completo:** 30-60 minutos

---

**¿Listo para configurar?** 🚀

