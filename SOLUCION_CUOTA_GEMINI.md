# ⚠️ Solución: Error de Cuota de Gemini API

## 🔴 Problema Identificado

El error `429 You exceeded your current quota` con `limit: 0` significa que:
- ✅ El modelo **SÍ está funcionando** (gemini-2.5-pro-exp)
- ❌ Pero **NO tienes cuota habilitada** en tu proyecto

## ✅ Solución: Habilitar Facturación

Aunque Gemini tiene tier gratuito, **necesitas habilitar facturación** en Google Cloud (no te cobrará si no excedes los límites gratuitos).

### Paso 1: Ir a Google Cloud Console
1. Ve a: **https://console.cloud.google.com/**
2. Selecciona tu proyecto: **493556265665** o **bingo-y-rifa-jym**

### Paso 2: Habilitar Facturación
1. Ve a: **Billing** (Facturación) en el menú lateral
2. Si no tienes facturación habilitada:
   - Click en **"Link a billing account"** o **"Vincular cuenta de facturación"**
   - O crea una nueva cuenta de facturación
   - **NO te preocupes:** Gemini tiene tier gratuito generoso

### Paso 3: Verificar Cuotas
1. Ve a: **https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas**
2. Verifica que las cuotas estén habilitadas
3. Deberías ver límites como:
   - 60 requests/minuto
   - 1,500 requests/día
   - Tokens gratuitos

### Paso 4: Esperar
1. Después de habilitar facturación, espera 5-10 minutos
2. Prueba el chatbot de nuevo

## 💰 ¿Cuánto Cuesta?

**Nada si usas el tier gratuito:**
- 60 solicitudes/minuto gratis
- 1,500 solicitudes/día gratis
- Suficiente para uso moderado

Solo se cobra si excedes estos límites (muy poco probable para tu caso).

## 🔍 Verificar Estado Actual

Para ver tu uso actual:
1. Ve a: **https://ai.dev/usage?tab=rate-limit**
2. Verás tu uso y límites

## 📋 Checklist

- [ ] Facturación habilitada en Google Cloud
- [ ] Proyecto correcto seleccionado (493556265665)
- [ ] Esperado 5-10 minutos después de habilitar
- [ ] Probado el chatbot nuevamente

## 🎯 Si No Quieres Habilitar Facturación

Si prefieres no habilitar facturación, la IA funcionará en modo limitado (sin análisis avanzado, solo funciones básicas).
















