# 🚀 GUÍA: Crear Entorno de Desarrollo en Railway

## ⚠️ IMPORTANTE - SEGURIDAD

**Este proceso NO tocará tu proyecto de producción:**
- ✅ Crearemos un **NUEVO proyecto** en Railway
- ✅ Con una **base de datos completamente separada**
- ✅ Con **variables de entorno independientes**
- ✅ Tu proyecto de producción seguirá funcionando normalmente
- ✅ Tu rifa activa está 100% segura

---

## 📋 PASOS A SEGUIR

### **PASO 1: Crear Nuevo Proyecto en Railway**

1. Ve a: https://railway.app
2. Inicia sesión con tu cuenta
3. Haz clic en **"New Project"** (Nuevo Proyecto)
4. Selecciona **"Empty Project"** (Proyecto Vacío)
5. Dale un nombre al proyecto, por ejemplo:
   - `bingo-desarrollo`
   - `bingo-dev`
   - `bingo-testing`
   - (Cualquier nombre que identifique que es desarrollo)

**✅ Resultado:** Tendrás un proyecto nuevo y vacío en Railway

---

### **PASO 2: Crear Base de Datos PostgreSQL**

1. Dentro del nuevo proyecto, haz clic en **"+ New"**
2. Selecciona **"Database"**
3. Selecciona **"Add PostgreSQL"**
4. Espera a que se cree (puede tomar 1-2 minutos)

**✅ Resultado:** Tendrás una base de datos PostgreSQL nueva y separada

---

### **PASO 3: Obtener URL de la Base de Datos**

1. Haz clic en la base de datos que acabas de crear
2. Ve a la pestaña **"Variables"**
3. Busca la variable **`DATABASE_URL`**
4. **Copia esa URL completa** (algo como: `postgresql://postgres:password@host:port/database`)
5. **Guárdala en un lugar seguro** (la necesitarás después)

**✅ Resultado:** Tienes la URL de conexión a tu base de datos de desarrollo

---

### **PASO 4: Conectar el Código de Desarrollo**

Ahora necesitamos conectar tu carpeta `bingo-desarrollo` con Railway.

#### **Opción A: Usando GitHub (Recomendado)**

1. **Crear repositorio en GitHub:**
   - Ve a: https://github.com/new
   - Crea un repositorio nuevo (ej: `bingo-desarrollo`)
   - **NO inicialices con README** (está vacío)
   - Haz clic en "Create repository"

2. **Subir código a GitHub:**
   - En PowerShell, ve a tu carpeta de desarrollo:
     ```powershell
     cd "C:\Users\DELL VOSTRO 7500\bingo-desarrollo"
     ```
   - Inicializa Git (si no está inicializado):
     ```powershell
     git init
     ```
   - Agrega todos los archivos:
     ```powershell
     git add .
     ```
   - Haz commit:
     ```powershell
     git commit -m "Initial commit - desarrollo"
     ```
   - Conecta con GitHub (reemplaza TU_USUARIO y TU_REPO):
     ```powershell
     git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
     git branch -M main
     git push -u origin main
     ```

3. **Conectar Railway con GitHub:**
   - En Railway, en tu proyecto nuevo
   - Haz clic en **"+ New"**
   - Selecciona **"GitHub Repo"**
   - Selecciona el repositorio que acabas de crear
   - Railway detectará automáticamente que es Django

#### **Opción B: Usando Railway CLI (Alternativa)**

Si prefieres no usar GitHub, puedes usar Railway CLI, pero GitHub es más fácil.

---

### **PASO 5: Configurar Variables de Entorno**

1. En Railway, en tu proyecto nuevo
2. Haz clic en el servicio de tu aplicación (no la base de datos)
3. Ve a la pestaña **"Variables"**
4. Agrega las siguientes variables:

#### **Variables Obligatorias:**

```
DATABASE_URL=<La URL que copiaste en el Paso 3>
SECRET_KEY=<Genera una nueva clave secreta>
DEBUG=True
ALLOWED_HOSTS=*.railway.app,tu-dominio-dev.railway.app
```

#### **Cómo generar SECRET_KEY:**

En PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copia el resultado y úsalo como SECRET_KEY.

#### **Variables Opcionales (puedes copiarlas de producción si las necesitas):**

```
SENDGRID_API_KEY=<tu_key_si_la_necesitas>
GOOGLE_CLIENT_ID=<tu_client_id>
GOOGLE_SECRET=<tu_secret>
FACEBOOK_CLIENT_ID=<tu_client_id>
FACEBOOK_SECRET=<tu_secret>
AGORA_APP_ID=<tu_app_id>
AGORA_APP_CERTIFICATE=<tu_certificate>
GEMINI_API_KEY=<tu_key>
SENTRY_DSN=<tu_dsn>
```

**⚠️ IMPORTANTE:** 
- Usa las **mismas claves** de producción si quieres probar integraciones
- O déjalas vacías si solo quieres probar funcionalidades básicas

---

### **PASO 6: Configurar Build y Deploy**

1. En Railway, ve a la pestaña **"Settings"** de tu servicio
2. Configura:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn bingo_project.wsgi:application --bind 0.0.0.0:$PORT
```

O si usas el Procfile que ya tienes, Railway lo detectará automáticamente.

---

### **PASO 7: Ejecutar Migraciones**

Railway debería ejecutar las migraciones automáticamente, pero si no:

1. Ve a la pestaña **"Deployments"**
2. Haz clic en el deployment más reciente
3. Ve a la pestaña **"Logs"**
4. Verifica que las migraciones se ejecutaron correctamente

Si necesitas ejecutarlas manualmente:
1. Ve a la pestaña **"Settings"**
2. Busca **"Deploy"** o **"Run Command"**
3. Ejecuta: `python manage.py migrate`

---

### **PASO 8: Crear Superusuario**

1. En Railway, ve a la pestaña **"Settings"** de tu servicio
2. Busca **"Run Command"** o **"Shell"**
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones para crear el usuario admin

---

### **PASO 9: Verificar que Funciona**

1. Railway te dará una URL automática (algo como: `tu-proyecto.railway.app`)
2. Haz clic en la URL o ve a la pestaña **"Settings"** → **"Domains"**
3. Abre la URL en tu navegador
4. Deberías ver tu juego funcionando

---

## ✅ VERIFICACIÓN FINAL

**Asegúrate de que tienes:**

- ✅ Proyecto nuevo en Railway (diferente al de producción)
- ✅ Base de datos PostgreSQL nueva y separada
- ✅ Variables de entorno configuradas
- ✅ Código desplegado correctamente
- ✅ Migraciones ejecutadas
- ✅ Superusuario creado
- ✅ Sitio accesible en la URL de Railway

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

## 📝 NOTAS IMPORTANTES

1. **Nunca mezcles las variables de entorno** entre producción y desarrollo
2. **El proyecto de desarrollo tendrá una URL diferente** (ej: `bingo-dev.railway.app`)
3. **Puedes hacer cambios en desarrollo** sin afectar producción
4. **Cuando estés listo**, te guiaré para unificar todo

---

## 🆘 SI ALGO FALLA

- Revisa los logs en Railway (pestaña "Deployments" → "Logs")
- Verifica que todas las variables de entorno estén configuradas
- Asegúrate de que la base de datos esté conectada
- Verifica que las migraciones se ejecutaron

---

## 🎯 RESUMEN

**Lo que acabamos de hacer:**
1. ✅ Crear proyecto nuevo en Railway
2. ✅ Crear base de datos separada
3. ✅ Conectar código de desarrollo
4. ✅ Configurar variables de entorno
5. ✅ Desplegar en Railway
6. ✅ Verificar que funciona

**Resultado:**
- ✅ Tienes tu juego en desarrollo funcionando en línea
- ✅ Completamente separado de producción
- ✅ Puedes probar desde cualquier dispositivo
- ✅ Tu producción sigue intacta

---

¿Listo para empezar? Te guiaré paso a paso cuando estés en Railway. 🚀


