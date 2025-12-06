# 📋 Guía: Habilitar Facturación en Google Cloud

## 🎯 Tu Proyecto Actual
- **Número:** 493556265665
- **ID:** bingo-y-rifa-jym
- **Estado:** Sin facturación habilitada

---

## ✅ Paso 1: Ir a Facturación

1. En la página de Google Cloud Console que estás viendo
2. Click en **"Facturación"** en el menú lateral
3. O ve directamente a: https://console.cloud.google.com/billing

---

## ✅ Paso 2: Habilitar Facturación

### Si NO tienes cuenta de facturación:

1. Click en **"Crear cuenta de facturación"** o **"Link billing account"**
2. Completa el formulario:
   - **Nombre de cuenta:** Puede ser "Bingo App" o cualquier nombre
   - **País:** Selecciona tu país
   - **Información de facturación:** Necesitarás una tarjeta de crédito
3. ⚠️ **IMPORTANTE:** 
   - Google NO te cobrará automáticamente
   - Gemini tiene tier gratuito generoso (60 req/min, 1,500/día)
   - Solo se cobra si excedes los límites (muy poco probable)
   - Puedes establecer límites de gasto

### Si YA tienes cuenta de facturación:

1. Click en **"Link billing account"** o **"Vincular cuenta"**
2. Selecciona tu cuenta existente
3. Listo

---

## ✅ Paso 3: Verificar que la API esté Habilitada

1. Ve a: **"APIs y servicios"** → **"APIs habilitadas"**
2. O directamente: https://console.cloud.google.com/apis/library
3. Busca: **"Generative Language API"** o **"Gemini API"**
4. Si NO está habilitada:
   - Click en ella
   - Click en **"Enable"** o **"Habilitar"**
5. Si YA está habilitada, pasa al siguiente paso

---

## ✅ Paso 4: Verificar Cuotas

1. Ve a: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. O desde el menú: **"APIs y servicios"** → **"Cuotas"**
3. Busca cuotas relacionadas con Gemini
4. Deberías ver:
   - **GenerateRequestsPerMinutePerProjectPerModel-FreeTier:** 60
   - **GenerateRequestsPerDayPerProjectPerModel-FreeTier:** 1,500
   - Si ves "0" o "limit: 0", significa que aún no está habilitada la cuota

---

## ✅ Paso 5: Esperar y Probar

1. Después de habilitar facturación, espera **5-10 minutos**
2. Ve a tu dashboard: `/admin-panel/dashboard/`
3. Prueba el chatbot
4. Debería funcionar sin errores de cuota

---

## 💰 ¿Cuánto Cuesta?

**Nada si te mantienes en el tier gratuito:**
- ✅ 60 solicitudes/minuto gratis
- ✅ 1,500 solicitudes/día gratis
- ✅ Suficiente para uso moderado de la IA

**Solo se cobra si:**
- Excedes 1,500 solicitudes/día (muy poco probable)
- El costo es muy bajo: ~$0.001 por 1,000 tokens

---

## 🔒 Seguridad

- Puedes establecer **límites de gasto** en Google Cloud
- Puedes recibir **alertas** cuando te acerques a los límites
- El tier gratuito es muy generoso

---

## ❓ Si No Quieres Habilitar Facturación

Si prefieres no habilitar facturación:
- La IA funcionará en **modo limitado**
- Solo funciones básicas (sin análisis avanzado)
- El chatbot mostrará mensajes informativos
















