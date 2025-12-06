#!/usr/bin/env python3
"""
Script para verificar la configuración de SendGrid
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("VERIFICACIÓN DE CONFIGURACIÓN DE SENDGRID".center(70))
print("=" * 70)
print()

# 1. Verificar EMAIL_HOST_PASSWORD
email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')
sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
email_backend = getattr(settings, 'EMAIL_BACKEND', None)

print("1. VARIABLES DE ENTORNO:")
print("-" * 70)
if email_host_password:
    # Ocultar parte de la clave por seguridad
    if len(email_host_password) > 20:
        mostrar = email_host_password[:10] + "..." + email_host_password[-5:]
    else:
        mostrar = email_host_password[:5] + "..." if len(email_host_password) > 5 else "***"
    print(f"   EMAIL_HOST_PASSWORD: {mostrar}")
    
    # Verificar formato de API key de SendGrid
    if email_host_password.startswith('SG.'):
        print("   ✅ Formato correcto (empieza con 'SG.')")
        formato_ok = True
    else:
        print("   ⚠️  Formato sospechoso (no empieza con 'SG.')")
        print("      Las API keys de SendGrid normalmente empiezan con 'SG.'")
        formato_ok = False
else:
    print("   ❌ EMAIL_HOST_PASSWORD: NO configurado")
    formato_ok = False

print()

# 2. Verificar configuración de Django
print("2. CONFIGURACIÓN DE DJANGO:")
print("-" * 70)
if email_backend:
    print(f"   EMAIL_BACKEND: {email_backend}")
    if 'sendgrid' in email_backend.lower():
        print("   ✅ Usando SendGrid backend")
    else:
        print("   ⚠️  No está usando SendGrid backend")
else:
    print("   ❌ EMAIL_BACKEND: No configurado")

if sendgrid_api_key:
    if len(sendgrid_api_key) > 20:
        mostrar = sendgrid_api_key[:10] + "..." + sendgrid_api_key[-5:]
    else:
        mostrar = sendgrid_api_key[:5] + "..." if len(sendgrid_api_key) > 5 else "***"
    print(f"   SENDGRID_API_KEY (desde settings): {mostrar}")
    if sendgrid_api_key == email_host_password:
        print("   ✅ Coincide con EMAIL_HOST_PASSWORD")
    else:
        print("   ⚠️  NO coincide con EMAIL_HOST_PASSWORD")
else:
    print("   ❌ SENDGRID_API_KEY: No configurado en settings")

if default_from_email:
    print(f"   DEFAULT_FROM_EMAIL: {default_from_email}")
    print("   ✅ Configurado")
else:
    print("   ❌ DEFAULT_FROM_EMAIL: No configurado")

print()

# 3. Intentar prueba de conexión (opcional)
print("3. PRUEBA DE CONEXIÓN:")
print("-" * 70)
if email_host_password and formato_ok:
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail
        
        sg = sendgrid.SendGridAPIClient(api_key=email_host_password)
        
        # Intentar obtener información de la cuenta (prueba simple)
        # Esto no envía emails, solo verifica que la API key sea válida
        try:
            response = sg.client.api_keys.get()
            if response.status_code == 200:
                print("   ✅ API Key válida - Conexión exitosa con SendGrid")
                conexion_ok = True
            else:
                print(f"   ⚠️  Respuesta inesperada de SendGrid: {response.status_code}")
                conexion_ok = False
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                print("   ❌ API Key inválida o no autorizada")
            elif "403" in error_msg or "Forbidden" in error_msg:
                print("   ❌ API Key sin permisos suficientes")
            else:
                print(f"   ⚠️  Error al verificar: {error_msg}")
            conexion_ok = False
            
    except ImportError:
        print("   ⚠️  Librería 'sendgrid' no instalada")
        print("      Instalar con: pip install sendgrid")
        conexion_ok = None
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
        conexion_ok = False
else:
    print("   ⏭️  No se puede probar (falta API key o formato incorrecto)")
    conexion_ok = None

print()

# 4. Resumen final
print("=" * 70)
print("RESUMEN:")
print("=" * 70)

if email_host_password and formato_ok and conexion_ok:
    print("✅ SendGrid está CORRECTAMENTE configurado")
    print("   - API Key presente y con formato correcto")
    print("   - Conexión exitosa con SendGrid")
    print("   - Listo para enviar emails")
    sys.exit(0)
elif email_host_password and formato_ok and conexion_ok is None:
    print("⚠️  SendGrid PARCIALMENTE configurado")
    print("   - API Key presente y con formato correcto")
    print("   - No se pudo verificar la conexión (falta librería)")
    print("   - Probablemente funcione, pero no se verificó")
    sys.exit(0)
elif email_host_password and formato_ok:
    print("❌ SendGrid configurado pero API Key INVÁLIDA")
    print("   - API Key presente y con formato correcto")
    print("   - Pero la conexión falló (API key inválida o sin permisos)")
    print("   - Revisar la API key en SendGrid")
    sys.exit(1)
elif email_host_password:
    print("⚠️  SendGrid PARCIALMENTE configurado")
    print("   - EMAIL_HOST_PASSWORD existe pero formato sospechoso")
    print("   - Las API keys de SendGrid normalmente empiezan con 'SG.'")
    print("   - Verificar que sea una API key válida de SendGrid")
    sys.exit(1)
else:
    print("❌ SendGrid NO está configurado")
    print("   - EMAIL_HOST_PASSWORD no está configurado")
    print("   - No se pueden enviar emails")
    sys.exit(1)

print("=" * 70)







