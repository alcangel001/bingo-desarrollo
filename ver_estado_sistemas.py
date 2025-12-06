#!/usr/bin/env python
"""
Script simple para VER y CAMBIAR el estado de Referidos y Promociones
Sin necesidad de usar el Admin de Django
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import PercentageSettings

def mostrar_estado():
    """Muestra el estado actual en formato simple"""
    settings = PercentageSettings.objects.first()
    
    if not settings:
        print("❌ No hay configuración creada. Creando una por defecto...")
        settings = PercentageSettings.objects.create()
    
    print("\n" + "="*60)
    print("ESTADO DE REFERIDOS Y PROMOCIONES".center(60))
    print("="*60)
    print()
    
    # Referidos
    ref_estado = "✅ ACTIVO" if settings.referral_system_enabled else "❌ DESACTIVADO"
    ref_efecto = "Los usuarios VEN el enlace 'Referidos' en el lobby" if settings.referral_system_enabled else "Los usuarios NO ven el enlace 'Referidos'"
    print(f"🤝 SISTEMA DE REFERIDOS: {ref_estado}")
    print(f"   → {ref_efecto}")
    print()
    
    # Promociones
    promo_estado = "✅ ACTIVO" if settings.promotions_enabled else "❌ DESACTIVADO"
    promo_efecto = "Los usuarios VEN el enlace 'Promociones' en el lobby" if settings.promotions_enabled else "Los usuarios NO ven el enlace 'Promociones'"
    print(f"🎁 SISTEMA DE PROMOCIONES: {promo_estado}")
    print(f"   → {promo_efecto}")
    print()
    
    print("="*60)
    print()

def cambiar_referidos():
    """Cambia el estado de referidos"""
    settings = PercentageSettings.objects.first()
    settings.referral_system_enabled = not settings.referral_system_enabled
    settings.save()
    
    nuevo_estado = "ACTIVADO" if settings.referral_system_enabled else "DESACTIVADO"
    print(f"\n✅ Sistema de REFERIDOS ahora está: {nuevo_estado}")
    
    if settings.referral_system_enabled:
        print("   → El enlace 'Referidos' APARECERÁ en el lobby")
    else:
        print("   → El enlace 'Referidos' DESAPARECERÁ del lobby")

def cambiar_promociones():
    """Cambia el estado de promociones"""
    settings = PercentageSettings.objects.first()
    settings.promotions_enabled = not settings.promotions_enabled
    settings.save()
    
    nuevo_estado = "ACTIVADO" if settings.promotions_enabled else "DESACTIVADO"
    print(f"\n✅ Sistema de PROMOCIONES ahora está: {nuevo_estado}")
    
    if settings.promotions_enabled:
        print("   → El enlace 'Promociones' APARECERÁ en el lobby")
    else:
        print("   → El enlace 'Promociones' DESAPARECERÁ del lobby")

def menu():
    """Menú interactivo"""
    while True:
        mostrar_estado()
        
        print("¿Qué deseas hacer?")
        print()
        print("1. Cambiar estado de REFERIDOS")
        print("2. Cambiar estado de PROMOCIONES")
        print("3. Activar AMBOS sistemas")
        print("4. Desactivar AMBOS sistemas")
        print("5. Actualizar vista")
        print("0. Salir")
        print()
        
        opcion = input("Selecciona (0-5): ").strip()
        
        if opcion == '0':
            print("\n👋 ¡Hasta luego!\n")
            break
        elif opcion == '1':
            cambiar_referidos()
            input("\nPresiona ENTER para continuar...")
        elif opcion == '2':
            cambiar_promociones()
            input("\nPresiona ENTER para continuar...")
        elif opcion == '3':
            settings = PercentageSettings.objects.first()
            settings.referral_system_enabled = True
            settings.promotions_enabled = True
            settings.save()
            print("\n✅ Ambos sistemas ACTIVADOS")
            input("\nPresiona ENTER para continuar...")
        elif opcion == '4':
            settings = PercentageSettings.objects.first()
            settings.referral_system_enabled = False
            settings.promotions_enabled = False
            settings.save()
            print("\n⚠️ Ambos sistemas DESACTIVADOS")
            input("\nPresiona ENTER para continuar...")
        elif opcion == '5':
            continue
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

