#!/usr/bin/env python
"""
Script para gestionar los toggles de Promociones y Referidos
Uso: python gestionar_promociones_referidos.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import PercentageSettings

def get_or_create_settings():
    """Obtiene o crea la configuración del sistema"""
    settings, created = PercentageSettings.objects.get_or_create(
        pk=1,
        defaults={
            'platform_commission': 10.00,
            'game_creation_fee': 1.00,
            'image_promotion_price': 10.00,
            'video_promotion_price': 15.00,
            'referral_system_enabled': True,
            'promotions_enabled': True,
            'credits_purchase_enabled': True,
            'credits_withdrawal_enabled': True,
        }
    )
    if created:
        print("✅ Configuración inicial creada")
    return settings

def mostrar_estado(settings):
    """Muestra el estado actual de los toggles"""
    print("\n" + "="*60)
    print("ESTADO ACTUAL DEL SISTEMA")
    print("="*60)
    print(f"1. Sistema de REFERIDOS: {'✅ ACTIVO' if settings.referral_system_enabled else '❌ DESACTIVADO'}")
    print(f"2. Sistema de PROMOCIONES: {'✅ ACTIVO' if settings.promotions_enabled else '❌ DESACTIVADO'}")
    print(f"3. Compra de Créditos: {'✅ ACTIVO' if settings.credits_purchase_enabled else '❌ DESACTIVADO'}")
    print(f"4. Retiro de Créditos: {'✅ ACTIVO' if settings.credits_withdrawal_enabled else '❌ DESACTIVADO'}")
    print("="*60)

def toggle_referidos(settings):
    """Activa/Desactiva el sistema de referidos"""
    settings.referral_system_enabled = not settings.referral_system_enabled
    settings.save()
    estado = "ACTIVADO" if settings.referral_system_enabled else "DESACTIVADO"
    print(f"\n✅ Sistema de REFERIDOS ahora está: {estado}")
    print(f"   {'→ El enlace APARECERÁ en el lobby' if settings.referral_system_enabled else '→ El enlace DESAPARECERÁ del lobby'}")

def toggle_promociones(settings):
    """Activa/Desactiva el sistema de promociones"""
    settings.promotions_enabled = not settings.promotions_enabled
    settings.save()
    estado = "ACTIVADO" if settings.promotions_enabled else "DESACTIVADO"
    print(f"\n✅ Sistema de PROMOCIONES ahora está: {estado}")
    print(f"   {'→ El enlace APARECERÁ en el lobby' if settings.promotions_enabled else '→ El enlace DESAPARECERÁ del lobby'}")

def toggle_compra(settings):
    """Activa/Desactiva la compra de créditos"""
    settings.credits_purchase_enabled = not settings.credits_purchase_enabled
    settings.save()
    estado = "ACTIVADO" if settings.credits_purchase_enabled else "DESACTIVADO"
    print(f"\n✅ Compra de Créditos ahora está: {estado}")

def toggle_retiro(settings):
    """Activa/Desactiva el retiro de créditos"""
    settings.credits_withdrawal_enabled = not settings.credits_withdrawal_enabled
    settings.save()
    estado = "ACTIVADO" if settings.credits_withdrawal_enabled else "DESACTIVADO"
    print(f"\n✅ Retiro de Créditos ahora está: {estado}")

def menu_principal():
    """Menú principal del script"""
    print("\n" + "="*60)
    print("🎮 GESTOR DE SISTEMAS - LOBBY BINGO")
    print("="*60)
    
    settings = get_or_create_settings()
    mostrar_estado(settings)
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Toggle Sistema de REFERIDOS")
        print("2. Toggle Sistema de PROMOCIONES")
        print("3. Toggle Compra de Créditos")
        print("4. Toggle Retiro de Créditos")
        print("5. Ver estado actual")
        print("0. Salir")
        print("-"*60)
        
        try:
            opcion = input("Selecciona una opción (0-5): ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!\n")
                break
            elif opcion == '1':
                toggle_referidos(settings)
                settings.refresh_from_db()
                mostrar_estado(settings)
            elif opcion == '2':
                toggle_promociones(settings)
                settings.refresh_from_db()
                mostrar_estado(settings)
            elif opcion == '3':
                toggle_compra(settings)
                settings.refresh_from_db()
                mostrar_estado(settings)
            elif opcion == '4':
                toggle_retiro(settings)
                settings.refresh_from_db()
                mostrar_estado(settings)
            elif opcion == '5':
                settings.refresh_from_db()
                mostrar_estado(settings)
            else:
                print("❌ Opción inválida. Por favor selecciona 0-5")
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

def activar_todo():
    """Activa todos los sistemas"""
    settings = get_or_create_settings()
    settings.referral_system_enabled = True
    settings.promotions_enabled = True
    settings.credits_purchase_enabled = True
    settings.credits_withdrawal_enabled = True
    settings.save()
    print("\n✅ TODOS los sistemas han sido ACTIVADOS")
    mostrar_estado(settings)

def desactivar_todo():
    """Desactiva todos los sistemas"""
    settings = get_or_create_settings()
    settings.referral_system_enabled = False
    settings.promotions_enabled = False
    settings.credits_purchase_enabled = False
    settings.credits_withdrawal_enabled = False
    settings.save()
    print("\n⚠️ TODOS los sistemas han sido DESACTIVADOS")
    mostrar_estado(settings)

if __name__ == "__main__":
    import sys
    
    # Permitir uso con argumentos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        settings = get_or_create_settings()
        
        if comando == 'status':
            mostrar_estado(settings)
        elif comando == 'activar-todo':
            activar_todo()
        elif comando == 'desactivar-todo':
            desactivar_todo()
        elif comando == 'referidos':
            toggle_referidos(settings)
            mostrar_estado(settings)
        elif comando == 'promociones':
            toggle_promociones(settings)
            mostrar_estado(settings)
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("\nComandos disponibles:")
            print("  python gestionar_promociones_referidos.py status")
            print("  python gestionar_promociones_referidos.py referidos")
            print("  python gestionar_promociones_referidos.py promociones")
            print("  python gestionar_promociones_referidos.py activar-todo")
            print("  python gestionar_promociones_referidos.py desactivar-todo")
    else:
        # Modo interactivo
        menu_principal()

