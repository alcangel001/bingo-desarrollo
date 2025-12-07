from django.core.management.base import BaseCommand
from bingo_app.models import PackageTemplate


class Command(BaseCommand):
    help = 'Crea las plantillas preconfiguradas de paquetes para franquicias'

    def handle(self, *args, **options):
        templates = [
            {
                'package_type': 'BASIC_BINGO',
                'name': 'Básico Bingo',
                'description': 'Paquete básico para organizadores que solo quieren bingos',
                'default_monthly_price': 30.00,
                'default_commission_rate': 5.00,
                'bingos_enabled': True,
                'custom_manual_enabled': True,
            },
            {
                'package_type': 'PRO_BINGO',
                'name': 'PRO Bingo',
                'description': 'Paquete completo para organizadores que quieren bingos + todo',
                'default_monthly_price': 80.00,
                'default_commission_rate': 3.00,
                'bingos_enabled': True,
                'raffles_enabled': True,
                'accounts_receivable_enabled': True,
                'video_calls_bingos_enabled': True,
                'video_calls_raffles_enabled': True,
                'custom_manual_enabled': True,
                'notifications_push_enabled': True,
                'advanced_reports_enabled': True,
                'advanced_promotions_enabled': True,
                'banners_enabled': True,
            },
            {
                'package_type': 'BASIC_RAFFLE',
                'name': 'Básico Rifa',
                'description': 'Paquete básico para organizadores que solo quieren rifas',
                'default_monthly_price': 30.00,
                'default_commission_rate': 5.00,
                'raffles_enabled': True,
                'custom_manual_enabled': True,
            },
            {
                'package_type': 'PRO_RAFFLE',
                'name': 'PRO Rifa',
                'description': 'Paquete completo para organizadores que quieren rifas + todo',
                'default_monthly_price': 80.00,
                'default_commission_rate': 3.00,
                'bingos_enabled': True,
                'raffles_enabled': True,
                'accounts_receivable_enabled': True,
                'video_calls_bingos_enabled': True,
                'video_calls_raffles_enabled': True,
                'custom_manual_enabled': True,
                'notifications_push_enabled': True,
                'advanced_reports_enabled': True,
                'advanced_promotions_enabled': True,
                'banners_enabled': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = PackageTemplate.objects.get_or_create(
                package_type=template_data['package_type'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Creada plantilla: {template.name}')
                )
            else:
                # Actualizar solo los campos que pueden cambiar (precios)
                template.current_monthly_price = template_data['default_monthly_price']
                template.current_commission_rate = template_data['default_commission_rate']
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[INFO] Plantilla ya existe: {template.name} (precios actualizados)')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Proceso completado: {created_count} plantillas creadas, {updated_count} actualizadas'
            )
        )

