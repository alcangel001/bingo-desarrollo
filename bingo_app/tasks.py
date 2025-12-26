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
from django.contrib.auth.models import User


def process_matchmaking_queue():
    """
    Proceso que se ejecuta cada 2-3 segundos.
    Agrupa jugadores de 3 en 3 y crea partidas.
    """
    print(f"🔄 [MATCHMAKING] ========== INICIANDO PROCESO DE MATCHMAKING ==========")
    
    # Obtener todos los precios únicos en la cola (sin duplicados)
    all_waiting = DiceMatchmakingQueue.objects.filter(status='WAITING')
    unique_prices = list(set(all_waiting.values_list('entry_price', flat=True)))
    
    total_count = all_waiting.count()
    print(f"🔄 [MATCHMAKING] Total en cola: {total_count}")
    print(f"🔄 [MATCHMAKING] Precios únicos encontrados: {unique_prices}")
    
    # Mostrar todos los usuarios en cola
    for q in all_waiting[:10]:  # Mostrar hasta 10
        print(f"   - {q.user.username}: ${q.entry_price}, estado: {q.status}, unido: {q.joined_at}")
    
    if total_count == 0:
        print(f"⏳ [MATCHMAKING] No hay jugadores en cola, terminando...")
        return None
    
    games_created = []
    
    for price in unique_prices:
        # Procesar múltiples partidas si hay más de 3 jugadores
        max_iterations = 10  # Limitar iteraciones para evitar loops infinitos
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Buscar jugadores que busquen este precio específico
            # NO filtrar por tiempo - solo por estado WAITING
            # Primero contar sin bloquear para mostrar información
            waiting_players_query = DiceMatchmakingQueue.objects.filter(
                status='WAITING',
                entry_price=price
            ).order_by('joined_at')
            
            total_waiting = waiting_players_query.count()
            if iteration == 1:
                print(f"🔄 [MATCHMAKING] Precio ${price}: {total_waiting} jugadores totales esperando")
            
            if total_waiting < 3:
                if iteration == 1:
                    print(f"⏳ [MATCHMAKING] Precio ${price}: No hay suficientes jugadores ({total_waiting}/3)")
                break  # No hay suficientes jugadores para este precio, pasar al siguiente precio
            
            # Crear partida con los 3 jugadores
            # IMPORTANTE: Usar select_for_update() DENTRO de la transacción para bloquear las filas
            try:
                print(f"   🔄 Iniciando transacción para crear partida...")
                with transaction.atomic():
                    # Ahora sí usar select_for_update dentro de la transacción
                    waiting_players_query_locked = DiceMatchmakingQueue.objects.filter(
                        status='WAITING',
                        entry_price=price
                    ).order_by('joined_at').select_for_update(skip_locked=True)
                    
                    # Convertir a lista para contar correctamente (esto bloquea las filas)
                    waiting_players_list = list(waiting_players_query_locked[:3])
                    player_count = len(waiting_players_list)
                    
                    if player_count < 3:
                        print(f"⏳ [MATCHMAKING] Precio ${price}: No hay suficientes jugadores disponibles después de bloqueo ({player_count}/3)")
                        break  # No hay suficientes jugadores disponibles, pasar al siguiente precio
                    
                    if iteration == 1 and player_count > 0:
                        print(f"   Primeros 3: {[p.user.username for p in waiting_players_list]}")
                    
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
                        print(f"   Jugadores con saldo suficiente: {[p.user.username for p in players_list]}")
                        break  # No hay suficientes jugadores válidos, pasar al siguiente precio
                    
                    print(f"✅ [MATCHMAKING] Precio ${price} (iteración {iteration}): ¡3 jugadores encontrados! Creando partida...")
                    print(f"   Jugadores: {[p.user.username for p in players_list]}")
                    print(f"   IDs de cola: {[p.id for p in players_list]}")
                    print(f"   Saldos: {[(p.user.username, float(p.user.credit_balance)) for p in players_list]}")
                    # Verificar nuevamente que los jugadores sigan en WAITING (doble verificación)
                    # Esto previene condiciones de carrera donde otro proceso ya los procesó
                    fresh_queue_entries = []
                    for queue_entry in players_list:
                        queue_entry.refresh_from_db()
                        # Verificar que el jugador no esté ya en otra partida activa
                        active_game = DiceGame.objects.filter(
                            dice_players__user=queue_entry.user,
                            status__in=['WAITING', 'SPINNING', 'PLAYING']
                        ).exclude(status='FINISHED').first()
                        
                        if active_game:
                            print(f"   ⚠️ Jugador {queue_entry.user.username} ya está en partida activa {active_game.room_code}, saltando...")
                            # Marcar esta entrada como procesada para evitar intentos futuros
                            queue_entry.status = 'TIMEOUT'
                            queue_entry.save()
                            continue
                        
                        if queue_entry.status != 'WAITING':
                            print(f"   ⚠️ Jugador {queue_entry.user.username} ya no está en WAITING (estado: {queue_entry.status}), saltando...")
                            continue
                        
                        fresh_queue_entries.append(queue_entry)
                    
                    # Si no tenemos 3 jugadores válidos después de la verificación, cancelar
                    if len(fresh_queue_entries) < 3:
                        print(f"   ⚠️ No hay suficientes jugadores válidos después de verificación ({len(fresh_queue_entries)}/3), cancelando creación de partida")
                        # Marcar las entradas restantes como TIMEOUT para limpiar
                        for q in fresh_queue_entries:
                            q.status = 'TIMEOUT'
                            q.save()
                        break
                    
                    # Usar solo los jugadores válidos
                    players_list = fresh_queue_entries
                    
                    # IMPORTANTE: Bloquear usuarios con select_for_update antes de descontar saldo
                    # Esto previene condiciones de carrera donde múltiples procesos intentan descontar
                    users_to_block = []
                    for queue_entry in players_list:
                        # Bloquear el usuario en la base de datos
                        user = User.objects.select_for_update().get(id=queue_entry.user.id)
                        users_to_block.append((user, queue_entry))
                    
                    # Bloquear créditos de los 3 jugadores (ahora con usuarios bloqueados)
                    blocked_users = []  # Para revertir en caso de error
                    for user, queue_entry in users_to_block:
                        try:
                            # Refrescar saldo desde DB para asegurar valor actualizado
                            user.refresh_from_db()
                            
                            # Verificar saldo nuevamente después del bloqueo
                            if user.credit_balance < queue_entry.entry_price:
                                raise ValueError(f"Usuario {user.username} no tiene saldo suficiente después del bloqueo")
                            
                            # Descontar y bloquear créditos
                            user.credit_balance -= queue_entry.entry_price
                            user.blocked_credits += queue_entry.entry_price
                            user.save()
                            
                            blocked_users.append((user, queue_entry))
                            
                            # Crear transacción con logging detallado
                            transaction_obj = Transaction.objects.create(
                                user=user,
                                amount=-queue_entry.entry_price,
                                transaction_type='ENTRY_FEE',
                                description=f"Entrada a partida de dados (${queue_entry.entry_price})"
                            )
                            print(f"💰 [TRANSACTION] ENTRY_FEE creada: ID={transaction_obj.id}, Usuario={user.username}, Monto=${queue_entry.entry_price}, Saldo antes={user.credit_balance + queue_entry.entry_price}, Saldo después={user.credit_balance}, Bloqueado={user.blocked_credits}")
                        except Exception as e:
                            print(f"❌ [MATCHMAKING] Error bloqueando créditos para {user.username}: {e}")
                            # Revertir créditos bloqueados hasta ahora
                            for revert_user, revert_entry in blocked_users:
                                revert_user.blocked_credits -= revert_entry.entry_price
                                revert_user.credit_balance += revert_entry.entry_price
                                revert_user.save()
                                print(f"🔄 [MATCHMAKING] Créditos revertidos para {revert_user.username}")
                            raise
                    
                    # Calcular premio base
                    base_prize = price * Decimal('3')  # 3 jugadores
                    
                    # Crear partida
                    dice_game = DiceGame.objects.create(
                        entry_price=price,
                        base_prize=base_prize,
                        status='WAITING',
                    )
                    
                    # Agregar jugadores a la partida
                    created_players = []
                    for queue_entry in players_list:
                        # Refrescar el usuario para asegurar datos actualizados
                        queue_entry.user.refresh_from_db()
                        
                        # Crear el jugador
                        player = DicePlayer.objects.create(
                            user=queue_entry.user,
                            game=dice_game,
                            lives=3,
                        )
                        created_players.append(player)
                        print(f"   ✅ Jugador {queue_entry.user.username} agregado a partida {dice_game.room_code}")
                        
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
                    
                    # Refrescar la partida para asegurar que los jugadores estén guardados
                    dice_game.refresh_from_db()
                    
                    # Verificar que los 3 jugadores estén en la partida
                    players_in_game = list(dice_game.dice_players.all())
                    print(f"   📊 Jugadores en partida después de crear: {len(players_in_game)}")
                    for p in players_in_game:
                        print(f"      - {p.user.username} (ID: {p.user.id})")
                    
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
                    
                    # Notificar a los 3 jugadores vía WebSocket (sin bloquear)
                    try:
                        notify_players_match_found(dice_game, players_list)
                        print(f"📢 [MATCHMAKING] Notificaciones enviadas a los 3 jugadores")
                    except Exception as notify_error:
                        print(f"⚠️ [MATCHMAKING] Error al notificar: {notify_error}")
                        # Continuar aunque falle la notificación
                    
                    # NOTA: El cambio de SPINNING a PLAYING se maneja de forma pasiva en el WebSocket
                    # cuando un jugador se conecta después de 7 segundos o cuando intenta la primera acción
                    # Esto evita problemas si el servidor se reinicia
                    print(f"⏱️ [MATCHMAKING] Partida {dice_game.room_code} en estado SPINNING. El WebSocket cambiará a PLAYING automáticamente después de 7 segundos")
                    
                    games_created.append(dice_game)
                    
            except Exception as e:
                # Si hay error, REVERTIR todos los blocked_credits a credit_balance
                print(f"❌ [MATCHMAKING] Error creando partida: {e}")
                import traceback
                traceback.print_exc()
                
                # Revertir créditos bloqueados si se habían bloqueado antes del error
                try:
                    # Buscar usuarios que puedan tener créditos bloqueados de este intento
                    # (Esto es una medida de seguridad adicional)
                    for queue_entry in players_list if 'players_list' in locals() else []:
                        try:
                            user = User.objects.get(id=queue_entry.user.id)
                            if user.blocked_credits > 0:
                                # Verificar si hay una transacción ENTRY_FEE reciente sin partida asociada
                                recent_transaction = Transaction.objects.filter(
                                    user=user,
                                    transaction_type='ENTRY_FEE',
                                    created_at__gte=timezone.now() - timedelta(seconds=10)
                                ).order_by('-created_at').first()
                                
                                if recent_transaction:
                                    # Revertir créditos bloqueados
                                    refund_amount = min(user.blocked_credits, queue_entry.entry_price)
                                    user.blocked_credits -= refund_amount
                                    user.credit_balance += refund_amount
                                    user.save()
                                    
                                    # Crear transacción de reversión
                                    Transaction.objects.create(
                                        user=user,
                                        amount=refund_amount,
                                        transaction_type='REFUND',
                                        description=f"Reversión de entrada a partida de dados (error en creación)"
                                    )
                                    print(f"🔄 [MATCHMAKING] Créditos revertidos para {user.username}: ${refund_amount}")
                        except Exception as revert_error:
                            print(f"⚠️ [MATCHMAKING] Error al revertir créditos para {queue_entry.user.username}: {revert_error}")
                except Exception as revert_all_error:
                    print(f"⚠️ [MATCHMAKING] Error general al revertir créditos: {revert_all_error}")
                
                # NO hacer break aquí - continuar intentando con el siguiente grupo
                continue  # Continuar con la siguiente iteración
    
    # Retornar la primera partida creada (o None si no se creó ninguna)
    if games_created:
        print(f"✅ [MATCHMAKING] ========== MATCHMAKING COMPLETADO: {len(games_created)} partida(s) creada(s) ==========")
        return games_created[0]
    else:
        print(f"⏳ [MATCHMAKING] ========== MATCHMAKING COMPLETADO: No se crearon partidas ==========")
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


def emergency_cleanup_dice_games():
    """
    Sistema de limpieza de emergencia (El "Botón de Pánico").
    Busca partidas fantasma y limpia la cola de matchmaking.
    """
    print(f"🧹 [CLEANUP] ========== INICIANDO LIMPIEZA DE EMERGENCIA ==========")
    
    cleanup_count = 0
    refund_total = Decimal('0.00')
    
    # 1. Buscar partidas fantasma (más de 20 minutos en WAITING, SPINNING o PLAYING)
    cutoff_time = timezone.now() - timedelta(minutes=20)
    ghost_games = DiceGame.objects.filter(
        status__in=['WAITING', 'SPINNING', 'PLAYING'],
        created_at__lt=cutoff_time
    )
    
    print(f"🔍 [CLEANUP] Partidas fantasma encontradas: {ghost_games.count()}")
    
    for game in ghost_games:
        print(f"   🗑️ Limpiando partida fantasma: {game.room_code} (Estado: {game.status}, Creada: {game.created_at})")
        
        # Obtener todos los jugadores de la partida
        players = DicePlayer.objects.filter(game=game)
        
        for player in players:
            # Devolver blocked_credits a credit_balance
            if player.user.blocked_credits >= game.entry_price:
                refund_amount = game.entry_price
                player.user.blocked_credits -= refund_amount
                player.user.credit_balance += refund_amount
                player.user.save()
                
                # Crear transacción de reembolso
                Transaction.objects.create(
                    user=player.user,
                    amount=refund_amount,
                    transaction_type='REFUND',
                    description=f"Reembolso de partida fantasma {game.room_code} (limpieza automática)"
                )
                
                refund_total += refund_amount
                print(f"      💰 Reembolsado ${refund_amount} a {player.user.username}")
                print(f"💰 [TRANSACTION] REFUND creada: Usuario={player.user.username}, Monto=${refund_amount}, Partida={game.room_code}")
        
        # Marcar partida como FINISHED o CANCELLED
        game.status = 'FINISHED'
        game.finished_at = timezone.now()
        game.save()
        
        cleanup_count += 1
    
    # 2. Limpiar cola de matchmaking (usuarios WAITING más de 5 minutos)
    queue_cutoff_time = timezone.now() - timedelta(minutes=5)
    stale_queue_entries = DiceMatchmakingQueue.objects.filter(
        status='WAITING',
        joined_at__lt=queue_cutoff_time
    )
    
    stale_count = stale_queue_entries.count()
    print(f"🔍 [CLEANUP] Entradas de cola obsoletas encontradas: {stale_count}")
    
    for queue_entry in stale_queue_entries:
        print(f"   🗑️ Limpiando entrada de cola: {queue_entry.user.username} (Unido: {queue_entry.joined_at})")
        queue_entry.status = 'TIMEOUT'
        queue_entry.save()
    
    print(f"✅ [CLEANUP] ========== LIMPIEZA COMPLETADA ==========")
    print(f"   Partidas limpiadas: {cleanup_count}")
    print(f"   Entradas de cola limpiadas: {stale_count}")
    print(f"   Total reembolsado: ${refund_total}")
    
    return {
        'games_cleaned': cleanup_count,
        'queue_entries_cleaned': stale_count,
        'total_refunded': float(refund_total)
    }

