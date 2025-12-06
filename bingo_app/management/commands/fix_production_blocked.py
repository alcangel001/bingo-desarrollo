from django.core.management.base import BaseCommand
from django.db.models import Sum
from bingo_app.models import User, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Fix negative blocked credits in production'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write("=== DRY RUN: Checking for negative blocked credits ===\n")
        else:
            self.stdout.write("=== FIXING NEGATIVE BLOCKED CREDITS ===\n")
        
        # Buscar usuarios con saldo bloqueado negativo
        users_with_negative = User.objects.filter(blocked_credits__lt=0)
        
        if not users_with_negative.exists():
            self.stdout.write("OK: No hay usuarios con saldo bloqueado negativo")
            return
        
        self.stdout.write(f"Encontrados {users_with_negative.count()} usuarios con saldo bloqueado negativo:")
        
        for user in users_with_negative:
            self.stdout.write(f"\n--- Usuario: {user.username} ---")
            self.stdout.write(f"Saldo bloqueado actual: ${user.blocked_credits}")
            self.stdout.write(f"Saldo total: ${user.credit_balance}")
            
            # Mostrar transacciones relevantes
            prize_lock_transactions = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_LOCK'
            ).order_by('-created_at')[:5]
            
            prize_unlock_transactions = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_UNLOCK'
            ).order_by('-created_at')[:5]
            
            self.stdout.write(f"\nTransacciones PRIZE_LOCK recientes:")
            for tx in prize_lock_transactions:
                self.stdout.write(f"  - ${tx.amount} ({tx.description}) - {tx.created_at}")
            
            self.stdout.write(f"\nTransacciones PRIZE_UNLOCK recientes:")
            for tx in prize_unlock_transactions:
                self.stdout.write(f"  - ${tx.amount} ({tx.description}) - {tx.created_at}")
            
            # Calcular saldo esperado
            total_locks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_LOCK'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            total_unlocks = Transaction.objects.filter(
                user=user,
                transaction_type='PRIZE_UNLOCK'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Los locks son negativos, unlocks son positivos
            expected_blocked = abs(total_locks) - total_unlocks
            
            self.stdout.write(f"\nAnálisis:")
            self.stdout.write(f"  Total bloqueos: ${abs(total_locks)}")
            self.stdout.write(f"  Total desbloqueos: ${total_unlocks}")
            self.stdout.write(f"  Saldo bloqueado esperado: ${expected_blocked}")
            self.stdout.write(f"  Saldo bloqueado actual: ${user.blocked_credits}")
            
            if not dry_run:
                # Arreglar el saldo bloqueado
                if expected_blocked < 0:
                    # Si el esperado es negativo, ajustar a 0
                    new_blocked = Decimal('0.00')
                    self.stdout.write(f"  Acción: Ajustando saldo bloqueado a $0.00 (era negativo)")
                else:
                    # Si el esperado es positivo, usar ese valor
                    new_blocked = expected_blocked
                    self.stdout.write(f"  Acción: Corrigiendo saldo bloqueado a ${new_blocked}")
                
                user.blocked_credits = new_blocked
                user.save()
                self.stdout.write(f"  Saldo bloqueado corregido: ${user.blocked_credits}")
            else:
                self.stdout.write(f"  [DRY RUN] Se corregiría a: ${max(expected_blocked, 0)}")
        
        if dry_run:
            self.stdout.write(f"\n=== DRY RUN COMPLETADO ===")
            self.stdout.write("Para aplicar las correcciones, ejecuta sin --dry-run")
        else:
            self.stdout.write(f"\n=== CORRECCIÓN COMPLETADA ===")
            self.stdout.write("Todos los saldos bloqueados negativos han sido corregidos")
