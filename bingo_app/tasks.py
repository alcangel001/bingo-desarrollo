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
    print(f"🔄 [MATCHMAKING] Iniciando proceso de matchmaking...")
    
    # Obtener todos los precios únicos en la cola
    unique_prices = DiceMatchmakingQueue.objects.filter(
        status='WAITING'
    ).values_list('entry_price', flat=True).distinct()
    
    print(f"🔄 [MATCHMAKING] Precios únicos encontrados: {list(unique_prices)}")
    
    for price in unique_prices:
        # Buscar jugadores que busquen este precio específico
        waiting_players_query = DiceMatchmakingQueue.objects.filter(
            status='WAITING',
            entry_price=price,
            joined_at__gte=timezone.now() - timedelta(minutes=5)  # Timeout de 5 minutos
        ).order_by('joined_at')
        
        # Convertir a lista para contar correctamente
        waiting_players_list = list(waiting_players_query[:3])
        player_count = len(waiting_players_list)
        
        print(f"🔄 [MATCHMAKING] Precio ${price}: {player_count} jugadores esperando")
        if player_count > 0:
            print(f"   Jugadores: {[p.user.username for p in waiting_players_list]}")
        
        if player_count < 3:
            print(f"⏳ [MATCHMAKING] Precio ${price}: No hay suficientes jugadores ({player_count}/3)")
            continue  # No hay suficientes jugadores para este precio
        
        # Usar la lista directamente
        waiting_players = waiting_players_list
        
        # Verificar que todos tienen suficiente saldo
        players_list = []
        for queue_entry in waiting_players:
            # Refrescar el usuario desde la base de datos para obtener el saldo actualizado
            queue_entry.user.refresh_from_db()
            if queue_entry.user.credit_balance >= queue_entry.entry_price:
                players_list.append(queue_entry)
            else:
                # Jugador sin saldo - remover de cola
                print(f"⚠️ [MATCHMAKING] Jugador {queue_entry.user.username} sin saldo suficiente")
                queue_entry.status = 'TIMEOUT'
                queue_entry.save()
        
        if len(players_list) < 3:
            print(f"⚠️ [MATCHMAKING] Precio ${price}: No hay suficientes jugadores válidos después de validar saldo ({len(players_list)}/3)")
            continue  # No hay suficientes jugadores válidos
        
        print(f"✅ [MATCHMAKING] Precio ${price}: ¡3 jugadores encontrados! Creando partida...")
        print(f"   Jugadores: {[p.user.username for p in players_list]}")
        
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
                
                print(f"✅ [MATCHMAKING] Partida creada: {dice_game.room_code}")
                print(f"   Estado: {dice_game.status}")
                print(f"   Multiplicador: {dice_game.multiplier}")
                print(f"   Premio: ${dice_game.final_prize}")
                print(f"   Jugadores: {[p.user.username for p in dice_game.dice_players.all()]}")
                
                # Notificar a los 3 jugadores vía WebSocket
                notify_players_match_found(dice_game, players_list)
                
                print(f"📢 [MATCHMAKING] Notificaciones enviadas a los 3 jugadores")
                
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

