# 🌐 GUÍA SIMPLE: CONECTAR TU DOMINIO `bingoyrifajym.com` CON RAILWAY

## 👋 ¡Hola! Esta guía es para principiantes, paso a paso

Tu dominio: **bingoyrifajym.com**  
Tu aplicación está en: **Railway**

---

## 📍 ¿DÓNDE ESTÁS AHORA?

Estás en la página de Namecheap que dice "Próximos pasos" con 3 opciones:
- ⚠️ **NO hagas clic** en "Configura un sitio web de WordPress"
- ⚠️ **NO hagas clic** en "Redirige tu dominio"
- ✅ **SÍ necesitas** "Configura tu DNS" (pero lo haremos paso a paso)

**Por ahora, cierra esa página o ignórala. Vamos a hacerlo desde cero.**

---

## 🎯 PASO 1: IR A RAILWAY Y AGREGAR TU DOMINIO

### 1.1. Abre Railway en tu navegador

1. Ve a: **https://railway.app/**
2. Inicia sesión con tu cuenta
3. Busca tu proyecto (el que tiene tu aplicación de bingo)

### 1.2. Encuentra la sección de Dominios

1. Haz clic en tu **servicio web** (normalmente se llama algo como "web" o tiene el nombre de tu app)
2. Busca la pestaña **"Settings"** (Configuración) y haz clic
3. Desplázate hacia abajo hasta encontrar **"Domains"** (Dominios)

### 1.3. Agrega tu dominio

1. Verás un botón que dice **"Custom Domain"** o **"Add Domain"** o **"Generate Domain"**
2. Haz clic en ese botón
3. Te pedirá que ingreses tu dominio
4. Escribe: **bingoyrifajym.com** (sin www, sin http, solo el nombre)
5. Haz clic en **"Add"** o **"Generate"**

### 1.4. ¡IMPORTANTE! Copia la información que Railway te da

Después de agregar el dominio, Railway te mostrará algo como esto:

```
Para configurar tu dominio, agrega este registro DNS:

Tipo: CNAME
Host: www
Valor: xxxxx.up.railway.app
```

**⚠️ COPIA ESTA INFORMACIÓN** - La necesitarás en el siguiente paso.

**Ejemplo de lo que verás:**
- Tipo: **CNAME** (o puede ser A)
- Host: **www** (o puede ser @)
- Valor: algo como **xxxxx.up.railway.app** (este será diferente para ti)

**📝 Anota esto en un papel o cópialo en un documento de texto.**

---

## 🎯 PASO 2: CONFIGURAR DNS EN NAMECHEAP

### 2.1. Volver a Namecheap

1. Ve a: **https://www.namecheap.com/**
2. Inicia sesión
3. En el menú de la izquierda, busca **"Domain List"** (Lista de dominios)
4. Haz clic en **"Domain List"**

### 2.2. Encontrar tu dominio

1. Verás una lista con tu dominio: **bingoyrifajym.com**
2. Al lado de tu dominio, verás un botón que dice **"Manage"** (Administrar)
3. Haz clic en **"Manage"**

### 2.3. Ir a la configuración DNS

1. En la página de gestión de tu dominio, busca una pestaña o sección que diga **"Advanced DNS"** o **"DNS"**
2. Haz clic en **"Advanced DNS"** (DNS Avanzado)

### 2.4. Ver los registros actuales

Verás una tabla con registros DNS. Puede estar vacía o tener algunos registros. **No te preocupes**, vamos a agregar los nuevos.

### 2.5. Agregar el registro DNS de Railway

**IMPORTANTE:** Usa la información que copiaste de Railway en el Paso 1.4.

#### Si Railway te dio un registro CNAME:

1. Busca un botón que diga **"Add New Record"** o **"Add Record"** o un símbolo **"+"**
2. Haz clic en ese botón
3. Se abrirá un formulario. Completa así:
   - **Tipo:** Selecciona **CNAME Record** (o solo CNAME)
   - **Host:** Escribe **www** (o lo que Railway te dijo, puede ser @)
   - **Value** o **Target** o **Points to:** Pega el valor que Railway te dio (algo como `xxxxx.up.railway.app`)
   - **TTL:** Déjalo como está (normalmente "Automatic" o "30 min")
4. Busca un botón **"Save"** o un **checkmark (✓)** y haz clic para guardar

#### Si Railway te dio un registro A:

1. Haz clic en **"Add New Record"**
2. Completa así:
   - **Tipo:** Selecciona **A Record**
   - **Host:** Escribe **@** (para el dominio principal) o **www** (si Railway lo pidió)
   - **Value** o **IP Address:** Pega la dirección IP que Railway te dio
   - **TTL:** Déjalo como está
3. Guarda

### 2.6. Agregar también el dominio sin www (opcional pero recomendado)

Si agregaste el registro para `www`, también deberías agregar uno para el dominio principal (sin www):

1. Haz clic en **"Add New Record"** otra vez
2. Completa igual que antes, pero esta vez:
   - **Host:** Escribe **@** (esto significa el dominio principal sin www)
   - **Value:** El mismo valor que usaste antes
3. Guarda

**⚠️ NOTA:** Si Namecheap no te deja usar CNAME con @, usa un registro **ALIAS** o **ANAME** en su lugar.

### 2.7. Verificar que se guardó

Después de guardar, deberías ver tu nuevo registro en la lista. Si lo ves, ¡perfecto! Los cambios se guardan automáticamente.

---

## 🎯 PASO 3: ACTUALIZAR CONFIGURACIÓN EN RAILWAY

Ahora necesitas decirle a tu aplicación Django que acepte tu dominio personalizado.

### 3.1. Ir a Variables de Entorno en Railway

1. En Railway, en tu proyecto
2. Busca la pestaña o sección **"Variables"** (puede tener un ícono de engranaje ⚙️)
3. Haz clic en **"Variables"**

### 3.2. Actualizar ALLOWED_HOSTS

1. Busca una variable llamada **ALLOWED_HOSTS**
2. Si existe, haz clic para editarla
3. Si NO existe, haz clic en **"New Variable"** o **"Add Variable"**
4. Completa así:
   - **Name:** `ALLOWED_HOSTS`
   - **Value:** `bingoyrifajym.com,www.bingoyrifajym.com`
   
   (Si ya tenías un dominio de Railway, agrégalo también separado por comas, ejemplo: `tu-app.railway.app,bingoyrifajym.com,www.bingoyrifajym.com`)
5. Guarda

### 3.3. Actualizar CSRF_TRUSTED_ORIGINS

1. Busca una variable llamada **CSRF_TRUSTED_ORIGINS**
2. Si existe, edítala. Si no, créala
3. Completa así:
   - **Name:** `CSRF_TRUSTED_ORIGINS`
   - **Value:** `https://bingoyrifajym.com,https://www.bingoyrifajym.com`
   
   (Si ya tenías un dominio de Railway, agrégalo también: `https://tu-app.railway.app,https://bingoyrifajym.com,https://www.bingoyrifajym.com`)
4. Guarda

---

## 🎯 PASO 4: ESPERAR (Esto es importante)

### 4.1. ¿Qué está pasando?

Después de configurar los DNS, los cambios necesitan "propagarse" por internet. Esto significa que todos los servidores del mundo necesitan saber que tu dominio ahora apunta a Railway.

**Esto puede tardar:**
- Mínimo: 15-30 minutos
- Normal: 1-2 horas
- Máximo: 24-48 horas (raro)

### 4.2. ¿Cómo saber si ya funcionó?

**Opción 1: Verificar en Railway**
1. Ve a Railway → Tu proyecto → Settings → Domains
2. Verás el estado de tu dominio:
   - 🟡 **Pending** = Aún esperando
   - 🟢 **Active** = ¡Listo! Ya funciona
   - 🔴 **Error** = Hay un problema

**Opción 2: Verificar en el navegador**
1. Espera al menos 30 minutos
2. Abre tu navegador
3. Ve a: **https://bingoyrifajym.com**
4. Si ves tu aplicación, ¡funcionó! 🎉
5. Si ves un error o "This site can't be reached", espera más tiempo

**Opción 3: Verificar con herramientas online**
1. Ve a: **https://www.whatsmydns.net/**
2. Ingresa: `bingoyrifajym.com`
3. Selecciona el tipo: **CNAME** (o A, según lo que configuraste)
4. Verifica si aparece el valor de Railway en diferentes lugares del mundo

---

## ✅ CHECKLIST - ¿QUÉ YA HICISTE?

Marca cada paso cuando lo completes:

- [ ] **Paso 1:** Agregué el dominio `bingoyrifajym.com` en Railway
- [ ] **Paso 1:** Copié la información DNS que Railway me dio
- [ ] **Paso 2:** Fui a Namecheap → Domain List → Manage
- [ ] **Paso 2:** Fui a Advanced DNS
- [ ] **Paso 2:** Agregué el registro DNS (CNAME o A) con la información de Railway
- [ ] **Paso 2:** Guardé el registro
- [ ] **Paso 3:** Actualicé `ALLOWED_HOSTS` en Railway con `bingoyrifajym.com,www.bingoyrifajym.com`
- [ ] **Paso 3:** Actualicé `CSRF_TRUSTED_ORIGINS` en Railway con `https://bingoyrifajym.com,https://www.bingoyrifajym.com`
- [ ] **Paso 4:** Esperé al menos 30 minutos
- [ ] **Paso 4:** Verifiqué en Railway que el dominio esté "Active"
- [ ] **Paso 4:** Probé abrir `https://bingoyrifajym.com` en el navegador
- [ ] **¡Funciona!** 🎉

---

## 🚨 PROBLEMAS COMUNES

### "No veo la opción de agregar dominio en Railway"

**Solución:**
- Asegúrate de estar en el servicio web correcto (no en la base de datos)
- Busca en la pestaña "Settings" o "Configuración"
- Si no la encuentras, Railway puede estar usando una versión diferente. Busca "Custom Domain" en el menú principal del proyecto

---

### "Namecheap no me deja agregar el registro"

**Solución:**
- Verifica que estés en "Advanced DNS" (no en "Basic DNS")
- Asegúrate de copiar exactamente el valor que Railway te dio (sin espacios extra)
- Si usas `@` y no funciona con CNAME, intenta usar ALIAS o ANAME

---

### "El dominio sigue en 'Pending' después de 2 horas"

**Solución:**
1. Verifica que los registros DNS en Namecheap sean correctos
2. Usa https://www.whatsmydns.net/ para ver si los cambios se propagaron
3. Verifica que el valor en Namecheap coincida exactamente con lo que Railway te pidió

---

### "Veo mi aplicación pero sin el candado verde (HTTPS)"

**Solución:**
- Espera 10-15 minutos más. Railway genera el certificado SSL automáticamente
- Verifica en Railway que el dominio esté marcado como "Active"
- Si después de 30 minutos no funciona, verifica la configuración del dominio en Railway

---

### "Error: Invalid HTTP_HOST header"

**Solución:**
- Verifica que `ALLOWED_HOSTS` incluya tu dominio
- Debe ser: `bingoyrifajym.com,www.bingoyrifajym.com`
- Guarda los cambios y espera unos minutos

---

## 📞 ¿NECESITAS AYUDA?

Si algo no funciona después de seguir todos los pasos:

1. **Verifica los logs de Railway:**
   - Ve a Railway → Tu proyecto → Logs
   - Busca mensajes de error

2. **Verifica el estado del dominio:**
   - Railway → Settings → Domains
   - Revisa si hay mensajes de error

3. **Verifica los registros DNS:**
   - Namecheap → Advanced DNS
   - Compara con lo que Railway te pidió

---

## 🎉 ¡FELICIDADES!

Una vez que todo esté configurado, tu aplicación estará disponible en:
- **https://bingoyrifajym.com**
- **https://www.bingoyrifajym.com**

¡Tu dominio personalizado estará funcionando! 🚀

---

**Última actualización:** Diciembre 2025  
**Dominio configurado:** bingoyrifajym.com





