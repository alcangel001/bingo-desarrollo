# 📋 Guía: Copiar Variables de Producción a Desarrollo

## ⚠️ IMPORTANTE - SEGURIDAD

**Estamos copiando variables de PRODUCCIÓN a DESARROLLO:**
- ✅ Solo estamos COPIANDO, no modificando producción
- ✅ Producción sigue intacta
- ✅ Tu rifa activa está segura

---

## 📋 PASO 1: Obtener Variables de Producción

1. **En Railway, ve a tu proyecto de PRODUCCIÓN** (el que tiene tu rifa activa)
2. **Haz clic en tu servicio de la aplicación** (no PostgreSQL)
3. **Ve a la pestaña "Variables"**
4. **Copia TODAS las variables** que necesitas (anótalas en un papel o documento temporal)

---

## 📋 PASO 2: Agregar Variables a Desarrollo

1. **En Railway, ve a tu proyecto de DESARROLLO** (el nuevo proyecto)
2. **Haz clic en tu servicio de la aplicación** (no PostgreSQL)
3. **Ve a la pestaña "Variables"**
4. **Agrega cada variable una por una:**

### Variables que DEBES copiar (si las tienes en producción):

#### **Obligatorias (ya las tienes):**
- ✅ `DATABASE_URL` - Ya configurada (es diferente, de tu PostgreSQL de desarrollo)
- ✅ `SECRET_KEY` - Ya configurada (es diferente, para desarrollo)
- ✅ `DEBUG` - Ya configurada (True para desarrollo)
- ✅ `ALLOWED_HOSTS` - Ya configurada (*.railway.app)
- ✅ `DJANGO_SUPERUSER_PASSWORD` - Ya configurada

#### **Opcionales pero recomendadas (copia de producción):**

**Agora (Videollamadas):**
- `AGORA_APP_ID` - Copia de producción
- `AGORA_APP_CERTIFICATE` - Copia de producción

**OAuth (Login Social):**
- `GOOGLE_CLIENT_ID` - Copia de producción
- `GOOGLE_SECRET` - Copia de producción
- `FACEBOOK_CLIENT_ID` - Copia de producción
- `FACEBOOK_SECRET` - Copia de producción

**Email (SendGrid):**
- `SENDGRID_API_KEY` - Copia de producción
- `DEFAULT_FROM_EMAIL` - Copia de producción

**Redis (Cache/WebSockets):**
- `REDIS_URL` - Copia de producción (o déjala vacía si no usas Redis en desarrollo)

**IA (Gemini):**
- `GEMINI_API_KEY` - Copia de producción

**Monitoreo:**
- `SENTRY_DSN` - Copia de producción (opcional)

**Otros:**
- `CSRF_TRUSTED_ORIGINS` - Agrega tu URL de desarrollo: `https://web-production-14f41.up.railway.app`
- `CACHE_BUST` - Puedes usar el mismo de producción o uno nuevo

---

## 📋 PASO 3: Variables Específicas de Email (si usas SMTP personalizado)

Si en producción usas SMTP personalizado (no SendGrid), copia también:
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_SSL`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_FROM`

---

## 📋 PASO 4: Verificar Variables

Después de agregar todas las variables:

1. **Verifica que tienes todas las necesarias**
2. **Haz un redeploy** para que se apliquen
3. **Prueba las funcionalidades** que requieren esas variables:
   - Login con Google/Facebook
   - Envío de emails
   - Videollamadas (si las usas)
   - IA (si la usas)

---

## ⚠️ IMPORTANTE - Variables que NO debes copiar iguales:

1. **`DATABASE_URL`** - Debe ser diferente (la de tu PostgreSQL de desarrollo)
2. **`SECRET_KEY`** - Debe ser diferente (ya la tienes configurada)
3. **`DEBUG`** - Debe ser `True` en desarrollo (ya está configurada)
4. **`ALLOWED_HOSTS`** - Debe incluir tu URL de desarrollo

---

## ✅ Resumen

1. Ve a producción → Copia variables
2. Ve a desarrollo → Agrega variables
3. Redeploy desarrollo
4. Prueba funcionalidades

---

## 🆘 Si algo no funciona

- Verifica que copiaste el valor completo (sin espacios)
- Verifica que el nombre de la variable es exactamente igual
- Revisa los logs del deploy para ver errores
- Algunas variables pueden no ser necesarias en desarrollo (como Sentry)

---

¡Listo! Copia las variables y tendrás tu entorno de desarrollo completo. 🚀




