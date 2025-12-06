"""
Comando de Django para verificar premios y distribución de créditos en juegos recientes
"""
from django.core.management.base import BaseCommand
from bingo_app.models import Game, Transaction, Player
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Verifica premios y distribución de créditos en juegos recientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Número de horas hacia atrás para buscar juegos (default: 24)',
        )
        parser.add_argument(
            '--game-id',
            type=int,
            help='ID específico de juego a verificar',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        game_id = options.get('game_id')
        
        self.stdout.write("=" * 80)
        self.stdout.write("VERIFICACIÓN DE JUEGOS Y DISTRIBUCIÓN DE PREMIOS")
        self.stdout.write("=" * 80)
        
        if game_id:
            juegos = Game.objects.filter(id=game_id, is_finished=True)
        else:
            desde = timezone.now() - timedelta(hours=hours)
            juegos = Game.objects.filter(is_finished=True, created_at__gte=desde).order_by('-created_at')[:10]
        
        if not juegos:
            self.stdout.write(self.style.WARNING(f"\nNo se encontraron juegos finalizados en las últimas {hours} horas."))
            return
        
        for juego in juegos:
            self.stdout.write(f"\n{'='*80}")
            self.stdout.write(f"JUEGO ID: {juego.id} - {juego.name}")
            self.stdout.write(f"Organizador: {juego.organizer.username}")
            self.stdout.write(f"Fecha creación: {juego.created_at}")
            self.stdout.write(f"Premio base configurado: {juego.base_prize}")
            self.stdout.write(f"Premios progresivos: {juego.progressive_prizes}")
            self.stdout.write(f"Premio calculado (prize): {juego.prize}")
            self.stdout.write(f"Cartones vendidos: {juego.total_cards_sold}")
            self.stdout.write(f"Cartones máximos: {juego.max_cards_sold}")
            
            # Calcular premio esperado
            premio_esperado = Decimal(str(juego.base_prize))
            if juego.progressive_prizes:
                for pp in sorted(juego.progressive_prizes, key=lambda x: x.get('target', 0)):
                    if juego.max_cards_sold >= pp.get('target', 0):
                        premio_esperado += Decimal(str(pp.get('prize', 0)))
            
            self.stdout.write(f"Premio esperado (base + progresivos): {premio_esperado}")
            
            if premio_esperado != juego.prize:
                self.stdout.write(self.style.ERROR(f"  ⚠️  ADVERTENCIA: El premio calculado ({juego.prize}) no coincide con el esperado ({premio_esperado})!"))
            
            # Verificar ganadores
            ganadores = Player.objects.filter(game=juego, is_winner=True)
            self.stdout.write(f"\nGanadores encontrados: {ganadores.count()}")
            
            if ganadores.count() > 0:
                premio_por_ganador = juego.prize / ganadores.count()
                self.stdout.write(f"Premio por ganador (debería ser): {premio_por_ganador}")
            
            problemas_encontrados = False
            
            for ganador in ganadores:
                self.stdout.write(f"\n  - Ganador: {ganador.user.username} (ID: {ganador.user.id})")
                self.stdout.write(f"    Saldo actual: {ganador.user.credit_balance}")
                
                # Buscar transacciones de premio para este jugador en este juego
                transacciones = Transaction.objects.filter(
                    user=ganador.user,
                    related_game=juego,
                    transaction_type='PRIZE'
                )
                
                self.stdout.write(f"    Transacciones de premio: {transacciones.count()}")
                total_recibido = Decimal('0.00')
                for trans in transacciones:
                    self.stdout.write(f"      - {trans.amount} créditos el {trans.created_at}")
                    total_recibido += trans.amount
                
                self.stdout.write(f"    Total recibido en transacciones: {total_recibido}")
                
                # Verificar si recibió el premio correcto
                if ganadores.count() > 0:
                    premio_esperado_ganador = juego.prize / ganadores.count()
                    if total_recibido != premio_esperado_ganador:
                        self.stdout.write(self.style.ERROR(
                            f"    ⚠️  PROBLEMA: {ganador.user.username} recibió {total_recibido} pero debería recibir {premio_esperado_ganador}"
                        ))
                        problemas_encontrados = True
                    elif total_recibido == Decimal('0.00'):
                        self.stdout.write(self.style.ERROR(
                            f"    ⚠️  PROBLEMA CRÍTICO: {ganador.user.username} NO recibió créditos (0 transacciones de premio)"
                        ))
                        problemas_encontrados = True
            
            if not problemas_encontrados and ganadores.count() > 0:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Distribución de premios correcta para este juego"))
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("VERIFICACIÓN COMPLETADA")
        self.stdout.write("=" * 80)

