# 🔑 Configurar API Key de Gemini en Railway

## ✅ Tu API Key está lista
- **Nombre**: Clave API de lenguaje generativo
- **Proyecto**: 493556265665
- **Estado**: Lista para usar

## 📋 Pasos para configurar en Railway

### Opción 1: Desde el Dashboard de Railway (Recomendado)

1. Ve a https://railway.app/
2. Inicia sesión
3. Selecciona tu proyecto "bingo-mejorado"
4. Click en **"Variables"** (ícono de engranaje en la barra lateral)
5. Click en **"New Variable"** o **"+ New"**
6. Completa:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyCCTE4U3HFMXOGaaqXmv56arwL70g90VfI`
7. Click en **"Add"** o **"Save"**

### Opción 2: Desde la Terminal (Railway CLI)

Si tienes Railway CLI instalado:

```bash
railway login
railway link
railway variables set GEMINI_API_KEY="AIzaSyCCTE4U3HFMXOGaaqXmv56arwL70g90VfI"
```

## ✅ Verificación

Después de configurar:
1. Railway hará un redeploy automático
2. Espera 2-3 minutos
3. Ve a `/admin-panel/dashboard/`
4. Deberías ver el panel de "Análisis Inteligente de IA"
5. El botón flotante del chatbot aparecerá abajo a la derecha

## 🔒 Seguridad

- ✅ La API key está asociada a tu proyecto de Google Cloud
- ✅ Tiene límites de uso (gratis hasta 60 req/min)
- ✅ Solo visible para administradores del sistema
- ✅ No se expone en el código, solo en variables de entorno

## 🎯 Próximos pasos

Una vez configurada, la IA estará activa y podrás:
- Ver análisis automático en el dashboard
- Usar el chatbot para hacer preguntas
- Generar reportes automáticos


