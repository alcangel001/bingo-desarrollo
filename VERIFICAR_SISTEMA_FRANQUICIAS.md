# ✅ Guía para Verificar el Sistema de Franquicias

## 🔍 Pasos de Verificación

### 1. **Verificar que los Paquetes estén Inicializados**

**Opción A: Desde el Admin de Django**
1. Accede a: `https://tu-dominio-railway.app/admin/`
2. Inicia sesión como super admin
3. Ve a la sección **"Bingo App"**
4. Deberías ver:
   - ✅ **Plantillas de Paquetes** (PackageTemplate) - Debe tener 4 paquetes
   - ✅ **Franquicias** (Franchise)
   - ✅ **Manuales de Franquicias** (FranchiseManual)

**Opción B: Desde el Panel de Precios**
1. Accede a: `https://tu-dominio-railway.app/admin-panel/package-prices/`
2. Deberías ver 4 paquetes:
   - 🎲 Básico Bingo ($30/mes + 5%)
   - 🎲 PRO Bingo ($80/mes + 3%)
   - 🎫 Básico Rifa ($30/mes + 5%)
   - 🎫 PRO Rifa ($80/mes + 3%)

---

### 2. **Verificar Panel de Gestión de Franquicias**

1. Accede como **super admin**
2. Ve a: `https://tu-dominio-railway.app/admin-panel/franchises/`
3. Deberías ver:
   - Lista vacía (si no has creado franquicias aún)
   - Botón "Crear Nueva Franquicia"

---

### 3. **Crear una Franquicia de Prueba**

1. Ve a: `https://tu-dominio-railway.app/admin-panel/franchises/create/`
2. Completa el formulario:
   - **Nombre**: "Franquicia de Prueba"
   - **Slug**: "franquicia-prueba"
   - **Usuario Propietario**: Username de un usuario existente (que NO tenga ya una franquicia)
   - **Paquete**: Selecciona uno de los 4 paquetes
3. Haz clic en "Crear Franquicia"
4. Deberías ser redirigido a la página de detalles de la franquicia

---

### 4. **Verificar Detalles de la Franquicia**

1. En la página de detalles deberías ver:
   - ✅ Información general (nombre, propietario, paquete, precios)
   - ✅ Estadísticas (0 juegos, 0 rifas, 1 usuario, etc.)
   - ✅ Botones para editar y cambiar imágenes

---

### 5. **Verificar que el Usuario Propietario fue Actualizado**

1. Ve al Admin de Django: `/admin/bingo_app/user/`
2. Busca el usuario que asignaste como propietario
3. Verifica que:
   - ✅ Tiene `is_organizer = True`
   - ✅ Tiene `franchise` asignada
   - ✅ Tiene `owned_franchise` (relación OneToOne)

---

### 6. **Verificar Panel de Precios**

1. Ve a: `https://tu-dominio-railway.app/admin-panel/package-prices/`
2. Deberías poder:
   - ✅ Ver los 4 paquetes con sus precios actuales
   - ✅ Editar los precios (cambiar valores)
   - ✅ Guardar cambios
   - ✅ Restaurar precios por defecto

---

### 7. **Verificar desde la Base de Datos (Opcional)**

Si tienes acceso a la base de datos PostgreSQL en Railway:

```sql
-- Verificar que los paquetes fueron creados
SELECT * FROM bingo_app_packagetemplate;

-- Deberías ver 4 filas:
-- BASIC_BINGO, PRO_BINGO, BASIC_RAFFLE, PRO_RAFFLE

-- Verificar franquicias creadas
SELECT * FROM bingo_app_franchise;

-- Verificar que el usuario tiene franquicia asignada
SELECT username, is_organizer, franchise_id 
FROM bingo_app_user 
WHERE franchise_id IS NOT NULL;
```

---

## 🎯 Checklist de Verificación Completa

- [ ] Los 4 paquetes están creados en el admin
- [ ] El panel de precios (`/admin-panel/package-prices/`) funciona
- [ ] Puedo acceder a la lista de franquicias (`/admin-panel/franchises/`)
- [ ] Puedo crear una nueva franquicia
- [ ] La franquicia se crea correctamente
- [ ] El usuario propietario fue actualizado (is_organizer = True, franchise asignada)
- [ ] Puedo ver los detalles de la franquicia
- [ ] Puedo editar la información de la franquicia
- [ ] Puedo cambiar el logo/imagen de la franquicia

---

## 🐛 Si Algo No Funciona

### Error: "No tienes permisos"
- **Solución**: Asegúrate de estar logueado como **super admin** (`is_superuser = True`)

### Error: "Usuario ya tiene una franquicia"
- **Solución**: El usuario que intentas asignar ya es propietario de otra franquicia. Usa otro usuario.

### Error: "Paquete no encontrado"
- **Solución**: Ejecuta manualmente: `python manage.py setup_package_templates`

### Los paquetes no aparecen
- **Solución**: Ve a Railway → Run Command → Ejecuta: `python manage.py setup_package_templates`

---

## 📝 Notas Importantes

1. **Solo super admins** pueden crear/editar franquicias
2. **Cada usuario** solo puede ser propietario de **una** franquicia
3. Los **precios** se pueden editar desde el panel de precios
4. Las **funcionalidades** de los paquetes están preconfiguradas y no se pueden cambiar

---

## 🚀 Próximos Pasos

Una vez verificado que todo funciona:
1. Crear más franquicias de prueba
2. Asignar usuarios a franquicias
3. Probar el middleware (cada franquicia solo ve sus datos)
4. Implementar el panel para franquiciado




