# 🚀 PASOS PARA SUBIR A GITHUB Y CONECTAR CON RAILWAY

## ✅ Lo que ya hicimos:
- ✅ Git inicializado
- ✅ Archivos agregados
- ⏳ Falta: Configurar Git y hacer commit

---

## 📋 PASO 1: Configurar Git (Una sola vez)

Abre PowerShell en la carpeta `bingo-desarrollo` y ejecuta:

```powershell
cd "C:\Users\DELL VOSTRO 7500\bingo-desarrollo"
git config user.name "Tu Nombre"
git config user.email "tu-email@ejemplo.com"
```

**Reemplaza:**
- `Tu Nombre` → Tu nombre real o el que quieras usar
- `tu-email@ejemplo.com` → El email de tu cuenta de GitHub

---

## 📋 PASO 2: Hacer Commit

```powershell
git commit -m "Initial commit - Entorno de desarrollo separado"
```

---

## 📋 PASO 3: Crear Repositorio en GitHub

1. Ve a: https://github.com/new
2. **Nombre del repositorio:** `bingo-desarrollo` (o el nombre que prefieras)
3. **Descripción (opcional):** "Entorno de desarrollo - Bingo"
4. **Visibilidad:** 
   - ✅ **Private** (recomendado - solo tú puedes verlo)
   - O Public si quieres
5. **NO marques:**
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Haz clic en **"Create repository"**

---

## 📋 PASO 4: Conectar y Subir Código

GitHub te mostrará comandos. Ejecuta estos (reemplaza TU_USUARIO con tu usuario de GitHub):

```powershell
git branch -M main
git remote add origin https://github.com/TU_USUARIO/bingo-desarrollo.git
git push -u origin main
```

**Si te pide usuario y contraseña:**
- Usuario: Tu usuario de GitHub
- Contraseña: Usa un **Personal Access Token** (no tu contraseña normal)

**Cómo crear Personal Access Token:**
1. Ve a: https://github.com/settings/tokens
2. Click en "Generate new token" → "Generate new token (classic)"
3. Dale un nombre (ej: "Railway Development")
4. Selecciona scope: `repo` (marca la casilla)
5. Click en "Generate token"
6. **Copia el token** (solo se muestra una vez)
7. Úsalo como contraseña cuando Git te la pida

---

## 📋 PASO 5: Conectar con Railway

1. Ve a Railway: https://railway.app
2. Abre tu proyecto nuevo (el que tiene PostgreSQL y Redis)
3. Click en **"+ New"** o **"+ Add Service"**
4. Selecciona **"GitHub Repo"**
5. Selecciona el repositorio `bingo-desarrollo` que acabas de crear
6. Railway detectará automáticamente que es Django

---

## 📋 PASO 6: Configurar Variables de Entorno en Railway

1. En Railway, haz clic en el servicio de tu aplicación (no PostgreSQL ni Redis)
2. Ve a la pestaña **"Variables"**
3. Agrega estas variables:

### Variables Obligatorias:

```
DATABASE_URL=<Copia la URL de tu PostgreSQL>
SECRET_KEY=<Genera una nueva>
DEBUG=True
ALLOWED_HOSTS=*.railway.app
```

### Cómo obtener DATABASE_URL:
1. En Railway, haz clic en tu servicio **PostgreSQL**
2. Ve a la pestaña **"Variables"**
3. Busca `DATABASE_URL`
4. Copia esa URL completa

### Cómo generar SECRET_KEY:
En PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copia el resultado y úsalo como `SECRET_KEY`

### Variables Opcionales (si las necesitas):
Puedes copiar las mismas de producción si quieres probar integraciones:
- `SENDGRID_API_KEY`
- `GOOGLE_CLIENT_ID` / `GOOGLE_SECRET`
- `FACEBOOK_CLIENT_ID` / `FACEBOOK_SECRET`
- `AGORA_APP_ID` / `AGORA_APP_CERTIFICATE`
- `GEMINI_API_KEY`
- `SENTRY_DSN`

---

## 📋 PASO 7: Conectar Base de Datos

1. En Railway, en tu servicio de la aplicación
2. Ve a la pestaña **"Variables"**
3. Busca `DATABASE_URL` (debería estar configurada)
4. Si no está, agrega la URL de tu PostgreSQL

---

## 📋 PASO 8: Ejecutar Migraciones

Railway debería ejecutarlas automáticamente, pero verifica:

1. Ve a la pestaña **"Deployments"**
2. Haz clic en el deployment más reciente
3. Ve a **"Logs"**
4. Busca mensajes como "Applying migrations" o "Operations to perform"

Si no se ejecutaron, en **"Settings"** → **"Run Command"** ejecuta:
```bash
python manage.py migrate
```

---

## 📋 PASO 9: Crear Superusuario

1. En Railway, en tu servicio de la aplicación
2. Ve a **"Settings"** → **"Run Command"** o **"Shell"**
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones para crear el usuario

---

## 📋 PASO 10: Verificar que Funciona

1. En Railway, ve a la pestaña **"Settings"** de tu servicio
2. Busca **"Domains"** o la URL automática
3. Haz clic en la URL (algo como: `tu-proyecto.railway.app`)
4. Deberías ver tu juego funcionando

---

## ✅ VERIFICACIÓN FINAL

**Asegúrate de tener:**
- ✅ Repositorio en GitHub con el código
- ✅ Proyecto en Railway conectado a GitHub
- ✅ PostgreSQL configurado y conectado
- ✅ Variables de entorno configuradas
- ✅ Migraciones ejecutadas
- ✅ Superusuario creado
- ✅ Sitio accesible en Railway

---

## 🔒 SEGURIDAD - CONFIRMACIÓN

**Tu proyecto de producción:**
- ✅ Sigue funcionando normalmente
- ✅ No fue modificado
- ✅ Tiene su propia base de datos
- ✅ Tu rifa activa está segura

**Tu proyecto de desarrollo:**
- ✅ Está completamente separado
- ✅ Tiene su propia base de datos
- ✅ Puedes experimentar sin riesgo

---

## 🆘 SI ALGO FALLA

- Revisa los logs en Railway (pestaña "Deployments" → "Logs")
- Verifica que todas las variables estén configuradas
- Asegúrate de que la base de datos esté conectada
- Verifica que las migraciones se ejecutaron

---

¡Listo! Sigue estos pasos y tendrás tu entorno de desarrollo funcionando en Railway. 🚀

