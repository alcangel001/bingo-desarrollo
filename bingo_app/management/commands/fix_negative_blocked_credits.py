from django.core.management.base import BaseCommand
from django.db import transaction
from bingo_app.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Corrige saldos bloqueados negativos ajustándolos a 0'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué cambios se harían sin ejecutarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Buscar usuarios con blocked_credits negativos
        users_with_negative_blocked = User.objects.filter(blocked_credits__lt=0)
        
        if not users_with_negative_blocked.exists():
            self.stdout.write(
                self.style.SUCCESS('No se encontraron usuarios con saldos bloqueados negativos.')
            )
            
            # Mostrar estado actual de organizadores
            self.stdout.write('\n=== ESTADO ACTUAL DE ORGANIZADORES ===')
            organizers = User.objects.filter(is_organizer=True)
            for org in organizers:
                self.stdout.write(f'{org.username}:')
                self.stdout.write(f'  - Saldo Actual: ${org.credit_balance}')
                self.stdout.write(f'  - Saldo Bloqueado: ${org.blocked_credits}')
                self.stdout.write(f'  - Total Eventos: {org.total_completed_events}')
                self.stdout.write()
            return
        
        self.stdout.write(f'Encontrados {users_with_negative_blocked.count()} usuarios con saldos bloqueados negativos:')
        
        for user in users_with_negative_blocked:
            self.stdout.write(f'  - {user.username}: ${user.blocked_credits}')
            
            if not dry_run:
                with transaction.atomic():
                    # Ajustar blocked_credits a 0
                    old_blocked = user.blocked_credits
                    user.blocked_credits = Decimal('0.00')
                    user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'    ✅ Corregido: ${old_blocked} → $0.00')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'    🔍 DRY RUN: Se corregiría ${user.blocked_credits} → $0.00')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 MODO DRY RUN - No se realizaron cambios reales')
            )
            self.stdout.write('Ejecuta sin --dry-run para aplicar los cambios')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Se corrigieron {users_with_negative_blocked.count()} usuarios')
            )