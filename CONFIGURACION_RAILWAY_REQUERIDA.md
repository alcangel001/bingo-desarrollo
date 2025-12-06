#!/usr/bin/env python
"""
Script para verificar qué variables de entorno están configuradas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')

# Lista de variables requeridas
REQUIRED_VARS = {
    'obligatorias': [
        ('DATABASE_URL', 'Base de datos PostgreSQL'),
        ('REDIS_URL', 'Redis para WebSockets'),
        ('SECRET_KEY', 'Clave secreta de Django'),
        ('ALLOWED_HOSTS', 'Dominios permitidos'),
    ],
    'importantes': [
        ('SENDGRID_API_KEY', 'Envío de emails (SendGrid)'),
        ('DEFAULT_FROM_EMAIL', 'Email remitente'),
    ],
    'opcionales': [
        ('GOOGLE_CLIENT_ID', 'Login con Google'),
        ('GOOGLE_SECRET', 'Login con Google'),
        ('FACEBOOK_CLIENT_ID', 'Login con Facebook'),
        ('FACEBOOK_SECRET', 'Login con Facebook'),
        ('AGORA_APP_ID', 'Videollamadas'),
        ('AGORA_APP_CERTIFICATE', 'Videollamadas'),
        ('SENTRY_DSN', 'Monitoreo de errores'),
        ('RAILWAY_PUBLIC_DOMAIN', 'Dominio público (auto)'),
        ('CSRF_TRUSTED_ORIGINS', 'Protección CSRF'),
    ]
}

def verificar_variable(var_name):
    """Verifica si una variable está configurada"""
    valor = os.environ.get(var_name)
    if valor:
        # Ocultar parte del valor por seguridad
        if len(valor) > 20:
            mostrar = valor[:10] + "..." + valor[-5:]
        else:
            mostrar = valor[:5] + "..." if len(valor) > 5 else "***"
        return True, mostrar
    return False, None

print("\n" + "="*70)
print("VERIFICACIÓN DE VARIABLES DE ENTORNO PARA RAILWAY".center(70))
print("="*70)

# Verificar obligatorias
print("\n🔴 VARIABLES OBLIGATORIAS:")
print("-"*70)
obligatorias_faltantes = 0
for var, descripcion in REQUIRED_VARS['obligatorias']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"✅ {var:<25} → {descripcion}")
        print(f"   Valor: {valor}")
    else:
        print(f"❌ {var:<25} → {descripcion}")
        print(f"   ⚠️  FALTA - Debes configurarla")
        obligatorias_faltantes += 1

# Verificar importantes
print("\n🟡 VARIABLES IMPORTANTES (Según funcionalidades):")
print("-"*70)
for var, descripcion in REQUIRED_VARS['importantes']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"✅ {var:<25} → {descripcion}")
        print(f"   Valor: {valor}")
    else:
        print(f"⚠️  {var:<25} → {descripcion}")
        print(f"   Sin configurar - Emails NO funcionarán")

# Verificar opcionales
print("\n🟢 VARIABLES OPCIONALES:")
print("-"*70)
for var, descripcion in REQUIRED_VARS['opcionales']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"✅ {var:<25} → {descripcion}")
    else:
        print(f"○  {var:<25} → {descripcion} (No configurada)")

# Resumen
print("\n" + "="*70)
print("RESUMEN:")
print("="*70)

if obligatorias_faltantes == 0:
    print("✅ Todas las variables obligatorias están configuradas")
    print("🟢 SISTEMA LISTO PARA FUNCIONAR")
else:
    print(f"❌ Faltan {obligatorias_faltantes} variables obligatorias")
    print("🔴 SISTEMA NO FUNCIONARÁ hasta configurarlas")

print("\n" + "="*70)
print("\nPara configurar variables en Railway:")
print("  railway variables set NOMBRE_VARIABLE=\"valor\"")
print("\nPara ver todas las variables actuales:")
print("  railway variables list")
print("="*70 + "\n")

