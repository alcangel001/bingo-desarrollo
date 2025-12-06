from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verificar el estado de las migraciones y modelos'

    def handle(self, *args, **options):
        # Verificar si las tablas existen
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%bingo%'
                ORDER BY name;
            """)
            tables = cursor.fetchall()
            
            self.stdout.write("Tablas relacionadas con bingo:")
            for table in tables:
                self.stdout.write(f"  OK {table[0]}")
            
            # Verificar tablas específicas
            required_tables = [
                'bingo_app_bingoticket',
                'bingo_app_dailybingoschedule', 
                'bingo_app_bingoticketsettings'
            ]
            
            self.stdout.write("\nVerificando tablas requeridas:")
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                exists = cursor.fetchone()
                if exists:
                    self.stdout.write(f"  OK {table} - Existe")
                else:
                    self.stdout.write(f"  ERROR {table} - NO EXISTE")
            
            # Verificar migraciones aplicadas
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app='bingo_app' 
                ORDER BY name;
            """)
            migrations = cursor.fetchall()
            
            self.stdout.write("\nMigraciones aplicadas:")
            for migration in migrations:
                self.stdout.write(f"  OK {migration[0]}")
            
            # Verificar si la migración 0040 está aplicada
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app='bingo_app' AND name LIKE '%0040%';
            """)
            migration_0040 = cursor.fetchone()
            
            if migration_0040:
                self.stdout.write(f"\nOK Migración 0040 aplicada: {migration_0040[0]}")
            else:
                self.stdout.write("\nERROR Migración 0040 NO aplicada")
