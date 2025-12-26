# 🌐 CONFIGURAR DOMINIO rifasjaj.com

## 📋 Propósito

El dominio `rifasjaj.com` se usa para identificar que los usuarios vienen de la aplicación y no de anuncios publicitarios. Esto permite hacer tracking y análisis del tráfico orgánico vs tráfico pagado.

## ✅ Cambios Realizados en el Código

1. **Agregado a `CSRF_TRUSTED_ORIGINS`** en `settings.py`
2. **Agregado a `ALLOWED_HOSTS`** en `settings.py`
3. **Incluye versión con `www.`** (rifasjaj.com y www.rifasjaj.com)

## 🚀 Configuración en Railway

### Paso 1: Agregar el Dominio en Railway

1. Ve a Railway → Tu proyecto → **Settings** → **Domains**
2. Haz clic en **"Custom Domain"** o **"Add Domain"**
3. Ingresa: `rifasjaj.com`
4. Railway te dará los registros DNS que necesitas configurar

### Paso 2: Configurar DNS

**En tu proveedor de dominios (ej: Namecheap, GoDaddy, etc.):**

1. Ve a la configuración DNS de tu dominio
2. Agrega un registro **CNAME**:
   - **Host:** `@` (para rifasjaj.com) o `www` (para www.rifasjaj.com)
   - **Value:** El valor que Railway te dio (ej: `tu-app.railway.app`)
   - **TTL:** Automatic

**Ejemplo:**
```
Tipo: CNAME
Host: @
Value: tu-app.railway.app
```

### Paso 3: Actualizar ALLOWED_HOSTS en Railway

**IMPORTANTE:** Debes agregar el dominio a `ALLOWED_HOSTS` en Railway:

```bash
# Ver ALLOWED_HOSTS actual
railway variables get ALLOWED_HOSTS

# Agregar rifasjaj.com (mantén los dominios existentes)
railway variables set ALLOWED_HOSTS="tu-app.railway.app,rifasjaj.com,www.rifasjaj.com"
```

**Nota:** Si ya tienes otros dominios, agrégalos también separados por comas.

### Paso 4: Actualizar CSRF_TRUSTED_ORIGINS

También debes agregar el dominio a `CSRF_TRUSTED_ORIGINS`:

```bash
# Ver CSRF_TRUSTED_ORIGINS actual
railway variables get CSRF_TRUSTED_ORIGINS

# Agregar rifasjaj.com (mantén los dominios existentes)
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app,https://rifasjaj.com,https://www.rifasjaj.com"
```

## 🎯 Uso del Dominio

Una vez configurado, puedes usar `rifasjaj.com` para:

1. **Tracking de tráfico orgánico:** Identificar usuarios que vienen directamente de la app
2. **Diferenciar de anuncios:** Saber qué usuarios vienen de publicidad vs orgánico
3. **Analytics:** Medir el rendimiento de la aplicación vs campañas publicitarias
4. **Enlaces en la app:** Usar `rifasjaj.com` en lugar del dominio principal para tracking

## 📝 Ejemplo de Uso

```html
<!-- En lugar de usar el dominio principal -->
<a href="https://tu-app.railway.app/lobby/">Lobby</a>

<!-- Usar rifasjaj.com para tracking -->
<a href="https://rifasjaj.com/lobby/">Lobby</a>
```

## ⚠️ Consideraciones

1. **DNS debe estar configurado:** El dominio debe apuntar correctamente a Railway
2. **Propagación DNS:** Puede tardar hasta 24 horas (usualmente 5-30 minutos)
3. **SSL automático:** Railway proporciona certificados SSL automáticamente
4. **Mismo contenido:** `rifasjaj.com` mostrará el mismo contenido que el dominio principal

## 🔍 Verificación

1. **Verificar DNS:**
   ```bash
   nslookup rifasjaj.com
   ```

2. **Verificar en Railway:**
   - Ve a Settings → Domains
   - Debe aparecer como "Active"

3. **Probar acceso:**
   - Abre `https://rifasjaj.com` en el navegador
   - Debe mostrar la aplicación normalmente

## 📚 Archivos Modificados

- `bingo_project/settings.py`: Agregado dominio a ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS

---

**Fecha de configuración:** 17 de diciembre de 2025
**Dominio:** rifasjaj.com



