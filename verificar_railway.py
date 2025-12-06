#!/usr/bin/env python
"""
Script para verificar qué variables de entorno están configuradas
"""

import os

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
        ('EMAIL_HOST_PASSWORD', 'Password de SendGrid (alias)'),
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
        ('RAILWAY_ENVIRONMENT', 'Entorno de Railway (auto)'),
        ('CSRF_TRUSTED_ORIGINS', 'Protección CSRF'),
        ('DEBUG', 'Modo debug'),
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
print("\n[OBLIGATORIAS] VARIABLES OBLIGATORIAS:")
print("-"*70)
obligatorias_faltantes = []
for var, descripcion in REQUIRED_VARS['obligatorias']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"[OK] {var:<30} -> {descripcion}")
        print(f"     Valor: {valor}")
    else:
        print(f"[FALTA] {var:<30} -> {descripcion}")
        print(f"        Debes configurarla en Railway")
        obligatorias_faltantes.append(var)

# Verificar importantes
print("\n[IMPORTANTES] VARIABLES IMPORTANTES (Recomendadas):")
print("-"*70)
importantes_faltantes = []
for var, descripcion in REQUIRED_VARS['importantes']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"[OK] {var:<30} -> {descripcion}")
        print(f"     Valor: {valor}")
    else:
        print(f"[WARN] {var:<30} -> {descripcion}")
        print(f"       Sin configurar - Funcionalidad limitada")
        importantes_faltantes.append(var)

# Verificar opcionales
print("\n[OPCIONALES] VARIABLES OPCIONALES:")
print("-"*70)
opcionales_configuradas = 0
for var, descripcion in REQUIRED_VARS['opcionales']:
    configurada, valor = verificar_variable(var)
    if configurada:
        print(f"[OK] {var:<30} -> {descripcion}")
        opcionales_configuradas += 1
    else:
        print(f"[ ] {var:<30} -> {descripcion}")

# Resumen
print("\n" + "="*70)
print("RESUMEN:")
print("="*70)

if not obligatorias_faltantes:
    print("[OK] Todas las variables OBLIGATORIAS estan configuradas")
    print("[OK] Sistema puede funcionar en Railway")
else:
    print(f"[ERROR] Faltan {len(obligatorias_faltantes)} variables OBLIGATORIAS:")
    for var in obligatorias_faltantes:
        print(f"   - {var}")
    print("[ERROR] Sistema NO funcionara hasta configurarlas")

if importantes_faltantes:
    print(f"\n[ADVERTENCIA] {len(importantes_faltantes)} variables IMPORTANTES sin configurar:")
    for var in importantes_faltantes:
        print(f"   - {var}")
    print("   Algunas funcionalidades estaran limitadas")

print(f"\n[INFO] {opcionales_configuradas}/{len(REQUIRED_VARS['opcionales'])} variables opcionales configuradas")

print("\n" + "="*70)
print("COMANDOS UTILES:")
print("="*70)
print("\nPara CONFIGURAR una variable en Railway:")
print("   railway variables set NOMBRE_VARIABLE=\"valor\"")
print("\nPara VER todas las variables actuales:")
print("   railway variables list")
print("\nPara GENERAR SECRET_KEY segura:")
print("   python -c \"import secrets; print(secrets.token_urlsafe(50))\"")
print("="*70 + "\n")

