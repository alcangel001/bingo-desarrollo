# 🔗 LINKS DEL SISTEMA DE FRANQUICIAS

**Dominio Base:** `https://web-production-14f41.up.railway.app`

---

## 👑 ADMINISTRADOR PRINCIPAL (Super Admin)

### 📦 Gestión de Paquetes y Precios
- **Editar Precios de Paquetes:**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/package-prices/
  ```
- **Restaurar Precios por Defecto:**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/package-prices/reset/
  ```

### 🏪 Gestión de Franquicias
- **Lista de Franquicias:**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/franchises/
  ```
- **Crear Nueva Franquicia:**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/franchises/create/
  ```
- **Ver Detalle de Franquicia (reemplazar `<franchise_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/franchises/<franchise_id>/
  ```
- **Editar Franquicia (reemplazar `<franchise_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/franchises/<franchise_id>/edit/
  ```
- **Cambiar Imagen de Franquicia (reemplazar `<franchise_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/admin-panel/franchises/<franchise_id>/change-image/
  ```

---

## 👨‍💼 PROPIETARIO DE FRANQUICIA

### 📊 Panel Principal
- **Dashboard de Franquicia:**
  ```
  https://web-production-14f41.up.railway.app/franchise/dashboard/
  ```

### 💳 Gestión de Solicitudes de Crédito
- **Lista de Solicitudes de Crédito:**
  ```
  https://web-production-14f41.up.railway.app/franchise/credit-requests/
  ```
- **Procesar Solicitud de Crédito (reemplazar `<request_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/franchise/credit-requests/<request_id>/process/
  ```

### 💰 Gestión de Solicitudes de Retiro
- **Lista de Solicitudes de Retiro:**
  ```
  https://web-production-14f41.up.railway.app/franchise/withdrawal-requests/
  ```
- **Procesar Solicitud de Retiro (reemplazar `<request_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/franchise/withdrawal-requests/<request_id>/process/
  ```

### 🏦 Gestión de Cuentas Bancarias
- **Lista de Cuentas Bancarias:**
  ```
  https://web-production-14f41.up.railway.app/franchise/bank-accounts/
  ```
- **Crear Nueva Cuenta Bancaria:**
  ```
  https://web-production-14f41.up.railway.app/franchise/bank-accounts/create/
  ```
- **Editar Cuenta Bancaria (reemplazar `<account_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/franchise/bank-accounts/<account_id>/edit/
  ```
- **Eliminar Cuenta Bancaria (reemplazar `<account_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/franchise/bank-accounts/<account_id>/delete/
  ```
- **Activar/Desactivar Cuenta Bancaria (reemplazar `<account_id>` con el ID):**
  ```
  https://web-production-14f41.up.railway.app/franchise/bank-accounts/<account_id>/toggle/
  ```

---

## 👥 CLIENTES DE FRANQUICIA

### 🎯 Landing Page de Franquicia
- **Página de Inicio de Franquicia (reemplazar `<franchise_slug>` con el slug de la franquicia):**
  ```
  https://web-production-14f41.up.railway.app/franchise/<franchise_slug>/
  ```
  
  **Ejemplo:** Si el slug es `jenirecano`:
  ```
  https://web-production-14f41.up.railway.app/franchise/jenirecano/
  ```

### 🔐 Registro y Login con Franquicia
- **Registro (con código de franquicia en URL):**
  ```
  https://web-production-14f41.up.railway.app/register/?franchise=<franchise_slug>
  ```
  
  **Ejemplo:**
  ```
  https://web-production-14f41.up.railway.app/register/?franchise=jenirecano
  ```

- **Login (con código de franquicia en URL):**
  ```
  https://web-production-14f41.up.railway.app/login/?franchise=<franchise_slug>
  ```
  
  **Ejemplo:**
  ```
  https://web-production-14f41.up.railway.app/login/?franchise=jenirecano
  ```

---

## 📝 NOTAS IMPORTANTES

1. **Reemplazar IDs:** En las URLs que tienen `<franchise_id>`, `<request_id>`, o `<account_id>`, debes reemplazar estos valores con los IDs reales de la base de datos.

2. **Reemplazar Slugs:** En las URLs que tienen `<franchise_slug>`, debes usar el slug de la franquicia (ejemplo: `jenirecano`).

3. **Acceso:** 
   - Las URLs de **Super Admin** solo son accesibles para usuarios con `is_superuser=True`
   - Las URLs de **Propietario de Franquicia** solo son accesibles para usuarios que tienen una franquicia asignada (`owned_franchise`)
   - Las URLs de **Clientes** son públicas y accesibles para todos

4. **Dominio:** Si cambias el dominio de Railway, actualiza todas las URLs reemplazando `web-production-14f41.up.railway.app` con el nuevo dominio.

---

## 🚀 ACCESO RÁPIDO

### Para Super Admin:
1. Ir a: `https://web-production-14f41.up.railway.app/admin-panel/franchises/`
2. Crear/editar franquicias desde ahí

### Para Propietario de Franquicia:
1. Iniciar sesión con tu cuenta de propietario
2. Ir a: `https://web-production-14f41.up.railway.app/franchise/dashboard/`
3. Desde ahí acceder a todas las opciones

### Para Compartir con Clientes:
1. Obtener el slug de la franquicia (ejemplo: `jenirecano`)
2. Compartir: `https://web-production-14f41.up.railway.app/franchise/jenirecano/`

---

**Última actualización:** Diciembre 2025

