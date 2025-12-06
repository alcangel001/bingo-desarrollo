"""
Auditoría completa del sistema de créditos y premios
"""
from django.core.management.base import BaseCommand
from bingo_app.models import Game, Transaction, Player, User, PercentageSettings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from collections import defaultdict


class Command(BaseCommand):
    help = 'Auditoría completa del sistema de créditos y premios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de días hacia atrás para auditar (default: 30)',
        )
        parser.add_argument(
            '--game-id',
            type=int,
            help='ID específico de juego a auditar',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID específico de usuario a auditar',
        )

    def handle(self, *args, **options):
        days = options['days']
        game_id = options.get('game_id')
        user_id = options.get('user_id')
        
        self.stdout.write("=" * 100)
        self.stdout.write("AUDITORÍA COMPLETA DEL SISTEMA DE CRÉDITOS Y PREMIOS")
        self.stdout.write("=" * 100)
        self.stdout.write(f"\nFecha: {timezone.now()}")
        self.stdout.write(f"Período: Últimos {days} días\n")
        
        # 1. AUDITORÍA DE JUEGOS
        self.auditar_juegos(days, game_id)
        
        # 2. AUDITORÍA DE TRANSACCIONES
        self.auditar_transacciones(days, user_id)
        
        # 3. AUDITORÍA DE BALANCES
        self.auditar_balances()
        
        # 4. AUDITORÍA DE CASOS ESPECIALES
        self.auditar_casos_especiales(days, game_id)
        
        # 5. RESUMEN Y RECOMENDACIONES
        self.generar_resumen(days)
        
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("AUDITORÍA COMPLETADA")
        self.stdout.write("=" * 100)

    def auditar_juegos(self, days, game_id=None):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("1. AUDITORÍA DE JUEGOS")
        self.stdout.write("=" * 100)
        
        desde = timezone.now() - timedelta(days=days)
        
        if game_id:
            juegos = Game.objects.filter(id=game_id, is_finished=True)
        else:
            juegos = Game.objects.filter(is_finished=True, created_at__gte=desde).order_by('-created_at')
        
        total_juegos = juegos.count()
        self.stdout.write(f"\nTotal de juegos finalizados: {total_juegos}")
        
        if total_juegos == 0:
            self.stdout.write(self.style.WARNING("No se encontraron juegos finalizados en el período."))
            return
        
        problemas_encontrados = []
        juegos_auditados = 0
        juegos_con_problemas = 0
        
        for juego in juegos:
            juegos_auditados += 1
            problemas_juego = []
            
            # Verificar premio calculado
            premio_esperado = Decimal(str(juego.base_prize))
            if juego.progressive_prizes:
                for pp in sorted(juego.progressive_prizes, key=lambda x: x.get('target', 0)):
                    if juego.max_cards_sold >= pp.get('target', 0):
                        premio_esperado += Decimal(str(pp.get('prize', 0)))
            
            if premio_esperado != juego.prize:
                problemas_juego.append(f"Premio calculado ({juego.prize}) no coincide con esperado ({premio_esperado})")
            
            # Verificar ganadores
            ganadores = Player.objects.filter(game=juego, is_winner=True)
            num_ganadores = ganadores.count()
            
            if num_ganadores == 0:
                if juego.prize > 0:
                    problemas_juego.append("Juego con premio pero sin ganadores")
            else:
                premio_por_ganador = juego.prize / num_ganadores if num_ganadores > 0 else 0
                
                # Verificar que cada ganador recibió su premio
                for ganador in ganadores:
                    transacciones = Transaction.objects.filter(
                        user=ganador.user,
                        related_game=juego,
                        transaction_type='PRIZE'
                    )
                    total_recibido = sum(t.amount for t in transacciones)
                    
                    if total_recibido == 0:
                        problemas_juego.append(f"Ganador {ganador.user.username} no recibió créditos (0 transacciones)")
                    elif total_recibido != premio_por_ganador:
                        problemas_juego.append(
                            f"Ganador {ganador.user.username} recibió {total_recibido} pero debería recibir {premio_por_ganador}"
                        )
                    
                    # Verificar balance actual vs transacciones
                    transacciones_totales = Transaction.objects.filter(user=ganador.user).aggregate(
                        total=Sum('amount')
                    )['total'] or Decimal('0.00')
                    
                    # Calcular balance esperado (balance inicial + todas las transacciones)
                    # Nota: Esto es aproximado, asume balance inicial de 0
                    if abs(ganador.user.credit_balance - transacciones_totales) > Decimal('0.01'):
                        problemas_juego.append(
                            f"Ganador {ganador.user.username}: Balance ({ganador.user.credit_balance}) no coincide con suma de transacciones ({transacciones_totales})"
                        )
                
                # Verificar si organizador es ganador
                organizador_es_ganador = any(g.user.id == juego.organizer.id for g in ganadores)
                if organizador_es_ganador:
                    # Verificar que el organizador recibió tanto el premio como el revenue
                    trans_premio = Transaction.objects.filter(
                        user=juego.organizer,
                        related_game=juego,
                        transaction_type='PRIZE'
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    trans_revenue = Transaction.objects.filter(
                        user=juego.organizer,
                        related_game=juego,
                        transaction_type='ORGANIZER_REVENUE'
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    if trans_premio == 0:
                        problemas_juego.append(f"Organizador {juego.organizer.username} es ganador pero no recibió premio")
            
            if problemas_juego:
                juegos_con_problemas += 1
                problemas_encontrados.append({
                    'juego_id': juego.id,
                    'juego_nombre': juego.name,
                    'problemas': problemas_juego
                })
                
                self.stdout.write(f"\n[PROBLEMA] JUEGO ID {juego.id} - {juego.name}")
                self.stdout.write(f"   Organizador: {juego.organizer.username}")
                self.stdout.write(f"   Premio: {juego.prize} (Base: {juego.base_prize})")
                self.stdout.write(f"   Ganadores: {num_ganadores}")
                for problema in problemas_juego:
                    self.stdout.write(self.style.ERROR(f"   [X] {problema}"))
        
        self.stdout.write(f"\nRESUMEN:")
        self.stdout.write(f"   Juegos auditados: {juegos_auditados}")
        self.stdout.write(f"   Juegos con problemas: {juegos_con_problemas}")
        self.stdout.write(f"   Juegos correctos: {juegos_auditados - juegos_con_problemas}")

    def auditar_transacciones(self, days, user_id=None):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("2. AUDITORÍA DE TRANSACCIONES")
        self.stdout.write("=" * 100)
        
        desde = timezone.now() - timedelta(days=days)
        
        filtro = Q(created_at__gte=desde)
        if user_id:
            filtro &= Q(user_id=user_id)
        
        transacciones = Transaction.objects.filter(filtro)
        
        total_trans = transacciones.count()
        self.stdout.write(f"\nTotal de transacciones: {total_trans}")
        
        # Agrupar por tipo
        por_tipo = transacciones.values('transaction_type').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('transaction_type')
        
        self.stdout.write("\nTransacciones por tipo:")
        for tipo in por_tipo:
            self.stdout.write(f"   {tipo['transaction_type']}: {tipo['count']} transacciones, Total: {tipo['total']}")
        
        # Verificar transacciones de premio
        trans_premios = transacciones.filter(transaction_type='PRIZE')
        self.stdout.write(f"\nTransacciones de PREMIO: {trans_premios.count()}")
        
        # Verificar duplicados
        duplicados = transacciones.values('user', 'amount', 'transaction_type', 'related_game', 'created_at').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicados.exists():
            self.stdout.write(self.style.ERROR(f"\n[ADVERTENCIA] Se encontraron {duplicados.count()} grupos de transacciones duplicadas"))
            for dup in duplicados[:10]:  # Mostrar solo los primeros 10
                self.stdout.write(self.style.ERROR(f"   Usuario {dup['user']}, Monto: {dup['amount']}, Tipo: {dup['transaction_type']}"))
        else:
            self.stdout.write(self.style.SUCCESS("\n[OK] No se encontraron transacciones duplicadas"))

    def auditar_balances(self):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("3. AUDITORÍA DE BALANCES")
        self.stdout.write("=" * 100)
        
        # Solo seleccionar campos necesarios para evitar errores de columnas faltantes
        usuarios = User.objects.only('id', 'username', 'credit_balance').all()
        total_usuarios = usuarios.count()
        problemas_balance = 0
        
        self.stdout.write(f"\nTotal de usuarios: {total_usuarios}")
        
        for usuario in usuarios[:100]:  # Limitar a primeros 100 para no sobrecargar
            transacciones = Transaction.objects.filter(user=usuario)
            suma_transacciones = transacciones.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Calcular diferencia (asumiendo balance inicial de 0)
            diferencia = abs(usuario.credit_balance - suma_transacciones)
            
            if diferencia > Decimal('0.01'):  # Tolerancia para errores de redondeo
                problemas_balance += 1
                if problemas_balance <= 10:  # Mostrar solo los primeros 10
                    self.stdout.write(
                        self.style.ERROR(
                            f"[PROBLEMA] {usuario.username}: Balance={usuario.credit_balance}, Suma transacciones={suma_transacciones}, Diferencia={diferencia}"
                        )
                    )
        
        if problemas_balance == 0:
            self.stdout.write(self.style.SUCCESS("\n[OK] Todos los balances coinciden con las transacciones"))
        else:
            self.stdout.write(f"\n[ADVERTENCIA] Se encontraron {problemas_balance} usuarios con discrepancias en balance")

    def auditar_casos_especiales(self, days, game_id=None):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("4. AUDITORÍA DE CASOS ESPECIALES")
        self.stdout.write("=" * 100)
        
        desde = timezone.now() - timedelta(days=days)
        
        if game_id:
            juegos = Game.objects.filter(id=game_id, is_finished=True)
        else:
            juegos = Game.objects.filter(is_finished=True, created_at__gte=desde)
        
        # Caso 1: Organizador también es ganador
        casos_organizador_ganador = 0
        problemas_organizador = []
        
        for juego in juegos:
            ganadores = Player.objects.filter(game=juego, is_winner=True)
            organizador_es_ganador = any(g.user.id == juego.organizer.id for g in ganadores)
            
            if organizador_es_ganador:
                casos_organizador_ganador += 1
                
                # Verificar que recibió premio
                trans_premio = Transaction.objects.filter(
                    user=juego.organizer,
                    related_game=juego,
                    transaction_type='PRIZE'
                ).count()
                
                # Verificar que recibió revenue
                trans_revenue = Transaction.objects.filter(
                    user=juego.organizer,
                    related_game=juego,
                    transaction_type='ORGANIZER_REVENUE'
                ).count()
                
                if trans_premio == 0:
                    problemas_organizador.append(f"Juego {juego.id}: Organizador ganador no recibió premio")
                if trans_revenue == 0 and juego.held_balance > 0:
                    problemas_organizador.append(f"Juego {juego.id}: Organizador no recibió revenue")
        
        self.stdout.write(f"\nCasos donde organizador también es ganador: {casos_organizador_ganador}")
        if problemas_organizador:
            self.stdout.write(self.style.ERROR(f"PROBLEMAS encontrados: {len(problemas_organizador)}"))
            for problema in problemas_organizador[:5]:
                self.stdout.write(self.style.ERROR(f"   {problema}"))
        else:
            self.stdout.write(self.style.SUCCESS("Todos los casos de organizador-ganador están correctos"))
        
        # Caso 2: Múltiples ganadores
        casos_multiples_ganadores = 0
        for juego in juegos:
            ganadores = Player.objects.filter(game=juego, is_winner=True)
            if ganadores.count() > 1:
                casos_multiples_ganadores += 1
        
        self.stdout.write(f"\nCasos con múltiples ganadores: {casos_multiples_ganadores}")
        
        # Caso 3: Juegos sin ganadores pero con premio
        juegos_sin_ganadores = juegos.filter(prize__gt=0).exclude(
            id__in=Player.objects.filter(is_winner=True).values_list('game_id', flat=True)
        ).count()
        
        if juegos_sin_ganadores > 0:
            self.stdout.write(self.style.WARNING(f"\n[ADVERTENCIA] Juegos con premio pero sin ganadores: {juegos_sin_ganadores}"))
        else:
            self.stdout.write(self.style.SUCCESS("\n[OK] Todos los juegos con premio tienen ganadores"))

    def generar_resumen(self, days):
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write("5. RESUMEN Y RECOMENDACIONES")
        self.stdout.write("=" * 100)
        
        desde = timezone.now() - timedelta(days=days)
        
        total_juegos = Game.objects.filter(is_finished=True, created_at__gte=desde).count()
        total_transacciones = Transaction.objects.filter(created_at__gte=desde).count()
        total_premios = Transaction.objects.filter(
            transaction_type='PRIZE',
            created_at__gte=desde
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        self.stdout.write(f"\nESTADISTICAS GENERALES (últimos {days} días):")
        self.stdout.write(f"   Juegos finalizados: {total_juegos}")
        self.stdout.write(f"   Transacciones totales: {total_transacciones}")
        self.stdout.write(f"   Premios pagados: {total_premios}")
        
        self.stdout.write("\nRECOMENDACIONES:")
        self.stdout.write("   1. Monitorear regularmente los logs para detectar problemas temprano")
        self.stdout.write("   2. Ejecutar esta auditoría semanalmente")
        self.stdout.write("   3. Verificar balances después de cada juego importante")
        self.stdout.write("   4. Revisar casos donde organizador también es ganador")
        self.stdout.write("   5. Mantener backups regulares de la base de datos")

