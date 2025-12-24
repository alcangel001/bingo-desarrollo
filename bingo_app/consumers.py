from decimal import Decimal
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import asyncio
from datetime import datetime
from collections import defaultdict
from .models import Game, Player, ChatMessage, Transaction, Message, User, DiceGame, DicePlayer
from django.utils import timezone
from django.db.models import Sum

# Manager global para auto-calling persistente
class AutoCallManager:
    _instance = None
    _tasks = {}  # {game_id: task}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def start_auto_call(self, game_id, consumer):
        """Inicia auto-calling persistente para un juego"""
        if game_id in self._tasks and not self._tasks[game_id].done():
            return  # Ya está ejecutándose
        
        print(f"🔄 AutoCallManager: Iniciando auto-calling persistente para juego {game_id}")
        self._tasks[game_id] = asyncio.create_task(self._persistent_auto_call(game_id, consumer))
    
    def stop_auto_call(self, game_id):
        """Detiene auto-calling persistente para un juego"""
        if game_id in self._tasks and not self._tasks[game_id].done():
            print(f"🔄 AutoCallManager: Deteniendo auto-calling persistente para juego {game_id}")
            self._tasks[game_id].cancel()
            del self._tasks[game_id]
    
    async def _persistent_auto_call(self, game_id, consumer):
        """Tarea persistente de auto-calling"""
        try:
            while True:
                # Verificar si el juego sigue activo
                game_active = await consumer.is_auto_calling_active()
                if not game_active:
                    print(f"🔄 AutoCallManager: Auto-calling terminado para juego {game_id} - juego inactivo")
                    break
                
                # Llamar siguiente número
                number = await consumer.call_next_number()
                if not number:
                    await asyncio.sleep(1)
                    continue

                called_numbers = await consumer.get_current_numbers()
                
                # Notificar a todos los conectados
                await consumer.notify_number_called(number, called_numbers)

                # Verificar ganadores
                winner = await consumer.check_all_players_for_bingo()
                if winner:
                    prize = await consumer.process_winner(winner)
                    await consumer.notify_game_ended(winner.user.username, prize, called_numbers)
                    print(f"🔄 AutoCallManager: Auto-calling terminado para juego {game_id} - juego terminado")
                    break

                # Esperar intervalo
                interval = await database_sync_to_async(lambda: consumer.game.auto_call_interval)()
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            print(f"🔄 AutoCallManager: Auto-calling cancelado para juego {game_id}")
        except Exception as e:
            print(f"❌ AutoCallManager: Error en auto-calling para juego {game_id}: {str(e)}")
        finally:
            if game_id in self._tasks:
                del self._tasks[game_id]

# Instancia global del manager
auto_call_manager = AutoCallManager()
active_game_connections = defaultdict(dict)


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_group_name = 'lobby'
        self.raffle_lobby_group_name = 'raffle_lobby'

        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.raffle_lobby_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.raffle_lobby_group_name,
            self.channel_name
        )

    async def new_game_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_game',
            'html': event['html']
        }))

    async def new_raffle_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_raffle',
            'html': event['html']
        }))

    async def raffle_winner_announcement(self, event):
        # Broadcast simple para usuarios en lobby
        await self.send(text_data=json.dumps({
            'type': 'raffle_winner_announcement',
            'raffle_title': event.get('raffle_title'),
            'winning_number': event.get('winning_number'),
            'winner_username': event.get('winner_username'),
            'prize': event.get('prize'),
            'raffle_id': event.get('raffle_id'),
            'raffle_url': event.get('raffle_url')
        }))

    async def raffle_draw_announcement(self, event):
        # Anuncio de que un sorteo iniciará pronto (lobby)
        await self.send(text_data=json.dumps({
            'type': 'raffle_draw_announcement',
            'message': event.get('message'),
            'raffle_title': event.get('raffle_title'),
            'raffle_id': event.get('raffle_id'),
            'raffle_url': event.get('raffle_url')
        }))

    async def raffle_draw_start(self, event):
        # Inicio de suspenso en lobby (countdown + ruleta)
        await self.send(text_data=json.dumps({
            'type': 'raffle_draw_start',
            'duration_ms': event.get('duration_ms', 5000),
            'countdown_seconds': event.get('countdown_seconds', 3),
            'raffle_title': event.get('raffle_title'),
            'raffle_id': event.get('raffle_id'),
            'raffle_url': event.get('raffle_url')
        }))

class BingoConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_call_task = None
        self.game = None
        self.game_id = None
        self.game_group_name = None
        self.user = None

    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'
        self.game_key = str(self.game_id)
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        self.game = await self.get_game()
        if not self.game:
            await self.close()
            return
            
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        await self.accept()
        self.register_connection()

        # Enviar estado actual del juego al conectar
        await self.send_game_status()
        await self.broadcast_presence()

    async def send_game_status(self):
        """Envía el estado actual del juego al cliente"""
        game_data = await self.get_game_data()

        await self.send(text_data=json.dumps({
            'type': 'game_status',
            'is_started': game_data['is_started'],
            'is_finished': game_data['is_finished'],
            'is_auto_calling': game_data['is_auto_calling'],
            'current_number': game_data['current_number'],
            'called_numbers': game_data['called_numbers'],
            'prize': float(game_data['prize']) if isinstance(game_data['prize'], Decimal) else game_data['prize'],
            'total_cards_sold': game_data['total_cards_sold'],
            'next_prize_target': game_data['next_prize_target'],
            'progress_percentage': game_data['progress_percentage']
        }))

    @database_sync_to_async
    def get_game_data(self):
        if not self.game:
            return None
            
        self.game.refresh_from_db()
        return {
            'is_started': self.game.is_started,
            'is_finished': self.game.is_finished,
            'is_auto_calling': self.game.is_auto_calling,
            'current_number': self.game.current_number,
            'called_numbers': self.game.called_numbers,
            'prize': self.game.prize,
            'total_cards_sold': self.game.total_cards_sold,
            'next_prize_target': self.game.next_prize_target,
            'progress_percentage': self.game.progress_percentage
        }

    async def disconnect(self, close_code):
        # Solo detener auto-calling si el organizador se desconecta Y el juego NO está en modo automático
        try:
            is_organizer = await database_sync_to_async(lambda: self.user == self.game.organizer)()
            is_auto_calling = await database_sync_to_async(lambda: self.game.is_auto_calling)()
            
            # Solo detener si es el organizador Y el juego NO está en modo automático
            if is_organizer and not is_auto_calling:
                auto_call_manager.stop_auto_call(self.game_id)
                print(f"🔄 Organizador desconectado - deteniendo auto-calling para juego {self.game_id}")
            # Si es el organizador pero el juego SÍ está en modo automático, NO detener
            # El auto-calling debe continuar ejecutándose en el servidor
        except Exception as e:
            print(f"❌ Error en disconnect: {str(e)}")
        
        self.unregister_connection()
        await self.broadcast_presence()
        
        if hasattr(self, 'game_group_name'):
            await self.channel_layer.group_discard(
                self.game_group_name,
                self.channel_name
            )

    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def start_game(self):
        if not self.game or self.game.is_started or self.game.is_finished:
            return False
            
        self.game.is_started = True
        self.game.save()
        return True

    @database_sync_to_async
    def call_next_number(self):
        if not self.game:
            return None
        return self.game.call_number()

    @database_sync_to_async
    def get_current_numbers(self):
        if not self.game:
            return []
        return self.game.called_numbers

    @database_sync_to_async
    def check_all_players_for_bingo(self):
        if not self.game:
            return None
        
        # Verificar que el juego no haya terminado (previene doble pago)
        if self.game.is_finished:
            return None
            
        players = Player.objects.filter(game=self.game).select_related('user')
        for player in players:
            if player.check_bingo():
                return player
        return None

    @database_sync_to_async
    def process_winner(self, player):
        if not self.game or not player:
            return 0.0
            
        self.game.refresh_from_db()
        prize = float(self.game.prize) if self.game.prize else 0.0
        
        self.game.end_game()
        return prize

    @database_sync_to_async
    def toggle_auto_call_mode(self):
        if not self.game:
            return False
            
        if self.game.is_auto_calling:
            self.game.stop_auto_calling()
            # Detener auto-calling persistente
            auto_call_manager.stop_auto_call(self.game_id)
            return False
        else:
            self.game.start_auto_calling()
            return True

    async def start_auto_call_task(self):
        """Inicia la tarea de llamada automática persistente usando el manager global"""
        # Usar el manager global para auto-calling persistente
        auto_call_manager.start_auto_call(self.game_id, self)

    async def persistent_auto_call_numbers(self):
        """Tarea persistente de auto-calling que continúa incluso si el organizador se desconecta"""
        print(f"🔄 Iniciando auto-calling persistente para juego {self.game_id}")
        
        while True:
            try:
                # Verificar si el juego sigue activo y en modo auto-calling
                game_active = await self.is_auto_calling_active()
                if not game_active:
                    print(f"🔄 Auto-calling persistente terminado para juego {self.game_id} - juego inactivo")
                    break
                
                # Llamar siguiente número
                number = await self.call_next_number()
                if not number:
                    await asyncio.sleep(1)
                    continue

                called_numbers = await self.get_current_numbers()
                
                # Notificar a todos los conectados
                await self.notify_number_called(number, called_numbers)

                # Verificar ganadores
                winner = await self.check_all_players_for_bingo()
                if winner:
                    prize = await self.process_winner(winner)
                    await self.notify_game_ended(winner.user.username, prize, called_numbers)
                    print(f"🔄 Auto-calling persistente terminado para juego {self.game_id} - juego terminado")
                    break

                # Esperar intervalo
                interval = await database_sync_to_async(lambda: self.game.auto_call_interval)()
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                print(f"🔄 Auto-calling persistente cancelado para juego {self.game_id}")
                break
            except Exception as e:
                print(f"❌ Error en auto-calling persistente para juego {self.game_id}: {str(e)}")
                await asyncio.sleep(5)  # Esperar antes de reintentar

    async def auto_call_numbers(self):
        """Tarea asíncrona para llamada automática de números"""
        while await self.is_auto_calling_active():
            try:
                number = await self.call_next_number()
                if not number:
                    await asyncio.sleep(1)
                    continue

                called_numbers = await self.get_current_numbers()
                

                await self.notify_number_called(number, called_numbers)

                winner = await self.check_all_players_for_bingo()

                if winner:
                    prize = await self.process_winner(winner)
                    await self.notify_game_ended(winner.user.username, prize, called_numbers)
                    break

                
                await asyncio.sleep(self.game.auto_call_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en auto_call_numbers: {str(e)}")
                break

    @database_sync_to_async
    def is_auto_calling_active(self):
        if not self.game:
            return False
        return self.game.is_auto_calling and self.game.is_started and not self.game.is_finished

    async def notify_number_called(self, number, called_numbers):
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'number_called',
                'number': number,
                'called_numbers': called_numbers
            }
        )

    async def notify_game_ended(self, winner, prize, called_numbers):
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_ended',
                'winner': winner,
                'prize': float(prize) if isinstance(prize, Decimal) else prize,
                'called_numbers': called_numbers
            }
        )

    async def notify_game_started(self):
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'game_started',
                'is_started': True,
                'is_auto_calling': self.game.is_auto_calling
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data['type'] == 'start_game':
                if await database_sync_to_async(lambda: self.user == self.game.organizer)():
                    if await self.start_game():
                        await self.notify_game_started()
                        if await database_sync_to_async(lambda: self.game.is_auto_calling)():
                            await self.start_auto_call_task()

            elif data['type'] == 'toggle_auto_call':
                if await database_sync_to_async(lambda: self.user == self.game.organizer)():
                    is_auto_calling = await self.toggle_auto_call_mode()
                    await self.channel_layer.group_send(
                        self.game_group_name,
                        {
                            'type': 'auto_call_toggled',
                            'is_auto_calling': is_auto_calling
                        }
                    )
                    if is_auto_calling:
                        await self.start_auto_call_task()

            elif data['type'] == 'chat_message':
                message = data.get('message', '').strip()
                if message:
                    await self.handle_chat_message(message)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    async def handle_chat_message(self, message):
        await database_sync_to_async(ChatMessage.objects.create)(
            game=self.game,
            user=self.user,
            message=message
        )
        
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'timestamp': datetime.now().isoformat()
            }
        )

    # Handlers para mensajes recibidos del grupo
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp']
        }))

    def register_connection(self):
        if not hasattr(self, 'game_key'):
            return
        active_game_connections[self.game_key][self.channel_name] = getattr(self.user, 'id', None)

    def unregister_connection(self):
        if not hasattr(self, 'game_key'):
            return
        connections = active_game_connections.get(self.game_key, {})
        if self.channel_name in connections:
            del connections[self.channel_name]
        if not connections and self.game_key in active_game_connections:
            del active_game_connections[self.game_key]

    async def broadcast_presence(self):
        if not hasattr(self, 'game_group_name'):
            return
        connections = active_game_connections.get(getattr(self, 'game_key', ''), {})
        unique_users = {uid for uid in connections.values() if uid is not None}
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'presence_update',
                'count': len(unique_users)
            }
        )

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence_update',
            'count': event.get('count', 0)
        }))

    async def number_called(self, event):
        await self.send(text_data=json.dumps({
            'type': 'number_called',
            'number': event['number'],
            'called_numbers': event['called_numbers']
        }))

    async def game_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_ended',
            'winner': event['winner'],
            'prize': event['prize'],
            'called_numbers': event['called_numbers']
        }))

    async def auto_call_toggled(self, event):
        await self.send(text_data=json.dumps({
            'type': 'auto_call_toggled',
            'is_auto_calling': event['is_auto_calling']
        }))

    async def game_started(self, event):
        game_data = await self.get_game_data()
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'is_started': game_data['is_started'],
            'is_auto_calling': game_data['is_auto_calling'],
            'total_cards_sold': game_data['total_cards_sold'],
            'max_cards_sold': self.game.max_cards_sold,
        }))

    async def game_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def prize_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'prize_updated',
            'new_prize': event['new_prize'],
            'increase_amount': event['increase_amount'],
            'total_cards': event['total_cards'],
            'next_target': event['next_target'],
            'progress_percentage': event.get('progress_percentage', 0)
        }))

    async def card_purchased(self, event):
        await self.send(text_data=json.dumps({
            'type': 'card_purchased',
            'user': event.get('user'),
            'new_balance': event.get('new_balance'),
            'player_cards_count': event.get('player_cards_count'),
            'new_cards': event.get('new_cards'),
            'prize_increased': event.get('prize_increased'),
            'new_prize': event.get('new_prize'),
            'increase_amount': event.get('increase_amount'),
            'total_cards_sold': event.get('total_cards_sold'),
            'max_cards_sold': event.get('max_cards_sold'),
            'next_prize_target': event.get('next_prize_target'),
            'progress_percentage': event.get('progress_percentage', 0)
        }))


class MessageConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_group = None

    async def connect(self):
        self.user = self.scope.get('user')
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
            
        self.user_group = f'user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data['type'] == 'private_message':
                recipient_id = data.get('recipient_id')
                content = data.get('content', '').strip()
                
                if not recipient_id or not content:
                    return
                    
                try:
                    message = await self.create_message(recipient_id, content)
                    
                    # Enviar al remitente (confirmación)
                    await self.channel_layer.group_send(
                        f'user_{self.user.id}',
                        {
                            'type': 'message_sent',
                            'message': await self.serialize_message(message)
                        }
                    )
                    
                    # Enviar al destinatario
                    await self.channel_layer.group_send(
                        f'user_{recipient_id}',
                        {
                            'type': 'new_message',
                            'message': await self.serialize_message(message),
                            'sound_type': 'new_message'
                        }
                    )
                except User.DoesNotExist:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Recipient not found'
                    }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    @database_sync_to_async
    def create_message(self, recipient_id, content):
        recipient = User.objects.get(id=recipient_id)
        return Message.objects.create(
            sender=self.user,
            recipient=recipient,
            content=content
        )
    
    @database_sync_to_async
    def serialize_message(self, message):
        return {
            'id': message.id,
            'sender': {
                'id': message.sender.id,
                'username': message.sender.username,
                'is_admin': message.sender.is_admin,
                'is_organizer': message.sender.is_organizer
            },
            'recipient': {
                'id': message.recipient.id,
                'username': message.recipient.username
            },
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read
        }

    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
        
    async def message_sent(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'message': event['message']
        }))
   
class RaffleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.raffle_id = self.scope['url_route']['kwargs'].get('raffle_id')
        self.user = self.scope.get('user', AnonymousUser())
        self.raffle_group_name = f"raffle_{self.raffle_id}"
        await self.channel_layer.group_add(self.raffle_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.raffle_group_name, self.channel_name)

    async def raffle_draw_announcement(self, event):
        await self.send(text_data=json.dumps({
            'type': 'raffle_draw_announcement',
            'message': event.get('message', '¡El sorteo está por comenzar!')
        }))

    async def raffle_draw_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'raffle_draw_start',
            'duration_ms': event.get('duration_ms', 5000),
            'countdown_seconds': event.get('countdown_seconds', 3)
        }))

    async def raffle_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'raffle_winner',
            'winning_number': event.get('winning_number'),
            'winner_username': event.get('winner_username'),
            'prize': event.get('prize')
        }))

    async def ticket_purchased(self, event):
        numbers = event.get('numbers') or []
        single_number = event.get('number')
        if not numbers and single_number is not None:
            numbers = [single_number]

        await self.send(text_data=json.dumps({
            'type': 'ticket_purchased',
            'number': single_number,
            'numbers': numbers,
            'buyer': event.get('buyer'),
            'progress_percentage': event.get('progress_percentage'),
            'total_tickets_sold': event.get('total_tickets_sold')
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        # Suscripción al canal personal del usuario
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        print(f"🔊 NotificationConsumer: Usuario {self.user.username} conectado al grupo {self.user_group_name}")

        # Los superusuarios Y los propietarios de franquicia deben recibir notificaciones de admin
        is_superuser = await database_sync_to_async(lambda: self.user.is_superuser)()
        
        # Verificar si es propietario de franquicia
        def check_franchise_owner(user):
            try:
                from .models import Franchise
                return Franchise.objects.filter(owner=user, is_active=True).exists()
            except:
                return False
        
        is_franchise_owner = await database_sync_to_async(check_franchise_owner)(self.user)
        
        if is_superuser or is_franchise_owner:
            self.admin_group_name = 'admin_notifications'
            await self.channel_layer.group_add(
                self.admin_group_name,
                self.channel_name
            )
            user_type = "SUPERUSER" if is_superuser else "FRANCHISE_OWNER"
            print(f"🔊 NotificationConsumer: Usuario {self.user.username} ({user_type}) conectado al grupo admin_notifications")

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        if hasattr(self, 'admin_group_name'):
            await self.channel_layer.group_discard(
                self.admin_group_name,
                self.channel_name
            )

    # Handler para notificaciones enviadas al grupo de administradores
    async def admin_notification(self, event):
        print(f"🔊 NotificationConsumer: admin_notification recibida por {self.user.username}")
        print(f"🔊 NotificationConsumer: event data: {event}")
        await self.send(text_data=json.dumps({
            'type': 'admin_notification',
            'notification_type': event.get('notification_type'),
            'message': event.get('message'),
            'url': event.get('url'),
            'sound_type': event.get('sound_type'),
            'notification_id': event.get('notification_id')
        }))

    # Handlers para notificaciones enviadas al grupo personal del usuario
    async def credit_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'credit_notification',
            'notification': event['notification']
        }))

    async def withdrawal_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'withdrawal_notification',
            'notification': event['notification']
        }))

    async def win_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'win_notification',
            'message': event['message'],
        }))

    async def credit_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'credit_update',
            'new_balance': event.get('new_balance', 0),
        }))

    async def new_message(self, event):
        # Handler for receiving new message notifications
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sound_type': event.get('sound_type')
        }))
    
    async def credit_approved_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'credit_approved_notification',
            'amount': event['amount'],
            'message': event['message'],
            'sound_type': 'credit_purchase'
        }))
    
    async def credit_rejected_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'credit_rejected_notification',
            'amount': event['amount'],
            'message': event['message'],
            'sound_type': 'credit_purchase'
        }))
    
    async def withdrawal_approved_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'withdrawal_approved_notification',
            'amount': event['amount'],
            'message': event['message'],
            'sound_type': 'withdrawal_request'
        }))
    
    async def withdrawal_completed_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'withdrawal_completed_notification',
            'amount': event['amount'],
            'message': event['message'],
            'sound_type': 'withdrawal_request'
        }))
    
    async def withdrawal_rejected_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'withdrawal_rejected_notification',
            'amount': event['amount'],
            'message': event['message'],
            'sound_type': 'withdrawal_request'
        }))


class DiceGameConsumer(AsyncWebsocketConsumer):
    """
    WebSocket para partidas de dados en tiempo real.
    Maneja: lanzamientos, resultados, eliminaciones, final.
    """
    
    async def connect(self):
        # Aceptar conexión primero para poder enviar errores
        await self.accept()
        
        try:
            # Verificar autenticación
            self.user = self.scope.get('user')
            if not self.user or self.user.is_anonymous:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Debes estar autenticado para jugar'
                }))
                await self.close()
                return
            
            self.room_code = self.scope['url_route']['kwargs']['room_code']
            self.room_group_name = f'dice_game_{self.room_code}'
            
            # Verificar que el usuario es parte de la partida
            try:
                dice_game = await database_sync_to_async(DiceGame.objects.get)(room_code=self.room_code)
            except DiceGame.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Partida no encontrada'
                }))
                await self.close()
                return
            
            # Obtener jugador correctamente usando database_sync_to_async
            def get_player(dice_game, user):
                try:
                    return DicePlayer.objects.get(game=dice_game, user=user)
                except DicePlayer.DoesNotExist:
                    return None
            
            player = await database_sync_to_async(get_player)(dice_game, self.user)
            
            if not player:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'No eres parte de esta partida'
                }))
                await self.close()
                return
            
            # Verificar si el juego debería cambiar de SPINNING a PLAYING
            # Si lleva más de 7 segundos en SPINNING, cambiarlo automáticamente
            if dice_game.status == 'SPINNING' and dice_game.started_at:
                from django.utils import timezone
                from datetime import timedelta
                time_elapsed = timezone.now() - dice_game.started_at
                if time_elapsed.total_seconds() > 7:
                    # Ya debería estar en PLAYING, cambiarlo
                    def change_status_to_playing():
                        try:
                            game = DiceGame.objects.get(room_code=dice_game.room_code)
                            if game.status == 'SPINNING':
                                game.status = 'PLAYING'
                                game.save(update_fields=['status'])
                                from .tasks import notify_game_status_change
                                notify_game_status_change(game)
                                print(f"✅ Estado cambiado de SPINNING a PLAYING para {game.room_code} (verificación al conectar)")
                        except Exception as e:
                            print(f"❌ Error al cambiar estado al conectar: {e}")
                    
                    await database_sync_to_async(change_status_to_playing)()
                    # Recargar el juego para tener el estado actualizado
                    dice_game = await database_sync_to_async(DiceGame.objects.get)(room_code=self.room_code)
            
            # Unirse al grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Enviar estado actual del juego
            await self.send_game_state()
        except Exception as e:
            import traceback
            print(f"Error en connect DiceGameConsumer: {e}")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error al conectar: {str(e)}'
            }))
            await self.close()
    
    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Recibe mensajes del cliente.
        """
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'roll_dice':
            # Jugador quiere lanzar dados
            await self.handle_roll_dice(data)
        elif message_type == 'ready':
            # Jugador está listo para la siguiente ronda
            await self.handle_player_ready(data)
    
    async def handle_roll_dice(self, data):
        """
        Maneja el lanzamiento de dados de un jugador.
        """
        import random
        
        try:
            def roll_dice_and_validate(room_code, user_id):
                try:
                    dice_game = DiceGame.objects.get(room_code=room_code)
                    
                    # Verificar que el juego esté en estado PLAYING
                    if dice_game.status == 'SPINNING':
                        return {'error': 'El juego aún no ha comenzado. Espera a que termine la animación del premio.'}
                    elif dice_game.status != 'PLAYING':
                        return {'error': f'El juego no está disponible para lanzar dados. Estado actual: {dice_game.status}'}
                    
                    # Obtener jugador
                    try:
                        player = DicePlayer.objects.get(game=dice_game, user_id=user_id)
                    except DicePlayer.DoesNotExist:
                        return {'error': 'No eres parte de esta partida.'}
                    
                    # Verificar que el jugador no esté eliminado
                    if player.is_eliminated:
                        return {'error': 'Ya estás eliminado de esta partida.'}
                    
                    # Verificar si el jugador ya lanzó en esta ronda
                    # Obtener la ronda actual (o crear una nueva)
                    from .models import DiceRound
                    current_round = dice_game.rounds.filter(eliminated_player__isnull=True).order_by('-round_number').first()
                    
                    if not current_round:
                        # Crear nueva ronda
                        last_round = dice_game.rounds.order_by('-round_number').first()
                        round_number = (last_round.round_number + 1) if last_round else 1
                        current_round = DiceRound.objects.create(
                            game=dice_game,
                            round_number=round_number,
                            player_results={}
                        )
                    
                    # Verificar si el jugador ya lanzó en esta ronda
                    if str(user_id) in current_round.player_results:
                        return {'error': 'Ya lanzaste los dados en esta ronda. Espera a que todos terminen.'}
                    
                    # Lanzar dados (esto se hace en el servidor para evitar trampas)
                    die1 = random.randint(1, 6)
                    die2 = random.randint(1, 6)
                    total = die1 + die2
                    
                    # Guardar resultado en la ronda
                    current_round.player_results[str(user_id)] = [die1, die2, total]
                    current_round.save()
                    
                    return {
                        'user_id': user_id,
                        'username': player.user.username,
                        'die1': die1,
                        'die2': die2,
                        'total': total,
                        'round_number': current_round.round_number,
                        'current_round_id': current_round.id,
                    }
                except DiceGame.DoesNotExist:
                    return {'error': 'Partida no encontrada'}
                except Exception as e:
                    return {'error': f'Error: {str(e)}'}
            
            result = await database_sync_to_async(roll_dice_and_validate)(self.room_code, self.scope['user'].id)
            
            if 'error' in result:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result['error']
                }))
                return
            
            # Notificar a todos los jugadores del lanzamiento
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'dice_rolled',
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'die1': result['die1'],
                    'die2': result['die2'],
                    'total': result['total'],
                }
            )
            
            # Verificar si todos los jugadores han lanzado en esta ronda
            def check_round_complete(round_id):
                try:
                    from .models import DiceRound, DicePlayer
                    current_round = DiceRound.objects.get(id=round_id)
                    dice_game = current_round.game
                    
                    # Obtener jugadores activos (no eliminados)
                    active_players = DicePlayer.objects.filter(
                        game=dice_game,
                        is_eliminated=False
                    )
                    
                    # Verificar si todos han lanzado
                    if len(current_round.player_results) >= active_players.count():
                        # Todos han lanzado, procesar ronda
                        return process_round_results(dice_game, current_round)
                    
                    return None
                except Exception as e:
                    print(f"Error verificando ronda completa: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            
            def process_round_results(dice_game, current_round):
                """Procesa los resultados de la ronda y determina el perdedor"""
                from .models import DicePlayer
                from django.db import transaction
                
                with transaction.atomic():
                    # Obtener todos los jugadores activos
                    active_players = list(DicePlayer.objects.filter(
                        game=dice_game,
                        is_eliminated=False
                    ).select_for_update())
                    
                    if len(active_players) <= 1:
                        # Solo queda 1 jugador, es el ganador
                        winner = active_players[0]
                        dice_game.winner = winner.user
                        dice_game.status = 'FINISHED'
                        dice_game.finished_at = timezone.now()
                        dice_game.save()
                        
                        # Acreditar premio al ganador
                        from .models import Transaction
                        winner.user.credit_balance += dice_game.final_prize
                        winner.user.save()
                        Transaction.objects.create(
                            user=winner.user,
                            amount=dice_game.final_prize,
                            transaction_type='DICE_WIN',
                            description=f"Ganador de partida de dados {dice_game.room_code}"
                        )
                        
                        return {
                            'round_complete': True,
                            'round_number': current_round.round_number,
                            'results': current_round.player_results,
                            'eliminated': None,
                            'winner': winner.user.username,
                            'game_finished': True,
                            'final_prize': str(dice_game.final_prize)
                        }
                    
                    # Encontrar el jugador con el número más bajo
                    lowest_total = float('inf')
                    loser_player = None
                    
                    for player in active_players:
                        player_result = current_round.player_results.get(str(player.user.id))
                        if player_result:
                            total = player_result[2]  # El total está en el índice 2
                            if total < lowest_total:
                                lowest_total = total
                                loser_player = player
                    
                    # Reducir vida del perdedor
                    if loser_player:
                        loser_player.lives -= 1
                        current_round.eliminated_player = loser_player.user
                        
                        if loser_player.lives <= 0:
                            loser_player.is_eliminated = True
                            eliminated_msg = loser_player.user.username
                        else:
                            eliminated_msg = None
                        
                        loser_player.save()
                        current_round.save()
                        
                        # Verificar si solo queda 1 jugador
                        remaining_players = DicePlayer.objects.filter(
                            game=dice_game,
                            is_eliminated=False
                        )
                        
                        if remaining_players.count() == 1:
                            # Hay un ganador
                            winner = remaining_players.first()
                            dice_game.winner = winner.user
                            dice_game.status = 'FINISHED'
                            dice_game.finished_at = timezone.now()
                            dice_game.save()
                            
                            # Acreditar premio
                            from .models import Transaction
                            winner.user.credit_balance += dice_game.final_prize
                            winner.user.save()
                            Transaction.objects.create(
                                user=winner.user,
                                amount=dice_game.final_prize,
                                transaction_type='DICE_WIN',
                                description=f"Ganador de partida de dados {dice_game.room_code}"
                            )
                            
                            return {
                                'round_complete': True,
                                'round_number': current_round.round_number,
                                'results': current_round.player_results,
                                'eliminated': eliminated_msg,
                                'winner': winner.user.username,
                                'game_finished': True,
                                'final_prize': str(dice_game.final_prize)
                            }
                        
                        return {
                            'round_complete': True,
                            'round_number': current_round.round_number,
                            'results': current_round.player_results,
                            'eliminated': eliminated_msg,
                            'winner': None,
                            'game_finished': False
                        }
                    
                    return None
            
            # Verificar si la ronda está completa
            round_result = await database_sync_to_async(check_round_complete)(result['current_round_id'])
            
            if round_result:
                # Ronda completa, notificar resultados
                if round_result.get('game_finished'):
                    # Juego terminado
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_finished',
                            'winner': round_result['winner'],
                            'prize': round_result['final_prize'],
                            'multiplier': dice_game.multiplier,
                        }
                    )
                else:
                    # Ronda terminada, hay perdedor pero el juego continúa
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'round_result',
                            'round_number': round_result['round_number'],
                            'results': round_result['results'],
                            'eliminated': round_result.get('eliminated'),
                        }
                    )
        except Exception as e:
            import traceback
            print(f"Error en handle_roll_dice: {e}")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al lanzar dados'
            }))
    
    async def dice_rolled(self, event):
        """
        Envía resultado de lanzamiento a todos los jugadores.
        """
        await self.send(text_data=json.dumps({
            'type': 'dice_rolled',
            'user_id': event['user_id'],
            'username': event['username'],
            'die1': event['die1'],
            'die2': event['die2'],
            'total': event['total'],
        }))
    
    async def prize_spun(self, event):
        """
        Notifica que el premio fue determinado.
        """
        await self.send(text_data=json.dumps({
            'type': 'prize_spun',
            'multiplier': event['multiplier'],
            'final_prize': str(event['final_prize']),
        }))
    
    async def round_result(self, event):
        """
        Notifica resultado de una ronda.
        """
        await self.send(text_data=json.dumps({
            'type': 'round_result',
            'round_number': event['round_number'],
            'results': event['results'],
            'eliminated': event.get('eliminated'),
        }))
    
    async def game_finished(self, event):
        """
        Notifica que el juego terminó.
        """
        await self.send(text_data=json.dumps({
            'type': 'game_finished',
            'winner': event['winner'],
            'prize': str(event['prize']),
            'multiplier': event['multiplier'],
        }))
    
    async def game_status_changed(self, event):
        """
        Notifica cambio de estado del juego.
        """
        await self.send(text_data=json.dumps({
            'type': 'game_status_changed',
            'status': event['status'],
            'multiplier': event.get('multiplier'),
            'final_prize': event.get('final_prize'),
        }))
    
    async def send_game_state(self):
        """
        Envía el estado actual del juego al conectarse.
        """
        try:
            def get_game_state(room_code):
                try:
                    dice_game = DiceGame.objects.get(room_code=room_code)
                    players_data = []
                    
                    for p in dice_game.dice_players.all():
                        avatar_url = ''  # Usar string vacío para que el cliente use su lógica por defecto
                        
                        # Obtener avatar de forma segura
                        try:
                            if hasattr(p.user, 'get_avatar_url'):
                                avatar_url = p.user.get_avatar_url()
                            elif hasattr(p.user, 'avatar') and p.user.avatar:
                                if hasattr(p.user.avatar, 'custom_avatar') and p.user.avatar.custom_avatar:
                                    avatar_url = p.user.avatar.custom_avatar.url
                        except:
                            pass  # Usar avatar por defecto si falla
                        
                        players_data.append({
                            'user_id': p.user.id,
                            'username': p.user.username,
                            'avatar_url': avatar_url,
                            'lives': p.lives,
                            'is_eliminated': p.is_eliminated,
                        })
                    
                    return {
                        'type': 'game_state',
                        'status': dice_game.status,
                        'multiplier': dice_game.multiplier,
                        'final_prize': str(dice_game.final_prize),
                        'players': players_data,
                    }
                except DiceGame.DoesNotExist:
                    return {
                        'type': 'error',
                        'message': 'Partida no encontrada'
                    }
            
            state = await database_sync_to_async(get_game_state)(self.room_code)
            await self.send(text_data=json.dumps(state))
        except Exception as e:
            import traceback
            print(f"Error en send_game_state: {e}")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al obtener estado del juego'
            }))
    
    async def handle_player_ready(self, data):
        """
        Maneja cuando un jugador está listo.
        """
        # Implementar lógica de "ready" si es necesaria
        pass