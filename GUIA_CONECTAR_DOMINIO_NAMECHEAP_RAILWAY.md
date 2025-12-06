# 🌐 GUÍA COMPLETA: CONECTAR DOMINIO DE NAMECHEAP CON RAILWAY

## 📋 RESUMEN RÁPIDO

Esta guía te explica paso a paso cómo conectar tu dominio comprado en Namecheap con tu aplicación desplegada en Railway.

**Tiempo estimado:** 15-30 minutos  
**Propagación DNS:** 1-48 horas (normalmente 1-2 horas)

---

## 🎯 PASO 1: CONFIGURAR EL DOMINIO EN RAILWAY

### 1.1. Acceder a Railway

1. Ve a https://railway.app/
2. Inicia sesión en tu cuenta
3. Selecciona tu proyecto (el que tiene tu aplicación de bingo)

### 1.2. Agregar dominio personalizado

1. En tu proyecto, haz clic en tu **servicio web** (el que ejecuta tu aplicación Django)
2. Ve a la pestaña **"Settings"** (Configuración)
3. Desplázate hasta la sección **"Domains"** (Dominios)
4. Haz clic en **"Custom Domain"** o **"Add Domain"**
5. Ingresa tu dominio (por ejemplo: `tudominio.com` o `www.tudominio.com`)
6. Haz clic en **"Add"** o **"Generate Domain"**

### 1.3. Obtener los registros DNS

Después de agregar el dominio, Railway te mostrará los registros DNS que necesitas configurar. **¡IMPORTANTE! Copia estos valores**, los necesitarás en Namecheap.

Railway te dará algo como esto:

```
Tipo: CNAME
Nombre: www (o @)
Valor: xxxxx.up.railway.app
```

O también puede ser:

```
Tipo: A
Nombre: @
Valor: [IP address]
```

**⚠️ NOTA:** Railway puede usar diferentes métodos. Lo más común es usar un registro **CNAME** o **ALIAS**.

---

## 🎯 PASO 2: CONFIGURAR DNS EN NAMECHEAP

### 2.1. Acceder a Namecheap

1. Ve a https://www.namecheap.com/
2. Inicia sesión en tu cuenta
3. Ve a **"Domain List"** (Lista de dominios) en el menú lateral
4. Haz clic en **"Manage"** junto a tu dominio

### 2.2. Ir a configuración DNS

1. En la página de gestión de tu dominio, busca la sección **"Advanced DNS"** o **"DNS"**
2. Haz clic en **"Advanced DNS"** (DNS Avanzado)

### 2.3. Agregar registros DNS

Necesitas agregar los registros que Railway te proporcionó. Hay dos escenarios comunes:

#### **Escenario A: Railway usa CNAME (más común)**

Si Railway te dio un registro CNAME:

1. En la sección **"Host Records"** o **"Records"**, haz clic en **"Add New Record"**
2. Selecciona el tipo: **CNAME Record**
3. **Host:** `www` (si quieres www.tudominio.com) o `@` (si quieres tudominio.com)
4. **Value/Target:** Pega el valor que Railway te dio (algo como `xxxxx.up.railway.app`)
5. **TTL:** Deja el valor por defecto (normalmente "Automatic" o "30 min")
6. Haz clic en el **checkmark (✓)** para guardar

**Para el dominio raíz (@):**

Si Railway también requiere configurar el dominio sin www (tudominio.com):

1. Agrega otro registro CNAME:
   - **Host:** `@`
   - **Value/Target:** El mismo valor de Railway
   - Guarda

**⚠️ IMPORTANTE:** Algunos proveedores DNS no permiten CNAME en el dominio raíz (@). Si Namecheap no te permite esto, usa un registro **ALIAS** o **ANAME** en su lugar.

#### **Escenario B: Railway usa registro A (menos común)**

Si Railway te dio una dirección IP:

1. Selecciona el tipo: **A Record**
2. **Host:** `@` (para tudominio.com) o `www` (para www.tudominio.com)
3. **Value:** Pega la dirección IP que Railway te dio
4. **TTL:** Deja el valor por defecto
5. Guarda

### 2.4. Verificar registros existentes

**⚠️ IMPORTANTE:** Antes de agregar nuevos registros, revisa si ya existen registros que puedan causar conflictos:

- Si hay registros **A** o **CNAME** antiguos para `@` o `www`, puedes eliminarlos o modificarlos
- Si no estás seguro, puedes dejarlos y agregar los nuevos. Railway te dirá si hay conflictos

### 2.5. Guardar cambios

Después de agregar todos los registros:
1. Verifica que todos los registros estén guardados correctamente
2. Los cambios se aplican automáticamente (no hay botón "Save" adicional en Namecheap)

---

## 🎯 PASO 3: ACTUALIZAR VARIABLES DE ENTORNO EN RAILWAY

Una vez que hayas configurado el DNS, necesitas actualizar las variables de entorno en Railway para que Django acepte tu dominio personalizado.

### 3.1. Actualizar ALLOWED_HOSTS

**Opción A: Desde el Dashboard de Railway**

1. En tu proyecto de Railway, ve a **"Variables"** (ícono de engranaje)
2. Busca la variable `ALLOWED_HOSTS`
3. Si existe, haz clic para editarla
4. Si no existe, haz clic en **"New Variable"**
5. **Name:** `ALLOWED_HOSTS`
6. **Value:** Agrega tu dominio (puedes incluir ambos con y sin www):
   ```
   tudominio.com,www.tudominio.com
   ```
   O si ya tenías el dominio de Railway, agrégalo también:
   ```
   tudominio.railway.app,tudominio.com,www.tudominio.com
   ```
7. Haz clic en **"Add"** o **"Update"**

**Opción B: Desde la terminal (Railway CLI)**

```bash
# Si solo quieres tu dominio personalizado:
railway variables set ALLOWED_HOSTS="tudominio.com,www.tudominio.com"

# Si quieres incluir también el dominio de Railway:
railway variables set ALLOWED_HOSTS="tudominio.railway.app,tudominio.com,www.tudominio.com"
```

### 3.2. Actualizar CSRF_TRUSTED_ORIGINS

**Opción A: Desde el Dashboard**

1. Busca la variable `CSRF_TRUSTED_ORIGINS`
2. Edítala o créala si no existe
3. **Name:** `CSRF_TRUSTED_ORIGINS`
4. **Value:** Agrega tu dominio con `https://`:
   ```
   https://tudominio.com,https://www.tudominio.com
   ```
   O si ya tenías el dominio de Railway:
   ```
   https://tudominio.railway.app,https://tudominio.com,https://www.tudominio.com
   ```
5. Guarda

**Opción B: Desde la terminal**

```bash
# Solo tu dominio personalizado:
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.com,https://www.tudominio.com"

# Incluyendo dominio de Railway:
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app,https://tudominio.com,https://www.tudominio.com"
```

---

## 🎯 PASO 4: ESPERAR PROPAGACIÓN DNS

### 4.1. ¿Qué es la propagación DNS?

Después de configurar los registros DNS, los cambios necesitan propagarse por todo el internet. Esto puede tardar desde unos minutos hasta 48 horas, pero normalmente toma **1-2 horas**.

### 4.2. Verificar el estado

Puedes verificar si los cambios ya se han propagado usando estas herramientas:

1. **What's My DNS:** https://www.whatsmydns.net/
   - Ingresa tu dominio
   - Selecciona el tipo de registro (CNAME o A)
   - Verifica en diferentes ubicaciones del mundo

2. **DNS Checker:** https://dnschecker.org/
   - Similar a la anterior

3. **Desde la terminal (Windows PowerShell):**
   ```powershell
   # Para verificar CNAME:
   nslookup -type=CNAME www.tudominio.com
   
   # Para verificar A:
   nslookup tudominio.com
   ```

### 4.3. Verificar en Railway

1. Ve a tu proyecto en Railway
2. Ve a **Settings** → **Domains**
3. Railway mostrará el estado de tu dominio:
   - 🟡 **Pending** = Aún propagándose
   - 🟢 **Active** = ¡Listo! Tu dominio está funcionando
   - 🔴 **Error** = Hay un problema con la configuración

---

## 🎯 PASO 5: VERIFICAR QUE TODO FUNCIONA

### 5.1. Probar acceso al dominio

Una vez que Railway muestre el dominio como **"Active"**:

1. Abre tu navegador
2. Ve a `https://tudominio.com` o `https://www.tudominio.com`
3. Deberías ver tu aplicación funcionando

### 5.2. Verificar HTTPS

Railway automáticamente proporciona certificados SSL (HTTPS) para tu dominio. Si ves un candado 🔒 en la barra de direcciones, ¡todo está bien!

Si ves una advertencia de seguridad:
- Espera unos minutos más (el certificado SSL puede tardar en generarse)
- Verifica que el dominio esté correctamente configurado en Railway

### 5.3. Probar funcionalidades

Asegúrate de probar:
- ✅ Login de usuarios
- ✅ Crear cuenta
- ✅ Navegación general
- ✅ Si tienes login social (Google/Facebook), verifica que funcione

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "Domain not found" o "This site can't be reached"

**Causa:** Los registros DNS aún no se han propagado o están mal configurados.

**Solución:**
1. Verifica que los registros DNS en Namecheap sean correctos
2. Espera más tiempo (puede tardar hasta 48 horas)
3. Verifica con las herramientas de DNS mencionadas arriba
4. Asegúrate de que el dominio esté agregado correctamente en Railway

---

### Problema 2: "Invalid HTTP_HOST header" en Railway

**Causa:** La variable `ALLOWED_HOSTS` no incluye tu dominio personalizado.

**Solución:**
```bash
# Verificar qué dominios están permitidos:
railway variables get ALLOWED_HOSTS

# Actualizar para incluir tu dominio:
railway variables set ALLOWED_HOSTS="tudominio.railway.app,tudominio.com,www.tudominio.com"
```

---

### Problema 3: "Forbidden (CSRF token missing or incorrect)"

**Causa:** `CSRF_TRUSTED_ORIGINS` no incluye tu dominio.

**Solución:**
```bash
# Actualizar CSRF_TRUSTED_ORIGINS:
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app,https://tudominio.com,https://www.tudominio.com"
```

---

### Problema 4: El dominio muestra "Pending" por mucho tiempo

**Causa:** Los registros DNS no están configurados correctamente en Namecheap.

**Solución:**
1. Verifica que los registros en Namecheap coincidan exactamente con lo que Railway te dio
2. Asegúrate de que no haya espacios extra o caracteres incorrectos
3. Verifica que el tipo de registro sea correcto (CNAME vs A)
4. Si usas `@` para el dominio raíz y no funciona, intenta usar un registro ALIAS/ANAME

---

### Problema 5: El dominio funciona pero sin HTTPS (sin candado)

**Causa:** Railway está generando el certificado SSL, puede tardar unos minutos.

**Solución:**
1. Espera 10-15 minutos
2. Verifica en Railway que el dominio esté marcado como "Active"
3. Si después de 30 minutos aún no funciona, verifica que el dominio esté correctamente configurado en Railway

---

## 📋 CHECKLIST COMPLETO

Usa este checklist para asegurarte de que todo esté configurado:

- [ ] **Paso 1:** Dominio agregado en Railway
- [ ] **Paso 1:** Registros DNS copiados de Railway
- [ ] **Paso 2:** Registros DNS agregados en Namecheap
- [ ] **Paso 2:** Registros guardados correctamente
- [ ] **Paso 3:** Variable `ALLOWED_HOSTS` actualizada en Railway
- [ ] **Paso 3:** Variable `CSRF_TRUSTED_ORIGINS` actualizada en Railway
- [ ] **Paso 4:** Esperado tiempo de propagación (1-2 horas)
- [ ] **Paso 4:** Verificado estado en Railway (debe mostrar "Active")
- [ ] **Paso 5:** Dominio accesible en el navegador
- [ ] **Paso 5:** HTTPS funcionando (candado verde)
- [ ] **Paso 5:** Aplicación funcionando correctamente

---

## 🎯 RESUMEN RÁPIDO (TL;DR)

1. **Railway:** Agrega tu dominio en Settings → Domains
2. **Copia** los registros DNS que Railway te da
3. **Namecheap:** Ve a Advanced DNS y agrega los registros (CNAME o A)
4. **Railway:** Actualiza `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` con tu dominio
5. **Espera** 1-2 horas para la propagación DNS
6. **Verifica** que el dominio funcione en el navegador

---

## 📞 ¿NECESITAS AYUDA?

Si después de seguir todos los pasos algo no funciona:

1. **Verifica los logs de Railway:**
   ```bash
   railway logs
   ```

2. **Verifica el estado del dominio en Railway:**
   - Ve a Settings → Domains
   - Revisa si hay mensajes de error

3. **Verifica los registros DNS:**
   - Usa https://www.whatsmydns.net/ para verificar propagación
   - Compara con lo que Railway te pidió

4. **Verifica las variables de entorno:**
   ```bash
   railway variables
   ```

---

## ✅ ¡LISTO!

Una vez que todo esté configurado y propagado, tu aplicación estará accesible en tu dominio personalizado. ¡Felicidades! 🎉

---

**Última actualización:** Diciembre 2025





