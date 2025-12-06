# 🤖 Guía Paso a Paso: IA en el Dashboard del Administrador

## 📋 Resumen

Esta guía te mostrará cómo usar y configurar la Inteligencia Artificial (IA) en el dashboard del administrador para obtener reportes automáticos y análisis del estado del sistema.

## ✅ Estado Actual

El sistema ya tiene integrada una IA **local** que funciona sin necesidad de APIs externas. Esta IA puede:
- ✅ Analizar métricas del dashboard
- ✅ Generar alertas automáticas
- ✅ Proporcionar recomendaciones
- ✅ Responder preguntas sobre el sistema
- ✅ Generar reportes diarios, semanales y mensuales

---

## 🚀 Paso 1: Verificar que la IA está Funcionando

### 1.1 Acceder al Dashboard

1. Inicia sesión como administrador
2. Ve a: **Dashboard de Administrador** (`/admin-panel/dashboard/`)
3. Deberías ver una sección llamada **"Análisis Inteligente de IA"** en la parte superior

### 1.2 Verificar el Análisis Automático

El dashboard muestra automáticamente:
- **Score de Salud del Sistema** (0-100%)
- **Estado General**: Bueno / Preocupante / Crítico
- **Resumen Ejecutivo**
- **Alertas Prioritarias** (máximo 3)
- **Recomendaciones** (máximo 5)

Si ves esta sección, **¡la IA está funcionando!** ✅

---

## 💬 Paso 2: Usar el Chatbot de IA

### 2.1 Acceder al Chatbot

En el dashboard, verás un botón flotante con un ícono de robot (🤖) en la esquina inferior derecha.

1. Haz clic en el botón del robot
2. Se abrirá un modal con el chatbot

### 2.2 Hacer Preguntas

Puedes preguntar cosas como:
- "¿Cómo está el sistema?"
- "¿Cuántos usuarios hay?"
- "¿Cuáles son los ingresos?"
- "¿Hay retiros pendientes?"
- "¿Qué problemas detectaste?"
- "Dame recomendaciones"

### 2.3 Generar Reportes

El chatbot tiene botones para generar reportes:
- **Reporte Diario**: Análisis de las últimas 24 horas
- **Reporte Semanal**: Análisis de los últimos 7 días
- **Reporte Mensual**: Análisis del último mes

---

## 🔧 Paso 3: Entender Qué Analiza la IA

La IA analiza automáticamente:

### 3.1 Métricas Financieras
- Ingresos de plataforma
- Balance del sistema
- Entradas vs Salidas
- Liquidez total
- Fondos en escrow

### 3.2 Métricas de Usuarios
- Usuarios registrados
- Usuarios activos (últimos 7 días)
- Nuevos usuarios
- Usuarios bloqueados

### 3.3 Métricas de Actividad
- Juegos activos
- Juegos con problemas
- Rifas activas
- Transacciones sospechosas

### 3.4 Alertas Automáticas
- Balance negativo del sistema
- Muchos retiros pendientes
- Juegos sin actividad
- Transacciones sospechosas
- Liquidez baja

---

## 📊 Paso 4: Interpretar los Reportes

### 4.1 Score de Salud (0-100%)

- **80-100%**: ✅ Sistema saludable
- **60-79%**: ⚠️ Requiere atención
- **0-59%**: 🔴 Problemas críticos

### 4.2 Alertas

Las alertas tienen prioridades:
- **Prioridad 5**: Crítico (acción inmediata)
- **Prioridad 4**: Alta (atención urgente)
- **Prioridad 3**: Media (revisar pronto)

### 4.3 Recomendaciones

Las recomendaciones tienen impacto:
- **Alto**: Acción importante
- **Medio**: Mejora recomendada
- **Bajo**: Optimización opcional

---

## 🎯 Paso 5: Usar la IA para Toma de Decisiones

### 5.1 Revisión Diaria Recomendada

1. Abre el dashboard
2. Revisa el análisis automático
3. Lee las alertas prioritarias
4. Revisa las recomendaciones
5. Genera un reporte diario si es necesario

### 5.2 Preguntas Útiles para el Chatbot

- "¿Qué necesito revisar hoy?"
- "¿Hay algo que requiera atención inmediata?"
- "¿Cuál es el estado de los retiros?"
- "¿Hay usuarios con comportamientos sospechosos?"
- "¿Cómo va el crecimiento de usuarios?"

---

## 🔌 Paso 6: Configurar IA Avanzada con Gemini (Opcional)

Si quieres análisis más avanzados usando Google Gemini, sigue estos pasos:

### 6.1 Obtener API Key de Gemini

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una cuenta o inicia sesión
3. Crea una nueva API Key
4. Copia la clave

### 6.2 Configurar la Variable de Entorno

En tu servidor (Railway, Heroku, etc.), agrega la variable de entorno:

```bash
GEMINI_API_KEY=tu_api_key_aqui
```

### 6.3 Verificar que Funciona

1. El sistema intentará usar Gemini automáticamente
2. Si Gemini no está disponible, usará el asistente local
3. El asistente local siempre funciona, así que no hay problema si Gemini falla

**Nota**: El asistente local ya funciona muy bien. Gemini es opcional para análisis más profundos.

---

## 🐛 Paso 7: Solución de Problemas

### 7.1 Error: "Cuota de Gemini API Excedida"

**Problema**: Ves un mensaje sobre cuota de Gemini API.

**Solución**:
1. **¡No necesitas Gemini!** El sistema usa un asistente local que funciona sin APIs externas
2. El asistente local ya está activo y funcionando
3. Si ves este error, significa que algo está intentando usar Gemini
4. **Solución rápida**: El asistente local ya funciona. Ignora el error de Gemini
5. Para más detalles, consulta: `SOLUCION_ERROR_GEMINI_CUOTA.md`

**Nota**: El sistema está configurado para usar `smart_assistant` (local), no `ai_assistant` (Gemini). El asistente local funciona perfectamente sin necesidad de Gemini.

### 7.2 No Veo el Análisis de IA

**Solución**:
1. Verifica que eres administrador
2. Recarga la página
3. Revisa la consola del navegador (F12) por errores
4. Verifica que el servidor esté ejecutándose correctamente

### 7.3 El Chatbot No Responde

**Solución**:
1. Verifica tu conexión a internet
2. Revisa los logs del servidor
3. Asegúrate de que el endpoint `/admin-panel/ai/chatbot/` esté accesible
4. Verifica que `smart_assistant` esté importado correctamente

### 7.4 Los Reportes No se Generan

**Solución**:
1. Verifica que tengas permisos de administrador
2. Revisa los logs del servidor
3. Prueba generar un reporte desde el chatbot
4. Verifica que no haya errores en la consola del navegador

---

## 📝 Paso 8: Ejemplos de Uso

### Ejemplo 1: Revisión Matutina

```
1. Abre el dashboard
2. Revisa el score de salud
3. Lee las alertas
4. Pregunta al chatbot: "¿Qué necesito revisar hoy?"
5. Si hay retiros pendientes, procésalos
```

### Ejemplo 2: Análisis Semanal

```
1. Abre el dashboard
2. Haz clic en el botón del robot
3. Genera "Reporte Semanal"
4. Lee el reporte completo
5. Toma decisiones basadas en las recomendaciones
```

### Ejemplo 3: Investigación de Problemas

```
1. Abre el dashboard
2. Ve una alerta de "Transacciones Sospechosas"
3. Pregunta al chatbot: "¿Cuáles son las transacciones sospechosas?"
4. Revisa los detalles
5. Toma acción apropiada
```

---

## 🎓 Paso 9: Mejores Prácticas

### 9.1 Revisión Regular

- **Diaria**: Revisa el dashboard y las alertas
- **Semanal**: Genera reporte semanal
- **Mensual**: Genera reporte mensual y analiza tendencias

### 9.2 Actuar sobre Recomendaciones

- Las recomendaciones de "impacto alto" deben atenderse primero
- Las recomendaciones de "impacto medio" pueden esperar
- Las recomendaciones de "impacto bajo" son opcionales

### 9.3 Monitoreo Continuo

- Configura alertas si el score de salud baja de 60%
- Revisa usuarios de alto saldo regularmente
- Monitorea retiros pendientes

---

## 📚 Recursos Adicionales

### Archivos Importantes

- `bingo_app/smart_assistant.py`: Asistente local (siempre funciona)
- `bingo_app/ai_assistant.py`: Asistente con Gemini (opcional)
- `bingo_app/views.py`: Vistas del dashboard y APIs de IA
- `bingo_app/templates/bingo_app/admin/dashboard.html`: Template del dashboard

### Endpoints de API

- `/admin-panel/ai/chatbot/`: Chatbot de IA
- `/admin-panel/ai/report/`: Generar reportes
- `/admin-panel/ai/analysis/`: Obtener análisis

---

## ✅ Checklist de Configuración

Marca cada paso cuando esté completo:

- [ ] Acceso al dashboard de administrador
- [ ] Visualización del análisis automático de IA
- [ ] Botón del chatbot visible y funcional
- [ ] Prueba de preguntas al chatbot
- [ ] Generación exitosa de reporte diario
- [ ] Generación exitosa de reporte semanal
- [ ] (Opcional) Configuración de Gemini API Key
- [ ] (Opcional) Verificación de análisis con Gemini

---

## 🎉 ¡Listo!

Ya tienes la IA funcionando en tu dashboard. La IA analiza automáticamente todas las métricas y te proporciona:
- Alertas cuando algo necesita atención
- Recomendaciones para mejorar el sistema
- Respuestas a tus preguntas
- Reportes detallados

**¿Necesitas ayuda?** Revisa los logs del servidor o consulta la documentación del código.

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en `logs/django.log`
2. Verifica la consola del navegador
3. Asegúrate de tener permisos de administrador
4. Revisa que todas las dependencias estén instaladas

---

**Última actualización**: 2025-01-27
**Versión**: 1.0

