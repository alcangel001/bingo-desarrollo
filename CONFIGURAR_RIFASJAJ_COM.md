# 🚀 CONFIGURACIÓN COMPLETA: rifasjaj.com

## 📋 Información del Proyecto

- **Dominio Railway:** `2im38s96.up.railway.app`
- **Dominio Personalizado:** `rifasjaj.com`
- **Puerto:** (el que seleccionaste en Railway)

---

## ✅ PASO 1: Verificar que el Dominio esté en Railway

1. Ve a Railway → Tu proyecto → Settings → Domains
2. Verifica que `rifasjaj.com` aparezca en la lista
3. Si aparece como "Pending", espera unos minutos
4. Railway te debería mostrar algo como:
   ```
   Para configurar tu dominio, agrega este registro DNS:
   
   Tipo: CNAME
   Host: @
   Value: 2im38s96.up.railway.app
   ```

**⚠️ IMPORTANTE:** Copia el valor que Railway te da (puede ser `2im38s96.up.railway.app` o similar).

---

## ✅ PASO 2: Configurar DNS en tu Proveedor de Dominios

### Si usas Namecheap:

1. Ve a https://www.namecheap.com/
2. Inicia sesión
3. Ve a **"Domain List"** → Busca `rifasjaj.com` → Click en **"Manage"**
4. Ve a la pestaña **"Advanced DNS"**
5. Busca la sección **"Host Records"**
6. Haz clic en **"Add New Record"** o el botón **"+"**

**Configuración para el dominio principal:**
- **Tipo:** Selecciona **CNAME Record**
- **Host:** Escribe **@**
- **Value:** Pega `2im38s96.up.railway.app` (o el valor que Railway te dio)
- **TTL:** Deja en **Automatic** o **30 min**
- Haz clic en **"Save"** (✓)

**Configuración para www (opcional pero recomendado):**
- Haz clic en **"Add New Record"** otra vez
- **Tipo:** Selecciona **CNAME Record**
- **Host:** Escribe **www**
- **Value:** Pega `2im38s96.up.railway.app` (mismo valor)
- **TTL:** Deja en **Automatic** o **30 min**
- Haz clic en **"Save"** (✓)

### Si usas otro proveedor (GoDaddy, Google Domains, etc.):

La configuración es similar:
- **Tipo:** CNAME
- **Host/Name:** `@` (para el dominio principal) o `www` (para www)
- **Value/Target:** `2im38s96.up.railway.app`
- **TTL:** 30 minutos o Automatic

---

## ✅ PASO 3: Actualizar ALLOWED_HOSTS en Railway

Abre PowerShell o Terminal y ejecuta:

```bash
# Ver el valor actual
railway variables get ALLOWED_HOSTS

# Agregar rifasjaj.com (mantén los existentes)
railway variables set ALLOWED_HOSTS="2im38s96.up.railway.app,rifasjaj.com,www.rifasjaj.com"
```

**Nota:** Si ya tienes otros dominios, agrégalos también separados por comas:
```bash
railway variables set ALLOWED_HOSTS="2im38s96.up.railway.app,rifasjaj.com,www.rifasjaj.com,otro-dominio.com"
```

---

## ✅ PASO 4: Actualizar CSRF_TRUSTED_ORIGINS en Railway

```bash
# Ver el valor actual
railway variables get CSRF_TRUSTED_ORIGINS

# Agregar rifasjaj.com con https:// (mantén los existentes)
railway variables set CSRF_TRUSTED_ORIGINS="https://2im38s96.up.railway.app,https://rifasjaj.com,https://www.rifasjaj.com"
```

**Nota:** Si ya tienes otros dominios, agrégalos también:
```bash
railway variables set CSRF_TRUSTED_ORIGINS="https://2im38s96.up.railway.app,https://rifasjaj.com,https://www.rifasjaj.com,https://otro-dominio.com"
```

---

## ✅ PASO 5: Asignar el Dominio en el Admin de Django

1. Ve a: `https://2im38s96.up.railway.app/admin/`
2. Inicia sesión como superadmin
3. Ve a **"Franquicias"** en el menú izquierdo
4. Busca la franquicia a la que quieres asignar `rifasjaj.com`
5. Haz clic en la franquicia para editarla
6. Desplázate hasta la sección **"🌐 Dominio Personalizado"**
7. En el campo **"Dominio Personalizado"**, ingresa:
   ```
   rifasjaj.com
   ```
   **IMPORTANTE:** 
   - ❌ NO incluyas `http://` o `https://`
   - ❌ NO incluyas `www.`
   - ✅ Solo: `rifasjaj.com`

8. Haz clic en **"Guardar"**

---

## ✅ PASO 6: Esperar Propagación DNS

Los cambios de DNS pueden tardar:
- **Mínimo:** 5-10 minutos
- **Usual:** 15-30 minutos
- **Máximo:** 24 horas (raro)

### Verificar DNS (mientras esperas):

**En Windows (PowerShell):**
```powershell
nslookup rifasjaj.com
```

Debería mostrar algo como:
```
Name:    rifasjaj.com
Address: [IP de Railway]
Aliases: 2im38s96.up.railway.app
```

**En Linux/Mac:**
```bash
dig rifasjaj.com
```

---

## ✅ PASO 7: Verificar en Railway

1. Ve a Railway → Tu proyecto → Settings → Domains
2. Verifica el estado de `rifasjaj.com`:
   - 🟡 **Pending** = Aún propagándose (espera más)
   - 🟢 **Active** = ¡Listo! El dominio está funcionando

---

## ✅ PASO 8: Probar el Dominio

1. Espera a que Railway muestre el dominio como **"Active"**
2. Abre tu navegador
3. Ve a: `https://rifasjaj.com`
4. Deberías ver la aplicación funcionando

**Si asignaste el dominio a una franquicia:**
- Deberías ver automáticamente la imagen y contenido de esa franquicia
- No necesitas agregar parámetros en la URL

---

## 📝 Comandos Rápidos (Copia y Pega)

```bash
# 1. Ver variables actuales
railway variables get ALLOWED_HOSTS
railway variables set CSRF_TRUSTED_ORIGINS

# 2. Actualizar ALLOWED_HOSTS
railway variables set ALLOWED_HOSTS="2im38s96.up.railway.app,rifasjaj.com,www.rifasjaj.com"

# 3. Actualizar CSRF_TRUSTED_ORIGINS
railway variables set CSRF_TRUSTED_ORIGINS="https://2im38s96.up.railway.app,https://rifasjaj.com,https://www.rifasjaj.com"

# 4. Verificar DNS (PowerShell)
nslookup rifasjaj.com
```

---

## ⚠️ Problemas Comunes

### "El dominio sigue en Pending"
- Espera más tiempo (hasta 30 minutos)
- Verifica que el DNS esté configurado correctamente
- Verifica que el registro CNAME tenga el valor correcto: `2im38s96.up.railway.app`

### "Invalid HTTP_HOST header"
- Verifica que `ALLOWED_HOSTS` incluya `rifasjaj.com`
- Ejecuta: `railway variables get ALLOWED_HOSTS`
- Si no está, ejecuta el comando del Paso 3

### "Forbidden (CSRF token invalid)"
- Verifica que `CSRF_TRUSTED_ORIGINS` incluya `https://rifasjaj.com`
- Ejecuta: `railway variables get CSRF_TRUSTED_ORIGINS`
- Si no está, ejecuta el comando del Paso 4

### "El dominio no muestra la imagen de la franquicia"
- Verifica que el dominio esté asignado en el admin (Paso 5)
- Verifica que la franquicia tenga una imagen configurada
- Limpia la caché del navegador (Ctrl+Shift+R)

---

## ✅ Checklist Final

- [ ] Dominio `rifasjaj.com` agregado en Railway (Settings → Domains)
- [ ] DNS configurado en tu proveedor (CNAME apuntando a `2im38s96.up.railway.app`)
- [ ] `ALLOWED_HOSTS` actualizado en Railway (incluye `rifasjaj.com`)
- [ ] `CSRF_TRUSTED_ORIGINS` actualizado en Railway (incluye `https://rifasjaj.com`)
- [ ] Dominio asignado en el admin de Django (Franquicia → Dominio Personalizado)
- [ ] Esperado propagación DNS (15-30 minutos)
- [ ] Dominio aparece como "Active" en Railway
- [ ] Dominio funciona en el navegador (`https://rifasjaj.com`)

---

**¡Listo!** Una vez completados todos los pasos, `rifasjaj.com` estará funcionando y los usuarios verán automáticamente el contenido de la franquicia cuando accedan por ese dominio.



