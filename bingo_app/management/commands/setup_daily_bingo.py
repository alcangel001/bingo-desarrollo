from django.core.management.base import BaseCommand
from bingo_app.models import DailyBingoSchedule, BingoTicketSettings


class Command(BaseCommand):
    help = 'Configura los horarios de bingo diario por defecto'

    def handle(self, *args, **options):
        # Crear configuración de tickets si no existe
        ticket_settings, created = BingoTicketSettings.objects.get_or_create(
            pk=1,
            defaults={
                'is_system_active': False,  # Por defecto desactivado
                'referral_ticket_bonus': 1,
                'referred_ticket_bonus': 1,
                'ticket_expiration_days': 7,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Configuración de tickets creada')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Configuración de tickets ya existe')
            )

        # Crear horarios de bingo diario
        schedules_data = [
            {
                'time_slot': '09:00',
                'is_active': True,
                'max_players': 50,
                'prize_amount': 10.00,
                'description': 'Bingo matutino gratuito'
            },
            {
                'time_slot': '14:00',
                'is_active': True,
                'max_players': 50,
                'prize_amount': 10.00,
                'description': 'Bingo vespertino gratuito'
            },
            {
                'time_slot': '19:00',
                'is_active': True,
                'max_players': 50,
                'prize_amount': 10.00,
                'description': 'Bingo nocturno gratuito'
            }
        ]

        for schedule_data in schedules_data:
            schedule, created = DailyBingoSchedule.objects.get_or_create(
                time_slot=schedule_data['time_slot'],
                defaults=schedule_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Horario {schedule.get_time_slot_display()} creado')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Horario {schedule.get_time_slot_display()} ya existe')
                )

        self.stdout.write(
            self.style.SUCCESS('Configuración de bingo diario completada')
        )
