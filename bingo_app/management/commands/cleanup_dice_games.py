"""
Comando de limpieza de emergencia para partidas de dados.
Ejecutar: python manage.py cleanup_dice_games
"""

from django.core.management.base import BaseCommand
from bingo_app.tasks import emergency_cleanup_dice_games


class Command(BaseCommand):
    help = 'Limpia partidas fantasma de dados y entradas obsoletas de matchmaking'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🧹 Iniciando limpieza de emergencia...'))
        
        result = emergency_cleanup_dice_games()
        
        if result:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Limpieza completada:\n'
                    f'   - Partidas limpiadas: {result["games_cleaned"]}\n'
                    f'   - Entradas de cola limpiadas: {result["queue_entries_cleaned"]}\n'
                    f'   - Total reembolsado: ${result["total_refunded"]:.2f}'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('✅ No se encontraron partidas o entradas para limpiar'))

