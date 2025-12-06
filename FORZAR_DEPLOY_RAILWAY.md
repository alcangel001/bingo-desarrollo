# 🚀 CÓMO FORZAR DEPLOY EN RAILWAY

## Problema
Los cambios están en GitHub pero Railway no ha desplegado automáticamente.

## Soluciones

### Opción 1: Verificar configuración de Railway (RECOMENDADO)

1. **Ve al Dashboard de Railway:**
   - https://railway.app/
   - Inicia sesión
   - Selecciona tu proyecto

2. **Verifica la rama configurada:**
   - Ve a **Settings** → **Source**
   - Verifica que esté configurada la rama **`main`**
   - Si está en otra rama, cámbiala a `main`

3. **Verifica el repositorio conectado:**
   - En **Settings** → **Source**
   - Verifica que el repositorio sea: `alcangel001/bingo-mejorado`
   - Verifica que esté conectado correctamente

### Opción 2: Forzar redeploy manual

1. **Desde el Dashboard de Railway:**
   - Ve a tu proyecto
   - Click en **Deployments** (o **Deploys**)
   - Busca el último deployment
   - Click en los **3 puntos** (⋯) del último deployment
   - Selecciona **"Redeploy"**

2. **O desde Settings:**
   - Ve a **Settings** → **Source**
   - Click en **"Redeploy"** o **"Manual Deploy"**

### Opción 3: Usar Railway CLI

Si tienes Railway CLI instalado:

```bash
# Login
railway login

# Seleccionar proyecto
railway link

# Forzar redeploy
railway up
```

### Opción 4: Verificar logs de Railway

1. Ve al Dashboard de Railway
2. Click en **Deployments**
3. Revisa el último deployment:
   - Si está en estado **"Failed"** → Revisa los logs de error
   - Si está en estado **"Building"** → Espera a que termine
   - Si está en estado **"Active"** → El deploy ya está activo

### Opción 5: Verificar que los cambios estén en main

```bash
# Verificar último commit en main
git checkout main
git pull origin main
git log --oneline -3

# Deberías ver:
# 0c0033f Fix: Corregir error ERRO133 en reproductor de video YouTube...
```

## Verificación de cambios desplegados

Los cambios que deberían estar desplegados son:

1. ✅ `bingo_app/templatetags/bingo_filters.py` - Filtro mejorado
2. ✅ `bingo_app/templates/bingo_app/lobby.html` - Iframe actualizado
3. ✅ `bingo_app/templates/bingo_app/raffle_lobby.html` - Iframe actualizado

## Si Railway sigue sin desplegar

1. **Desconectar y reconectar el repositorio:**
   - Settings → Source → Disconnect
   - Luego Connect nuevamente
   - Selecciona la rama `main`

2. **Verificar webhook de GitHub:**
   - Ve a tu repositorio en GitHub
   - Settings → Webhooks
   - Verifica que haya un webhook de Railway
   - Si no existe, Railway debería crearlo automáticamente al conectar

3. **Contactar soporte de Railway:**
   - Si nada funciona, puede haber un problema con la cuenta o el proyecto

## Estado actual del código

- ✅ Commit en GitHub: `0c0033f`
- ✅ Rama: `main`
- ✅ Repositorio: `alcangel001/bingo-mejorado`
- ⏳ Pendiente: Deploy en Railway


