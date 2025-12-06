# 📹 Sistema de Videollamadas - Guía de Usuario

## ✨ Características Implementadas

### 🎯 Funcionalidades Principales

1. **Salas Públicas y Privadas**
   - Crear salas públicas: visibles para todos
   - Crear salas privadas: protegidas con contraseña

2. **Controles Profesionales**
   - 🎥 Activar/Desactivar Cámara
   - 🎤 Activar/Desactivar Micrófono
   - ☎️ Colgar (salir de la llamada)

3. **Integración con Juegos**
   - Vincular salas de videollamada a juegos activos
   - Ver qué juego está asociado a cada sala

4. **Gestión de Participantes**
   - Ver lista de participantes en tiempo real
   - Identificar al creador de la sala
   - Contador de participantes

---

## 🚀 Cómo Usar

### 1. Acceder al Lobby de Videollamadas

**URL:** `https://tu-dominio.railway.app/video-lobby/`

En el lobby verás:
- **Salas Públicas:** Todas las salas disponibles para unirse
- **Salas Privadas:** Requieren contraseña
- Botón para crear nueva sala

### 2. Crear una Nueva Sala

1. Click en **"Crear Nueva Sala"**
2. Completar el formulario:
   - **Nombre:** Elige un nombre descriptivo (ej: "Sala de Amigos")
   - **Juego Asociado:** (Opcional) Vincula la sala a un juego
   - **Tipo de Sala:**
     - ✅ Pública: Cualquiera puede unirse
     - ⚠️ Privada: Requiere contraseña
   - **Contraseña:** (Solo para salas privadas)
3. Click en **"Crear Sala"**

### 3. Unirse a una Sala

**Sala Pública:**
- Click en **"Unirse"** directamente

**Sala Privada:**
- Click en **"Acceder"**
- Ingresar contraseña
- Click en **"Acceder"**

### 4. Usar los Controles de Video

Una vez dentro de la sala:

#### 🎥 Control de Cámara
- **Verde (activa):** Cámara encendida
- **Rojo (inactiva):** Cámara apagada
- Click para alternar

#### 🎤 Control de Micrófono
- **Verde (activo):** Micrófono encendido
- **Rojo (inactivo):** Micrófono silenciado
- Click para alternar

#### ☎️ Salir de la Llamada
- Click en el botón rojo de teléfono
- Confirmar salida
- Volverás al lobby

---

## 🎨 Elementos Visuales

### Vista de Video

- **Tu Video:** Esquina inferior derecha
- **Videos Remotos:** Grid principal (ajuste automático)
- **Controles:** Barra flotante en la parte inferior
- **Panel Lateral:** Lista de participantes

### Indicadores

- 🟢 **Verde:** Función activa
- 🔴 **Rojo:** Función desactivada
- 🔵 **Azul:** Información/Estado
- 🟡 **Amarillo:** Advertencia/Privado

---

## 🔧 Configuración Técnica

### Variables de Entorno Necesarias

En Railway, asegúrate de tener configuradas:

```env
AGORA_APP_ID=tu_app_id_de_agora
AGORA_APP_CERTIFICATE=tu_certificado_de_agora
```

### URLs Disponibles

| Ruta | Descripción |
|------|-------------|
| `/video-lobby/` | Lobby principal |
| `/video/create/` | Crear nueva sala |
| `/video/room/<id>/` | Sala de videollamada |
| `/api/get-agora-token/` | API para tokens |
| `/api/videocallgroups/` | API de grupos |

---

## 🐛 Solución de Problemas

### La cámara/micrófono no funcionan

1. **Verificar permisos del navegador:**
   - Chrome: Click en el candado 🔒 en la barra de URL
   - Permitir acceso a cámara y micrófono

2. **Probar en HTTPS:**
   - Agora requiere conexión segura (HTTPS)
   - Railway proporciona HTTPS automáticamente

### No puedo unirme a una sala

1. **Sala Privada:** Verificar contraseña correcta
2. **Token expirado:** Recargar la página
3. **Revisar logs de Sentry** para errores

### La videollamada se congela

1. Verificar conexión a internet
2. Cerrar otras aplicaciones que usen cámara/mic
3. Recargar la página

---

## 📊 Modelo de Datos

### VideoCallGroup

```python
{
    'name': str,              # Nombre de la sala
    'is_public': bool,        # True: pública, False: privada
    'password': str,          # Solo para salas privadas
    'game': ForeignKey,       # Juego asociado (opcional)
    'created_by': User,       # Creador de la sala
    'participants': M2M,      # Participantes actuales
    'agora_channel_name': str # Nombre del canal en Agora
}
```

---

## 🎯 Mejoras Futuras Sugeridas

1. **Compartir Pantalla** 📺
2. **Chat de Texto** 💬
3. **Grabación de Llamadas** 🎬
4. **Efectos de Fondo** 🖼️
5. **Reacciones en Vivo** 👍❤️
6. **Estadísticas de Llamada** 📈

---

## 🔐 Seguridad

- Las contraseñas NO están encriptadas (solo comparación directa)
- Los tokens de Agora expiran según configuración
- Solo participantes pueden ver el interior de salas privadas

---

## 📞 Soporte

Para reportar problemas:
1. Revisar logs en Railway
2. Revisar errores en Sentry
3. Verificar configuración de Agora

---

**Implementado por:** AI Assistant  
**Fecha:** 13 de octubre de 2025  
**Versión:** 1.0.0

