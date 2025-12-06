# 🤖 Configurar IA Real con Gemini

## ⚠️ Importante

El sistema ahora usa **IA real (Gemini)** cuando está disponible. Si no tienes Gemini configurado, usa el asistente local (basado en reglas) como respaldo.

## 🚀 Configuración Rápida

### Paso 1: Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Create API Key"
4. Copia la clave generada

### Paso 2: Habilitar Facturación (Gratis)

**IMPORTANTE**: Aunque el tier gratuito no cobra, necesitas habilitar facturación:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo o selecciona uno existente
3. Ve a **Billing** (Facturación)
4. Habilita facturación (elige el plan gratuito)
5. Ve a **APIs & Services** → **Library**
6. Busca "Generative Language API"
7. Haz clic en "Enable" (Habilitar)
8. Ve a **APIs & Services** → **Credentials**
9. Verifica que tu API Key esté creada

### Paso 3: Configurar Variable de Entorno

En tu servidor (Railway, Heroku, etc.), agrega la variable de entorno:

```bash
GEMINI_API_KEY=tu_api_key_aqui
```

**En Railway:**
1. Ve a tu proyecto
2. Settings → Environment Variables
3. Agrega: `GEMINI_API_KEY` = `tu_api_key`
4. Guarda y redeploy

**En Heroku:**
```bash
heroku config:set GEMINI_API_KEY=tu_api_key_aqui
```

**En local (.env):**
```bash
GEMINI_API_KEY=tu_api_key_aqui
```

### Paso 4: Reiniciar el Servidor

Después de configurar la variable de entorno, reinicia el servidor.

## ✅ Verificar que Funciona

1. Abre el dashboard del administrador
2. Si ves el badge **"🤖 IA Real"** en el análisis, entonces Gemini está funcionando
3. Si ves el badge **"⚙️ Asistente Local"**, entonces está usando el asistente local

## 🔍 Cómo Funciona el Sistema Híbrido

El sistema ahora funciona así:

1. **Primero intenta usar Gemini** (IA real)
   - Si Gemini está disponible → Usa IA real
   - Si Gemini falla → Usa asistente local

2. **Si Gemini no está configurado** → Usa asistente local automáticamente

3. **El asistente local siempre funciona** como respaldo

## 📊 Diferencias

### IA Real (Gemini)
- ✅ Análisis más profundo y contextual
- ✅ Respuestas más naturales
- ✅ Puede entender preguntas complejas
- ✅ Análisis más inteligente
- ⚠️ Requiere API Key
- ⚠️ Puede tener límites de cuota

### Asistente Local
- ✅ Siempre funciona (sin APIs)
- ✅ No requiere configuración
- ✅ Sin límites de cuota
- ✅ Respuestas rápidas
- ⚠️ Basado en reglas predefinidas
- ⚠️ Menos flexible que IA real

## 🐛 Solución de Problemas

### Error: "Cuota de Gemini API Excedida"

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Verifica que la facturación esté habilitada
3. Revisa los límites de cuota en APIs & Services → Quotas
4. Si es necesario, espera a que se resetee la cuota

### El Sistema No Usa Gemini

1. Verifica que `GEMINI_API_KEY` esté configurada
2. Verifica que el servidor se haya reiniciado
3. Revisa los logs del servidor
4. El sistema usará automáticamente el asistente local si Gemini no está disponible

### Gemini Funciona Pero Quiero Usar Local

Simplemente elimina o no configures `GEMINI_API_KEY`. El sistema usará automáticamente el asistente local.

## 📝 Notas Importantes

- **El tier gratuito de Gemini no cobra**, pero necesitas habilitar facturación
- **El asistente local siempre funciona** como respaldo
- **No necesitas configurar Gemini** si prefieres el asistente local
- **El sistema detecta automáticamente** qué usar

## 🎯 Recomendación

- **Para producción**: Configura Gemini para análisis más avanzados
- **Para desarrollo**: El asistente local es suficiente
- **Si tienes problemas con Gemini**: El sistema automáticamente usa el asistente local

---

**Última actualización**: 2025-01-27















