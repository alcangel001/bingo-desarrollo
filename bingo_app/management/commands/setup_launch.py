from django.core.management.base import BaseCommand
from bingo_app.models import LaunchPromotion, LaunchAchievement
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Configurar promociones y logros de lanzamiento'

    def handle(self, *args, **options):
        self.stdout.write('Configurando promociones de lanzamiento...')
        
        # Crear promociones de lanzamiento
        promotions = [
            {
                'name': 'Bono de Bienvenida',
                'promotion_type': 'WELCOME_BONUS',
                'description': '¡Bienvenido a Bingo y Rifa JyM! Recibe créditos gratis para empezar a jugar.',
                'bonus_amount': 10.00,
                'max_uses': 1000,
            },
            {
                'name': 'Bono Primer Depósito',
                'promotion_type': 'FIRST_DEPOSIT',
                'description': 'Deposita por primera vez y recibe un 50% extra en créditos.',
                'bonus_amount': 0,  # Se calculará como 50% del depósito
                'min_deposit': 20.00,
                'max_bonus': 50.00,
                'max_uses': 500,
            },
            {
                'name': 'Promoción de Lanzamiento',
                'promotion_type': 'LAUNCH_SPECIAL',
                'description': 'Promoción especial solo por el lanzamiento. ¡No te la pierdas!',
                'bonus_amount': 15.00,
                'end_date': timezone.now() + timedelta(days=30),
                'max_uses': 200,
            },
        ]
        
        for promo_data in promotions:
            promotion, created = LaunchPromotion.objects.get_or_create(
                name=promo_data['name'],
                defaults=promo_data
            )
            if created:
                self.stdout.write(f'Promocion creada: {promotion.name}')
            else:
                self.stdout.write(f'Promocion ya existe: {promotion.name}')
        
        # Crear logros de lanzamiento
        achievements = [
            {
                'name': 'Pionero',
                'achievement_type': 'PIONEER',
                'description': 'Eres uno de los primeros 100 usuarios en registrarse.',
                'icon': 'fas fa-star',
                'bonus_credits': 5.00,
                'max_recipients': 100,
            },
            {
                'name': 'Fundador',
                'achievement_type': 'FOUNDER',
                'description': 'Te registraste el primer día del lanzamiento.',
                'icon': 'fas fa-crown',
                'bonus_credits': 10.00,
                'max_recipients': 50,
            },
            {
                'name': 'Campeón Inaugural',
                'achievement_type': 'CHAMPION',
                'description': 'Ganaste el primer torneo oficial.',
                'icon': 'fas fa-trophy',
                'bonus_credits': 25.00,
                'max_recipients': 1,
            },
            {
                'name': 'Madrugador',
                'achievement_type': 'EARLY_BIRD',
                'description': 'Fuiste uno de los primeros 10 usuarios en registrarse.',
                'icon': 'fas fa-sun',
                'bonus_credits': 15.00,
                'max_recipients': 10,
            },
            {
                'name': 'Mariposa Social',
                'achievement_type': 'SOCIAL_BUTTERFLY',
                'description': 'Invitaste a 5 amigos a la plataforma.',
                'icon': 'fas fa-users',
                'bonus_credits': 20.00,
                'max_recipients': None,  # Sin límite
            },
        ]
        
        for achievement_data in achievements:
            achievement, created = LaunchAchievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                self.stdout.write(f'Logro creado: {achievement.name}')
            else:
                self.stdout.write(f'Logro ya existe: {achievement.name}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Configuración de lanzamiento completada!')
        )
