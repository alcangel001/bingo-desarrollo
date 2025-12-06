# ✅ CHECKLIST DE LANZAMIENTO RÁPIDO

## 🚨 ANTES DE LANZAR (OBLIGATORIO)

### 🔴 CRÍTICO - Hacer HOY (3-4 horas)

- [ ] **1. Validar saldo negativo**
  - Archivo: `bingo_app/models.py`
  - Agregar `MinValueValidator(Decimal('0.00'))` a `credit_balance`
  - Crear migración: `python manage.py makemigrations`
  - Aplicar: `python manage.py migrate`

- [ ] **2. Validar saldo antes de descontar**
  - Archivo: `bingo_app/views.py`
  - Funciones: `game_room`, `buy_card`, `buy_multiple_cards`, `buy_ticket`, `create_game`, `create_raffle`
  - Agregar: `if user.credit_balance < amount: raise error`

- [ ] **3. Transacciones atómicas**
  - Funciones: `buy_card`, `game_room`
  - Envolver en: `with transaction.atomic():`
  - Usar: `User.objects.select_for_update()`

- [ ] **4. Validar SECRET_KEY**
  - Archivo: `bingo_project/settings.py`
  - Agregar validación: `if not SECRET_KEY: raise ValueError(...)`

- [ ] **5. Rate limiting**
  - Instalar: `pip install django-ratelimit`
  - Aplicar a: `register`, `request_credits`, `create_game`

---

### 🟡 IMPORTANTE - Hacer esta semana

- [ ] **6. Validar archivos subidos**
  - Archivo: `bingo_app/forms.py`
  - Máximo 5MB
  - Solo JPG, PNG, PDF

- [ ] **7. Probar flujos críticos**
  - Compra de cartones sin saldo → debe fallar
  - Retiro mayor al saldo → debe fallar
  - Creación de juego sin saldo → debe fallar

- [ ] **8. Configurar variables de entorno en Railway**
  - DATABASE_URL
  - REDIS_URL
  - SECRET_KEY (generar nueva)
  - SENDGRID_API_KEY
  - ALLOWED_HOSTS
  - CSRF_TRUSTED_ORIGINS

- [ ] **9. Backup de producción**
  - Hacer backup de la base de datos actual
  - Guardar en lugar seguro

- [ ] **10. Documentación de usuario**
  - Manual de uso básico
  - Cómo comprar créditos
  - Cómo jugar
  - Cómo retirar

---

## 🧪 TESTING ANTES DE LANZAR

### Tests funcionales:

- [ ] **Login/Registro**
  - Crear cuenta nueva
  - Login exitoso
  - Login fallido (contraseña incorrecta)

- [ ] **Compra de créditos**
  - Solicitar compra
  - Admin aprueba
  - Créditos se acreditan

- [ ] **Compra de cartones**
  - Con saldo suficiente → OK
  - Sin saldo suficiente → Error

- [ ] **Juego de bingo**
  - Crear juego
  - Unirse al juego
  - Comprar cartones
  - Iniciar juego
  - Cantar bingo
  - Recibir premio

- [ ] **Rifas**
  - Crear rifa
  - Comprar tickets
  - Sortear
  - Recibir premio

- [ ] **Retiro de créditos**
  - Solicitar retiro
  - Admin procesa
  - Créditos se descuentan

- [ ] **Sistema de toggles**
  - Desactivar referidos → enlace desaparece
  - Desactivar promociones → enlace desaparece
  - Reactivar → enlaces aparecen

---

## 🔧 CONFIGURACIÓN DE RAILWAY

### Variables de entorno obligatorias:

```bash
railway variables set DATABASE_URL="postgresql://..."
railway variables set REDIS_URL="redis://..."
railway variables set SECRET_KEY="[generar con: python -c 'import secrets; print(secrets.token_urlsafe(50))']"
railway variables set SENDGRID_API_KEY="SG...."
railway variables set DEFAULT_FROM_EMAIL="noreply@tudominio.com"
railway variables set ALLOWED_HOSTS="tudominio.railway.app,tudominio.com"
railway variables set CSRF_TRUSTED_ORIGINS="https://tudominio.railway.app,https://tudominio.com"
railway variables set DEBUG="False"
```

### Variables opcionales:

```bash
railway variables set GOOGLE_CLIENT_ID="..."
railway variables set GOOGLE_SECRET="..."
railway variables set FACEBOOK_CLIENT_ID="..."
railway variables set FACEBOOK_SECRET="..."
railway variables set AGORA_APP_ID="..."
railway variables set AGORA_APP_CERTIFICATE="..."
railway variables set SENTRY_DSN="..."
```

---

## 📊 MONITOREO POST-LANZAMIENTO

### Primera hora:
- [ ] Verificar que el sitio carga
- [ ] Probar login
- [ ] Monitorear logs en Railway
- [ ] Verificar Sentry (sin errores)

### Primer día:
- [ ] Revisar transacciones
- [ ] Verificar saldos de usuarios
- [ ] Monitorear errores en Sentry
- [ ] Responder a feedback de usuarios

### Primera semana:
- [ ] Análisis de uso
- [ ] Identificar problemas
- [ ] Ajustes según feedback
- [ ] Monitoreo intensivo

---

## 🚀 PROCESO DE LANZAMIENTO

### Día del lanzamiento:

1. **08:00** - Backup final de producción
2. **09:00** - Deploy de cambios críticos
3. **10:00** - Testing completo en producción
4. **11:00** - Soft launch (invitar usuarios beta)
5. **14:00** - Monitoreo y ajustes
6. **17:00** - Lanzamiento público (si todo OK)
7. **20:00** - Revisión del día

### Post-lanzamiento:

- Monitoreo 24/7 primera semana
- Respuesta rápida a problemas
- Backup diario
- Análisis de métricas

---

## 📝 DOCUMENTOS RELACIONADOS

- `AUDITORIA_PRE_LANZAMIENTO_22OCT2025.md` - Auditoría completa
- `SOLUCION_PROBLEMAS_CRITICOS.md` - Guía de implementación
- `INFO_BACKUP_22OCT2025.md` - Información del backup

---

## ⚠️ SEÑALES DE ALERTA

Si ves esto, **DETÉN EL LANZAMIENTO**:

- ❌ Usuarios con saldo negativo
- ❌ Transacciones duplicadas
- ❌ Errores 500 frecuentes
- ❌ Pérdida de créditos sin explicación
- ❌ WebSockets no funcionando
- ❌ Premios no se pagan

---

## ✅ CRITERIOS DE ÉXITO

El lanzamiento es exitoso si:

- ✅ No hay errores críticos en 24 horas
- ✅ Todas las transacciones son correctas
- ✅ Usuarios pueden jugar sin problemas
- ✅ No hay quejas de pérdida de créditos
- ✅ Sistema de pagos funciona
- ✅ Performance es aceptable

---

## 🔄 ROLLBACK

Si algo sale muy mal:

```bash
# 1. Restaurar código anterior
git revert <commit-hash>
git push origin version-mejorada

# 2. Restaurar base de datos desde backup
railway run python manage.py dbshell < backup.sql

# 3. Notificar a usuarios
```

---

## 📞 CONTACTOS DE EMERGENCIA

- **Admin Principal:** [Tu info]
- **Soporte Técnico:** [Tu info]
- **Railway Support:** https://railway.app/help

---

**Estado:** ⚠️ **NO LANZAR AÚN** - Completar checklist primero

**Última actualización:** 22 Oct 2025
