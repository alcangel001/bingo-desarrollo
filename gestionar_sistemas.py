#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ACTIVAR/DESACTIVAR sistemas del juego de bingo
Permite controlar qué funcionalidades están disponibles para los usuarios
"""

import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import PercentageSettings, BingoTicketSettings

def mostrar_estado_actual():
    """Muestra el estado actual de todos los sistemas"""
    print("\n" + "="*60)
    print("ESTADO ACTUAL DE LOS SISTEMAS")
    print("="*60)
    
    percentage_settings = PercentageSettings.objects.first()
    ticket_settings = BingoTicketSettings.get_settings()
    
    if percentage_settings:
        print(f"\n[COMPRA DE CREDITOS]       {'[ACTIVO]' if percentage_settings.credits_purchase_enabled else '[DESACTIVADO]'}")
        print(f"[RETIRO DE CREDITOS]       {'[ACTIVO]' if percentage_settings.credits_withdrawal_enabled else '[DESACTIVADO]'}")
        print(f"[SISTEMA DE REFERIDOS]     {'[ACTIVO]' if percentage_settings.referral_system_enabled else '[DESACTIVADO]'}")
        print(f"[PROMOCIONES Y BONOS]      {'[ACTIVO]' if percentage_settings.promotions_enabled else '[DESACTIVADO]'}")
    else:
        print("\n[ADVERTENCIA] No hay configuración creada")
    
    print(f"[SISTEMA DE TICKETS]       {'[ACTIVO]' if ticket_settings.is_system_active else '[DESACTIVADO]'}")
    
    if ticket_settings.is_system_active:
        print(f"\n   Configuracion de Tickets:")
        print(f"   - Tickets por referido: {ticket_settings.referred_ticket_bonus}")
        print(f"   - Tickets para referidor: {ticket_settings.referral_ticket_bonus}")
        print(f"   - Dias de expiracion: {ticket_settings.ticket_expiration_days}")
    
    print("\n" + "="*60)

def toggle_sistema(sistema):
    """Activa o desactiva un sistema específico"""
    settings = PercentageSettings.objects.first()
    if not settings:
        settings = PercentageSettings.objects.create()
    
    if sistema == '1':  # Compra de créditos
        settings.credits_purchase_enabled = not settings.credits_purchase_enabled
        settings.save()
        estado = "ACTIVADO" if settings.credits_purchase_enabled else "DESACTIVADO"
        print(f"\n[OK] Sistema de COMPRA DE CREDITOS {estado}")
        if not settings.credits_purchase_enabled:
            print("   [!] Los usuarios NO podran solicitar compra de creditos")
        
    elif sistema == '2':  # Retiro de créditos
        settings.credits_withdrawal_enabled = not settings.credits_withdrawal_enabled
        settings.save()
        estado = "ACTIVADO" if settings.credits_withdrawal_enabled else "DESACTIVADO"
        print(f"\n[OK] Sistema de RETIRO DE CREDITOS {estado}")
        if not settings.credits_withdrawal_enabled:
            print("   [!] Los usuarios NO podran solicitar retiros")
        
    elif sistema == '3':  # Referidos
        settings.referral_system_enabled = not settings.referral_system_enabled
        settings.save()
        estado = "ACTIVADO" if settings.referral_system_enabled else "DESACTIVADO"
        print(f"\n[OK] Sistema de REFERIDOS {estado}")
        if not settings.referral_system_enabled:
            print("   [!] Los codigos de referido NO estaran visibles")
            print("   [!] Los nuevos registros NO recibiran bonos por referidos")
        
    elif sistema == '4':  # Tickets
        ticket_settings = BingoTicketSettings.get_settings()
        ticket_settings.is_system_active = not ticket_settings.is_system_active
        ticket_settings.save()
        estado = "ACTIVADO" if ticket_settings.is_system_active else "DESACTIVADO"
        print(f"\n[OK] Sistema de TICKETS {estado}")
        if ticket_settings.is_system_active:
            print("   [INFO] Los referidos ahora recibiran TICKETS en lugar de creditos")
            print("   [INFO] Debes configurar bingos diarios para usar los tickets")
        else:
            print("   [INFO] Los referidos ahora recibiran CREDITOS ($5)")
    
    elif sistema == '5':  # Promociones
        settings.promotions_enabled = not settings.promotions_enabled
        settings.save()
        estado = "ACTIVADO" if settings.promotions_enabled else "DESACTIVADO"
        print(f"\n[OK] Sistema de PROMOCIONES Y BONOS {estado}")
        if not settings.promotions_enabled:
            print("   [!] Los usuarios NO veran las promociones disponibles")
            print("   [!] No podran reclamar bonos de bienvenida ni promociones especiales")

def menu_principal():
    """Menú principal del script"""
    while True:
        mostrar_estado_actual()
        
        print("\nQUE SISTEMA DESEAS ACTIVAR/DESACTIVAR?")
        print("\n1. Compra de Creditos")
        print("2. Retiro de Creditos")
        print("3. Sistema de Referidos")
        print("4. Sistema de Tickets")
        print("5. Promociones y Bonos")
        print("6. Ver Estado Actual")
        print("0. Salir")
        
        opcion = input("\nSelecciona una opcion (0-6): ").strip()
        
        if opcion == '0':
            print("\nHasta luego!")
            break
        elif opcion in ['1', '2', '3', '4', '5']:
            toggle_sistema(opcion)
            input("\nPresiona ENTER para continuar...")
        elif opcion == '6':
            continue
        else:
            print("\n[ERROR] Opcion invalida. Intenta de nuevo.")
            input("\nPresiona ENTER para continuar...")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("GESTOR DE SISTEMAS - BINGO JYM".center(60))
    print("="*60)
    print("\nEste script te permite activar/desactivar sistemas del juego.")
    print("Cuando un sistema esta desactivado, los usuarios NO veran esa opcion.\n")
    
    menu_principal()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrumpido. Hasta luego!")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
