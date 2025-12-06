#!/usr/bin/env python3
"""
Verificación Final de Lanzamiento - Bingo JyM
Verifica los puntos críticos antes de abrir al público
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from django.conf import settings
from django.db import connection
from bingo_app.models import PercentageSettings, BankAccount, User

print("=" * 70)
print("VERIFICACIÓN FINAL DE LANZAMIENTO".center(70))
print("=" * 70)
print()

checks_passed = 0
checks_failed = 0
checks_warning = 0

# 1. Verificar DEBUG
print("1. SEGURIDAD:")
print("-" * 70)
debug = getattr(settings, 'DEBUG', True)
if debug:
    print("   ❌ DEBUG=True (DEBE estar en False para producción)")
    checks_failed += 1
else:
    print("   ✅ DEBUG=False (correcto)")
    checks_passed += 1

# 2. Verificar SECRET_KEY
secret_key = getattr(settings, 'SECRET_KEY', '')
if secret_key.startswith('django-insecure-dev-key'):
    print("   ❌ SECRET_KEY es la de desarrollo (INSEGURO)")
    checks_failed += 1
else:
    print("   ✅ SECRET_KEY configurada correctamente")
    checks_passed += 1

# 3. Verificar ALLOWED_HOSTS
allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
if allowed_hosts:
    print(f"   ✅ ALLOWED_HOSTS configurado ({len(allowed_hosts)} dominio(s))")
    checks_passed += 1
else:
    print("   ❌ ALLOWED_HOSTS no configurado")
    checks_failed += 1

# 4. Verificar HTTPS
csrf_secure = getattr(settings, 'CSRF_COOKIE_SECURE', False)
session_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
if csrf_secure and session_secure:
    print("   ✅ HTTPS configurado (cookies seguras)")
    checks_passed += 1
else:
    print("   ⚠️  HTTPS no completamente configurado")
    checks_warning += 1

print()

# 5. Verificar Base de Datos
print("2. BASE DE DATOS:")
print("-" * 70)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("   ✅ Conexión a base de datos: OK")
            checks_passed += 1
        else:
            print("   ❌ Error de conexión a base de datos")
            checks_failed += 1
except Exception as e:
    print(f"   ❌ Error de conexión: {str(e)}")
    checks_failed += 1

print()

# 6. Verificar PercentageSettings
print("3. CONFIGURACIÓN DE NEGOCIO:")
print("-" * 70)
try:
    percentage_settings = PercentageSettings.objects.first()
    if percentage_settings:
        print(f"   ✅ PercentageSettings configurado")
        print(f"      - Comisión plataforma: {percentage_settings.platform_commission}%")
        checks_passed += 1
    else:
        print("   ❌ PercentageSettings NO configurado")
        print("      ⚠️  CRÍTICO: Debes configurarlo antes de lanzar")
        print("      Ir a: /admin/bingo_app/percentagesettings/add/")
        checks_failed += 1
except Exception as e:
    print(f"   ❌ Error verificando PercentageSettings: {str(e)}")
    checks_failed += 1

# 7. Verificar Métodos de Pago
try:
    active_methods = BankAccount.objects.filter(is_active=True)
    all_methods = BankAccount.objects.all()
    
    if not all_methods.exists():
        print("   ❌ No hay métodos de pago configurados")
        print("      ⚠️  CRÍTICO: Debes configurar al menos uno antes de lanzar")
        print("      Ir a: /admin/bingo_app/bankaccount/add/")
        checks_failed += 1
    elif not active_methods.exists():
        print(f"   ⚠️  Hay {all_methods.count()} método(s) pero NINGUNO activo")
        print("      ⚠️  CRÍTICO: Debes activar al menos uno antes de lanzar")
        checks_failed += 1
    else:
        print(f"   ✅ {active_methods.count()} método(s) de pago activo(s)")
        for method in active_methods:
            print(f"      - {method.title}")
        checks_passed += 1
except Exception as e:
    print(f"   ❌ Error verificando métodos de pago: {str(e)}")
    checks_failed += 1

# 8. Verificar Superusuario
try:
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"   ✅ {superusers.count()} superusuario(s) configurado(s)")
        checks_passed += 1
    else:
        print("   ❌ No hay superusuarios configurados")
        print("      ⚠️  CRÍTICO: Debes crear uno antes de lanzar")
        print("      Ejecutar: python manage.py createsuperuser")
        checks_failed += 1
except Exception as e:
    print(f"   ❌ Error verificando superusuarios: {str(e)}")
    checks_failed += 1

print()

# 9. Verificar Variables de Entorno Críticas
print("4. VARIABLES DE ENTORNO:")
print("-" * 70)
critical_vars = {
    'DATABASE_URL': 'Base de datos',
    'REDIS_URL': 'Redis',
    'SECRET_KEY': 'Clave secreta',
    'ALLOWED_HOSTS': 'Dominios permitidos',
}

all_vars_ok = True
for var, desc in critical_vars.items():
    value = os.environ.get(var)
    if value:
        print(f"   ✅ {var}: Configurado")
        checks_passed += 1
    else:
        print(f"   ❌ {var}: NO configurado ({desc})")
        checks_failed += 1
        all_vars_ok = False

print()

# Resumen Final
print("=" * 70)
print("RESUMEN FINAL:")
print("=" * 70)
print(f"✅ Verificaciones exitosas: {checks_passed}")
print(f"⚠️  Advertencias: {checks_warning}")
print(f"❌ Verificaciones fallidas: {checks_failed}")
print()

if checks_failed == 0:
    print("🎉 ¡TODO ESTÁ LISTO PARA LANZAR!")
    print("   Todos los puntos críticos están verificados.")
    print("   Puedes abrir el juego al público.")
    sys.exit(0)
elif checks_failed <= 2:
    print("⚠️  CASI LISTO - FALTAN ALGUNOS AJUSTES")
    print("   Revisa los items marcados con ❌ arriba.")
    print("   Son críticos para el funcionamiento correcto.")
    sys.exit(1)
else:
    print("❌ NO ESTÁ LISTO PARA LANZAR")
    print("   Hay varios problemas críticos que deben resolverse.")
    print("   Revisa todos los items marcados con ❌ arriba.")
    sys.exit(1)







