# 🚀 GUÍA PASO A PASO: ASIGNAR DOMINIO A UNA FRANQUICIA

## 📋 Resumen

Esta guía te explica cómo asignar un dominio personalizado (ej: `mi-franquicia.com`) a una franquicia en el sistema.

---

## ✅ PASO 1: Asignar el Dominio en el Admin de Django

### 1.1. Acceder al Admin
1. Ve a tu aplicación: `https://tu-app.railway.app/admin/` (o tu URL)
2. Inicia sesión como **superadmin**

### 1.2. Ir a Franquicias
1. En el menú izquierdo, busca **"Franquicias"**
2. Haz clic en **"Franquicias"**

### 1.3. Seleccionar la Franquicia
1. Busca la franquicia a la que quieres asignar el dominio
2. Haz clic en el nombre de la franquicia para editarla

### 1.4. Agregar el Dominio
1. Desplázate hasta la sección **"🌐 Dominio Personalizado"**
2. En el campo **"Dominio Personalizado"**, ingresa tu dominio:
   ```
   mi-franquicia.com
   ```
   **IMPORTANTE:**
   - ❌ NO incluyas `http://` o `https://`
   - ❌ NO incluyas `www.` (se quita automáticamente)
   - ✅ Solo el dominio: `mi-franquicia.com`

3. Haz clic en **"Guardar"** (botón abajo a la derecha)

### 1.5. Verificar
- Si el dominio ya está en uso por otra franquicia, verás una advertencia
- Si todo está bien, verás el mensaje de éxito

---

## ✅ PASO 2: Configurar el Dominio en Railway

### 2.1. Ir a Railway
1. Ve a https://railway.app/
2. Inicia sesión
3. Selecciona tu proyecto

### 2.2. Agregar Dominio Personalizado
1. En tu proyecto, haz clic en tu **servicio web** (no en la base de datos)
2. Ve a la pestaña **"Settings"** (Configuración)
3. Desplázate hasta la sección **"Domains"** (Dominios)
4. Haz clic en **"Custom Domain"** o **"Add Domain"** o **"Generate Domain"**

### 2.3. Ingresar el Dominio
1. En el campo que aparece, ingresa tu dominio:
   ```
   mi-franquicia.com
   ```
2. Haz clic en **"Add"** o **"Generate"**

### 2.4. Copiar los Registros DNS
Railway te mostrará algo como esto:
```
Para configurar tu dominio, agrega este registro DNS:

Tipo: CNAME
Host: @
Value: tu-app.railway.app
```
**⚠️ IMPORTANTE: Copia estos valores**, los necesitarás en el siguiente paso.

---

## ✅ PASO 3: Configurar DNS en tu Proveedor de Dominios

### 3.1. Acceder a tu Proveedor
**Ejemplo con Namecheap** (similar en otros proveedores):

1. Ve a https://www.namecheap.com/
2. Inicia sesión
3. Ve a **"Domain List"** (Lista de dominios) en el menú izquierdo
4. Haz clic en **"Manage"** junto a tu dominio

### 3.2. Ir a Advanced DNS
1. En la página de gestión de tu dominio, busca la pestaña **"Advanced DNS"** o **"DNS"**
2. Haz clic en ella

### 3.3. Agregar Registro CNAME
1. Busca la sección **"Host Records"** o **"DNS Records"**
2. Haz clic en **"Add New Record"** o el botón **"+"**
3. Configura el registro:
   - **Tipo:** Selecciona **CNAME Record**
   - **Host:** Escribe **@** (para el dominio principal) o **www** (si Railway lo pidió)
   - **Value:** Pega el valor que Railway te dio (ej: `tu-app.railway.app`)
   - **TTL:** Deja en **Automatic** o **30 min**

4. Haz clic en **"Save"** o el ícono de guardar (✓)

### 3.4. Agregar también www (Opcional pero Recomendado)
Si quieres que funcione tanto `mi-franquicia.com` como `www.mi-franquicia.com`:

1. Agrega otro registro CNAME:
   - **Tipo:** CNAME Record
   - **Host:** `www`
   - **Value:** El mismo valor de Railway (ej: `tu-app.railway.app`)
   - **TTL:** Automatic

2. Guarda

---

## ✅ PASO 4: Actualizar ALLOWED_HOSTS en Railway

**IMPORTANTE:** Debes agregar el dominio a `ALLOWED_HOSTS` para que Django lo acepte.

### 4.1. Ver ALLOWED_HOSTS Actual
```bash
railway variables get ALLOWED_HOSTS
```

### 4.2. Agregar el Nuevo Dominio
```bash
# Reemplaza con tus dominios reales (mantén los existentes)
railway variables set ALLOWED_HOSTS="tu-app.railway.app,mi-franquicia.com,www.mi-franquicia.com"
```

**Ejemplo:**
Si ya tenías `tu-app.railway.app`, ahora será:
```
tu-app.railway.app,mi-franquicia.com,www.mi-franquicia.com
```

**Nota:** Separa los dominios con comas, sin espacios.

---

## ✅ PASO 5: Actualizar CSRF_TRUSTED_ORIGINS

También debes agregar el dominio a `CSRF_TRUSTED_ORIGINS`:

### 5.1. Ver CSRF_TRUSTED_ORIGINS Actual
```bash
railway variables get CSRF_TRUSTED_ORIGINS
```

### 5.2. Agregar el Nuevo Dominio con https://
```bash
# Reemplaza con tus dominios reales (mantén los existentes)
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app,https://mi-franquicia.com,https://www.mi-franquicia.com"
```

**Ejemplo:**
Si ya tenías `https://tu-app.railway.app`, ahora será:
```
https://tu-app.railway.app,https://mi-franquicia.com,https://www.mi-franquicia.com
```

---

## ✅ PASO 6: Esperar Propagación DNS

Los cambios de DNS pueden tardar:
- **Mínimo:** 5-10 minutos
- **Usual:** 15-30 minutos
- **Máximo:** 24 horas (raro)

### 6.1. Verificar DNS
Mientras esperas, puedes verificar si el DNS ya se propagó:

**En Windows (PowerShell):**
```powershell
nslookup mi-franquicia.com
```

**En Linux/Mac:**
```bash
dig mi-franquicia.com
```

Debería mostrar el valor de Railway (ej: `tu-app.railway.app`)

---

## ✅ PASO 7: Verificar en Railway

1. Ve a Railway → Tu proyecto → Settings → Domains
2. Verifica el estado de tu dominio:
   - 🟡 **Pending** = Aún propagándose (espera más)
   - 🟢 **Active** = ¡Listo! El dominio está funcionando

---

## ✅ PASO 8: Probar el Dominio

1. Espera a que Railway muestre el dominio como **"Active"**
2. Abre tu navegador
3. Ve a: `https://mi-franquicia.com`
4. Deberías ver la aplicación con la imagen de la franquicia automáticamente

---

## 📝 Ejemplo Completo

Supongamos que tienes:
- **Dominio:** `bingosanjuan.com`
- **Franquicia:** "Bingo San Juan"
- **Railway app:** `tu-app.railway.app`

### Paso 1: Admin Django
- Franquicia: "Bingo San Juan"
- Dominio Personalizado: `bingosanjuan.com`
- Guardar

### Paso 2: Railway
- Settings → Domains → Add Domain
- Dominio: `bingosanjuan.com`
- Copiar: `tu-app.railway.app`

### Paso 3: Namecheap (o tu proveedor)
- Advanced DNS → Add Record
- Tipo: CNAME
- Host: `@`
- Value: `tu-app.railway.app`

### Paso 4: Railway CLI
```bash
railway variables set ALLOWED_HOSTS="tu-app.railway.app,bingosanjuan.com,www.bingosanjuan.com"
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app,https://bingosanjuan.com,https://www.bingosanjuan.com"
```

### Paso 5: Esperar y Probar
- Esperar 15-30 minutos
- Verificar en Railway que esté "Active"
- Probar: `https://bingosanjuan.com`

---

## ⚠️ Problemas Comunes

### "El dominio sigue en Pending"
- Espera más tiempo (hasta 30 minutos)
- Verifica que el DNS esté configurado correctamente
- Verifica que el registro CNAME tenga el valor correcto

### "Invalid HTTP_HOST header"
- Verifica que `ALLOWED_HOSTS` incluya tu dominio
- Ejecuta: `railway variables get ALLOWED_HOSTS`

### "Forbidden (CSRF token invalid)"
- Verifica que `CSRF_TRUSTED_ORIGINS` incluya tu dominio con `https://`
- Ejecuta: `railway variables get CSRF_TRUSTED_ORIGINS`

### "El dominio no muestra la imagen de la franquicia"
- Verifica que el dominio esté correctamente asignado en el admin
- Verifica que la franquicia tenga una imagen configurada
- Limpia la caché del navegador

---

## ✅ Checklist Final

- [ ] Dominio asignado en el admin de Django
- [ ] Dominio agregado en Railway (Settings → Domains)
- [ ] DNS configurado en tu proveedor (CNAME apuntando a Railway)
- [ ] `ALLOWED_HOSTS` actualizado en Railway
- [ ] `CSRF_TRUSTED_ORIGINS` actualizado en Railway
- [ ] Esperado propagación DNS (15-30 minutos)
- [ ] Dominio aparece como "Active" en Railway
- [ ] Dominio funciona en el navegador (`https://mi-franquicia.com`)
- [ ] Se muestra la imagen de la franquicia correctamente

---

**¡Listo!** Una vez completados todos los pasos, tu dominio personalizado estará funcionando y los usuarios verán automáticamente el contenido de la franquicia cuando accedan por ese dominio.



