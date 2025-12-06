#!/usr/bin/env python
"""Script para verificar el estado de los toggles del sistema"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import PercentageSettings, BingoTicketSettings

print("=" * 60)
print("ESTADO DE LOS TOGGLES DEL SISTEMA")
print("=" * 60)

# Verificar PercentageSettings
percentage_settings = PercentageSettings.objects.first()
if percentage_settings:
    print("\n📊 CONFIGURACIÓN DEL SISTEMA (PercentageSettings):")
    print(f"  ✓ Referidos activos: {percentage_settings.referral_system_enabled}")
    print(f"  ✓ Promociones activas: {percentage_settings.promotions_enabled}")
    print(f"  ✓ Compra de créditos activa: {percentage_settings.credits_purchase_enabled}")
    print(f"  ✓ Retiro de créditos activo: {percentage_settings.credits_withdrawal_enabled}")
else:
    print("\n❌ No existe configuración de PercentageSettings")

# Verificar BingoTicketSettings
ticket_settings = BingoTicketSettings.get_settings()
if ticket_settings:
    print(f"\n🎫 CONFIGURACIÓN DE TICKETS (BingoTicketSettings):")
    print(f"  ✓ Sistema de tickets activo: {ticket_settings.is_system_active}")
    print(f"  ✓ Tickets por referido: {ticket_settings.referral_ticket_bonus}")
    print(f"  ✓ Días de expiración: {ticket_settings.ticket_expiration_days}")
else:
    print("\n❌ No existe configuración de BingoTicketSettings")

# Simular el context processor
from bingo_app.context_processors import system_settings_processor

class FakeRequest:
    pass

req = FakeRequest()
context = system_settings_processor(req)

print(f"\n🔧 CONTEXT PROCESSOR (lo que ve el template):")
for key, value in context['system_settings'].items():
    status = "✅ ACTIVO" if value else "❌ DESACTIVADO"
    print(f"  {key}: {status}")

print("\n" + "=" * 60)
print("Si 'ticket_system_enabled' está ACTIVO pero no ves los enlaces:")
print("1. Recarga la página con Ctrl+F5")
print("2. Cierra sesión y vuelve a iniciar")
print("3. Abre en ventana de incógnito")
print("4. Reinicia el servidor de desarrollo")
print("=" * 60)


