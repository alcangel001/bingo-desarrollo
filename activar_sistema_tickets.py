#!/usr/bin/env python3
"""
Script para ACTIVAR el sistema de tickets de bingo para referidos
También configura los horarios de bingos diarios gratuitos
"""

import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import BingoTicketSettings, DailyBingoSchedule

# Activar sistema de tickets
settings = BingoTicketSettings.get_settings()
settings.is_system_active = True
settings.referral_ticket_bonus = 1  # 1 ticket para el referidor
settings.referred_ticket_bonus = 1  # 1 ticket para el referido
settings.ticket_expiration_days = 7  # Los tickets expiran en 7 días
settings.save()

print("✅ Sistema de tickets ACTIVADO")
print("\nConfiguración de referidos:")
print(f"  - Tickets para referidor: {settings.referral_ticket_bonus}")
print(f"  - Tickets para referido: {settings.referred_ticket_bonus}")
print(f"  - Días de expiración: {settings.ticket_expiration_days}")

# Configurar horarios de bingos diarios (si no existen)
horarios = [
    ('09:00', '9:00 AM', 50, Decimal('10.00'), 'Bingo Matutino Gratuito'),
    ('14:00', '2:00 PM', 50, Decimal('15.00'), 'Bingo Vespertino Gratuito'),
    ('19:00', '7:00 PM', 100, Decimal('20.00'), 'Bingo Nocturno Gratuito - Premio Mayor'),
]

print("\n📅 Configurando horarios de bingos diarios...")
for time_slot, display, max_players, prize, description in horarios:
    schedule, created = DailyBingoSchedule.objects.get_or_create(
        time_slot=time_slot,
        defaults={
            'is_active': True,
            'max_players': max_players,
            'prize_amount': prize,
            'description': description,
        }
    )
    if created:
        print(f"✅ Creado: {display} - Premio: ${prize} - Max jugadores: {max_players}")
    else:
        print(f"ℹ️  Ya existe: {display}")

print("\n" + "="*60)
print("🎉 SISTEMA DE TICKETS CONFIGURADO")
print("="*60)
print("\nPRÓXIMOS PASOS:")
print("1. Los nuevos referidos recibirán TICKETS en lugar de créditos")
print("2. Debes crear juegos de bingo DIARIOS GRATUITOS a las 9am, 2pm y 7pm")
print("3. Los usuarios usarán sus tickets para entrar a esos bingos")
print("4. Los tickets expiran en 7 días")
print("\nPara crear un bingo diario automáticamente:")
print("  python manage.py setup_daily_bingo")

