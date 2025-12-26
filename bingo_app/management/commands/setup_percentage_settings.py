from django.core.management.base import BaseCommand
from bingo_app.models import PercentageSettings


class Command(BaseCommand):
    help = 'Crea o actualiza PercentageSettings si no existe'

    def handle(self, *args, **options):
        settings, created = PercentageSettings.objects.get_or_create(
            pk=1,
            defaults={
                'platform_commission': 10.00,
                'game_creation_fee': 1.00,
                'image_promotion_price': 10.00,
                'video_promotion_price': 15.00,
                'referral_system_enabled': True,
                'promotions_enabled': True,
                'credits_purchase_enabled': True,
                'credits_withdrawal_enabled': True,
                'accounts_receivable_enabled': True,  # Habilitar cuentas por cobrar
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ PercentageSettings creado exitosamente'))
        else:
            # Asegurar que accounts_receivable_enabled esté habilitado
            if not settings.accounts_receivable_enabled:
                settings.accounts_receivable_enabled = True
                settings.save()
                self.stdout.write(self.style.SUCCESS('✅ accounts_receivable_enabled habilitado'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ PercentageSettings ya existe y está configurado'))




