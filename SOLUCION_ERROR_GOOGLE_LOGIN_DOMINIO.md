# 🔧 SOLUCIÓN: Error Google Login y DisallowedHost

## 🚨 PROBLEMAS DETECTADOS

1. **Error Google OAuth:** `redirect_uri_mismatch`
   - Google no reconoce tu nuevo dominio `bingoyrifajym.com`
   
2. **Error Django:** `DisallowedHost: Invalid HTTP_HOST header: 'bingoyrifajym.com'`
   - Django no acepta tu dominio porque no está en `ALLOWED_HOSTS`

---

## ✅ SOLUCIÓN 1: ACTUALIZAR ALLOWED_HOSTS EN RAILWAY

### Paso 1: Ir a Variables en Railway

1. Ve a **Railway** → Tu proyecto
2. Haz clic en **"Variables"** (ícono de engranaje ⚙️ o pestaña "Variables")

### Paso 2: Actualizar ALLOWED_HOSTS

1. Busca la variable **`ALLOWED_HOSTS`**
2. Si existe, haz clic para **editarla**
3. Si NO existe, haz clic en **"New Variable"** o **"Add Variable"**
4. Completa así:
   - **Name:** `ALLOWED_HOSTS`
   - **Value:** `web-production-2d504.up.railway.app,bingoyrifajym.com,www.bingoyrifajym.com`
5. Haz clic en **"Save"** o **"Add"**

### Paso 3: Actualizar CSRF_TRUSTED_ORIGINS

1. Busca la variable **`CSRF_TRUSTED_ORIGINS`**
2. Si existe, edítala. Si no, créala
3. Completa así:
   - **Name:** `CSRF_TRUSTED_ORIGINS`
   - **Value:** `https://web-production-2d504.up.railway.app,https://bingoyrifajym.com,https://www.bingoyrifajym.com`
4. Guarda

**⚠️ IMPORTANTE:** Después de guardar, Railway reiniciará automáticamente tu aplicación. Espera 1-2 minutos.

---

## ✅ SOLUCIÓN 2: ACTUALIZAR GOOGLE OAUTH

### Paso 1: Ir a Google Cloud Console

1. Ve a: **https://console.cloud.google.com/**
2. Inicia sesión con tu cuenta de Google
3. Selecciona el proyecto donde configuraste OAuth (o busca el proyecto de tu aplicación)

### Paso 2: Ir a Credentials (Credenciales)

1. En el menú lateral, ve a **"APIs & Services"** → **"Credentials"**
2. Busca tu **OAuth 2.0 Client ID** (el que usas para login con Google)
3. Haz clic en el **nombre** del cliente OAuth para editarlo

### Paso 3: Agregar URLs de redirección

1. Busca la sección **"Authorized redirect URIs"** (URIs de redirección autorizadas)
2. Verás URLs como:
   ```
   https://web-production-2d504.up.railway.app/accounts/google/login/callback/
   ```
3. Haz clic en **"Add URI"** o el botón **"+"**
4. Agrega estas dos URLs nuevas:
   ```
   https://bingoyrifajym.com/accounts/google/login/callback/
   https://www.bingoyrifajym.com/accounts/google/login/callback/
   ```
5. Haz clic en **"Save"** (Guardar)

### Paso 4: Verificar configuración

Después de guardar, deberías ver algo como:

```
Authorized redirect URIs:
✅ https://web-production-2d504.up.railway.app/accounts/google/login/callback/
✅ https://bingoyrifajym.com/accounts/google/login/callback/
✅ https://www.bingoyrifajym.com/accounts/google/login/callback/
```

---

## ✅ SOLUCIÓN 3: ACTUALIZAR FACEBOOK (Si lo usas)

Si también usas login con Facebook, haz lo mismo:

### En Facebook Developers:

1. Ve a: **https://developers.facebook.com/**
2. Selecciona tu aplicación
3. Ve a **"Settings"** → **"Basic"**
4. Busca **"Valid OAuth Redirect URIs"**
5. Agrega:
   ```
   https://bingoyrifajym.com/accounts/facebook/login/callback/
   https://www.bingoyrifajym.com/accounts/facebook/login/callback/
   ```
6. Guarda

---

## 🧪 VERIFICAR QUE FUNCIONA

### 1. Esperar unos minutos

- Railway reinicia la aplicación automáticamente (1-2 minutos)
- Los cambios de Google pueden tardar unos minutos en aplicarse

### 2. Probar el dominio

1. Abre tu navegador
2. Ve a: **https://bingoyrifajym.com**
3. Deberías ver tu aplicación sin errores

### 3. Probar login con Google

1. En tu aplicación, haz clic en **"Iniciar sesión con Google"**
2. Debería funcionar sin el error `redirect_uri_mismatch`

### 4. Verificar en Sentry

1. Ve a tu dashboard de Sentry
2. El error `DisallowedHost` debería desaparecer
3. Si aún aparece, espera unos minutos más (puede tardar en actualizarse)

---

## 📋 CHECKLIST COMPLETO

Marca cada paso cuando lo completes:

- [ ] **ALLOWED_HOSTS** actualizado en Railway con `bingoyrifajym.com`
- [ ] **CSRF_TRUSTED_ORIGINS** actualizado en Railway con `https://bingoyrifajym.com`
- [ ] **Google OAuth** actualizado con las nuevas URLs de callback
- [ ] **Facebook OAuth** actualizado (si lo usas)
- [ ] Esperé 2-3 minutos para que Railway reinicie
- [ ] Probé acceder a `https://bingoyrifajym.com` - funciona ✅
- [ ] Probé login con Google - funciona ✅
- [ ] Verifiqué en Sentry - no hay más errores ✅

---

## 🚨 SI AÚN NO FUNCIONA

### Problema: ALLOWED_HOSTS no se actualiza

**Solución:**
1. Verifica que guardaste correctamente en Railway
2. Ve a Railway → Tu proyecto → Logs
3. Busca mensajes de error
4. Reinicia manualmente: Railway → Tu servicio → Settings → Restart

### Problema: Google sigue dando error

**Solución:**
1. Verifica que las URLs en Google Console sean exactamente:
   - `https://bingoyrifajym.com/accounts/google/login/callback/`
   - (Con https://, sin espacios, con la barra final /)
2. Espera 5-10 minutos (Google puede tardar en actualizar)
3. Prueba en modo incógnito (para limpiar cookies)

### Problema: Sentry sigue mostrando errores

**Solución:**
1. Los errores antiguos pueden seguir apareciendo
2. Espera a que lleguen nuevos eventos
3. Si después de 10 minutos siguen apareciendo, verifica que ALLOWED_HOSTS esté correcto

---

## 📝 RESUMEN DE VALORES CORRECTOS

### En Railway Variables:

**ALLOWED_HOSTS:**
```
web-production-2d504.up.railway.app,bingoyrifajym.com,www.bingoyrifajym.com
```

**CSRF_TRUSTED_ORIGINS:**
```
https://web-production-2d504.up.railway.app,https://bingoyrifajym.com,https://www.bingoyrifajym.com
```

### En Google Console:

**Authorized redirect URIs:**
```
https://web-production-2d504.up.railway.app/accounts/google/login/callback/
https://bingoyrifajym.com/accounts/google/login/callback/
https://www.bingoyrifajym.com/accounts/google/login/callback/
```

---

## ✅ ¡LISTO!

Después de hacer estos cambios, tu aplicación debería funcionar correctamente con:
- ✅ Tu dominio personalizado `bingoyrifajym.com`
- ✅ Login con Google funcionando
- ✅ Sin errores de DisallowedHost

**Tiempo estimado:** 5-10 minutos

---

**Última actualización:** Diciembre 2025





