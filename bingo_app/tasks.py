"""
Tareas para el módulo de dados.
Matchmaking automático.
"""

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    DiceMatchmakingQueue, DiceGame, DicePlayer, DiceModuleSettings, Transaction
)


def process_matchmaking_queue():
    """
    Proceso que se ejecuta cada 2-3 segundos.
    Agrupa jugadores de 3 en 3 y crea partidas.
    """
    # Obtener todos los precios únicos en la cola
    unique_prices = DiceMatchmakingQueue.objects.filter(
        status='WAITING'
    ).values_list('entry_price', flat=True).distinct()
    
    for price in unique_prices:
        # Buscar 3 jugadores que busquen este precio específico
        waiting_players = DiceMatchmakingQueue.objects.filter(
            status='WAITING',
            entry_price=price,
            joined_at__gte=timezone.now() - timedelta(minutes=5)  # Timeout de 5 minutos
        ).order_by('joined_at')[:3]
        
        if waiting_players.count() < 3:
            continue  # No hay suficientes jugadores para este precio
        
        # Verificar que todos tienen suficiente saldo
        players_list = list(waiting_players)
        for queue_entry in players_list[:]:
            if queue_entry.user.credit_balance < queue_entry.entry_price:
                # Jugador sin saldo - remover de cola
                queue_entry.status = 'TIMEOUT'
                queue_entry.save()
                players_list.remove(queue_entry)
        
        if len(players_list) < 3:
            continue  # No hay suficientes jugadores válidos
        
        # Crear partida con los 3 jugadores
        try:
            with transaction.atomic():
                # Bloquear créditos de los 3 jugadores
                for queue_entry in players_list:
                    user = queue_entry.user
                    user.credit_balance -= queue_entry.entry_price
                    user.blocked_credits += queue_entry.entry_price
                    user.save()
                    
                    # Crear transacción
                    Transaction.objects.create(
                        user=user,
                        amount=-queue_entry.entry_price,
                        transaction_type='ENTRY_FEE',
                        description=f"Entrada a partida de dados (${queue_entry.entry_price})"
                    )
                
                # Calcular premio base
                base_prize = price * Decimal('3')  # 3 jugadores
                
                # Crear partida
                dice_game = DiceGame.objects.create(
                    entry_price=price,
                    base_prize=base_prize,
                    status='WAITING',
                )
                
                # Agregar jugadores a la partida
                for queue_entry in players_list:
                    DicePlayer.objects.create(
                        user=queue_entry.user,
                        game=dice_game,
                        lives=3,
                    )
                    # Marcar como emparejado y limpiar cualquier otra entrada en cola del usuario
                    queue_entry.status = 'MATCHED'
                    queue_entry.matched_at = timezone.now()
                    queue_entry.save()
                    
                    # Limpiar cualquier otra entrada en cola del mismo usuario (por si hay duplicados)
                    DiceMatchmakingQueue.objects.filter(
                        user=queue_entry.user,
                        status='WAITING'
                    ).exclude(
                        id=queue_entry.id
                    ).update(status='TIMEOUT')
                
                # SPIN DEL PREMIO (determinar multiplicador)
                dice_game.spin_prize()
                
                # Cambiar estado a SPINNING (mostrando premio)
                dice_game.status = 'SPINNING'
                dice_game.started_at = timezone.now()
                dice_game.save()
                
                # Notificar a los 3 jugadores vía WebSocket
                notify_players_match_found(dice_game, players_list)
                
                # Programar cambio a PLAYING después de 7 segundos (tiempo para animación del spin)
                # Usar Celery o simplemente cambiar directamente con un delay
                # Por ahora, usar threading con mejor manejo
                from .models import DiceGame
                import threading
                import django
                django.setup()  # Asegurar que Django esté configurado en el thread
                
                def change_to_playing():
                    import time
                    time.sleep(7)  # Esperar 7 segundos para que termine la animación
                    try:
                        # Importar dentro del thread para evitar problemas
                        from django.db import transaction
                        from .models import DiceGame as DG
                        
                        print(f"🔄 Intentando cambiar estado de {dice_game.room_code} a PLAYING...")
                        
                        with transaction.atomic():
                            game = DG.objects.select_for_update().get(room_code=dice_game.room_code)
                            print(f"📊 Estado actual: {game.status}")
                            
                            if game.status == 'SPINNING':
                                game.status = 'PLAYING'
                                game.save(update_fields=['status'])
                                print(f"✅ Cambiado estado de {game.room_code} a PLAYING")
                                
                                # Notificar cambio de estado vía WebSocket
                                try:
                                    notify_game_status_change(game)
                                    print(f"📢 Notificación de cambio de estado enviada")
                                except Exception as notify_error:
                                    print(f"⚠️ Error al notificar cambio de estado: {notify_error}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                print(f"⚠️ El estado ya no es SPINNING, es {game.status}")
                    except DiceGame.DoesNotExist:
                        print(f"⚠️ Partida {dice_game.room_code} no encontrada al cambiar estado")
                    except Exception as e:
                        print(f"❌ Error al cambiar estado: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Ejecutar en hilo separado para no bloquear
                thread = threading.Thread(target=change_to_playing, daemon=True)
                thread.start()
                print(f"🧵 Thread iniciado para cambiar estado de {dice_game.room_code} después de 7 segundos")
                
                return dice_game
        except Exception as e:
            # Si hay error, no crear partida
            print(f"Error en matchmaking: {e}")
            return None
    
    return None


def notify_players_match_found(dice_game, players_list):
    """
    Notifica a los jugadores que se encontró partida.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        
        for queue_entry in players_list:
            async_to_sync(channel_layer.group_send)(
                f"dice_queue_{queue_entry.user.id}",
                {
                    'type': 'match_found',
                    'room_code': dice_game.room_code,
                    'multiplier': dice_game.multiplier,
                    'final_prize': str(dice_game.final_prize),
                }
            )
    except Exception as e:
        print(f"Error notificando jugadores: {e}")


def notify_game_status_change(dice_game):
    """
    Notifica cambio de estado del juego a todos los jugadores.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        group_name = f'dice_game_{dice_game.room_code}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'game_status_changed',
                'status': dice_game.status,
                'multiplier': dice_game.multiplier,
                'final_prize': str(dice_game.final_prize),
            }
        )
    except Exception as e:
        print(f"Error notificando cambio de estado: {e}")

