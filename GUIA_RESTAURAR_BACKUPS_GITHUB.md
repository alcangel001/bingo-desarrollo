# 🔄 GUÍA SIMPLE: Cómo Restaurar Backups desde GitHub

## 📦 **BACKUPS DISPONIBLES EN GITHUB**

Tienes varios backups guardados en GitHub. Aquí te explico cómo restaurarlos:

---

## 🏷️ **BACKUPS POR TAGS (Más Fáciles de Usar)**

Los tags son como "marcadores" de versiones específicas. Tienes estos disponibles:

1. **`backup-antes-ia-20251104`** - Backup antes de implementar IA (4 Nov 2025)
2. **`backup-personalizacion-2025-01-26`** - Backup con personalización (26 Ene 2025)
3. **`backup-pre-ia-assistant-2025-10-24`** - Backup antes del asistente IA (24 Oct 2025)
4. **`backup-videollamadas-v1.0`** - Backup con sistema de videollamadas (14 Oct 2024)
5. **`v2025-10-04`** - Versión del 4 Oct 2025

### **Cómo restaurar desde un TAG:**

```powershell
# 1. Ver todos los tags disponibles
git tag

# 2. Crear una nueva rama desde el tag que quieras restaurar
# Por ejemplo, para restaurar el backup de videollamadas:
git checkout -b restaurar-desde-backup backup-videollamadas-v1.0

# 3. Si quieres que esta sea tu rama principal, puedes hacer:
git checkout version-mejorada
git reset --hard backup-videollamadas-v1.0
git push origin version-mejorada --force
```

---

## 🌿 **BACKUPS POR RAMAS (Más Recientes)**

Las ramas son versiones completas del código. Tienes estas ramas de backup:

1. **`backup-antes-ia-20251104-214604`** - Backup más reciente (4 Nov 2025)
2. **`backup-branch-2025-10-24`** - Backup del 24 Oct 2025
3. **`backup-estable-14oct2024`** - Backup estable (14 Oct 2024)
4. **`emergencia-rollback`** - Para emergencias
5. **`version-restaurada-2025-10-28`** - Versión restaurada (28 Oct 2025)

### **Cómo restaurar desde una RAMA:**

```powershell
# 1. Ver todas las ramas disponibles
git branch -a

# 2. Cambiar a la rama de backup que quieras
# Por ejemplo, el backup más reciente:
git checkout backup-antes-ia-20251104-214604

# 3. Si quieres hacer esta tu rama principal:
git checkout version-mejorada
git merge backup-antes-ia-20251104-214604
git push origin version-mejorada
```

---

## 🚨 **RESTAURACIÓN RÁPIDA EN CASO DE EMERGENCIA**

Si algo salió mal y necesitas restaurar YA:

```powershell
# Opción 1: Restaurar el backup más reciente
git checkout version-mejorada
git reset --hard backup-antes-ia-20251104-214604
git push origin version-mejorada --force

# Opción 2: Usar la rama de emergencia
git checkout version-mejorada
git reset --hard emergencia-rollback
git push origin version-mejorada --force
```

---

## 📋 **PASOS DETALLADOS PARA RESTAURAR**

### **Escenario: Quieres volver al backup de videollamadas**

```powershell
# Paso 1: Asegúrate de estar en la rama principal
git checkout version-mejorada

# Paso 2: Verifica qué cambios tienes (opcional, para no perder nada)
git status

# Paso 3: Restaura desde el tag
git reset --hard backup-videollamadas-v1.0

# Paso 4: Sube los cambios a GitHub
git push origin version-mejorada --force

# Paso 5: Railway se actualizará automáticamente
```

---

## 🔍 **VER QUÉ CONTIENE CADA BACKUP**

Antes de restaurar, puedes ver qué cambios tiene cada backup:

```powershell
# Ver los commits de un backup específico
git log backup-antes-ia-20251104-214604 --oneline -10

# Ver diferencias entre tu versión actual y un backup
git diff version-mejorada backup-antes-ia-20251104-214604

# Ver qué archivos cambiaron en un backup
git diff --name-only version-mejorada backup-antes-ia-20251104-214604
```

---

## ⚠️ **ADVERTENCIAS IMPORTANTES**

1. **`git push --force`** sobrescribe el historial. Úsalo solo si estás seguro.
2. **Railway se actualizará automáticamente** cuando hagas push a `version-mejorada`.
3. **La base de datos NO se restaura** con estos comandos. Solo el código.
4. **Haz un backup nuevo** antes de restaurar uno viejo.

---

## 💡 **RECOMENDACIONES**

### **Para restaurar código:**
- Usa los tags o ramas de backup que están en GitHub
- El código está seguro en GitHub

### **Para restaurar base de datos:**
- Usa los archivos `.sqlite3` que están en la carpeta `backups/`
- O los archivos ZIP que creamos con el script

### **Backup más reciente recomendado:**
- **`backup-antes-ia-20251104-214604`** - Es el más reciente (4 Nov 2025)

---

## 🎯 **EJEMPLO PRÁCTICO COMPLETO**

Imagina que algo salió mal y quieres volver al backup del 4 de Noviembre:

```powershell
# 1. Ve a tu proyecto
cd "C:\Users\DELL VOSTRO 7500\bingo-mejorado"

# 2. Asegúrate de tener los últimos cambios de GitHub
git fetch origin

# 3. Cambia a la rama principal
git checkout version-mejorada

# 4. Restaura desde el backup
git reset --hard origin/backup-antes-ia-20251104-214604

# 5. Sube los cambios
git push origin version-mejorada --force

# 6. Listo! Railway se actualizará en unos minutos
```

---

## 📞 **RESUMEN RÁPIDO**

- **Tags:** Marcadores de versiones específicas (más fáciles)
- **Ramas:** Versiones completas del código (más recientes)
- **Restaurar:** `git reset --hard nombre-del-backup`
- **Subir:** `git push origin version-mejorada --force`
- **Railway:** Se actualiza automáticamente

---

**Última actualización:** 13 de Noviembre de 2025  
**Backup más reciente:** `backup-antes-ia-20251104-214604`








