# 🔄 Cómo Resetear la Base de Datos en Railway

## ⚠️ Problema

La base de datos tiene una transacción abortada que está causando errores en las migraciones.

## ✅ Solución: Resetear la Base de Datos

### Opción 1: Eliminar y Recrear PostgreSQL (Recomendado)

1. **En Railway, ve a tu proyecto**
2. **Haz clic en tu servicio PostgreSQL**
3. **Ve a la pestaña "Settings"**
4. **Busca "Delete" o "Remove"**
5. **Confirma la eliminación** (⚠️ Esto borrará todos los datos)
6. **Crea una nueva base de datos PostgreSQL:**
   - Click en "+ New" o "+ Add Service"
   - Selecciona "Database"
   - Selecciona "Add PostgreSQL"
7. **Actualiza la variable DATABASE_URL:**
   - Ve a tu servicio de la aplicación (no PostgreSQL)
   - Ve a "Variables"
   - Busca `DATABASE_URL`
   - Haz clic en editar
   - Copia la nueva URL de PostgreSQL (ve a PostgreSQL → Variables → DATABASE_URL)
   - Pega la nueva URL
   - Guarda

8. **Redeploy tu aplicación:**
   - Ve a tu servicio de la aplicación
   - Ve a "Settings"
   - Click en "Redeploy" o "Deploy"

### Opción 2: Resetear desde Railway CLI (Alternativa)

Si tienes Railway CLI instalado:

```bash
railway connect
railway run python manage.py flush --noinput
railway run python manage.py migrate
```

---

## ✅ Después de Resetear

Una vez que resetees la base de datos:

1. **Las migraciones deberían ejecutarse correctamente**
2. **El servidor debería arrancar sin problemas**
3. **Necesitarás crear un superusuario nuevo**

---

## 📝 Crear Superusuario Después del Reset

1. En Railway, ve a tu servicio de la aplicación
2. Ve a "Settings" → "Run Command" o "Shell"
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones para crear el usuario

---

## ⚠️ IMPORTANTE

**Esto borrará TODOS los datos de la base de datos de desarrollo.**

Como es un entorno de desarrollo nuevo, esto está bien. No afecta tu producción.

---

## 🎯 Resumen

1. Eliminar PostgreSQL actual
2. Crear nueva base de datos PostgreSQL
3. Actualizar DATABASE_URL en variables
4. Redeploy aplicación
5. Crear superusuario

¡Listo! 🚀

