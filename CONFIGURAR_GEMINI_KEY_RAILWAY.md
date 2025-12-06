# 🔑 Configurar API Key de Gemini en Railway

## ✅ Tu API Key

Tu API Key de Gemini está lista:
- **Clave**: `AIzaSyBpTsO0TRrYekF-gqKTs-cfen-L1copcWQ`
- **Proyecto**: `projects/493556265665`
- **Nombre**: ai de administardor de dashboar

## 🚀 Configuración en Railway (Pasos)

### Opción 1: Desde el Dashboard de Railway (Recomendado)

1. **Abre tu proyecto en Railway**
   - Ve a: https://railway.app
   - Selecciona tu proyecto

2. **Ve a Variables de Entorno**
   - Click en tu servicio (servicio de Django)
   - Ve a la pestaña **"Variables"**

3. **Agrega la Variable**
   - Click en **"New Variable"**
   - **Nombre**: `GEMINI_API_KEY`
   - **Valor**: `AIzaSyBpTsO0TRrYekF-gqKTs-cfen-L1copcWQ`
   - Click en **"Add"**

4. **Redeploy**
   - Railway detectará el cambio automáticamente
   - O puedes hacer click en **"Deploy"** → **"Redeploy"**

### Opción 2: Desde la Terminal (Railway CLI)

Si tienes Railway CLI instalado:

```bash
railway variables set GEMINI_API_KEY=AIzaSyBpTsO0TRrYekF-gqKTs-cfen-L1copcWQ
```

Luego redeploy:
```bash
railway up
```

## ✅ Verificar que Funciona

1. **Espera a que el redeploy termine** (1-2 minutos)

2. **Abre el dashboard del administrador**
   - Ve a: `https://tu-dominio.railway.app/admin-panel/dashboard/`

3. **Verifica el badge**
   - Si ves **"🤖 IA Real"** → ✅ Gemini está funcionando
   - Si ves **"⚙️ Asistente Local"** → ❌ Revisa la configuración

4. **Prueba el chatbot**
   - Haz clic en el botón del robot 🤖
   - Pregunta algo: "¿Cómo está el sistema?"
   - Si responde con análisis inteligente → ✅ Funciona

## 🔍 Verificar en los Logs

Si quieres verificar que la API Key se está usando:

1. En Railway, ve a tu servicio
2. Click en **"Deployments"** → Último deployment
3. Revisa los logs
4. Busca: `✅ Modelo configurado:` o `📋 Modelos disponibles`

Si ves esos mensajes, Gemini está funcionando.

## ⚠️ Seguridad

**IMPORTANTE**: 
- ✅ La API Key está configurada en Railway (seguro)
- ❌ NO la subas a GitHub
- ❌ NO la compartas públicamente
- ✅ El archivo `.env` local NO se sube a Git (está en .gitignore)

## 🐛 Solución de Problemas

### No veo el badge "IA Real"

1. Verifica que la variable esté configurada:
   - Railway → Variables → Busca `GEMINI_API_KEY`
   - Debe tener el valor correcto

2. Verifica que el redeploy se haya completado:
   - Railway → Deployments → Debe estar "Succeeded"

3. Revisa los logs:
   - Busca errores relacionados con Gemini
   - Si ves "GEMINI_API_KEY no configurada" → La variable no está configurada

### Error: "Cuota Excedida"

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Verifica que la facturación esté habilitada
3. Revisa los límites de cuota

### La IA sigue usando el asistente local

1. Reinicia el servicio manualmente:
   - Railway → Tu servicio → Settings → Restart

2. Verifica que la variable esté en el servicio correcto:
   - Si tienes múltiples servicios, asegúrate de configurarla en el servicio de Django

## 📝 Notas

- **La API Key se aplica automáticamente** después del redeploy
- **No necesitas reiniciar manualmente** (Railway lo hace)
- **El sistema detecta automáticamente** si Gemini está disponible
- **Si Gemini falla, usa el asistente local** automáticamente

---

**Última actualización**: 2025-01-27















