# CÓDIGO COMPLETO DEL JUEGO DE DADOS (DICE BATTLE)

Este documento contiene TODO el código del juego de dados para copiar y pegar.

---

## 1. MODELOS (models.py)

### DiceModuleSettings
```python
class DiceModuleSettings(models.Model):
    is_module_enabled = models.BooleanField(default=False)
    base_entry_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.10'))
    allow_custom_entry_price = models.BooleanField(default=True)
    max_entry_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    multiplier_probabilities = models.JSONField(default=dict)
    max_players_per_game = models.PositiveIntegerField(default=3)
    power_ups_enabled = models.BooleanField(default=False)
    platform_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    show_in_lobby = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'is_module_enabled': False,
                'multiplier_probabilities': {
                    '2x': 0.60, '3x': 0.25, '5x': 0.10, '10x': 0.03,
                    '25x': 0.01, '100x': 0.005, '500x': 0.003, '1000x': 0.002
                }
            }
        )
        return settings
```

### DiceGame
```python
class DiceGame(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Esperando jugadores'),
        ('SPINNING', 'Determinando premio'),
        ('PLAYING', 'En juego'),
        ('FINISHED', 'Terminada'),
    ]
    
    room_code = models.CharField(max_length=10, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING', db_index=True)
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.10'))
    base_prize = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    multiplier = models.CharField(max_length=10, default='1x')
    final_prize = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    players = models.ManyToManyField(User, through='DicePlayer', related_name='dice_games')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_dice_games')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    def generate_room_code(self):
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while DiceGame.objects.filter(room_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return code
    
    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = self.generate_room_code()
        super().save(*args, **kwargs)
    
    def calculate_base_prize(self):
        return self.entry_price * Decimal('3')
    
    def spin_prize(self):
        import random
        settings = DiceModuleSettings.get_settings()
        probabilities = settings.multiplier_probabilities
        rand = random.random()
        cumulative = 0.0
        sorted_probs = sorted(probabilities.items(), key=lambda x: float(x[1]))
        
        for multiplier, prob in sorted_probs:
            cumulative += float(prob)
            if rand <= cumulative:
                self.multiplier = multiplier
                break
        
        multiplier_value = float(self.multiplier.replace('x', ''))
        self.final_prize = self.base_prize * Decimal(str(multiplier_value))
        commission = self.final_prize * (settings.platform_commission_percentage / 100)
        self.final_prize = self.final_prize - commission
        self.status = 'SPINNING'
        self.save()
        return self.multiplier, self.final_prize
```

### DicePlayer
```python
class DicePlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dice_player_instances')
    game = models.ForeignKey(DiceGame, on_delete=models.CASCADE, related_name='dice_players')
    is_eliminated = models.BooleanField(default=False)
    lives = models.PositiveIntegerField(default=3)
    total_score = models.PositiveIntegerField(default=0)
    power_ups_used = models.JSONField(default=list)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'game')
```

### DiceRound
```python
class DiceRound(models.Model):
    game = models.ForeignKey(DiceGame, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField(default=1)
    player_results = models.JSONField(default=dict, help_text="Dict con user_id: [dado1, dado2, suma]")
    eliminated_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='eliminated_in_rounds')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['round_number']
```

### DiceMatchmakingQueue
```python
class DiceMatchmakingQueue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dice_queue_entries')
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.10'))])
    status = models.CharField(max_length=20, choices=[
        ('WAITING', 'Esperando jugadores'),
        ('MATCHED', 'Emparejado - Creando partida'),
        ('TIMEOUT', 'Timeout - Cancelado'),
    ], default='WAITING')
    joined_at = models.DateTimeField(auto_now_add=True, db_index=True)
    matched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['joined_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='WAITING'),
                name='unique_user_waiting_queue'
            )
        ]
```

---

## 2. VISTAS (views.py)

### dice_lobby
```python
@login_required
@dice_module_required
def dice_lobby(request):
    settings = DiceModuleSettings.get_settings()
    
    # Verificar si el usuario tiene una partida activa
    active_game = DiceGame.objects.filter(
        dice_players__user=request.user,
        status__in=['WAITING', 'SPINNING', 'PLAYING']
    ).exclude(status='FINISHED').order_by('-created_at').first()
    
    if active_game:
        return redirect('dice_game_room', room_code=active_game.room_code)
    
    # Limpiar entradas antiguas
    from django.utils import timezone
    from datetime import timedelta
    DiceMatchmakingQueue.objects.filter(
        user=request.user,
        status='WAITING',
        joined_at__lt=timezone.now() - timedelta(minutes=10)
    ).update(status='TIMEOUT')
    
    context = {
        'settings': settings,
        'entry_price': settings.base_entry_price,
        'min_price': Decimal('0.10'),
        'max_price': settings.max_entry_price,
        'active_game': None,
    }
    return render(request, 'bingo_app/dice_lobby.html', context)
```

### join_dice_queue
```python
@login_required
@dice_module_required
@require_POST
def join_dice_queue(request):
    try:
        entry_price = Decimal(request.POST.get('entry_price', '0.10'))
        
        if entry_price < Decimal('0.10'):
            return JsonResponse({'success': False, 'error': 'El precio mínimo es $0.10'}, status=400)
        
        if request.user.credit_balance < entry_price:
            return JsonResponse({'success': False, 'error': 'Saldo insuficiente'}, status=400)
        
        # Verificar partida activa
        active_player = DicePlayer.objects.filter(
            user=request.user,
            game__status__in=['WAITING', 'SPINNING', 'PLAYING']
        ).select_related('game').first()
        
        if active_player:
            return JsonResponse({
                'success': False,
                'error': 'Ya tienes una partida activa',
                'status': 'matched',
                'room_code': active_player.game.room_code
            }, status=400)
        
        # Limpiar entradas antiguas
        DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING',
            joined_at__lt=timezone.now() - timedelta(minutes=10)
        ).update(status='TIMEOUT')
        
        # Verificar si ya está en cola
        existing_queue = DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING'
        ).first()
        
        if existing_queue:
            return JsonResponse({
                'success': True,
                'status': 'waiting',
                'message': 'Ya estás en la cola, buscando oponentes...'
            })
        
        # Crear entrada en cola
        queue_entry = DiceMatchmakingQueue.objects.create(
            user=request.user,
            entry_price=entry_price,
            status='WAITING'
        )
        
        # Procesar matchmaking
        from .tasks import process_matchmaking_queue
        result = process_matchmaking_queue()
        
        if result:
            result.refresh_from_db()
            player = DicePlayer.objects.filter(user=request.user, game=result).first()
            if player:
                return JsonResponse({
                    'success': True,
                    'status': 'matched',
                    'room_code': result.room_code,
                    'message': '¡Partida encontrada!'
                })
        
        return JsonResponse({
            'success': True,
            'status': 'waiting',
            'message': 'Buscando oponentes...'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
```

### dice_queue_status
```python
@login_required
@dice_module_required
def dice_queue_status(request):
    try:
        # Verificar partida activa
        active_player = DicePlayer.objects.filter(
            user=request.user,
            game__status__in=['SPINNING', 'PLAYING', 'WAITING']
        ).select_related('game').order_by('-game__created_at').first()
        
        if active_player:
            return JsonResponse({
                'status': 'matched',
                'room_code': active_player.game.room_code,
                'message': 'Tienes una partida activa'
            })
        
        # Verificar cola
        queue_entry = DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status='WAITING'
        ).first()
        
        # Ejecutar matchmaking
        from .tasks import process_matchmaking_queue
        matchmaking_result = process_matchmaking_queue()
        
        if matchmaking_result:
            matchmaking_result.refresh_from_db()
            player = DicePlayer.objects.filter(user=request.user, game=matchmaking_result).first()
            if player:
                return JsonResponse({
                    'status': 'matched',
                    'room_code': matchmaking_result.room_code,
                    'message': '¡Partida encontrada!'
                })
        
        if not queue_entry:
            return JsonResponse({'status': 'not_in_queue'})
        
        same_price_count = DiceMatchmakingQueue.objects.filter(
            status='WAITING',
            entry_price=queue_entry.entry_price
        ).count()
        
        return JsonResponse({
            'status': 'waiting',
            'entry_price': float(queue_entry.entry_price),
            'players_waiting': same_price_count,
            'message': f'Buscando oponentes... ({same_price_count}/3 jugadores con precio ${queue_entry.entry_price})'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
```

### dice_game_room
```python
@login_required
@dice_module_required
def dice_game_room(request, room_code):
    try:
        dice_game = DiceGame.objects.get(room_code=room_code)
        player = DicePlayer.objects.filter(game=dice_game, user=request.user).first()
        
        if not player:
            messages.error(request, 'No eres parte de esta partida')
            return redirect('dice_lobby')
        
        # Limpiar cola
        DiceMatchmakingQueue.objects.filter(
            user=request.user,
            status__in=['WAITING', 'MATCHED']
        ).update(status='TIMEOUT')
        
        players = dice_game.dice_players.all()
        context = {
            'dice_game': dice_game,
            'player': player,
            'players': players,
            'room_code': room_code,
        }
        return render(request, 'bingo_app/dice_game_room.html', context)
    except DiceGame.DoesNotExist:
        messages.error(request, 'Partida no encontrada')
        return redirect('dice_lobby')
```

---

## 3. TASKS (tasks.py) - MATCHMAKING

```python
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import DiceMatchmakingQueue, DiceGame, DicePlayer, DiceModuleSettings, Transaction

def process_matchmaking_queue():
    print(f"🔄 [MATCHMAKING] ========== INICIANDO PROCESO DE MATCHMAKING ==========")
    
    all_waiting = DiceMatchmakingQueue.objects.filter(status='WAITING')
    unique_prices = list(set(all_waiting.values_list('entry_price', flat=True)))
    total_count = all_waiting.count()
    
    if total_count == 0:
        return None
    
    games_created = []
    
    for price in unique_prices:
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            waiting_players_query = DiceMatchmakingQueue.objects.filter(
                status='WAITING',
                entry_price=price
            ).order_by('joined_at')
            
            total_waiting = waiting_players_query.count()
            if total_waiting < 3:
                break
            
            try:
                with transaction.atomic():
                    # Bloquear filas dentro de la transacción
                    waiting_players_query_locked = DiceMatchmakingQueue.objects.filter(
                        status='WAITING',
                        entry_price=price
                    ).order_by('joined_at').select_for_update(skip_locked=True)
                    
                    waiting_players_list = list(waiting_players_query_locked[:3])
                    if len(waiting_players_list) < 3:
                        break
                    
                    # Verificar saldo
                    players_list = []
                    for queue_entry in waiting_players_list:
                        queue_entry.user.refresh_from_db()
                        if queue_entry.user.credit_balance >= queue_entry.entry_price:
                            players_list.append(queue_entry)
                        else:
                            queue_entry.status = 'TIMEOUT'
                            queue_entry.save()
                    
                    if len(players_list) < 3:
                        break
                    
                    # Verificar partidas activas
                    fresh_queue_entries = []
                    for queue_entry in players_list:
                        queue_entry.refresh_from_db()
                        active_game = DiceGame.objects.filter(
                            dice_players__user=queue_entry.user,
                            status__in=['WAITING', 'SPINNING', 'PLAYING']
                        ).exclude(status='FINISHED').first()
                        
                        if active_game:
                            queue_entry.status = 'TIMEOUT'
                            queue_entry.save()
                            continue
                        
                        if queue_entry.status != 'WAITING':
                            continue
                        
                        fresh_queue_entries.append(queue_entry)
                    
                    if len(fresh_queue_entries) < 3:
                        break
                    
                    players_list = fresh_queue_entries
                    
                    # Bloquear créditos
                    for queue_entry in players_list:
                        user = queue_entry.user
                        user.credit_balance -= queue_entry.entry_price
                        user.blocked_credits += queue_entry.entry_price
                        user.save()
                        
                        Transaction.objects.create(
                            user=user,
                            amount=-queue_entry.entry_price,
                            transaction_type='ENTRY_FEE',
                            description=f"Entrada a partida de dados (${queue_entry.entry_price})"
                        )
                    
                    # Crear partida
                    base_prize = price * Decimal('3')
                    dice_game = DiceGame.objects.create(
                        entry_price=price,
                        base_prize=base_prize,
                        status='WAITING',
                    )
                    
                    # Agregar jugadores
                    for queue_entry in players_list:
                        DicePlayer.objects.create(
                            user=queue_entry.user,
                            game=dice_game,
                            lives=3,
                        )
                        queue_entry.status = 'MATCHED'
                        queue_entry.matched_at = timezone.now()
                        queue_entry.save()
                        
                        DiceMatchmakingQueue.objects.filter(
                            user=queue_entry.user,
                            status='WAITING'
                        ).exclude(id=queue_entry.id).update(status='TIMEOUT')
                    
                    # Spin del premio
                    dice_game.spin_prize()
                    dice_game.status = 'SPINNING'
                    dice_game.started_at = timezone.now()
                    dice_game.save()
                    
                    # Notificar jugadores
                    notify_players_match_found(dice_game, players_list)
                    
                    # Cambiar a PLAYING después de 7 segundos
                    import threading
                    def change_to_playing():
                        import time
                        time.sleep(7)
                        try:
                            from django.db import transaction
                            from .models import DiceGame as DG
                            with transaction.atomic():
                                game = DG.objects.select_for_update().get(room_code=dice_game.room_code)
                                if game.status == 'SPINNING':
                                    game.status = 'PLAYING'
                                    game.save(update_fields=['status'])
                                    notify_game_status_change(game)
                        except Exception as e:
                            print(f"Error: {e}")
                    
                    thread = threading.Thread(target=change_to_playing, daemon=True)
                    thread.start()
                    
                    games_created.append(dice_game)
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    return games_created[0] if games_created else None

def notify_players_match_found(dice_game, players_list):
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

def notify_game_status_change(dice_game):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'dice_game_{dice_game.room_code}',
        {
            'type': 'game_status_changed',
            'status': dice_game.status,
            'multiplier': dice_game.multiplier,
            'final_prize': str(dice_game.final_prize),
        }
    )
```

---

## 4. CONSUMER (consumers.py) - WEBSOCKET

```python
class DiceGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            self.user = self.scope.get('user')
            if not self.user or self.user.is_anonymous:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Debes estar autenticado'
                }))
                await self.close()
                return
            
            self.room_code = self.scope['url_route']['kwargs']['room_code']
            self.room_group_name = f'dice_game_{self.room_code}'
            
            dice_game = await database_sync_to_async(DiceGame.objects.get)(room_code=self.room_code)
            
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
            
            # Verificar si debe cambiar de SPINNING a PLAYING
            if dice_game.status == 'SPINNING' and dice_game.started_at:
                from django.utils import timezone
                time_elapsed = timezone.now() - dice_game.started_at
                if time_elapsed.total_seconds() > 7:
                    def change_status_to_playing():
                        try:
                            game = DiceGame.objects.get(room_code=dice_game.room_code)
                            if game.status == 'SPINNING':
                                game.status = 'PLAYING'
                                game.save(update_fields=['status'])
                                from .tasks import notify_game_status_change
                                notify_game_status_change(game)
                        except Exception as e:
                            print(f"Error: {e}")
                    await database_sync_to_async(change_status_to_playing)()
                    dice_game = await database_sync_to_async(DiceGame.objects.get)(room_code=self.room_code)
            
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.send_game_state()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}'
            }))
            await self.close()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'roll_dice':
            await self.handle_roll_dice(data)
    
    async def handle_roll_dice(self, data):
        import random
        
        def roll_dice_and_validate(room_code, user_id):
            try:
                dice_game = DiceGame.objects.get(room_code=room_code)
                
                if dice_game.status == 'SPINNING':
                    return {'error': 'El juego aún no ha comenzado'}
                elif dice_game.status != 'PLAYING':
                    return {'error': f'Estado: {dice_game.status}'}
                
                player = DicePlayer.objects.get(game=dice_game, user_id=user_id)
                if player.is_eliminated:
                    return {'error': 'Ya estás eliminado'}
                
                # Obtener o crear ronda
                from .models import DiceRound
                current_round = dice_game.rounds.filter(eliminated_player__isnull=True).order_by('-round_number').first()
                
                if not current_round:
                    last_round = dice_game.rounds.order_by('-round_number').first()
                    round_number = (last_round.round_number + 1) if last_round else 1
                    current_round = DiceRound.objects.create(
                        game=dice_game,
                        round_number=round_number,
                        player_results={}
                    )
                
                # Verificar si ronda procesada
                active_players_count = DicePlayer.objects.filter(
                    game=dice_game,
                    is_eliminated=False
                ).count()
                
                rounds_results_count = len(current_round.player_results) if current_round.player_results else 0
                is_round_processed = (
                    current_round.eliminated_player is not None or
                    (rounds_results_count >= active_players_count and active_players_count > 0)
                )
                
                if is_round_processed:
                    from django.db import transaction
                    with transaction.atomic():
                        dice_game.refresh_from_db()
                        last_round = dice_game.rounds.order_by('-round_number').first()
                        if last_round:
                            active_players_count_check = DicePlayer.objects.filter(
                                game=dice_game,
                                is_eliminated=False
                            ).count()
                            last_round_results_count = len(last_round.player_results) if last_round.player_results else 0
                            is_last_round_processed = (
                                last_round.eliminated_player is not None or
                                (last_round_results_count >= active_players_count_check and active_players_count_check > 0)
                            )
                            
                            if is_last_round_processed:
                                round_number = last_round.round_number + 1
                                if not dice_game.rounds.filter(round_number=round_number).exists():
                                    current_round = DiceRound.objects.create(
                                        game=dice_game,
                                        round_number=round_number,
                                        player_results={}
                                    )
                                else:
                                    current_round = dice_game.rounds.get(round_number=round_number)
                            else:
                                current_round = last_round
                        else:
                            current_round = DiceRound.objects.create(
                                game=dice_game,
                                round_number=1,
                                player_results={}
                            )
                
                if str(user_id) in current_round.player_results:
                    return {'error': 'Ya lanzaste los dados en esta ronda'}
                
                # Lanzar dados
                die1 = random.randint(1, 6)
                die2 = random.randint(1, 6)
                total = die1 + die2
                
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
            except Exception as e:
                return {'error': str(e)}
        
        result = await database_sync_to_async(roll_dice_and_validate)(self.room_code, self.scope['user'].id)
        
        if 'error' in result:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': result['error']
            }))
            return
        
        # Notificar lanzamiento
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'dice_rolled',
            'user_id': result['user_id'],
            'username': result['username'],
            'die1': result['die1'],
            'die2': result['die2'],
            'total': result['total'],
        })
        
        # Procesar ronda
        def check_and_process_round(round_id):
            try:
                from .models import DiceRound, DicePlayer, Transaction
                from django.db import transaction
                from django.utils import timezone
                
                current_round = DiceRound.objects.get(id=round_id)
                dice_game = current_round.game
                
                active_players = DicePlayer.objects.filter(
                    game=dice_game,
                    is_eliminated=False
                )
                
                if len(current_round.player_results) < active_players.count():
                    return None
                
                with transaction.atomic():
                    dice_game.refresh_from_db()
                    current_round.refresh_from_db()
                    active_players = list(DicePlayer.objects.filter(
                        game=dice_game,
                        is_eliminated=False
                    ).select_for_update())
                    
                    if len(active_players) <= 1:
                        winner = active_players[0]
                        dice_game.winner = winner.user
                        dice_game.status = 'FINISHED'
                        dice_game.finished_at = timezone.now()
                        dice_game.save()
                        
                        winner.user.credit_balance += dice_game.final_prize
                        winner.user.save()
                        Transaction.objects.create(
                            user=winner.user,
                            amount=dice_game.final_prize,
                            transaction_type='DICE_WIN',
                            description=f"Ganador de partida de dados {dice_game.room_code}"
                        )
                        
                        complete_round_results = {}
                        all_players_in_game = DicePlayer.objects.filter(game=dice_game)
                        for player in all_players_in_game:
                            player_id_str = str(player.user.id)
                            if player_id_str in current_round.player_results:
                                complete_round_results[player_id_str] = current_round.player_results[player_id_str]
                            else:
                                complete_round_results[player_id_str] = [0, 0, 0]
                        
                        return {
                            'round_complete': True,
                            'round_number': current_round.round_number,
                            'results': complete_round_results,
                            'eliminated': None,
                            'winner': winner.user.username,
                            'game_finished': True,
                            'final_prize': str(dice_game.final_prize),
                            'multiplier': dice_game.multiplier
                        }
                    
                    # Encontrar perdedores
                    lowest_total = float('inf')
                    losers = []
                    
                    for player in active_players:
                        player_result = current_round.player_results.get(str(player.user.id))
                        if player_result:
                            total = player_result[2]
                            if total < lowest_total:
                                lowest_total = total
                    
                    for player in active_players:
                        player_result = current_round.player_results.get(str(player.user.id))
                        if player_result:
                            total = player_result[2]
                            if total == lowest_total:
                                losers.append(player)
                    
                    # Reducir vidas
                    eliminated_msg = None
                    eliminated_players = []
                    
                    for loser_player in losers:
                        loser_player.lives -= 1
                        if loser_player.lives <= 0:
                            loser_player.is_eliminated = True
                            eliminated_players.append(loser_player.user.username)
                        loser_player.save()
                    
                    if len(losers) == 1:
                        current_round.eliminated_player = losers[0].user
                        if losers[0].lives <= 0:
                            eliminated_msg = losers[0].user.username
                    else:
                        if eliminated_players:
                            eliminated_msg = ", ".join(eliminated_players)
                    
                    current_round.save()
                    
                    # Verificar ganador
                    remaining_players = DicePlayer.objects.filter(
                        game=dice_game,
                        is_eliminated=False
                    )
                    
                    if remaining_players.count() == 1:
                        winner = remaining_players.first()
                        dice_game.winner = winner.user
                        dice_game.status = 'FINISHED'
                        dice_game.finished_at = timezone.now()
                        dice_game.save()
                        
                        winner.user.credit_balance += dice_game.final_prize
                        winner.user.save()
                        Transaction.objects.create(
                            user=winner.user,
                            amount=dice_game.final_prize,
                            transaction_type='DICE_WIN',
                            description=f"Ganador de partida de dados {dice_game.room_code}"
                        )
                        
                        complete_round_results = {}
                        all_players_in_game = DicePlayer.objects.filter(game=dice_game)
                        for player in all_players_in_game:
                            player_id_str = str(player.user.id)
                            if player_id_str in current_round.player_results:
                                complete_round_results[player_id_str] = current_round.player_results[player_id_str]
                            else:
                                complete_round_results[player_id_str] = [0, 0, 0]
                        
                        return {
                            'round_complete': True,
                            'round_number': current_round.round_number,
                            'results': complete_round_results,
                            'eliminated': eliminated_msg,
                            'winner': winner.user.username,
                            'game_finished': True,
                            'final_prize': str(dice_game.final_prize),
                            'multiplier': dice_game.multiplier
                        }
                    
                    # Continuar juego
                    complete_round_results = {}
                    for player in active_players:
                        player_id_str = str(player.user.id)
                        if player_id_str in current_round.player_results:
                            complete_round_results[player_id_str] = current_round.player_results[player_id_str]
                        else:
                            complete_round_results[player_id_str] = [0, 0, 0]
                    
                    return {
                        'round_complete': True,
                        'round_number': current_round.round_number,
                        'results': complete_round_results,
                        'eliminated': eliminated_msg,
                        'winner': None,
                        'game_finished': False
                    }
            except Exception as e:
                print(f"Error: {e}")
                return None
        
        round_result = await database_sync_to_async(check_and_process_round)(result['current_round_id'])
        
        if round_result:
            if round_result.get('game_finished'):
                multiplier = round_result.get('multiplier')
                if not multiplier:
                    dice_game_refresh = await database_sync_to_async(DiceGame.objects.get)(room_code=self.room_code)
                    multiplier = dice_game_refresh.multiplier
                
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'game_finished',
                    'winner': round_result['winner'],
                    'prize': str(round_result['final_prize']),
                    'multiplier': str(multiplier) if multiplier else 'N/A',
                })
            else:
                await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'round_result',
                    'round_number': round_result['round_number'],
                    'results': round_result['results'],
                    'eliminated': round_result.get('eliminated'),
                })
    
    async def dice_rolled(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dice_rolled',
            'user_id': event['user_id'],
            'username': event['username'],
            'die1': event['die1'],
            'die2': event['die2'],
            'total': event['total'],
        }))
    
    async def round_result(self, event):
        results = event.get('results', {})
        try:
            def get_all_players(room_code):
                dice_game = DiceGame.objects.get(room_code=room_code)
                return list(dice_game.dice_players.all())
            
            players_list = await database_sync_to_async(get_all_players)(self.room_code)
            complete_results = {}
            for player in players_list:
                player_id_str = str(player.user.id)
                if player_id_str in results:
                    complete_results[player_id_str] = results[player_id_str]
                else:
                    complete_results[player_id_str] = {'total': 0, 'die1': 0, 'die2': 0}
            
            await self.send(text_data=json.dumps({
                'type': 'round_result',
                'round_number': event['round_number'],
                'results': complete_results,
                'eliminated': event.get('eliminated'),
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'round_result',
                'round_number': event['round_number'],
                'results': results,
                'eliminated': event.get('eliminated'),
            }))
    
    async def game_finished(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_finished',
            'winner': event['winner'],
            'prize': str(event['prize']),
            'multiplier': event['multiplier'],
        }))
    
    async def game_status_changed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_status_changed',
            'status': event['status'],
            'multiplier': event.get('multiplier'),
            'final_prize': event.get('final_prize'),
        }))
    
    async def send_game_state(self):
        def get_game_state(room_code):
            try:
                dice_game = DiceGame.objects.get(room_code=room_code)
                players_data = []
                
                for p in dice_game.dice_players.all():
                    avatar_url = ''
                    try:
                        if hasattr(p.user, 'get_avatar_url'):
                            avatar_url = p.user.get_avatar_url()
                        elif hasattr(p.user, 'avatar') and p.user.avatar:
                            if hasattr(p.user.avatar, 'custom_avatar') and p.user.avatar.custom_avatar:
                                avatar_url = p.user.avatar.custom_avatar.url
                    except:
                        pass
                    
                    players_data.append({
                        'user_id': p.user.id,
                        'username': p.user.username,
                        'avatar_url': avatar_url,
                        'lives': p.lives,
                        'is_eliminated': p.is_eliminated,
                    })
                
                while len(players_data) < 3:
                    players_data.append({
                        'user_id': None,
                        'username': 'Esperando...',
                        'avatar_url': '/static/avatars/default/male.png',
                        'lives': 0,
                        'is_eliminated': False,
                    })
                
                return {
                    'type': 'game_state',
                    'status': dice_game.status,
                    'multiplier': dice_game.multiplier,
                    'final_prize': str(dice_game.final_prize),
                    'players': players_data,
                }
            except DiceGame.DoesNotExist:
                return None
        
        game_state = await database_sync_to_async(get_game_state)(self.room_code)
        if game_state:
            await self.send(text_data=json.dumps(game_state))
```

---

## 5. URLS (urls.py)

```python
path('dice/', views.dice_lobby, name='dice_lobby'),
path('dice/join-queue/', views.join_dice_queue, name='join_dice_queue'),
path('dice/leave-queue/', views.leave_dice_queue, name='leave_dice_queue'),
path('dice/queue-status/', views.dice_queue_status, name='dice_queue_status'),
path('dice/game/<str:room_code>/', views.dice_game_room, name='dice_game_room'),
```

---

## 6. ROUTING (routing.py)

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/dice/game/(?P<room_code>[A-Z0-9]+)/$', consumers.DiceGameConsumer.as_asgi()),
]
```

---

## 7. TEMPLATES

### dice_lobby.html
[Ver archivo completo en: bingo_app/templates/bingo_app/dice_lobby.html]

### dice_game_room.html
[Ver archivo completo en: bingo_app/templates/bingo_app/dice_game_room.html]

---

## 8. JAVASCRIPT

### dice_websocket.js
[Ver archivo completo en: bingo_app/static/js/dice_websocket.js]

### dice_game.js
[Ver archivo completo en: bingo_app/static/js/dice_game.js]

### dice_table_colors.js
[Ver archivo completo en: bingo_app/static/js/dice_table_colors.js]

---

## 9. CSS

### dice_table.css
[Ver archivo completo en: bingo_app/static/css/dice_table.css]

---

## NOTAS IMPORTANTES:

1. **Dependencias**: Requiere Django Channels para WebSockets
2. **Base de datos**: Necesita migraciones para los modelos
3. **Decoradores**: Requiere `@dice_module_required` y `@login_required`
4. **Configuración**: El módulo debe estar activado en `DiceModuleSettings`
5. **WebSocket**: Requiere configuración de Channels en `settings.py`

---

## ESTRUCTURA DE ARCHIVOS:

```
bingo_app/
├── models.py          (DiceGame, DicePlayer, DiceRound, DiceMatchmakingQueue, DiceModuleSettings)
├── views.py           (dice_lobby, join_dice_queue, dice_queue_status, dice_game_room)
├── consumers.py       (DiceGameConsumer)
├── tasks.py           (process_matchmaking_queue, notify_players_match_found, notify_game_status_change)
├── urls.py            (Rutas del módulo)
├── routing.py         (WebSocket routing)
├── admin.py           (Admin para modelos)
├── templates/bingo_app/
│   ├── dice_lobby.html
│   └── dice_game_room.html
└── static/
    ├── js/
    │   ├── dice_websocket.js
    │   ├── dice_game.js
    │   └── dice_table_colors.js
    └── css/
        └── dice_table.css
```

---

**FIN DEL DOCUMENTO**

