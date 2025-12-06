# 🎯 Crear API Key de Gemini - Paso a Paso

## Método Más Fácil: Desde AI Studio (Recomendado)

Este método automáticamente habilita la API necesaria.

### Paso 1: Ir a Google AI Studio
1. Abre tu navegador
2. Ve a: **https://aistudio.google.com/app/apikey**
3. Inicia sesión con tu cuenta de Google

### Paso 2: Crear Nueva API Key
1. Verás una pantalla con tu proyecto (493556265665)
2. Click en el botón **"Create API Key"** o **"Crear clave de API"**
3. Si te pide seleccionar un proyecto, selecciona: **proyectos/493556265665**
4. Click en **"Create API Key in existing project"** o **"Crear clave de API en proyecto existente"**

### Paso 3: Copiar la Nueva Clave
1. Se generará una nueva clave (empieza con `AIza...`)
2. **Copia esta clave completa**
3. ⚠️ **IMPORTANTE:** Esta clave solo se muestra una vez, cópiala ahora

### Paso 4: Actualizar en Railway
1. Ve a Railway Dashboard: https://railway.app/
2. Selecciona tu proyecto
3. Click en **"Variables"**
4. Busca **`GEMINI_API_KEY`**
5. Click para editar
6. Pega la nueva clave
7. Guarda

### Paso 5: Verificar
1. Espera 2-3 minutos para el redeploy
2. Ve a tu dashboard: `/admin-panel/dashboard/`
3. Prueba el chatbot

## Si No Puedes Crear la Clave desde AI Studio

### Alternativa: Desde Google Cloud Console

1. Ve a: **https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com**
2. Selecciona tu proyecto: **493556265665**
3. Click en **"Enable"** o **"Habilitar"**
4. Espera 1-2 minutos
5. Luego ve a: **https://console.cloud.google.com/apis/credentials**
6. Click en **"Create Credentials"** → **"API Key"**
7. Copia la clave generada

## Verificar que la API Está Habilitada

1. Ve a: **https://console.cloud.google.com/apis/dashboard**
2. Busca en la lista: Debe aparecer algo relacionado con "Generative" o "Gemini"
3. Si no aparece, ve a: **https://console.cloud.google.com/apis/library**
4. Busca: **"Gemini"** o **"Generative"**
5. Deberías ver opciones como:
   - Generative Language API
   - Vertex AI API
   - Gemini API

## ¿Qué Hacer Si No Funciona?

1. **Verifica el proyecto:** Asegúrate de estar en el proyecto correcto (493556265665)
2. **Permisos:** Verifica que tu cuenta tenga permisos de "Editor" o "Owner"
3. **Facturación:** Algunas APIs requieren facturación habilitada (aunque Gemini tiene tier gratuito)
















