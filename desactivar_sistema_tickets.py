#!/usr/bin/env python3
"""
Script para DESACTIVAR el sistema de tickets y usar CRÉDITOS para referidos
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import BingoTicketSettings

# Desactivar sistema de tickets
settings = BingoTicketSettings.get_settings()
settings.is_system_active = False
settings.save()

print("✅ Sistema de tickets DESACTIVADO")
print("✅ Ahora los referidos reciben CRÉDITOS ($5 cada uno)")
print("\nConfiguración actual:")
print(f"  - Sistema activo: {settings.is_system_active}")
print(f"  - Tickets por referido: {settings.referred_ticket_bonus}")
print(f"  - Tickets para referidor: {settings.referral_ticket_bonus}")
print(f"  - Días de expiración: {settings.ticket_expiration_days}")

