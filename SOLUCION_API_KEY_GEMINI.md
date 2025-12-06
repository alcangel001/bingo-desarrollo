# 🔧 Solución: Crear Nueva API Key para Gemini

## 📋 Pasos para Crear API Key Específica para Gemini

### Paso 1: Ir a Google AI Studio
1. Ve a: **https://aistudio.google.com/app/apikey**
2. O: **https://makersuite.google.com/app/apikey**

### Paso 2: Crear Nueva API Key
1. Click en **"Create API Key"** o **"Crear clave de API"**
2. Selecciona un proyecto existente o crea uno nuevo
3. **IMPORTANTE:** Asegúrate de que el proyecto tenga **"Generative Language API"** habilitada

### Paso 3: Habilitar API de Gemini (Si no está habilitada)
Si ves error de permisos, necesitas habilitar la API:

1. Ve a: **https://console.cloud.google.com/apis/library**
2. Busca: **"Generative Language API"**
3. Click en **"Enable"** o **"Habilitar"**
4. Selecciona el proyecto correcto

### Paso 4: Copiar la Nueva API Key
1. Copia la nueva clave que se genera
2. Debe empezar con `AIza...`

### Paso 5: Configurar en Railway
1. Ve a Railway Dashboard
2. Variables → Edita `GEMINI_API_KEY`
3. Pega la nueva clave
4. Guarda

## 🔍 Verificar API Key Actual

Para verificar qué permisos tiene tu API key actual:

1. Ve a: **https://console.cloud.google.com/apis/credentials**
2. Busca tu API key: `AIzaSyCCTE4U3HFMXOGaaqXmv56arwL70g90VfI`
3. Click en ella para ver detalles
4. Verifica:
   - ✅ **API restrictions**: Debe incluir "Generative Language API" o estar en "Don't restrict"
   - ✅ **Application restrictions**: Puede estar en "None" o solo en tu dominio

## 🎯 Recomendación

**Opción A: Usar la clave actual pero habilitar permisos**
- Si tu clave ya existe, solo habilita "Generative Language API" en el proyecto

**Opción B: Crear nueva clave específica para Gemini** (Recomendado)
- Más seguro
- Separación de responsabilidades
- Fácil de revocar si es necesario

## ✅ Después de Configurar

1. Espera 2-3 minutos para que Railway haga redeploy
2. Prueba el chatbot de nuevo
3. Debería funcionar sin errores


