# 🌐 GUÍA: DOMINIOS PERSONALIZADOS PARA FRANQUICIAS

## 📋 Resumen

Este sistema permite asignar un dominio personalizado (ej: `mi-franquicia.com`) a cada franquicia. Cuando los usuarios accedan a través de ese dominio, automáticamente verán el contenido de esa franquicia específica.

## ✅ Funcionalidades Implementadas

1. **Campo `custom_domain` en el modelo Franchise**
   - Almacena el dominio personalizado de cada franquicia
   - Validación automática de formato
   - Limpieza automática (quita http://, https://, www., etc.)

2. **Middleware de detección automática**
   - Detecta la franquicia por dominio antes de procesar la solicitud
   - Si no hay dominio personalizado, usa la lógica normal de usuario

3. **Interfaz de administración**
   - Campo visible en el admin de Django
   - Validación y advertencias al guardar

## 🚀 Cómo Asignar un Dominio a una Franquicia

### Paso 1: Configurar el Dominio en el Admin

1. Ve al panel de administración de Django: `/admin/`
2. Navega a **Franquicias** → Selecciona la franquicia
3. En el campo **"Dominio Personalizado"**, ingresa el dominio:
   - Ejemplo: `mi-franquicia.com`
   - El sistema automáticamente limpiará el formato (quitará http://, www., etc.)
4. Guarda los cambios

### Paso 2: Configurar el DNS

El dominio debe apuntar al servidor donde está desplegada la aplicación:

**Para Railway:**
1. Ve a Railway → Tu proyecto → Settings → Domains
2. Agrega el dominio personalizado
3. Railway te dará los registros DNS que necesitas configurar

**Para otros proveedores:**
- Configura un registro **CNAME** o **A** apuntando a tu servidor
- Si usas CNAME, apunta a: `tu-app.railway.app` (o tu dominio principal)
- Si usas A, apunta a la IP de tu servidor

### Paso 3: Actualizar ALLOWED_HOSTS

**IMPORTANTE:** Debes agregar el dominio a `ALLOWED_HOSTS` en Railway:

```bash
# Ver ALLOWED_HOSTS actual
railway variables get ALLOWED_HOSTS

# Agregar el nuevo dominio (mantén los existentes)
railway variables set ALLOWED_HOSTS="tu-app.railway.app,mi-franquicia.com,www.mi-franquicia.com"
```

**Nota:** También agrega la versión con `www.` si quieres soportarla.

### Paso 4: Actualizar CSRF_TRUSTED_ORIGINS

También debes agregar el dominio a `CSRF_TRUSTED_ORIGINS`:

```bash
railway variables set CSRF_TRUSTED_ORIGINS="https://tu-app.railway.app,https://mi-franquicia.com,https://www.mi-franquicia.com"
```

### Paso 5: Verificar

1. Espera a que el DNS se propague (puede tardar hasta 24 horas, pero usualmente es más rápido)
2. Accede a `https://mi-franquicia.com`
3. Deberías ver el contenido de la franquicia automáticamente

## 🔧 Validaciones Automáticas

El sistema valida automáticamente:

- ✅ Formato de dominio válido
- ✅ Longitud mínima (3 caracteres)
- ✅ Presencia de punto (ej: ejemplo.com)
- ✅ Caracteres permitidos (solo letras, números, guiones y puntos)
- ✅ Unicidad (no puede haber dos franquicias con el mismo dominio)

## 📝 Ejemplos

### Ejemplo 1: Dominio simple
```
Dominio ingresado: "mi-franquicia.com"
Dominio guardado: "mi-franquicia.com"
```

### Ejemplo 2: Dominio con www
```
Dominio ingresado: "www.mi-franquicia.com"
Dominio guardado: "mi-franquicia.com" (www se quita automáticamente)
```

### Ejemplo 3: Dominio con protocolo
```
Dominio ingresado: "https://mi-franquicia.com"
Dominio guardado: "mi-franquicia.com" (protocolo se quita automáticamente)
```

## ⚠️ Consideraciones Importantes

1. **Un dominio por franquicia**: Cada dominio solo puede estar asignado a una franquicia
2. **Franquicia activa**: Solo las franquicias activas (`is_active=True`) pueden usar dominios personalizados
3. **DNS debe estar configurado**: El dominio debe apuntar correctamente al servidor
4. **ALLOWED_HOSTS**: Siempre actualiza ALLOWED_HOSTS en Railway después de agregar un dominio
5. **Propagación DNS**: Los cambios de DNS pueden tardar hasta 24 horas en propagarse

## 🐛 Solución de Problemas

### El dominio no funciona

1. **Verifica el DNS:**
   ```bash
   # En Windows
   nslookup mi-franquicia.com
   
   # En Linux/Mac
   dig mi-franquicia.com
   ```

2. **Verifica ALLOWED_HOSTS:**
   ```bash
   railway variables get ALLOWED_HOSTS
   ```

3. **Verifica que la franquicia esté activa:**
   - En el admin, verifica que `is_active=True`

4. **Verifica el formato del dominio:**
   - No debe tener http://, https://, www.
   - Debe tener al menos un punto (ej: ejemplo.com)

### Error: "Domain already in use"

- Significa que otra franquicia ya tiene ese dominio asignado
- Cada dominio solo puede estar asignado a una franquicia

### El dominio funciona pero muestra contenido incorrecto

- Verifica que el middleware esté activo en `settings.py`
- Verifica que la franquicia tenga el dominio correcto asignado
- Limpia la caché del navegador

## 📚 Archivos Modificados

- `bingo_app/models.py`: Agregado campo `custom_domain` y método `get_by_domain()`
- `bingo_app/middleware.py`: Actualizado para detectar por dominio
- `bingo_app/admin.py`: Agregado campo en el admin con validación
- `bingo_project/settings.py`: Preparado para dominios dinámicos
- `bingo_app/migrations/0060_add_custom_domain_to_franchise.py`: Migración creada

## 🎯 Próximos Pasos

1. Ejecutar la migración:
   ```bash
   python manage.py migrate
   ```

2. Agregar dominios a las franquicias desde el admin

3. Configurar DNS y ALLOWED_HOSTS en Railway

4. ¡Listo! Los usuarios podrán acceder por dominio personalizado

---

**Fecha de implementación:** 17 de diciembre de 2025
**Versión:** 1.0

