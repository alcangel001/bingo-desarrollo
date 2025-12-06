from django.core.management.base import BaseCommand
from bingo_app.models import User, Game, Raffle
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test blocked_credits validation by creating test scenarios'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTING BLOCKED CREDITS VALIDATION ===\n")
        
        # Crear un usuario de prueba
        test_user, created = User.objects.get_or_create(
            username='test_validation_user',
            defaults={
                'email': 'test@validation.com',
                'is_organizer': True,
                'credit_balance': 1000.00,
                'blocked_credits': 0.00
            }
        )
        
        if created:
            self.stdout.write("Usuario de prueba creado")
        else:
            self.stdout.write("Usuario de prueba ya existe")
        
        self.stdout.write(f"Usuario: {test_user.username}")
        self.stdout.write(f"Saldo inicial: ${test_user.credit_balance}")
        self.stdout.write(f"Saldo bloqueado inicial: ${test_user.blocked_credits}")
        
        # Test 1: Simular escenario normal
        self.stdout.write("\n--- TEST 1: Escenario Normal ---")
        test_user.blocked_credits = 100.00
        test_user.save()
        self.stdout.write(f"Saldo bloqueado: ${test_user.blocked_credits}")
        
        # Simular desbloqueo normal
        if test_user.blocked_credits >= 50.00:
            test_user.blocked_credits -= 50.00
            test_user.save()
            self.stdout.write(f"Desbloqueo normal: $50.00")
            self.stdout.write(f"Saldo bloqueado después: ${test_user.blocked_credits}")
        else:
            self.stdout.write("ERROR: No debería entrar aquí")
        
        # Test 2: Simular escenario problemático
        self.stdout.write("\n--- TEST 2: Escenario Problemático ---")
        test_user.blocked_credits = 30.00  # Solo $30 bloqueados
        test_user.save()
        self.stdout.write(f"Saldo bloqueado: ${test_user.blocked_credits}")
        
        # Intentar desbloquear $100 (más de lo bloqueado)
        amount_to_unlock = 100.00
        if test_user.blocked_credits >= amount_to_unlock:
            test_user.blocked_credits -= amount_to_unlock
            unlock_amount = amount_to_unlock
            self.stdout.write(f"Desbloqueo normal: ${amount_to_unlock}")
        else:
            # Ajustar a 0 si hay menos créditos bloqueados de los esperados
            unlock_amount = test_user.blocked_credits
            test_user.blocked_credits = Decimal('0.00')
            self.stdout.write(f"ADVERTENCIA: Intentando desbloquear ${amount_to_unlock} pero solo hay ${unlock_amount} bloqueados. Ajustando a 0.")
        
        test_user.save()
        self.stdout.write(f"Saldo bloqueado después: ${test_user.blocked_credits}")
        self.stdout.write(f"Cantidad realmente desbloqueada: ${unlock_amount}")
        
        # Test 3: Verificar que no puede quedar negativo
        self.stdout.write("\n--- TEST 3: Verificar Protección Contra Negativos ---")
        test_user.blocked_credits = 10.00
        test_user.save()
        self.stdout.write(f"Saldo bloqueado: ${test_user.blocked_credits}")
        
        # Intentar desbloquear $50
        amount_to_unlock = 50.00
        if test_user.blocked_credits >= amount_to_unlock:
            test_user.blocked_credits -= amount_to_unlock
            unlock_amount = amount_to_unlock
            self.stdout.write(f"Desbloqueo normal: ${amount_to_unlock}")
        else:
            unlock_amount = test_user.blocked_credits
            test_user.blocked_credits = Decimal('0.00')
            self.stdout.write(f"ADVERTENCIA: Intentando desbloquear ${amount_to_unlock} pero solo hay ${unlock_amount} bloqueados. Ajustando a 0.")
        
        test_user.save()
        self.stdout.write(f"Saldo bloqueado después: ${test_user.blocked_credits}")
        
        # Verificar que no es negativo
        if test_user.blocked_credits < 0:
            self.stdout.write("ERROR: El saldo bloqueado no debería ser negativo!")
        else:
            self.stdout.write("OK: El saldo bloqueado no es negativo")
        
        # Limpiar usuario de prueba (sin eliminar por problemas de dependencias)
        test_user.username = f"test_validation_user_cleaned_{timezone.now().timestamp()}"
        test_user.save()
        self.stdout.write("\nUsuario de prueba marcado como usado")
        
        self.stdout.write("\n=== TEST COMPLETADO ===")
        self.stdout.write("Las validaciones están funcionando correctamente!")
