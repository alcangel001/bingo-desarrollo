from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix missing database columns'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("🔧 Verificando y arreglando esquema de base de datos...")
            
            # Lista de columnas a verificar/agregar
            columns_to_add = [
                ('blocked_credits', 'DECIMAL(10, 2) DEFAULT 0.0 NOT NULL'),
                ('total_completed_events', 'INTEGER DEFAULT 0 NOT NULL'),
                ('reputation_score', 'INTEGER DEFAULT 0 NOT NULL'),
                ('manual_reputation', 'VARCHAR(10) DEFAULT \'AUTO\' NOT NULL'),
            ]
            
            for column_name, column_def in columns_to_add:
                # Verificar si la columna existe
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='bingo_app_user' 
                    AND column_name=%s;
                """, [column_name])
                
                if not cursor.fetchone():
                    # La columna no existe, agregarla
                    try:
                        cursor.execute(f"""
                            ALTER TABLE bingo_app_user 
                            ADD COLUMN {column_name} {column_def};
                        """)
                        self.stdout.write(self.style.SUCCESS(f'✅ Columna {column_name} agregada'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Error agregando {column_name}: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'ℹ️  Columna {column_name} ya existe'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Esquema de base de datos verificado/arreglado'))

