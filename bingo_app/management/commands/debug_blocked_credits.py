from django.core.management.base import BaseCommand
from bingo_app.models import User, Transaction, Game, Raffle
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Debug blocked_credits negative values'

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUGGING BLOCKED CREDITS ===\n")
        
        # Buscar usuarios con blocked_credits negativos
        negative_users = User.objects.filter(blocked_credits__lt=0)
        
        if not negative_users.exists():
            self.stdout.write("OK: No hay usuarios con saldo bloqueado negativo")
            return
        
        self.stdout.write(f"ERROR: Encontrados {negative_users.count()} usuarios con saldo bloqueado negativo:\n")
        
        for user in negative_users:
            self.stdout.write(f"Usuario: {user.username}")
            self.stdout.write(f"   Saldo bloqueado: ${user.blocked_credits}")
            self.stdout.write(f"   Saldo actual: ${user.credit_balance}")
            self.stdout.write(f"   Es organizador: {user.is_organizer}")
            
            # Buscar transacciones relacionadas con blocked_credits
            self.stdout.write("\n   Transacciones relevantes:")
            
            # Transacciones PRIZE_LOCK (deberían bloquear créditos)
            prize_locks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_LOCK'
            ).order_by('-created_at')[:5]
            
            if prize_locks.exists():
                self.stdout.write("   PRIZE_LOCK (bloqueos):")
                for tx in prize_locks:
                    self.stdout.write(f"      - ${tx.amount} - {tx.description} ({tx.created_at})")
            
            # Transacciones PRIZE_UNLOCK (deberían desbloquear créditos)
            prize_unlocks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_UNLOCK'
            ).order_by('-created_at')[:5]
            
            if prize_unlocks.exists():
                self.stdout.write("   PRIZE_UNLOCK (desbloqueos):")
                for tx in prize_unlocks:
                    self.stdout.write(f"      - ${tx.amount} - {tx.description} ({tx.created_at})")
            
            # Juegos creados por este usuario
            games = Game.objects.filter(organizer=user)
            if games.exists():
                self.stdout.write(f"\n   Juegos creados: {games.count()}")
                total_prizes = games.aggregate(Sum('prize'))['prize__sum'] or 0
                self.stdout.write(f"   Total premios de juegos: ${total_prizes}")
            
            # Rifas creadas por este usuario
            raffles = Raffle.objects.filter(organizer=user)
            if raffles.exists():
                self.stdout.write(f"\n   Rifas creadas: {raffles.count()}")
                total_prizes = raffles.aggregate(Sum('prize'))['prize__sum'] or 0
                self.stdout.write(f"   Total premios de rifas: ${total_prizes}")
            
            # Calcular diferencia
            total_locks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_LOCK'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_unlocks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_UNLOCK'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            expected_blocked = total_locks - total_unlocks
            
            self.stdout.write(f"\n   Analisis:")
            self.stdout.write(f"      Total bloqueos: ${total_locks}")
            self.stdout.write(f"      Total desbloqueos: ${total_unlocks}")
            self.stdout.write(f"      Esperado bloqueado: ${expected_blocked}")
            self.stdout.write(f"      Real bloqueado: ${user.blocked_credits}")
            self.stdout.write(f"      Diferencia: ${user.blocked_credits - expected_blocked}")
            
            self.stdout.write("\n" + "="*50 + "\n")
        
        self.stdout.write("\n=== FIN DEL DEBUG ===")
