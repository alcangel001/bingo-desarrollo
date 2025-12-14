from asyncio.log import logger
from django.utils import timezone  # ✅
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
from asgiref.sync import sync_to_async
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync  # Necesario para llamadas síncronas a Channels
from channels.layers import get_channel_layer  # Para enviar mensajes via WebSocket


REPUTATION_CHOICES = [
    ('AUTO', 'Automático'),
    ('BRONCE', 'Bronce'),
    ('PLATA', 'Plata'),
    ('ORO', 'Oro'),
    ('PLATINO', 'Platino'),
    ('LEYENDA', 'Leyenda'),
]

class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    credit_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Saldo de créditos del usuario. No puede ser negativo."
    )
    blocked_credits = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Créditos bloqueados por premios. No puede ser negativo."
    )
    
    manual_reputation = models.CharField(
        max_length=10,
        choices=REPUTATION_CHOICES,
        default='AUTO',
        help_text="Permite a un admin asignar un nivel de reputación manualmente."
    )

    theme_color = models.CharField(
        max_length=32,
        default='classic',
        blank=True,
        help_text="Preferencia de color del usuario para la interfaz."
    )

    win_effect = models.CharField(
        max_length=32,
        default='confetti',
        blank=True,
        help_text="Efecto visual mostrado cuando el usuario gana."
    )

    total_completed_events = models.PositiveIntegerField(default=0)

    @property
    def reputation_level(self):
        if self.manual_reputation != 'AUTO':
            return self.get_manual_reputation_display()

        completed_games = self.organized_games.filter(is_finished=True).count()
        completed_raffles = self.organized_raffles.filter(status='FINISHED').count()

        if completed_games >= 151 and completed_raffles >= 10:
            return "Platino"
        elif completed_games >= 61 and completed_raffles >= 4:
            return "Oro"
        elif completed_games >= 25:
            return "Plata"
        else:
            return "Bronce"


     # Nuevos campos para bloqueo
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='blocked_users'
    )
    
    @property
    def is_currently_blocked(self):
        if not self.is_blocked:
            return False
        if self.blocked_until and timezone.now() < self.blocked_until:
            return True
        if not self.blocked_until:  # Bloqueo permanente
            return True
        return False

    def unread_notifications(self, limit=5):
        return self.credit_notifications.filter(is_read=False).order_by('-created_at')[:limit]

    # Relación con franquicia (para usuarios que pertenecen a una franquicia)
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece este usuario (si aplica)"
    )

    def __str__(self):
        return self.username

class CreditRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_requests',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece esta solicitud"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proof = models.FileField(upload_to='credit_proofs/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    payment_method = models.ForeignKey(
        'BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_requests'
    )

    def __str__(self):
        return f"Solicitud de {self.user.username} - ${self.amount}"

class Game(models.Model):
    WINNING_PATTERNS = [
        ('HORIZONTAL', 'Línea horizontal'),
        ('VERTICAL', 'Línea vertical'),
        ('DIAGONAL', 'Línea diagonal (X)'),
        ('FULL', 'Tabla llena'),
        ('CORNERS', 'Cuatro esquinas'),
        ('CUSTOM', 'Patrón personalizado'),

    ]

    custom_pattern = models.JSONField(
        null=True, 
        blank=True,
        help_text="Matriz 5x5 que representa el patrón personalizado (1=casilla requerida, 0=no requerida)"
    )

    # Basic game info
    name = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_games')
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='games',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece este juego"
    )
    password = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Game configuration
    entry_price = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name="Precio de entrada"
    )
    winning_pattern = models.CharField(
        max_length=20, 
        choices=WINNING_PATTERNS, 
        default='FULL'
    )
    card_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.10'),
        validators=[MinValueValidator(Decimal('0.10'))],
        verbose_name="Precio por cartón"
    )
    
    max_cards_per_player = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    # Game state
    is_started = models.BooleanField(default=False, db_index=True)
    is_finished = models.BooleanField(default=False, db_index=True)
    winner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='won_games'
    )
    
    # Called numbers
    current_number = models.IntegerField(null=True, blank=True)
    called_numbers = models.JSONField(default=list)
    
    # Game prize
    base_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    progressive_prizes = models.JSONField(default=list)
    prize = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Premio Fijo"
    )
    
    # Escrow balance
    held_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo Bloqueado"
    )
    total_cards_sold = models.PositiveIntegerField(
        default=0,
        verbose_name="Cartones vendidos"
    )

    max_cards_sold = models.PositiveIntegerField(
        default=0,
        verbose_name="Máximo cartones vendidos"
    )
    
    # Auto-call settings
    auto_call_interval = models.PositiveIntegerField(
        default=5,
        help_text="Intervalo en segundos entre llamadas automáticas"
    )
    is_auto_calling = models.BooleanField(default=False)
    allows_printable_cards = models.BooleanField(default=False, verbose_name="Permitir cartones imprimibles")

    def __str__(self):
        return self.name

    
    @property
    def next_prize_target(self):
        if not self.progressive_prizes:
            return None
        
        sorted_prizes = sorted(self.progressive_prizes, key=lambda x: x['target'])
        
        for prize in sorted_prizes:
            if self.max_cards_sold < prize['target']:
                return prize['target']
        
        return None

    @property
    def progress_percentage(self):
        target = self.next_prize_target
        if not target or target == 0:
            return 100  # Si no hay un próximo objetivo, se asume el 100%
        
        # Asegurarse de que total_cards_sold no exceda el target para el cálculo
        cards_for_progress = min(self.total_cards_sold, target)
        
        return int((cards_for_progress / target) * 100)

    def call_number(self):
        available_numbers = [n for n in range(1, 76) if n not in self.called_numbers]
        if available_numbers:
            number = secrets.choice(available_numbers)
            self.current_number = number
            self.called_numbers.append(number)
            self.save()
            return number
        return None
    
    def start_game(self):
        if not self.is_started and not self.is_finished:
            self.is_started = True
            self.save()
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{self.id}',
                {
                    'type': 'game_started',
                    'is_started': True,
                    'is_auto_calling': self.is_auto_calling,
                    'total_cards_sold': self.total_cards_sold,
                    'max_cards_sold': self.max_cards_sold,
                }
            )
            return True
        return False

    def _distribute_revenue(self):
        logger.warning(f"[Game {self.id}] Iniciando _distribute_revenue.")
        percentage_settings = PercentageSettings.objects.first()
        if not percentage_settings:
            logger.error(f"[Game {self.id}] PercentageSettings no encontradas. No se puede distribuir la ganancia.")
            raise Exception("PercentageSettings no configuradas. No se puede distribuir la ganancia.")

        logger.warning(f"[Game {self.id}] Saldo retenido (held_balance): {self.held_balance}")
        if self.held_balance > 0:
            total_revenue = self.held_balance
            commission_percentage = percentage_settings.platform_commission
            commission_amount = total_revenue * (commission_percentage / 100)
            organizer_net_revenue = total_revenue - commission_amount

            logger.warning(f"[Game {self.id}] Ganancia neta del organizador: {organizer_net_revenue}")
            
            # IMPORTANTE: Refrescar el organizador desde la DB para obtener el balance actualizado
            # (puede haber recibido premio como ganador o desbloqueo de créditos)
            organizer = User.objects.select_for_update().get(id=self.organizer.id)
            logger.warning(f"[Game {self.id}] Saldo del organizador ANTES de revenue: {organizer.credit_balance}")
            organizer.credit_balance += organizer_net_revenue
            organizer.save()
            logger.warning(f"[Game {self.id}] Saldo del organizador DESPUÉS de revenue: {organizer.credit_balance}")
            
            # Actualizar la referencia del juego
            self.organizer.refresh_from_db()
            
            Transaction.objects.create(
                user=organizer,
                amount=organizer_net_revenue,
                transaction_type='ORGANIZER_REVENUE',
                description=f"Ingresos netos por juego finalizado: {self.name}",
                related_game=self
            )

            admin = User.objects.filter(is_admin=True).first()
            if admin:
                admin = User.objects.select_for_update().get(id=admin.id)
                admin.credit_balance += commission_amount
                admin.save()
                Transaction.objects.create(
                    user=admin,
                    amount=commission_amount,
                    transaction_type='PLATFORM_COMMISSION',
                    description=f"Comisión de plataforma por juego finalizado: {self.name}",
                    related_game=self
                )
            
            self.held_balance = Decimal('0.00')
            logger.warning(f"[Game {self.id}] Saldo retenido reseteado a 0.")
        
        # Actualizar eventos completados - refrescar organizador primero
        organizer = User.objects.get(id=self.organizer.id)
        organizer.total_completed_events += 1
        organizer.save()
        self.organizer.refresh_from_db()
        logger.warning(f"[Game {self.id}] Eventos completados del organizador: {self.organizer.total_completed_events}")

    def end_game(self):
        logger.warning(f"[Game {self.id}] Iniciando end_game.")
        
        # Verificar si ya está finalizado para evitar procesamiento duplicado
        if self.is_finished:
            logger.warning(f"[Game {self.id}] Juego ya finalizado, abortando end_game.")
            return False
            
        if not self.is_started:
            logger.warning(f"[Game {self.id}] Juego no iniciado, abortando end_game.")
            return False
            
        players = Player.objects.filter(game=self)
        winners = [player.user for player in players if player.check_bingo()]

        if not winners:
            logger.warning(f"[Game {self.id}] No se encontraron ganadores. Finalizando juego.")
            self.is_finished = True
            self.save()
            return False

        self.prize = self.calculate_prize()
        self.is_finished = True
        self.save()
        logger.warning(f"[Game {self.id}] Juego marcado como finalizado. Premio total: {self.prize}. Ganadores: {[w.username for w in winners]}")

        try:
            with transaction.atomic():
                logger.warning(f"[Game {self.id}] Iniciando transacción atómica para pagos.")
                num_winners = len(winners)
                player_prize_per_winner = self.prize / num_winners if num_winners > 0 else 0

                # Obtener IDs de ganadores para evitar problemas de referencia
                winner_ids = [w.id for w in winners]
                logger.warning(f"[Game {self.id}] Procesando {num_winners} ganadores. Premio por ganador: {player_prize_per_winner}")
                
                for winner_id in winner_ids:
                    # Obtener el ganador directamente desde la DB para cada iteración con select_for_update
                    winner = User.objects.select_for_update().get(id=winner_id)
                    logger.warning(f"[Game {self.id}] Pagando {player_prize_per_winner} al ganador {winner.username}. Saldo ANTES: {winner.credit_balance}")
                    winner.credit_balance += player_prize_per_winner
                    winner.save()
                    logger.warning(f"[Game {self.id}] Saldo DESPUÉS de {winner.username}: {winner.credit_balance}")
                    Transaction.objects.create(
                        user=winner,
                        amount=player_prize_per_winner,
                        transaction_type='PRIZE',
                        description=f"Premio por ganar {self.name}",
                        related_game=self
                    )
                    logger.warning(f"[Game {self.id}] Transacción de premio creada para {winner.username}")
                
                # Marcar todos los ganadores
                updated = Player.objects.filter(user__in=winners, game=self).update(is_winner=True)
                logger.warning(f"[Game {self.id}] {updated} jugadores marcados como ganadores")

                channel_layer = get_channel_layer()
                
                # Notificar a todo el grupo que el juego ha terminado con todos los ganadores
                winners_usernames = [w.username for w in winners]
                async_to_sync(channel_layer.group_send)(
                    f"game_{self.id}",
                    {
                        "type": "game_ended",
                        "winners": winners_usernames,  # Lista completa de ganadores
                        "winner": winners_usernames[0] if winners_usernames else None,  # Primer ganador para compatibilidad
                        "num_winners": num_winners,
                        "prize": float(self.prize),
                        "player_prize_per_winner": float(player_prize_per_winner),
                        "called_numbers": self.called_numbers,
                        "held_balance": float(self.held_balance),
                    },
                )
                
                # Notificar a cada ganador individualmente con su nuevo balance
                # Usar winner_ids para obtener cada ganador desde la DB
                for winner_id in winner_ids:
                    winner = User.objects.get(id=winner_id)
                    # Crear mensaje que indique si hubo múltiples ganadores
                    if num_winners > 1:
                        message = f"¡Felicidades! Has ganado junto con {num_winners - 1} otro(s) jugador(es).<br>Premio total: {self.prize:.2f} créditos<br>Premio dividido: {player_prize_per_winner:.2f} créditos cada uno"
                    else:
                        message = f"¡Ganaste {player_prize_per_winner:.2f} créditos en {self.name}!"
                    async_to_sync(channel_layer.group_send)(
                        f"user_{winner.id}", 
                        {
                            'type': 'win_notification', 
                            'message': message, 
                            'details': {
                                'player_prize': float(player_prize_per_winner), 
                                'total_winners': num_winners, 
                                'total_prize': float(self.prize),
                                'new_balance': float(winner.credit_balance)
                            }
                        }
                    )
                    # También enviar actualización de créditos
                    async_to_sync(channel_layer.group_send)(
                        f"user_{winner.id}",
                        {
                            'type': 'credit_update',
                            'new_balance': float(winner.credit_balance)
                        }
                    )

                logger.warning(f"[Game {self.id}] Desbloqueando {self.base_prize} de premio para el organizador {self.organizer.username}. Saldo bloqueado ANTES: {self.organizer.blocked_credits}")
                
                # IMPORTANTE: Refrescar el organizador desde la DB si también es ganador
                # para asegurar que tenemos el balance actualizado con el premio
                organizer_is_winner = self.organizer.id in winner_ids
                if organizer_is_winner:
                    logger.warning(f"[Game {self.id}] El organizador {self.organizer.username} también es ganador. Refrescando desde DB.")
                    self.organizer.refresh_from_db()
                    logger.warning(f"[Game {self.id}] Balance del organizador después de refrescar: {self.organizer.credit_balance}")
                
                # Validar que hay suficientes créditos bloqueados para desbloquear
                if self.organizer.blocked_credits >= self.base_prize:
                    self.organizer.blocked_credits -= self.base_prize
                    unlock_amount = self.base_prize
                    logger.warning(f"[Game {self.id}] Desbloqueo normal: {self.base_prize}")
                else:
                    # Ajustar a 0 si hay menos créditos bloqueados de los esperados
                    unlock_amount = self.organizer.blocked_credits
                    self.organizer.blocked_credits = Decimal('0.00')
                    logger.warning(f"[Game {self.id}] ADVERTENCIA: Intentando desbloquear {self.base_prize} pero solo hay {unlock_amount} bloqueados. Ajustando a 0.")
                
                # Usar select_for_update para asegurar que el balance se actualice correctamente
                organizer = User.objects.select_for_update().get(id=self.organizer.id)
                organizer.blocked_credits = self.organizer.blocked_credits
                organizer.save()
                self.organizer.refresh_from_db()
                logger.warning(f"[Game {self.id}] Saldo bloqueado DESPUÉS: {self.organizer.blocked_credits}")
                logger.warning(f"[Game {self.id}] Balance del organizador DESPUÉS de desbloqueo: {self.organizer.credit_balance}")
                
                if unlock_amount > 0:
                    Transaction.objects.create(
                        user=self.organizer, 
                        amount=unlock_amount, 
                        transaction_type='PRIZE_UNLOCK', 
                        description=f"Desbloqueo de créditos de premio del juego {self.name}", 
                        related_game=self
                    )

                self._distribute_revenue()
                
                self.save()
                logger.warning(f"[Game {self.id}] Transacción completada exitosamente.")
                return True
        except Exception as e:
            logger.error(f"[Game {self.id}] ERROR en transacción de end_game: {str(e)}", exc_info=True)
            return False
        return False
    
    def end_game_manual(self, winners):
        logger.warning(f"[Game {self.id}] Iniciando end_game_manual.")
        
        # Verificar nuevamente dentro de la transacción para evitar condiciones de carrera
        if self.is_finished:
            logger.warning(f"[Game {self.id}] Juego ya finalizado, abortando end_game_manual.")
            return False
            
        self.is_finished = True
        self.prize = self.calculate_prize()

        if not isinstance(winners, (list, tuple)):
            winners = [winners]

        self.save()
        logger.warning(f"[Game {self.id}] Juego (manual) marcado como finalizado. Premio: {self.prize}. Ganadores: {[w.username for w in winners]}")

        try:
            with transaction.atomic():
                logger.warning(f"[Game {self.id}] Iniciando transacción atómica para pagos (manual).")
                num_winners = len(winners)
                player_prize_per_winner = self.prize / num_winners if num_winners > 0 else 0

                # Obtener IDs de ganadores para evitar problemas de referencia
                winner_ids = [w.id for w in winners]
                logger.warning(f"[Game {self.id}] Procesando {num_winners} ganadores. Premio por ganador: {player_prize_per_winner}")
                
                for winner_id in winner_ids:
                    # Obtener el ganador directamente desde la DB para cada iteración con select_for_update
                    winner = User.objects.select_for_update().get(id=winner_id)
                    logger.warning(f"[Game {self.id}] Pagando {player_prize_per_winner} al ganador {winner.username}. Saldo ANTES: {winner.credit_balance}")
                    winner.credit_balance += player_prize_per_winner
                    winner.save()
                    logger.warning(f"[Game {self.id}] Saldo DESPUÉS de {winner.username}: {winner.credit_balance}")
                    Transaction.objects.create(
                        user=winner, 
                        amount=player_prize_per_winner, 
                        transaction_type='PRIZE', 
                        description=f"Premio por ganar {self.name}", 
                        related_game=self
                    )
                    logger.warning(f"[Game {self.id}] Transacción de premio creada para {winner.username}")
                
                # Marcar todos los ganadores
                updated = Player.objects.filter(user__in=winners, game=self).update(is_winner=True)
                logger.warning(f"[Game {self.id}] {updated} jugadores marcados como ganadores")

                logger.warning(f"[Game {self.id}] Desbloqueando {self.base_prize} de premio para el organizador {self.organizer.username}. Saldo bloqueado ANTES: {self.organizer.blocked_credits}")
                
                # IMPORTANTE: Refrescar el organizador desde la DB si también es ganador
                # para asegurar que tenemos el balance actualizado con el premio
                organizer_is_winner = self.organizer.id in winner_ids
                if organizer_is_winner:
                    logger.warning(f"[Game {self.id}] El organizador {self.organizer.username} también es ganador. Refrescando desde DB.")
                    self.organizer.refresh_from_db()
                    logger.warning(f"[Game {self.id}] Balance del organizador después de refrescar: {self.organizer.credit_balance}")
                
                # Validar que hay suficientes créditos bloqueados para desbloquear
                if self.organizer.blocked_credits >= self.base_prize:
                    self.organizer.blocked_credits -= self.base_prize
                    unlock_amount = self.base_prize
                    logger.warning(f"[Game {self.id}] Desbloqueo manual normal: {self.base_prize}")
                else:
                    # Ajustar a 0 si hay menos créditos bloqueados de los esperados
                    unlock_amount = self.organizer.blocked_credits
                    self.organizer.blocked_credits = Decimal('0.00')
                    logger.warning(f"[Game {self.id}] ADVERTENCIA MANUAL: Intentando desbloquear {self.base_prize} pero solo hay {unlock_amount} bloqueados. Ajustando a 0.")
                
                # Usar select_for_update para asegurar que el balance se actualice correctamente
                organizer = User.objects.select_for_update().get(id=self.organizer.id)
                organizer.blocked_credits = self.organizer.blocked_credits
                organizer.save()
                self.organizer.refresh_from_db()
                logger.warning(f"[Game {self.id}] Saldo bloqueado DESPUÉS: {self.organizer.blocked_credits}")
                logger.warning(f"[Game {self.id}] Balance del organizador DESPUÉS de desbloqueo: {self.organizer.credit_balance}")
                
                if unlock_amount > 0:
                    Transaction.objects.create(
                        user=self.organizer, 
                        amount=unlock_amount, 
                        transaction_type='PRIZE_UNLOCK', 
                        description=f"Desbloqueo de créditos de premio del juego {self.name}", 
                        related_game=self
                    )

                self._distribute_revenue()

                channel_layer = get_channel_layer()

                # Notificar a todo el grupo que el juego ha terminado con todos los ganadores
                winners_usernames = [w.username for w in winners]
                async_to_sync(channel_layer.group_send)(
                    f"game_{self.id}",
                    {
                        "type": "game_ended",
                        "winners": winners_usernames,  # Lista completa de ganadores
                        "winner": winners_usernames[0] if winners_usernames else None,  # Primer ganador para compatibilidad
                        "num_winners": num_winners,
                        "prize": float(self.prize),
                        "player_prize_per_winner": float(player_prize_per_winner),
                        "called_numbers": self.called_numbers,
                        "held_balance": float(self.held_balance),
                    },
                )

                # Notificar a los ganadores individualmente
                # Usar winner_ids para obtener cada ganador desde la DB
                for winner_id in winner_ids:
                    winner = User.objects.get(id=winner_id)
                    # Crear mensaje que indique si hubo múltiples ganadores
                    if num_winners > 1:
                        message = f"¡Felicidades! Has ganado junto con {num_winners - 1} otro(s) jugador(es).<br>Premio total: {self.prize:.2f} créditos<br>Premio dividido: {player_prize_per_winner:.2f} créditos cada uno"
                    else:
                        message = f"¡Ganaste {player_prize_per_winner:.2f} créditos en {self.name}!"
                    async_to_sync(channel_layer.group_send)(
                        f"user_{winner.id}",
                        {
                            "type": "win_notification",
                            "message": message,
                            "details": {
                                "player_prize": float(player_prize_per_winner),
                                "total_winners": num_winners,
                                "total_prize": float(self.prize),
                                "new_balance": float(winner.credit_balance)
                            },
                        },
                    )
                
                # Notificar al organizador sobre su nuevo saldo
                self.organizer.refresh_from_db()
                async_to_sync(channel_layer.group_send)(
                    f"user_{self.organizer.id}",
                    {
                        "type": "credit_update",
                        "new_balance": float(self.organizer.credit_balance),
                    },
                )

                self.save()
                logger.warning(f"[Game {self.id}] Transacción (manual) completada exitosamente.")
                return True
        except Exception as e:
            logger.error(f"[Game {self.id}] ERROR en transacción de end_game_manual: {str(e)}", exc_info=True)
            return False
        return False

    def start_auto_calling(self):
        if self.is_started and not self.is_finished and not self.is_auto_calling:
            self.is_auto_calling = True
            self.save()
            return True
        return False

    def stop_auto_calling(self):
        if self.is_auto_calling:
            self.is_auto_calling = False
            self.save()
            return True
        return False
    
    def calculate_prize(self):
        total_prize = self.base_prize
        
        if self.progressive_prizes:
            for prize in sorted(self.progressive_prizes, key=lambda x: x['target']):
                if self.max_cards_sold >= prize['target']:
                    total_prize += Decimal(str(prize['prize']))
        
        return total_prize
    
    @property
    def current_prize(self):
        """Retorna el premio actual calculado (base + progresivos aplicables)"""
        return self.calculate_prize()
    
    def check_progressive_prize(self):
        old_prize = self.prize
        self.prize = self.calculate_prize()
        self.save()
        
        prize_increase = self.prize - old_prize
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{self.id}',
            {
                'type': 'prize_updated',
                'new_prize': float(self.prize),
                'increase_amount': float(prize_increase) if prize_increase > 0 else 0,
                'total_cards': self.max_cards_sold,
                'next_target': self.next_prize_target
            }
        )
        
        return prize_increase
            

    
    def save(self, *args, **kwargs):
        """Sobrescribe save para actualizar automáticamente el prize y max_cards_sold"""
        # Actualizar max_cards_sold si es necesario
        if self.total_cards_sold > self.max_cards_sold:
            self.max_cards_sold = self.total_cards_sold
        
        # Asegurar que prize nunca sea menor que base_prize
        self.prize = self.calculate_prize()
        if self.prize < self.base_prize:
            self.prize = self.base_prize
        
        super().save(*args, **kwargs)

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    cards = models.JSONField(default=list)
    is_winner = models.BooleanField(default=False)
    is_manual_marking = models.BooleanField(default=False, help_text="Si True, el jugador marca números manualmente; si False, se marcan automáticamente")
    marked_numbers = models.JSONField(default=list, help_text="Números marcados manualmente por el jugador")

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"

    class Meta:
        unique_together = ('user', 'game')

    def generate_card(self):
        card = []
        for _ in range(5):
            row = sorted(secrets.sample(range(1, 91), 5))
            card.append(row)
        return card

    def check_bingo(self):
        called_numbers_set = set(self.game.called_numbers)
        manual_marked_set = set(self.marked_numbers or [])
        
        for card in self.cards:
            # Función auxiliar para verificar si un número está marcado
            def is_marked(num):
                if num == 0:  # Comodín siempre está marcado
                    return True
                # En modo automático, usa los números llamados
                if not self.is_manual_marking:
                    return num in called_numbers_set
                # En modo manual, usa los números marcados manualmente
                else:
                    return num in manual_marked_set
            
            if self.game.winning_pattern == 'HORIZONTAL':
                for row in card:
                    if all(is_marked(num) for num in row):
                        return True
            elif self.game.winning_pattern == 'VERTICAL':
                for col in range(5):
                    if all(is_marked(row[col]) for row in card):
                        return True
            elif self.game.winning_pattern == 'DIAGONAL':
                if all(is_marked(card[i][i]) for i in range(5)) or \
                all(is_marked(card[i][4-i]) for i in range(5)):
                    return True
            elif self.game.winning_pattern == 'FULL':
                if all(is_marked(num) for row in card for num in row):
                    return True
            elif self.game.winning_pattern == 'CORNERS':
                corners = [card[0][0], card[0][4], card[4][0], card[4][4]]
                print(f"DEBUG CORNERS: Checking corners {corners}")
                print(f"DEBUG CORNERS: Manual marking: {self.is_manual_marking}")
                print(f"DEBUG CORNERS: Called numbers: {called_numbers_set}")
                print(f"DEBUG CORNERS: Manual marked: {manual_marked_set}")
                
                corner_status = []
                for corner in corners:
                    is_marked_corner = is_marked(corner)
                    corner_status.append(f"{corner}:{is_marked_corner}")
                    print(f"DEBUG CORNERS: Corner {corner} marked: {is_marked_corner}")
                
                print(f"DEBUG CORNERS: Corner status: {corner_status}")
                
                if all(is_marked(corner) for corner in corners):
                    print("DEBUG CORNERS: BINGO! All corners marked!")
                    return True
            elif self.game.winning_pattern == 'CUSTOM' and self.game.custom_pattern:
                # Verificar patrón personalizado
                pattern = self.game.custom_pattern
                for i in range(5):
                    for j in range(5):
                        if pattern[i][j] == 1 and not is_marked(card[i][j]):
                            break
                    else:
                        continue
                    break
                else:
                    return True
        return False

    def acheck_bingo(self):
        return sync_to_async(self.check_bingo)()

class ChatMessage(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}..."

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('ENTRY_FEE', 'Entrada a juego'),
        ('PURCHASE', 'Compra de cartones'),
        ('ADMIN_ADD', 'Recarga administrativa'),
        ('PRIZE', 'Premio de juego'),
        ('GAME_CREATION_FEE', 'Tarifa de creación de juego'),
        ('RAFFLE_CREATION_FEE', 'Tarifa de creación de rifa'),
        ('PRIZE_LOCK', 'Bloqueo de premio'),
        ('PRIZE_UNLOCK', 'Desbloqueo de premio'),
        ('ORGANIZER_REVENUE', 'Ingresos del organizador'),
        ('PLATFORM_COMMISSION', 'Comisión de la plataforma'),
        ('WITHDRAWAL', 'Retiro de créditos'),
        ('WITHDRAWAL_REFUND', 'Reembolso de retiro'),
        ('OTHER', 'Otra transacción')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='PURCHASE')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - ${self.amount}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"De {self.sender.username} a {self.recipient.username}"

class Raffle(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Esperando jugadores'),
        ('IN_PROGRESS', 'En progreso'),
        ('FINISHED', 'Terminada'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_raffles')
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raffles',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece esta rifa"
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    prize = models.DecimalField(max_digits=10, decimal_places=2,editable=True,verbose_name="Premio base a distribuir")
    final_prize = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Premio final entregado"
    )
    tickets_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Total recaudado por tickets"
    )
    held_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Saldo Bloqueado"
    )
    start_number = models.PositiveIntegerField(default=1)
    end_number = models.PositiveIntegerField()
    number_format_digits = models.PositiveIntegerField(
        default=0,
        verbose_name="Dígitos para formato de números",
        help_text="Número de dígitos para mostrar los números (ej: 3 para 000, 001, 002...). 0 = sin formato"
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Número de WhatsApp",
        help_text="Número de WhatsApp para contacto (ej: 1234567890 o link de grupo). Se mostrará un botón con el logo de WhatsApp"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    draw_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    winning_number = models.PositiveIntegerField(null=True, blank=True)

    manual_winning_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número ganador manual"
    )
    is_manual_winner = models.BooleanField(default=False, null=True, blank=True)
    
    # Multiple winners support
    multiple_winners_enabled = models.BooleanField(
        default=False,
        verbose_name="Habilitar múltiples ganadores",
        help_text="Si está activado, se seleccionarán múltiples ganadores con premios escalonados"
    )
    manual_winning_numbers = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Números ganadores manuales",
        help_text="Lista de números ganadores ingresados manualmente (para múltiples ganadores). Ejemplo: [45, 78, 12]"
    )
    prize_structure = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Estructura de premios",
        help_text="Lista de premios escalonados. Ejemplo: [{'position': 1, 'prize': 1000}, {'position': 2, 'prize': 500}]"
    )
    winners = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Ganadores",
        help_text="Lista de ganadores con posición y premio asignado"
    )
    winning_numbers = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Números ganadores",
        help_text="Lista de números ganadores en orden de posición"
    )

    def format_ticket_number(self, number):
        """Formatea un número de ticket según number_format_digits"""
        if self.number_format_digits > 0:
            return str(number).zfill(self.number_format_digits)
        return str(number)
    
    def __str__(self):
        return self.title
    
    @property
    def total_tickets(self):
        return self.end_number - self.start_number + 1
    
    @property
    def available_tickets(self):
        return self.total_tickets - self.tickets.count()
    
    @property
    def progress_percentage(self):
        return (self.tickets.count() / self.total_tickets) * 100
    
    @property
    def total_tickets(self):
        return self.end_number - self.start_number + 1
    
    @property
    def available_tickets(self):
        return self.total_tickets - self.tickets.count()
    
    @property
    def progress_percentage(self):
        return (self.tickets.count() / self.total_tickets) * 100
    
    def can_be_drawn(self):
        """Determina si la rifa puede ser sorteada"""
        return self.status in ['WAITING', 'IN_PROGRESS'] and self.tickets.exists()
    
    def draw_winner(self):
        """Realiza el sorteo, entrega el premio y devuelve el ticket ganador"""
        if not self.can_be_drawn():
            return None

        percentage_settings = PercentageSettings.objects.first()
        if not percentage_settings:
            return None

        try:
            with transaction.atomic():
                # Broadcast de anuncio e inicio para todos los espectadores de la rifa
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"raffle_{self.id}",
                    {
                        'type': 'raffle_draw_announcement',
                        'message': f"¡El sorteo de {self.title} está por comenzar!"
                    }
                )
                async_to_sync(channel_layer.group_send)(
                    f"raffle_{self.id}",
                    {
                        'type': 'raffle_draw_start',
                        'duration_ms': 5000,
                        'countdown_seconds': 3
                    }
                )
                # Check if multiple winners are enabled
                if self.multiple_winners_enabled and self.prize_structure:
                    # Multiple winners logic - MUST use manual winning numbers
                    if not self.manual_winning_numbers:
                        logger.error(f"[Raffle {self.id}] Múltiples ganadores habilitados pero no hay números ganadores manuales definidos.")
                        return None
                    
                    winners_list = []
                    winning_numbers_list = []
                    total_prizes_distributed = Decimal('0.00')
                    
                    # Sort prize structure by position
                    sorted_prizes = sorted(self.prize_structure, key=lambda x: x.get('position', 0))
                    
                    # Validate that we have enough manual winning numbers
                    if len(self.manual_winning_numbers) < len(sorted_prizes):
                        logger.error(f"[Raffle {self.id}] No hay suficientes números ganadores manuales. Se requieren {len(sorted_prizes)} pero solo hay {len(self.manual_winning_numbers)}.")
                        return None
                    
                    # Select winners using manual winning numbers
                    selected_user_ids = set()
                    
                    for idx, prize_info in enumerate(sorted_prizes):
                        position = prize_info.get('position', 0)
                        prize_amount = Decimal(str(prize_info.get('prize', 0)))
                        manual_number = self.manual_winning_numbers[idx]
                        
                        # Find ticket with this number
                        try:
                            winning_ticket = self.tickets.get(number=manual_number)
                        except Ticket.DoesNotExist:
                            logger.warning(f"[Raffle {self.id}] El ticket #{manual_number} no ha sido vendido. Saltando este premio.")
                            continue  # Skip this prize if ticket not sold
                        
                        winner = winning_ticket.owner
                        
                        # If user already won, skip this prize (one user can only win once)
                        if winner.id in selected_user_ids:
                            logger.warning(f"[Raffle {self.id}] El usuario {winner.username} ya ganó con otro ticket. Saltando premio {position}° lugar.")
                            continue
                        
                        # Mark user as selected
                        selected_user_ids.add(winner.id)
                        
                        # Credit prize to the winner
                        winner.credit_balance += prize_amount
                        winner.save()
                        Transaction.objects.create(
                            user=winner,
                            amount=prize_amount,
                            transaction_type='PRIZE',
                            description=f"Premio {position}° lugar de la rifa: {self.title}"
                        )
                        
                        # Store winner info
                        winners_list.append({
                            'user_id': winner.id,
                            'username': winner.username,
                            'position': position,
                            'prize': float(prize_amount),
                            'ticket_number': winning_ticket.number,
                            'ticket_id': winning_ticket.id
                        })
                        winning_numbers_list.append(winning_ticket.number)
                        total_prizes_distributed += prize_amount
                    
                    # Unlock organizer's credits for total prizes distributed
                    # IMPORTANT: Refresh organizer from DB to get latest credit_balance if they won a prize
                    self.organizer.refresh_from_db()
                    logger.warning(f"[Raffle {self.id}] Desbloqueando {total_prizes_distributed} de premios para el organizador {self.organizer.username}. Saldo bloqueado ANTES: {self.organizer.blocked_credits}, Saldo créditos ANTES: {self.organizer.credit_balance}")
                    
                    if self.organizer.blocked_credits >= total_prizes_distributed:
                        self.organizer.blocked_credits -= total_prizes_distributed
                        unlock_amount = total_prizes_distributed
                        logger.warning(f"[Raffle {self.id}] Desbloqueo normal: {total_prizes_distributed}")
                    else:
                        unlock_amount = self.organizer.blocked_credits
                        self.organizer.blocked_credits = Decimal('0.00')
                        logger.warning(f"[Raffle {self.id}] ADVERTENCIA: Intentando desbloquear {total_prizes_distributed} pero solo hay {unlock_amount} bloqueados. Ajustando a 0.")
                    
                    self.organizer.save()
                    logger.warning(f"[Raffle {self.id}] Saldo bloqueado DESPUÉS: {self.organizer.blocked_credits}, Saldo créditos DESPUÉS: {self.organizer.credit_balance}")
                    
                    if unlock_amount > 0:
                        Transaction.objects.create(
                            user=self.organizer,
                            amount=unlock_amount,
                            transaction_type='PRIZE_UNLOCK',
                            description=f"Desbloqueo de créditos de premios de la rifa {self.title}"
                        )
                    
                    # Store winners and winning numbers
                    self.winners = winners_list
                    self.winning_numbers = winning_numbers_list
                    self.final_prize = total_prizes_distributed
                    
                    # Set first winner for backward compatibility
                    if winners_list:
                        first_winner = User.objects.get(id=winners_list[0]['user_id'])
                        self.winner = first_winner
                        self.winning_number = winning_numbers_list[0]
                    
                else:
                    # Single winner logic (original)
                    if self.manual_winning_number is not None:
                        try:
                            winning_ticket = self.tickets.get(number=self.manual_winning_number)
                        except Ticket.DoesNotExist:
                            return None  # Manual ticket not sold
                    else:
                        winning_ticket = secrets.choice(self.tickets.all())

                    winner = winning_ticket.owner
                    player_prize = self.prize

                    # 1. Credit prize to the winner
                    winner.credit_balance += player_prize
                    winner.save()
                    Transaction.objects.create(
                        user=winner,
                        amount=player_prize,
                        transaction_type='PRIZE',
                        description=f"Premio de la rifa: {self.title}"
                    )

                    # Unlock the organizer's credits for the prize (initial lock)
                    logger.warning(f"[Raffle {self.id}] Desbloqueando {self.prize} de premio para el organizador {self.organizer.username}. Saldo bloqueado ANTES: {self.organizer.blocked_credits}")
                    
                    # Validar que hay suficientes créditos bloqueados para desbloquear
                    if self.organizer.blocked_credits >= self.prize:
                        self.organizer.blocked_credits -= self.prize
                        unlock_amount = self.prize
                        logger.warning(f"[Raffle {self.id}] Desbloqueo normal: {self.prize}")
                    else:
                        # Ajustar a 0 si hay menos créditos bloqueados de los esperados
                        unlock_amount = self.organizer.blocked_credits
                        self.organizer.blocked_credits = Decimal('0.00')
                        logger.warning(f"[Raffle {self.id}] ADVERTENCIA: Intentando desbloquear {self.prize} pero solo hay {unlock_amount} bloqueados. Ajustando a 0.")
                    
                    self.organizer.save()
                    logger.warning(f"[Raffle {self.id}] Saldo bloqueado DESPUÉS: {self.organizer.blocked_credits}")
                    
                    if unlock_amount > 0:
                        Transaction.objects.create(
                            user=self.organizer,
                            amount=unlock_amount,
                            transaction_type='PRIZE_UNLOCK',
                            description=f"Desbloqueo de créditos de premio de la rifa {self.title}"
                        )
                    
                    self.final_prize = player_prize
                    self.winner = winner
                    self.winning_number = winning_ticket.number

                # --- NEW LOGIC FOR HELD BALANCE DISTRIBUTION ---
                total_revenue = self.held_balance
                percentage_settings = PercentageSettings.objects.first()
                if not percentage_settings:
                    # Handle case where settings are not configured
                    # This should ideally not happen as it's checked at the beginning of the method
                    commission_percentage = Decimal('0.00')
                else:
                    commission_percentage = percentage_settings.platform_commission

                commission_amount = total_revenue * (commission_percentage / 100)
                organizer_net_revenue = total_revenue - commission_amount

                # Credit organizer - Refresh from DB first to ensure we have latest balance (in case they won a prize)
                self.organizer.refresh_from_db()
                self.organizer.credit_balance += organizer_net_revenue
                self.organizer.save()
                Transaction.objects.create(
                    user=self.organizer,
                    amount=organizer_net_revenue,
                    transaction_type='ORGANIZER_REVENUE',
                    description=f"Ingresos netos por rifa finalizada: {self.title}"
                )
                # Increment total completed events for the organizer
                self.organizer.total_completed_events += 1
                self.organizer.save()

                # Credit admin
                admin = User.objects.filter(is_admin=True).first()
                if admin:
                    admin.credit_balance += commission_amount
                    admin.save()
                    Transaction.objects.create(
                        user=admin,
                        amount=commission_amount,
                        transaction_type='PLATFORM_COMMISSION',
                        description=f"Comisión de plataforma por rifa finalizada: {self.title}"
                    )
                
                # Reset held_balance after distribution
                self.held_balance = Decimal('0.00')
                self.save() # Save the raffle to update held_balance

                # --- END NEW LOGIC ---

                # 3. Update raffle status
                self.status = 'FINISHED'
                self.tickets_income = total_revenue
                self.save()

                # Notify winners
                if self.multiple_winners_enabled and self.winners:
                    # Multiple winners notification
                    async_to_sync(channel_layer.group_send)(
                        f"raffle_{self.id}",
                        {
                            'type': 'raffle_multiple_winners',
                            'winners': self.winners,
                            'winning_numbers': self.winning_numbers
                        }
                    )
                    
                    # Notify each winner individually
                    for winner_info in self.winners:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{winner_info['user_id']}",
                            {
                                'type': 'win_notification',
                                'message': f"¡Felicidades! Ganaste {winner_info['position']}° lugar en la rifa '{self.title}'",
                                'prize': winner_info['prize']
                            }
                        )
                    
                    # Announcement in raffle lobby
                    async_to_sync(channel_layer.group_send)(
                        'raffle_lobby',
                        {
                            'type': 'raffle_multiple_winners_announcement',
                            'raffle_title': self.title,
                            'winners': self.winners,
                            'winning_numbers': self.winning_numbers
                        }
                    )
                    
                    # Return first winning ticket for backward compatibility
                    if self.winners:
                        first_winner_id = self.winners[0]['ticket_id']
                        return Ticket.objects.get(id=first_winner_id)
                    return None
                else:
                    # Single winner notification (original)
                    async_to_sync(channel_layer.group_send)(
                        f"raffle_{self.id}",
                        {
                            'type': 'raffle_winner',
                            'winning_number': self.winning_number,
                            'winner_username': self.winner.username if self.winner else 'N/A',
                            'prize': float(self.final_prize) if self.final_prize else 0
                        }
                    )

                    # Notificar a todos los compradores por su canal personal
                    buyer_ids = list(self.tickets.values_list('owner_id', flat=True).distinct())
                    for uid in buyer_ids:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{uid}",
                            {
                                'type': 'win_notification',
                                'message': f"Resultado rifa '{self.title}': ganó {self.winner.username if self.winner else 'N/A'} con el número {self.winning_number} (premio {float(self.final_prize):.2f})."
                            }
                        )

                    # Anuncio en lobby de rifas
                    async_to_sync(channel_layer.group_send)(
                        'raffle_lobby',
                        {
                            'type': 'raffle_winner_announcement',
                            'raffle_title': self.title,
                            'winning_number': self.winning_number,
                            'winner_username': self.winner.username if self.winner else 'N/A',
                            'prize': float(self.final_prize) if self.final_prize else 0
                        }
                    )

                    # Notificación privada adicional al ganador
                    if self.winner:
                        async_to_sync(channel_layer.group_send)(
                            f"user_{self.winner.id}",
                            {
                                'type': 'win_notification',
                                'message': f"¡Felicidades! Ganaste la rifa '{self.title}'",
                                'prize': float(self.final_prize) if self.final_prize else 0
                            }
                        )

                    # Return winning ticket
                    if self.winning_number:
                        try:
                            return self.tickets.get(number=self.winning_number)
                        except Ticket.DoesNotExist:
                            return None
                    return None

        except Exception as e:
            logger.error(f"Error al sortear la rifa {self.id}: {str(e)}", exc_info=True)
            return None

class Ticket(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='tickets')
    number = models.PositiveIntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('raffle', 'number')
    
    def __str__(self):
        return f"Ticket #{self.number} - {self.raffle.title}"

class PercentageSettings(models.Model):
    platform_commission = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Comisión que la plataforma cobra al organizador sobre los ingresos totales (venta de cartones/tickets)."
    )
    image_promotion_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10.00, 
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Promoción con Imagen",
        help_text="Costo en créditos para promocionar un evento con una imagen."
    )
    video_promotion_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=15.00, 
        validators=[MinValueValidator(0)],
        verbose_name="Precio de Promoción con Video",
        help_text="Costo en créditos para promocionar un evento con un video."
    )
    
    # Configuración de tarifas con toggles
    game_creation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.00, 
        validators=[MinValueValidator(0)],
        verbose_name="Tarifa de Creación de Juego",
        help_text="Costo fijo en créditos para crear un nuevo juego."
    )
    
    game_creation_fee_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Tarifa de Creación",
        help_text="Activar o desactivar la tarifa de creación de juegos."
    )
    
    platform_commission_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Comisión por Cartón",
        help_text="Activar o desactivar la comisión sobre ventas de cartones."
    )
    
    # Control de sistemas de usuario
    credits_purchase_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Compra de Créditos",
        help_text="Permitir a los usuarios solicitar compra de créditos. Si se desactiva, los usuarios no verán esta opción."
    )
    
    credits_withdrawal_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Retiro de Créditos",
        help_text="Permitir a los usuarios solicitar retiros. Si se desactiva, los usuarios no verán esta opción."
    )
    
    referral_system_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Sistema de Referidos",
        help_text="Activar o desactivar el sistema de referidos. Si se desactiva, no se mostrarán códigos de referido."
    )
    
    promotions_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Promociones y Bonos",
        help_text="Activar o desactivar el sistema de promociones (bonos de bienvenida, promociones especiales, etc.). Si se desactiva, los usuarios no verán las promociones."
    )
    
    accounts_receivable_enabled = models.BooleanField(
        default=True,
        verbose_name="Activar Cuentas por Cobrar para Organizadores",
        help_text="Activar o desactivar el módulo de cuentas por cobrar para organizadores. Si se desactiva, los organizadores no verán esta opción."
    )
    
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"

    def __str__(self):
        return f"Configuración del Sistema (Comisión: {self.platform_commission}%)"
    

# models.py (opcional, solo si quieres guardar historial)
class FlashMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."
    
class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
        ('COMPLETED', 'Completado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='withdrawal_requests',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece esta solicitud"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    proof_screenshot = models.ImageField(upload_to='withdrawal_proofs/', null=True, blank=True) # New field
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Solicitud de Retiro'
        verbose_name_plural = 'Solicitudes de Retiro'
    
    def __str__(self):
        return f"Retiro de {self.user.username} - ${self.amount} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Si el estado cambia, actualizar la fecha de procesamiento
        super().save(*args, **kwargs)


class BankAccount(models.Model):
    """
    Modelo completamente personalizable para cuentas bancarias/métodos de pago
    """
    title = models.CharField(
        max_length=100, 
        verbose_name="Título/Nombre",
        help_text="Ej: Banco de Venezuela, Zelle, PayPal, Binance, etc."
    )
    franchise = models.ForeignKey(
        'Franchise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_accounts',
        verbose_name="Franquicia",
        help_text="Franquicia a la que pertenece esta cuenta bancaria"
    )
    details = models.TextField(
        verbose_name="Detalles completos",
        help_text="Información completa que verán los usuarios. Ej: Número de cuenta, titular, cédula, teléfono, email, etc."
    )
    instructions = models.TextField(
        blank=True,
        verbose_name="Instrucciones especiales",
        help_text="Instrucciones específicas para este método (opcional)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Mostrar este método a los usuarios"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización (mayor número = más arriba)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['-order', 'title']

    def __str__(self):
        return f"{self.title} ({'Activo' if self.is_active else 'Inactivo'})"
    

class CreditRequestNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_notifications')
    credit_request = models.ForeignKey(CreditRequest, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class UserBlockHistory(models.Model):
    BLOCK_TYPES = [
        ('CHAT', 'Bloqueo de chat'),
        ('FULL', 'Bloqueo completo'),
        ('GAMES', 'Bloqueo de juegos'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_history')
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_issued')
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    reason = models.TextField()
    blocked_at = models.DateTimeField(auto_now_add=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "User Block Histories"
        ordering = ['-blocked_at']
    
    def __str__(self):
        return f"{self.user.username} bloqueado por {self.blocked_by.username}"


class WithdrawalRequestNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_notifications')
    withdrawal_request = models.ForeignKey(WithdrawalRequest, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']



class PrintableCard(models.Model):
    unique_id = models.CharField(max_length=20, unique=True, db_index=True)
    card_data = models.JSONField()
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='printable_cards')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.unique_id


class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('GENERAL', 'General'),
        ('PROMOTION', 'Promoción de Evento'),
        ('EXTERNAL', 'Anuncio Externo'),
    ]

    # Campos existentes
    message = models.CharField(max_length=255, help_text="El texto principal del anuncio.")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Marcar para mostrar este anuncio.")
    order = models.PositiveIntegerField(default=0, help_text="Orden de aparición (número más bajo primero).")
    created_at = models.DateTimeField(auto_now_add=True)

    # Nuevos campos
    announcement_type = models.CharField(
        max_length=10,
        choices=ANNOUNCEMENT_TYPES,
        default='GENERAL',
        verbose_name="Tipo de Anuncio"
    )
    
    # Para anuncios externos y promociones con imagen
    image = models.ImageField(
        upload_to='announcements/',
        blank=True, null=True,
        verbose_name="Imagen del Anuncio",
        help_text="Opcional. Sube una imagen para el anuncio."
    )
    video_url = models.URLField(
        blank=True, null=True,
        verbose_name="URL de Video (Embed)",
        help_text="Opcional. URL de un video para embeber (ej. YouTube, Vimeo)."
    )
    external_link = models.URLField(
        blank=True, null=True,
        verbose_name="Enlace Externo",
        help_text="URL a la que se dirigirá el usuario al hacer clic."
    )

    # Para promociones de eventos internos
    related_game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Juego Relacionado",
        help_text="Si es una promoción, selecciona el juego."
    )
    related_raffle = models.ForeignKey(
        'Raffle',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name="Rifa Relacionada",
        help_text="Si es una promoción, selecciona la rifa."
    )
    
    # Gestión de promociones pagadas
    promoted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='promoted_announcements',
        verbose_name="Promocionado por"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fecha de Expiración",
        help_text="El anuncio se ocultará automáticamente después de esta fecha."
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.announcement_type == 'PROMOTION' and not self.related_game and not self.related_raffle:
            raise ValidationError('Las promociones deben estar vinculadas a un Juego o a una Rifa.')
        if self.announcement_type == 'EXTERNAL' and not self.external_link:
            raise ValidationError('Los anuncios externos deben tener un enlace externo.')

    def save(self, *args, **kwargs):
        # Si el anuncio es de tipo 'PROMOTION', el mensaje se puede autogenerar
        if self.announcement_type == 'PROMOTION' and not self.message:
            if self.related_game:
                self.message = f"¡No te pierdas el bingo '{self.related_game.name}'!"
            elif self.related_raffle:
                self.message = f"¡Participa en la rifa '{self.related_raffle.title}'!"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Anuncio y Promoción"
        verbose_name_plural = "Anuncios y Promociones"

    def __str__(self):
        return f"[{self.get_announcement_type_display()}] {self.message}"


class VideoCallGroup(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='video_call_groups', null=True, blank=True)
    raffle = models.ForeignKey('Raffle', on_delete=models.CASCADE, related_name='video_call_groups', null=True, blank=True)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name='created_video_call_groups', on_delete=models.CASCADE, null=True)
    participants = models.ManyToManyField(User, related_name='participated_video_call_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    agora_channel_name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)  # Para salas privadas
    is_public = models.BooleanField(default=True)
    # Nuevos campos para persistencia entre juegos
    is_persistent = models.BooleanField(default=True, help_text="Si es True, la sala se mantiene activa entre juegos")
    active_users = models.ManyToManyField(User, related_name='active_video_calls', blank=True)

    def __str__(self):
        return f"Video call group '{self.name}' created by {self.created_by.username}"

    @property
    def is_private(self):
        return bool(self.password)
        
    def update_game_context(self, new_game):
        """Actualiza el juego asociado a la videollamada sin desconectar a los usuarios"""
        self.game = new_game
        self.save(update_fields=['game'])
        return True


# Modelos para promociones de lanzamiento
class LaunchPromotion(models.Model):
    """Promociones especiales de lanzamiento"""
    
    PROMOTION_TYPES = [
        ('WELCOME_BONUS', 'Bono de Bienvenida'),
        ('FIRST_DEPOSIT', 'Bono Primer Depósito'),
        ('REFERRAL_BONUS', 'Bono por Referido'),
        ('DAILY_BONUS', 'Bono Diario'),
        ('LAUNCH_SPECIAL', 'Promoción de Lanzamiento'),
    ]
    
    name = models.CharField(max_length=100)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    description = models.TextField()
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True, help_text="Máximo número de usos (null = ilimitado)")
    current_uses = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_promotion_type_display()}"
    
    def is_available(self):
        """Verifica si la promoción está disponible"""
        now = timezone.now()
        
        if not self.is_active:
            return False
            
        if self.start_date > now:
            return False
            
        if self.end_date and self.end_date < now:
            return False
            
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
            
        return True
    
    def can_user_claim(self, user):
        """Verifica si un usuario puede reclamar esta promoción"""
        if not self.is_available():
            return False
            
        # Verificar si el usuario ya reclamó esta promoción
        if UserPromotion.objects.filter(user=user, promotion=self).exists():
            return False
            
        return True

class UserPromotion(models.Model):
    """Promociones reclamadas por usuarios"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claimed_promotions')
    promotion = models.ForeignKey(LaunchPromotion, on_delete=models.CASCADE)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claimed_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.promotion.name}"

class ReferralProgram(models.Model):
    """Sistema de referidos"""
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by')
    referral_code = models.CharField(max_length=20, unique=True)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} -> {self.referred_user.username}"

class LaunchAchievement(models.Model):
    """Logros especiales de lanzamiento"""
    
    ACHIEVEMENT_TYPES = [
        ('PIONEER', 'Pionero - Primeros 100 usuarios'),
        ('FOUNDER', 'Fundador - Usuario del primer día'),
        ('CHAMPION', 'Campeón Inaugural - Ganador del primer torneo'),
        ('EARLY_BIRD', 'Madrugador - Primeros 10 usuarios'),
        ('SOCIAL_BUTTERFLY', 'Mariposa Social - Invitó 5 amigos'),
    ]
    
    name = models.CharField(max_length=100)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    bonus_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    max_recipients = models.IntegerField(null=True, blank=True)
    current_recipients = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def can_award(self):
        """Verifica si se puede otorgar este logro"""
        if not self.is_active:
            return False
            
        if self.max_recipients and self.current_recipients >= self.max_recipients:
            return False
            
        return True

class UserAchievement(models.Model):
    """Logros otorgados a usuarios"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(LaunchAchievement, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    bonus_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class BingoTicket(models.Model):
    """Tickets para bingos gratuitos diarios"""
    
    TICKET_TYPES = [
        ('DAILY_MORNING', 'Bingo Matutino (9:00 AM)'),
        ('DAILY_AFTERNOON', 'Bingo Vespertino (2:00 PM)'),
        ('DAILY_EVENING', 'Bingo Nocturno (7:00 PM)'),
        ('REFERRAL', 'Ticket por Referido'),
        ('PROMOTION', 'Ticket Promocional'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bingo_tickets')
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    is_used = models.BooleanField(default=False)
    used_in_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Fecha de expiración del ticket")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_ticket_type_display()} ({'Usado' if self.is_used else 'Disponible'})"
    
    def is_valid(self):
        """Verifica si el ticket es válido para usar"""
        if self.is_used:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return True


class DailyBingoSchedule(models.Model):
    """Configuración de horarios para bingos diarios gratuitos"""
    
    SCHEDULE_TIMES = [
        ('09:00', '9:00 AM'),
        ('14:00', '2:00 PM'),
        ('19:00', '7:00 PM'),
    ]
    
    time_slot = models.CharField(max_length=5, choices=SCHEDULE_TIMES, unique=True)
    is_active = models.BooleanField(default=True, help_text="Activar/desactivar este horario")
    max_players = models.PositiveIntegerField(default=50, help_text="Máximo número de jugadores")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, help_text="Premio base para este horario")
    description = models.CharField(max_length=200, blank=True, help_text="Descripción del bingo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['time_slot']
    
    def __str__(self):
        return f"Bingo {self.get_time_slot_display()} ({'Activo' if self.is_active else 'Inactivo'})"
    
    @property
    def next_game_time(self):
        """Calcula la próxima hora del juego basada en el horario"""
        from datetime import datetime, time, timedelta
        
        now = timezone.now()
        today = now.date()
        
        # Convertir time_slot a objeto time
        hour, minute = map(int, self.time_slot.split(':'))
        game_time = time(hour, minute)
        
        # Crear datetime para hoy
        today_game = datetime.combine(today, game_time)
        today_game = timezone.make_aware(today_game)
        
        # Si ya pasó la hora de hoy, usar mañana
        if now > today_game:
            tomorrow = today + timedelta(days=1)
            tomorrow_game = datetime.combine(tomorrow, game_time)
            return timezone.make_aware(tomorrow_game)
        
        return today_game


class BingoTicketSettings(models.Model):
    """Configuración general del sistema de tickets"""
    
    is_system_active = models.BooleanField(default=False, help_text="Activar/desactivar todo el sistema de tickets")
    referral_ticket_bonus = models.PositiveIntegerField(default=1, help_text="Tickets que recibe el referidor por cada referido")
    referred_ticket_bonus = models.PositiveIntegerField(default=1, help_text="Tickets que recibe el usuario referido")
    ticket_expiration_days = models.PositiveIntegerField(default=7, help_text="Días hasta que expire un ticket")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Tickets"
        verbose_name_plural = "Configuración de Tickets"
    
    def __str__(self):
        return f"Configuración de Tickets ({'Activo' if self.is_system_active else 'Inactivo'})"
    
    @classmethod
    def get_settings(cls):
        """Obtiene la configuración actual o crea una por defecto"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class AccountsReceivable(models.Model):
    """
    Modelo para cuentas por cobrar creadas por organizadores
    """
    debtor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accounts_receivable',
        verbose_name="Usuario Deudor"
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_accounts_receivable',
        verbose_name="Organizador"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto Total"
    )
    concept = models.TextField(
        verbose_name="Concepto de la Deuda",
        help_text="Descripción del motivo de la deuda"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuenta por Cobrar"
        verbose_name_plural = "Cuentas por Cobrar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.debtor.username} - ${self.amount} - {self.organizer.username}"
    
    def get_total_paid(self):
        """Calcula el total abonado (método en lugar de property para evitar consultas N+1)"""
        return self.payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def total_paid(self):
        """Calcula el total abonado (property para compatibilidad)"""
        # Si tenemos el valor calculado con annotation, usarlo (más eficiente)
        if hasattr(self, 'total_paid_calculated'):
            return self.total_paid_calculated or Decimal('0.00')
        # Si ya tenemos los pagos precargados, usar esos
        if hasattr(self, '_prefetched_payments'):
            return sum(p.amount for p in self.payments.all()) or Decimal('0.00')
        # Si no, hacer la consulta (menos eficiente pero funciona)
        return self.payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def remaining_balance(self):
        """Calcula el saldo pendiente"""
        # Si tenemos el valor calculado con annotation, usarlo (más eficiente)
        if hasattr(self, 'total_paid_calculated'):
            total_paid = self.total_paid_calculated or Decimal('0.00')
        else:
            total_paid = self.total_paid
        return self.amount - total_paid
    
    @property
    def is_paid(self):
        """Verifica si la cuenta está completamente pagada"""
        return self.remaining_balance <= Decimal('0.00')


class AccountsReceivablePayment(models.Model):
    """
    Modelo para pagos/abonos realizados a cuentas por cobrar
    """
    account_receivable = models.ForeignKey(
        AccountsReceivable,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Cuenta por Cobrar"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto del Abono"
    )
    payment_method = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accounts_receivable_payments',
        verbose_name="Método de Pago"
    )
    proof = models.FileField(
        upload_to='accounts_receivable_proofs/',
        verbose_name="Comprobante de Pago"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales sobre el pago"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pago de Cuenta por Cobrar"
        verbose_name_plural = "Pagos de Cuentas por Cobrar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pago de ${self.amount} - {self.account_receivable.debtor.username}"
    
    def clean(self):
        """Validar que el monto del abono no exceda el saldo pendiente"""
        from django.core.exceptions import ValidationError
        if self.account_receivable_id:
            remaining = self.account_receivable.remaining_balance
            if self.amount > remaining:
                raise ValidationError(
                    f"El monto del abono (${self.amount}) no puede exceder el saldo pendiente (${remaining})"
                )


# ============================================================================
# SISTEMA DE FRANQUICIAS
# ============================================================================

class PackageTemplate(models.Model):
    """
    Plantillas preconfiguradas de paquetes para franquicias.
    No se pueden eliminar, solo editar precios.
    """
    PACKAGE_TYPES = [
        ('BASIC_BINGO', 'Básico Bingo'),
        ('PRO_BINGO', 'PRO Bingo'),
        ('BASIC_RAFFLE', 'Básico Rifa'),
        ('PRO_RAFFLE', 'PRO Rifa'),
    ]
    
    package_type = models.CharField(
        max_length=20, 
        choices=PACKAGE_TYPES, 
        unique=True,
        verbose_name="Tipo de Paquete"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre del Paquete"
    )
    description = models.TextField(
        help_text="Descripción del paquete",
        verbose_name="Descripción"
    )
    
    # Precios (EDITABLES por el super admin)
    default_monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio mensual por defecto (puedes cambiarlo)",
        verbose_name="Precio Mensual por Defecto"
    )
    current_monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio mensual actual (el que se usa)",
        verbose_name="Precio Mensual Actual"
    )
    default_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Comisión por defecto (puedes cambiarla)",
        verbose_name="Comisión por Defecto (%)"
    )
    current_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Comisión actual (la que se usa)",
        verbose_name="Comisión Actual (%)"
    )
    
    # Funcionalidades (PRECONFIGURADAS, no editables desde aquí)
    bingos_enabled = models.BooleanField(
        default=False,
        verbose_name="Bingos Habilitado"
    )
    raffles_enabled = models.BooleanField(
        default=False,
        verbose_name="Rifas Habilitado"
    )
    accounts_receivable_enabled = models.BooleanField(
        default=False,
        verbose_name="Cuentas por Cobrar Habilitado"
    )
    video_calls_bingos_enabled = models.BooleanField(
        default=False,
        verbose_name="Video Llamadas (Bingos) Habilitado"
    )
    video_calls_raffles_enabled = models.BooleanField(
        default=False,
        verbose_name="Video Llamadas (Rifas) Habilitado"
    )
    custom_manual_enabled = models.BooleanField(
        default=True,
        verbose_name="Manual Personalizable Habilitado"
    )
    notifications_push_enabled = models.BooleanField(
        default=False,
        verbose_name="Notificaciones Push Habilitado"
    )
    advanced_reports_enabled = models.BooleanField(
        default=False,
        verbose_name="Reportes Avanzados Habilitado"
    )
    advanced_promotions_enabled = models.BooleanField(
        default=False,
        verbose_name="Promociones Avanzadas Habilitado"
    )
    banners_enabled = models.BooleanField(
        default=False,
        verbose_name="Banners/Anuncios Habilitado"
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = 'Plantilla de Paquete'
        verbose_name_plural = 'Plantillas de Paquetes'
        ordering = ['package_type']
    
    def __str__(self):
        return f"{self.name} - ${self.current_monthly_price}/mes + {self.current_commission_rate}%"
    
    def save(self, *args, **kwargs):
        # Si es la primera vez, copiar default a current
        if not self.pk:
            self.current_monthly_price = self.default_monthly_price
            self.current_commission_rate = self.default_commission_rate
        super().save(*args, **kwargs)
    
    def reset_to_default(self):
        """Restaura los precios a los valores por defecto"""
        self.current_monthly_price = self.default_monthly_price
        self.current_commission_rate = self.default_commission_rate
        self.save()


class Franchise(models.Model):
    """
    Modelo para representar una franquicia del sistema.
    Cada franquicia es independiente y tiene su propio organizador/administrador.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Franquicia",
        help_text="Nombre que se mostrará en la plataforma"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Slug",
        help_text="URL amigable (ej: mi-franquicia)"
    )
    logo = models.ImageField(
        upload_to='franchises/logos/',
        null=True,
        blank=True,
        verbose_name="Logo",
        help_text="Logo de la franquicia"
    )
    image = models.ImageField(
        upload_to='franchises/images/',
        null=True,
        blank=True,
        verbose_name="Imagen",
        help_text="Imagen principal de la franquicia"
    )
    
    # Relación con el organizador/administrador de la franquicia
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owned_franchise',
        verbose_name="Propietario",
        help_text="Usuario que administra esta franquicia"
    )
    
    # Relación con el paquete contratado
    package_template = models.ForeignKey(
        PackageTemplate,
        on_delete=models.PROTECT,
        related_name='franchises',
        verbose_name="Paquete Contratado",
        help_text="Paquete que tiene contratado esta franquicia"
    )
    
    # Estado de la suscripción
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la franquicia está activa"
    )
    subscription_start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Inicio de Suscripción"
    )
    subscription_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Fin de Suscripción",
        help_text="Si es None, la suscripción es indefinida"
    )
    
    # Precio y comisión actuales (se copian del paquete al crear, pero pueden cambiar)
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Mensual",
        help_text="Precio mensual que paga esta franquicia"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Tasa de Comisión (%)",
        help_text="Porcentaje de comisión que se cobra"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_franchises',
        verbose_name="Creado por",
        help_text="Super admin que creó esta franquicia"
    )
    
    class Meta:
        verbose_name = 'Franquicia'
        verbose_name_plural = 'Franquicias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"
    
    @property
    def has_active_subscription(self):
        """Verifica si la suscripción está activa"""
        if not self.is_active:
            return False
        if self.subscription_end_date is None:
            return True
        return timezone.now() < self.subscription_end_date
    
    @property
    def current_package_features(self):
        """Retorna las funcionalidades del paquete actual"""
        return {
            'bingos_enabled': self.package_template.bingos_enabled,
            'raffles_enabled': self.package_template.raffles_enabled,
            'accounts_receivable_enabled': self.package_template.accounts_receivable_enabled,
            'video_calls_bingos_enabled': self.package_template.video_calls_bingos_enabled,
            'video_calls_raffles_enabled': self.package_template.video_calls_raffles_enabled,
            'custom_manual_enabled': self.package_template.custom_manual_enabled,
            'notifications_push_enabled': self.package_template.notifications_push_enabled,
            'advanced_reports_enabled': self.package_template.advanced_reports_enabled,
            'advanced_promotions_enabled': self.package_template.advanced_promotions_enabled,
            'banners_enabled': self.package_template.banners_enabled,
        }


class FranchiseManual(models.Model):
    """
    Manual personalizable para cada franquicia.
    Solo disponible si el paquete tiene custom_manual_enabled = True
    """
    franchise = models.OneToOneField(
        Franchise,
        on_delete=models.CASCADE,
        related_name='manual',
        verbose_name="Franquicia"
    )
    content = models.TextField(
        blank=True,
        default='',
        verbose_name="Contenido del Manual",
        help_text="Contenido HTML del manual personalizado"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_manuals',
        verbose_name="Actualizado por"
    )
    
    class Meta:
        verbose_name = 'Manual de Franquicia'
        verbose_name_plural = 'Manuales de Franquicias'
    
    def __str__(self):
        return f"Manual - {self.franchise.name}"