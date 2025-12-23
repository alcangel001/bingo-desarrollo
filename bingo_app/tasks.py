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
                    # Marcar como emparejado
                    queue_entry.status = 'MATCHED'
                    queue_entry.matched_at = timezone.now()
                    queue_entry.save()
                
                # SPIN DEL PREMIO (determinar multiplicador)
                dice_game.spin_prize()
                
                # Cambiar estado a SPINNING (mostrando premio)
                dice_game.status = 'SPINNING'
                dice_game.started_at = timezone.now()
                dice_game.save()
                
                # Notificar a los 3 jugadores vía WebSocket
                notify_players_match_found(dice_game, players_list)
                
                # Programar cambio a PLAYING después de 5 segundos (tiempo para animación del spin)
                from .models import DiceGame
                import threading
                def change_to_playing():
                    import time
                    time.sleep(5)  # Esperar 5 segundos
                    try:
                        game = DiceGame.objects.get(room_code=dice_game.room_code)
                        if game.status == 'SPINNING':
                            game.status = 'PLAYING'
                            game.save()
                            # Notificar cambio de estado vía WebSocket
                            notify_game_status_change(game)
                    except DiceGame.DoesNotExist:
                        pass
                
                # Ejecutar en hilo separado para no bloquear
                threading.Thread(target=change_to_playing, daemon=True).start()
                
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

