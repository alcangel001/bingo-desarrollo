#!/usr/bin/env python3
"""
Script de diagnóstico para el problema del correo de bienvenida
"""
import os
import sys
import django
from datetime import timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.core.mail import send_mail

User = get_user_model()

print("=" * 80)
print("DIAGNÓSTICO: CORREO DE BIENVENIDA".center(80))
print("=" * 80)
print()

# 1. Verificar configuración de email
print("1. CONFIGURACIÓN DE EMAIL:")
print("-" * 80)
email_backend = getattr(settings, 'EMAIL_BACKEND', None)
sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')

print(f"   EMAIL_BACKEND: {email_backend}")
print(f"   DEFAULT_FROM_EMAIL: {default_from_email}")
print(f"   EMAIL_HOST_PASSWORD configurado: {'Sí' if email_host_password else 'No'}")
if email_host_password:
    masked = email_host_password[:10] + "..." + email_host_password[-5:] if len(email_host_password) > 15 else "***"
    print(f"   EMAIL_HOST_PASSWORD: {masked}")
print(f"   SENDGRID_API_KEY configurado: {'Sí' if sendgrid_api_key else 'No'}")

if not email_host_password:
    print("   ❌ ERROR: EMAIL_HOST_PASSWORD no está configurado")
    print("      Esto es necesario para enviar emails con SendGrid")
elif not default_from_email:
    print("   ❌ ERROR: DEFAULT_FROM_EMAIL no está configurado")
else:
    print("   ✅ Configuración básica OK")
print()

# 2. Probar envío de email
print("2. PRUEBA DE ENVÍO DE EMAIL:")
print("-" * 80)
if default_from_email and email_host_password:
    try:
        test_email = default_from_email  # Enviar a sí mismo para prueba
        print(f"   Enviando email de prueba a: {test_email}")
        result = send_mail(
            '🧪 Prueba de Email - Diagnóstico',
            'Este es un email de prueba del sistema de diagnóstico.',
            default_from_email,
            [test_email],
            fail_silently=False,
        )
        if result == 1:
            print("   ✅ Email de prueba enviado exitosamente")
            print("   ✅ SendGrid está funcionando correctamente")
        else:
            print(f"   ⚠️  Email no se envió (resultado: {result})")
    except Exception as e:
        print(f"   ❌ Error al enviar email de prueba: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
else:
    print("   ⏭️  No se puede probar (falta configuración)")
print()

# 3. Verificar últimos usuarios registrados
print("3. ÚLTIMOS USUARIOS REGISTRADOS:")
print("-" * 80)
recent_users = User.objects.filter(
    date_joined__gte=timezone.now() - timedelta(hours=24)
).order_by('-date_joined')[:5]

if recent_users.exists():
    for user in recent_users:
        time_ago = timezone.now() - user.date_joined
        minutes_ago = int(time_ago.total_seconds() / 60)
        
        # Verificar si tiene cuenta social
        social_accounts = SocialAccount.objects.filter(user=user)
        has_social = social_accounts.exists()
        provider = social_accounts.first().provider if has_social else None
        
        print(f"   Usuario: {user.username} ({user.email})")
        print(f"   Registrado: {minutes_ago} minutos atrás")
        print(f"   Método: {'Social (' + provider + ')' if has_social else 'Manual'}")
        print(f"   Tiene email: {'Sí' if user.email else 'No'}")
        
        # Verificar si debería haber recibido email
        is_new = time_ago < timedelta(minutes=2)
        print(f"   Debería recibir email: {'Sí (usuario nuevo)' if is_new else 'No (muy antiguo)'}")
        print()
else:
    print("   No hay usuarios registrados en las últimas 24 horas")
print()

# 4. Verificar el último usuario registrado en detalle
print("4. ANÁLISIS DEL ÚLTIMO USUARIO REGISTRADO:")
print("-" * 80)
last_user = User.objects.order_by('-date_joined').first()
if last_user:
    print(f"   Usuario: {last_user.username}")
    print(f"   Email: {last_user.email}")
    print(f"   ID: {last_user.pk}")
    print(f"   Fecha de registro: {last_user.date_joined}")
    
    time_ago = timezone.now() - last_user.date_joined
    minutes_ago = time_ago.total_seconds() / 60
    print(f"   Tiempo desde registro: {minutes_ago:.2f} minutos")
    
    # Verificar cuenta social
    social_accounts = SocialAccount.objects.filter(user=last_user)
    has_social = social_accounts.exists()
    if has_social:
        social_account = social_accounts.first()
        print(f"   Cuenta social: {social_account.provider}")
        print(f"   UID social: {social_account.uid}")
    
    # Simular la lógica del adapter
    print()
    print("   Simulando lógica del adapter:")
    
    # Verificar si existía antes
    if last_user.email:
        existing_before = User.objects.filter(
            email__iexact=last_user.email
        ).exclude(pk=last_user.pk).exists()
        print(f"   - Existía usuario con este email antes: {existing_before}")
    
    # Verificar si es nuevo según date_joined
    is_new_by_time = time_ago < timedelta(minutes=2)
    print(f"   - Es nuevo por tiempo (< 2 min): {is_new_by_time}")
    
    # Verificar condiciones para enviar email
    should_send = is_new_by_time and last_user.email and not existing_before
    print(f"   - Debería enviar email: {should_send}")
    
    if should_send:
        print()
        print("   ⚠️  El usuario DEBERÍA haber recibido email pero no lo recibió")
        print("   Posibles causas:")
        print("      - Error al enviar (revisar logs)")
        print("      - Email bloqueado por spam")
        print("      - Problema con SendGrid")
        print("      - El código no se ejecutó correctamente")
    elif not last_user.email:
        print("   ⚠️  El usuario no tiene email, no se puede enviar")
    elif existing_before:
        print("   ℹ️  El usuario ya existía, no se envía email de bienvenida")
    else:
        print("   ℹ️  El usuario es muy antiguo (> 2 minutos), no se envía email")
else:
    print("   No hay usuarios en la base de datos")
print()

# 5. Recomendaciones
print("5. RECOMENDACIONES:")
print("-" * 80)
if not email_host_password:
    print("   ❌ Configurar EMAIL_HOST_PASSWORD en Railway")
if not default_from_email:
    print("   ❌ Configurar DEFAULT_FROM_EMAIL en Railway")
if last_user and last_user.email and not email_host_password:
    print("   ❌ El problema es la configuración de SendGrid")
elif last_user and last_user.email and email_host_password:
    print("   ✅ La configuración parece correcta")
    print("   💡 Siguiente paso: Revisar los logs del servidor para ver errores")
    print("   💡 También verificar que el email no esté en spam")
    print("   💡 Probar registrando un nuevo usuario y revisar logs en tiempo real")

print()
print("=" * 80)
print("FIN DEL DIAGNÓSTICO".center(80))
print("=" * 80)






