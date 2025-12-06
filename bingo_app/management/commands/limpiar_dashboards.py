from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Q
from decimal import Decimal

from bingo_app.models import (
    Game,
    Player,
    Transaction,
    Ticket,
    Raffle,
    ChatMessage,
    Message,
    CreditRequest,
    CreditRequestNotification,
    WithdrawalRequest,
    WithdrawalRequestNotification,
    PrintableCard,
    VideoCallGroup,
    BingoTicket,
    User,
)


class Command(BaseCommand):
    help = (
        "Limpia los dashboards eliminando datos históricos pero conservando "
        "usuarios y configuraciones. Por defecto hace limpieza completa."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--completo",
            action="store_true",
            help="[Por defecto activo] Limpieza completa: elimina todos los juegos, transacciones, rifas, etc.",
        )
        parser.add_argument(
            "--reset-saldos",
            action="store_true",
            help="Resetea todos los saldos de usuarios a 0",
        )
        parser.add_argument(
            "--sin-confirmacion",
            action="store_true",
            help="Ejecuta sin pedir confirmación (peligroso)",
        )
        parser.add_argument(
            "--solo-vista-previa",
            action="store_true",
            help="Solo muestra qué se eliminaría sin ejecutar nada",
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🧹 LIMPIEZA DE DASHBOARDS")
        self.stdout.write("=" * 60 + "\n")

        # Datos que se conservarán
        self.stdout.write("📋 DATOS QUE SE CONSERVARÁN:")
        self.stdout.write("  ✅ Todos los usuarios registrados")
        self.stdout.write("  ✅ Configuraciones del sistema (comisiones, etc.)")
        self.stdout.write("  ✅ Métodos de pago (cuentas bancarias)")
        self.stdout.write("  ✅ Anuncios generales")
        self.stdout.write("  ✅ Promociones y referidos (configuración)")
        self.stdout.write("  ✅ Logros (configuración)")
        self.stdout.write("  ✅ Historial de bloqueos\n")

        # Contar datos actuales
        total_games = Game.objects.count()
        total_players = Player.objects.count()
        total_transactions = Transaction.objects.count()
        total_tickets = Ticket.objects.count()
        total_bingotickets = BingoTicket.objects.count()
        total_raffles = Raffle.objects.count()
        total_chatmessages = ChatMessage.objects.count()
        total_messages = Message.objects.count()
        total_credit_requests = CreditRequest.objects.count()
        total_withdrawal_requests = WithdrawalRequest.objects.count()
        total_printable_cards = PrintableCard.objects.count()
        total_videocall_groups = VideoCallGroup.objects.count()
        total_users = User.objects.count()

        total_balance = (
            User.objects.aggregate(total_balance=Sum("credit_balance"))[
                "total_balance"
            ]
            or Decimal("0.00")
        )
        total_blocked = (
            User.objects.aggregate(total_blocked=Sum("blocked_credits"))[
                "total_blocked"
            ]
            or Decimal("0.00")
        )

        self.stdout.write("📊 DATOS ACTUALES:")
        self.stdout.write(f"  • Juegos: {total_games}")
        self.stdout.write(f"  • Jugadores en juegos: {total_players}")
        self.stdout.write(f"  • Transacciones: {total_transactions}")
        self.stdout.write(f"  • Tickets (Bingo clásico): {total_tickets}")
        self.stdout.write(f"  • BingoTickets (Bingo mejorado): {total_bingotickets}")
        self.stdout.write(f"  • Rifas: {total_raffles}")
        self.stdout.write(f"  • Mensajes de chat: {total_chatmessages}")
        self.stdout.write(f"  • Mensajes privados: {total_messages}")
        self.stdout.write(f"  • Solicitudes de crédito: {total_credit_requests}")
        self.stdout.write(f"  • Solicitudes de retiro: {total_withdrawal_requests}")
        self.stdout.write(f"  • Cartones imprimibles: {total_printable_cards}")
        self.stdout.write(f"  • Grupos de videollamada: {total_videocall_groups}")
        self.stdout.write(f"  • Usuarios: {total_users} ✅ (SE CONSERVAN)")
        self.stdout.write(f"  • Saldo total de usuarios: ${total_balance}")
        self.stdout.write(f"  • Saldo bloqueado total: ${total_blocked}\n")

        self.stdout.write("🗑️  DATOS QUE SE ELIMINARÁN:")
        self.stdout.write(f"  ❌ {total_games} juegos")
        self.stdout.write(f"  ❌ {total_players} jugadores en juegos")
        self.stdout.write(f"  ❌ {total_transactions} transacciones")
        self.stdout.write(f"  ❌ {total_tickets} tickets (bingo clásico)")
        self.stdout.write(f"  ❌ {total_bingotickets} bingotickets")
        self.stdout.write(f"  ❌ {total_raffles} rifas")
        self.stdout.write(f"  ❌ {total_chatmessages} mensajes de chat")
        self.stdout.write(f"  ❌ {total_messages} mensajes privados")
        self.stdout.write(f"  ❌ {total_credit_requests} solicitudes de crédito")
        self.stdout.write(f"  ❌ {total_withdrawal_requests} solicitudes de retiro")
        self.stdout.write(f"  ❌ {total_printable_cards} cartones imprimibles")
        self.stdout.write(f"  ❌ {total_videocall_groups} grupos de videollamada")

        if options.get("reset_saldos"):
            self.stdout.write(
                f"  ⚠️  Saldos de usuarios se resetearán a 0 "
                f"(Total a resetear: ${total_balance + total_blocked})"
            )

        self.stdout.write("")

        if options.get("solo_vista_previa"):
            self.stdout.write(
                "⚠️  MODO VISTA PREVIA - No se ejecutará ninguna acción\n"
            )
            return

        if not options.get("sin_confirmacion"):
            self.stdout.write("⚠️  ADVERTENCIA: Esta acción es IRREVERSIBLE\n")
            confirm = input(
                '¿Estás seguro de que quieres continuar? (escribe "SI" para confirmar): '
            )
            if confirm.upper() != "SI":
                self.stdout.write("❌ Operación cancelada.")
                return

        self.stdout.write("🚀 Iniciando limpieza...\n")

        try:
            with transaction.atomic():
                deleted_counts = {}

                # 1. Mensajes de chat
                count = ChatMessage.objects.count()
                ChatMessage.objects.all().delete()
                deleted_counts["chatmessages"] = count

                # 2. Jugadores
                count = Player.objects.count()
                Player.objects.all().delete()
                deleted_counts["players"] = count

                # 3. Tickets clásicos
                count = Ticket.objects.count()
                Ticket.objects.all().delete()
                deleted_counts["tickets"] = count

                # 4. BingoTickets
                count = BingoTicket.objects.count()
                BingoTicket.objects.all().delete()
                deleted_counts["bingotickets"] = count

                # 5. Transacciones con juego
                transactions_with_game = Transaction.objects.filter(
                    related_game__isnull=False
                ).count()
                Transaction.objects.filter(related_game__isnull=False).delete()
                deleted_counts["transactions_with_game"] = transactions_with_game

                # 6. Transacciones de retiro
                credit_transactions = Transaction.objects.filter(
                    transaction_type__in=["WITHDRAWAL", "WITHDRAWAL_REFUND"]
                ).count()
                Transaction.objects.filter(
                    transaction_type__in=["WITHDRAWAL", "WITHDRAWAL_REFUND"]
                ).delete()
                deleted_counts["credit_transactions"] = credit_transactions

                # 7. Notificaciones de crédito
                count = CreditRequestNotification.objects.count()
                CreditRequestNotification.objects.all().delete()
                deleted_counts["credit_notifications"] = count

                # 8. Notificaciones de retiro
                count = WithdrawalRequestNotification.objects.count()
                WithdrawalRequestNotification.objects.all().delete()
                deleted_counts["withdrawal_notifications"] = count

                # 9. Solicitudes de crédito
                count = CreditRequest.objects.count()
                CreditRequest.objects.all().delete()
                deleted_counts["credit_requests"] = count

                # 10. Solicitudes de retiro
                count = WithdrawalRequest.objects.count()
                WithdrawalRequest.objects.all().delete()
                deleted_counts["withdrawal_requests"] = count

                # 11. Cartones imprimibles
                count = PrintableCard.objects.count()
                PrintableCard.objects.all().delete()
                deleted_counts["printable_cards"] = count

                # 12. Grupos de videollamada
                count = VideoCallGroup.objects.count()
                VideoCallGroup.objects.all().delete()
                deleted_counts["videocall_groups"] = count

                # 13. Mensajes privados
                count = Message.objects.count()
                Message.objects.all().delete()
                deleted_counts["messages"] = count

                # 14. Rifas
                count = Raffle.objects.count()
                Raffle.objects.all().delete()
                deleted_counts["raffles"] = count

                # 15. Juegos
                count = Game.objects.count()
                Game.objects.all().delete()
                deleted_counts["games"] = count

                # 16. Reset saldos
                if options.get("reset_saldos"):
                    users_updated = (
                        User.objects.filter(
                            Q(credit_balance__gt=0) | Q(blocked_credits__gt=0)
                        )
                        .update(
                            credit_balance=Decimal("0.00"),
                            blocked_credits=Decimal("0.00"),
                        )
                    )
                    deleted_counts["reset_saldos"] = users_updated
                    User.objects.all().update(total_completed_events=0)

                # 17. Transacciones restantes
                remaining_transactions = Transaction.objects.count()
                if remaining_transactions > 0:
                    Transaction.objects.all().delete()
                    deleted_counts["remaining_transactions"] = remaining_transactions

            total_deleted = sum(deleted_counts.values())
            self.stdout.write("=" * 60)
            self.stdout.write("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
            self.stdout.write("=" * 60 + "\n")
            self.stdout.write(f"  • Total de registros eliminados: {total_deleted}\n")

        except Exception as e:
            self.stderr.write(f"❌ ERROR durante la limpieza: {str(e)}")
            raise

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from bingo_app.models import (
    Game, Player, Transaction, Ticket, Raffle, ChatMessage, Message,
    CreditRequest, CreditRequestNotification, WithdrawalRequest,
    WithdrawalRequestNotification, PrintableCard, VideoCallGroup,
    BingoTicket, User
)


class Command(BaseCommand):
    help = 'Limpia los dashboards eliminando datos históricos pero conservando usuarios y configuraciones. Por defecto hace limpieza completa.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--completo',
            action='store_true',
            help='[Por defecto activo] Limpieza completa: elimina todos los juegos, transacciones, rifas, etc.',
        )
        parser.add_argument(
            '--reset-saldos',
            action='store_true',
            help='Resetea todos los saldos de usuarios a 0',
        )
        parser.add_argument(
            '--sin-confirmacion',
            action='store_true',
            help='Ejecuta sin pedir confirmación (peligroso)',
        )
        parser.add_argument(
            '--solo-vista-previa',
            action='store_true',
            help='Solo muestra qué se eliminaría sin ejecutar nada',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🧹 LIMPIEZA DE DASHBOARDS'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # Mostrar resumen de lo que se conservará
        self.stdout.write(self.style.WARNING('📋 DATOS QUE SE CONSERVARÁN:'))
        self.stdout.write('  ✅ Todos los usuarios registrados')
        self.stdout.write('  ✅ Configuraciones del sistema (comisiones, etc.)')
        self.stdout.write('  ✅ Métodos de pago (cuentas bancarias)')
        self.stdout.write('  ✅ Anuncios generales')
        self.stdout.write('  ✅ Promociones y referidos (configuración)')
        self.stdout.write('  ✅ Logros (configuración)')
        self.stdout.write('  ✅ Historial de bloqueos')
        self.stdout.write('')

        # Contar datos actuales
        self.stdout.write(self.style.WARNING('📊 DATOS ACTUALES:'))
        
        total_games = Game.objects.count()
        total_players = Player.objects.count()
        total_transactions = Transaction.objects.count()
        total_tickets = Ticket.objects.count()
        total_bingotickets = BingoTicket.objects.count()
        total_raffles = Raffle.objects.count()
        total_chatmessages = ChatMessage.objects.count()
        total_messages = Message.objects.count()
        total_credit_requests = CreditRequest.objects.count()
        total_withdrawal_requests = WithdrawalRequest.objects.count()
        total_printable_cards = PrintableCard.objects.count()
        total_videocall_groups = VideoCallGroup.objects.count()
        total_users = User.objects.count()
        
        # Calcular saldos totales
        total_balance = User.objects.aggregate(
            total_balance=Sum('credit_balance')
        )['total_balance'] or Decimal('0.00')
        
        total_blocked = User.objects.aggregate(
            total_blocked=Sum('blocked_credits')
        )['total_blocked'] or Decimal('0.00')

        self.stdout.write(f'  • Juegos: {total_games}')
        self.stdout.write(f'  • Jugadores en juegos: {total_players}')
        self.stdout.write(f'  • Transacciones: {total_transactions}')
        self.stdout.write(f'  • Tickets (Bingo clásico): {total_tickets}')
        self.stdout.write(f'  • BingoTickets (Bingo mejorado): {total_bingotickets}')
        self.stdout.write(f'  • Rifas: {total_raffles}')
        self.stdout.write(f'  • Mensajes de chat: {total_chatmessages}')
        self.stdout.write(f'  • Mensajes privados: {total_messages}')
        self.stdout.write(f'  • Solicitudes de crédito: {total_credit_requests}')
        self.stdout.write(f'  • Solicitudes de retiro: {total_withdrawal_requests}')
        self.stdout.write(f'  • Cartones imprimibles: {total_printable_cards}')
        self.stdout.write(f'  • Grupos de videollamada: {total_videocall_groups}')
        self.stdout.write(f'  • Usuarios: {total_users} ✅ (SE CONSERVAN)')
        self.stdout.write(f'  • Saldo total de usuarios: ${total_balance}')
        self.stdout.write(f'  • Saldo bloqueado total: ${total_blocked}')
        self.stdout.write('')

        # Mostrar lo que se eliminará
        self.stdout.write(self.style.ERROR('🗑️  DATOS QUE SE ELIMINARÁN:'))
        self.stdout.write(f'  ❌ {total_games} juegos')
        self.stdout.write(f'  ❌ {total_players} jugadores en juegos')
        self.stdout.write(f'  ❌ {total_transactions} transacciones')
        self.stdout.write(f'  ❌ {total_tickets} tickets (bingo clásico)')
        self.stdout.write(f'  ❌ {total_bingotickets} bingotickets')
        self.stdout.write(f'  ❌ {total_raffles} rifas')
        self.stdout.write(f'  ❌ {total_chatmessages} mensajes de chat')
        self.stdout.write(f'  ❌ {total_messages} mensajes privados')
        self.stdout.write(f'  ❌ {total_credit_requests} solicitudes de crédito')
        self.stdout.write(f'  ❌ {total_withdrawal_requests} solicitudes de retiro')
        self.stdout.write(f'  ❌ {total_printable_cards} cartones imprimibles')
        self.stdout.write(f'  ❌ {total_videocall_groups} grupos de videollamada')
        
        if options['reset_saldos']:
            self.stdout.write(f'  ⚠️  Saldos de usuarios se resetearán a 0')
            self.stdout.write(f'     (Total a resetear: ${total_balance + total_blocked})')
        
        self.stdout.write('')

        # Solo vista previa
        if options['solo_vista_previa']:
            self.stdout.write(self.style.WARNING('⚠️  MODO VISTA PREVIA - No se ejecutará ninguna acción'))
            return

        # Confirmación
        if not options['sin_confirmacion']:
            self.stdout.write(self.style.ERROR('⚠️  ADVERTENCIA: Esta acción es IRREVERSIBLE'))
            self.stdout.write('')
            confirm = input('¿Estás seguro de que quieres continuar? (escribe "SI" para confirmar): ')
            if confirm.upper() != 'SI':
                self.stdout.write(self.style.WARNING('❌ Operación cancelada.'))
                return

        # Ejecutar limpieza
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando limpieza...'))
        self.stdout.write('')

        try:
            with transaction.atomic():
                deleted_counts = {}
                
                # 1. Eliminar mensajes de chat (dependen de juegos)
                count = ChatMessage.objects.count()
                ChatMessage.objects.all().delete()
                deleted_counts['chatmessages'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} mensajes de chat'))

                # 2. Eliminar jugadores en juegos
                count = Player.objects.count()
                Player.objects.all().delete()
                deleted_counts['players'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} jugadores en juegos'))

                # 3. Eliminar tickets (bingo clásico)
                count = Ticket.objects.count()
                Ticket.objects.all().delete()
                deleted_counts['tickets'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} tickets (bingo clásico)'))

                # 4. Eliminar bingotickets (bingo mejorado)
                count = BingoTicket.objects.count()
                BingoTicket.objects.all().delete()
                deleted_counts['bingotickets'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} bingotickets'))

                # 5. Eliminar transacciones relacionadas con juegos/rifas
                # Primero las que tienen related_game (se eliminarán en cascada si el juego se elimina)
                # Pero las eliminamos manualmente para tener control
                transactions_with_game = Transaction.objects.filter(related_game__isnull=False).count()
                Transaction.objects.filter(related_game__isnull=False).delete()
                deleted_counts['transactions_with_game'] = transactions_with_game
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {transactions_with_game} transacciones relacionadas con juegos'))

                # 6. Eliminar transacciones de crédito/retiro
                credit_transactions = Transaction.objects.filter(
                    transaction_type__in=['WITHDRAWAL', 'WITHDRAWAL_REFUND']
                ).count()
                Transaction.objects.filter(
                    transaction_type__in=['WITHDRAWAL', 'WITHDRAWAL_REFUND']
                ).delete()
                deleted_counts['credit_transactions'] = credit_transactions
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {credit_transactions} transacciones de retiro'))

                # 7. Eliminar notificaciones de crédito
                count = CreditRequestNotification.objects.count()
                CreditRequestNotification.objects.all().delete()
                deleted_counts['credit_notifications'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {count} notificaciones de crédito'))

                # 8. Eliminar notificaciones de retiro
                count = WithdrawalRequestNotification.objects.count()
                WithdrawalRequestNotification.objects.all().delete()
                deleted_counts['withdrawal_notifications'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {count} notificaciones de retiro'))

                # 9. Eliminar solicitudes de crédito
                count = CreditRequest.objects.count()
                CreditRequest.objects.all().delete()
                deleted_counts['credit_requests'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {count} solicitudes de crédito'))

                # 10. Eliminar solicitudes de retiro
                count = WithdrawalRequest.objects.count()
                WithdrawalRequest.objects.all().delete()
                deleted_counts['withdrawal_requests'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {count} solicitudes de retiro'))

                # 11. Eliminar cartones imprimibles
                count = PrintableCard.objects.count()
                PrintableCard.objects.all().delete()
                deleted_counts['printable_cards'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} cartones imprimibles'))

                # 12. Eliminar grupos de videollamada
                count = VideoCallGroup.objects.count()
                VideoCallGroup.objects.all().delete()
                deleted_counts['videocall_groups'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} grupos de videollamada'))

                # 13. Eliminar mensajes privados
                count = Message.objects.count()
                Message.objects.all().delete()
                deleted_counts['messages'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} mensajes privados'))

                # 14. Eliminar rifas
                count = Raffle.objects.count()
                Raffle.objects.all().delete()
                deleted_counts['raffles'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {count} rifas'))

                # 15. Eliminar juegos (último porque otros dependen de él)
                count = Game.objects.count()
                Game.objects.all().delete()
                deleted_counts['games'] = count
                self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminados {count} juegos'))

                # 16. Si se solicita, resetear saldos
                if options['reset_saldos']:
                    users_updated = User.objects.filter(
                        Q(credit_balance__gt=0) | Q(blocked_credits__gt=0)
                    ).update(
                        credit_balance=Decimal('0.00'),
                        blocked_credits=Decimal('0.00')
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Saldos reseteados para {users_updated} usuarios'))
                    
                    # También resetear contador de eventos completados
                    User.objects.all().update(total_completed_events=0)
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Contador de eventos completados reseteado'))

                # 17. Eliminar transacciones restantes (las que no tienen related_game)
                # Eliminar todas las transacciones restantes excepto ADMIN_ADD (recargas administrativas)
                # si queremos conservarlas, o eliminar todo si limpiamos completamente
                remaining_transactions = Transaction.objects.count()
                if remaining_transactions > 0:
                    # Eliminar todas las transacciones restantes
                    Transaction.objects.all().delete()
                    deleted_counts['remaining_transactions'] = remaining_transactions
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminadas {remaining_transactions} transacciones restantes'))

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(self.style.SUCCESS('✅ LIMPIEZA COMPLETADA EXITOSAMENTE'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('📊 RESUMEN:'))
            total_deleted = sum(deleted_counts.values())
            self.stdout.write(f'  • Total de registros eliminados: {total_deleted}')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ Datos conservados:'))
            self.stdout.write(f'  • Usuarios: {User.objects.count()}')
            self.stdout.write('  • Configuraciones del sistema')
            self.stdout.write('  • Métodos de pago')
            self.stdout.write('  • Anuncios')
            self.stdout.write('  • Promociones y referidos')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ ERROR durante la limpieza: {str(e)}'))
            self.stdout.write(self.style.ERROR('Se revirtieron todos los cambios (rollback)'))
            raise

