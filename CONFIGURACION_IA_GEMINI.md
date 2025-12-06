# 🤖 Configuración de IA con Google Gemini

## 📋 Pasos para Configurar

### 1. Obtener API Key de Google Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Click en "Get API Key" o "Crear API Key"
4. Copia la API key que se genera

### 2. Configurar en Railway

```bash
railway variables set GEMINI_API_KEY="tu-api-key-aqui"
```

O desde el dashboard de Railway:
1. Ve a tu proyecto en Railway
2. Click en **"Variables"**
3. Click en **"New Variable"**
4. Nombre: `GEMINI_API_KEY`
5. Valor: Tu API key de Gemini
6. Click en **"Add"**

### 3. Instalar Dependencia

La dependencia ya está agregada en `requirements.txt`:
```
google-generativeai==0.3.2
```

Railway la instalará automáticamente en el próximo deploy.

## ✅ Verificación

Una vez configurada, la IA aparecerá automáticamente en:
- Dashboard de administrador (`/admin-panel/dashboard/`)
- Panel de análisis inteligente
- Botón flotante del chatbot

Si no ves la IA, verifica:
1. Que `GEMINI_API_KEY` esté configurada
2. Que el deploy haya completado
3. Que tengas permisos de administrador

## 🎯 Funcionalidades Disponibles

### 1. Análisis Automático de Métricas
- Análisis de salud del sistema
- Detección de anomalías
- Predicciones de tendencias
- Score de salud (0-100)

### 2. Chatbot Administrativo
- Responde preguntas sobre el sistema
- Genera recomendaciones
- Explica métricas complejas
- Sugiere acciones

### 3. Reportes Automáticos
- Reporte diario
- Reporte semanal
- Reporte mensual
- Análisis detallado

## 💰 Costos

Google Gemini ofrece:
- **60 solicitudes/minuto** gratis
- **1,500 solicitudes/día** gratis
- Suficiente para uso moderado

Si necesitas más, consulta [pricing de Google AI](https://ai.google.dev/pricing)

## 🔧 Solución de Problemas

### La IA no aparece
- Verifica que `GEMINI_API_KEY` esté configurada
- Revisa los logs de Railway
- Verifica que tengas permisos de staff

### Error "IA no disponible"
- Verifica la API key
- Revisa que la librería esté instalada
- Verifica los logs para errores específicos

### Respuestas lentas
- Normal, puede tomar 2-5 segundos
- Depende de la complejidad de la pregunta
- Google Gemini tiene rate limits

## 📚 Documentación

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Python SDK](https://github.com/google/generative-ai-python)

