# Generated manually on 2025-10-13 - Fix all missing User columns

from django.db import migrations


def add_missing_user_columns(apps, schema_editor):
    """
    Agrega todas las columnas faltantes del modelo User de forma segura.
    Funciona tanto con SQLite como PostgreSQL.
    """
    db_engine = schema_editor.connection.vendor
    
    with schema_editor.connection.cursor() as cursor:
        existing_columns = []
        
        if db_engine == 'sqlite':
            # Para SQLite
            cursor.execute("PRAGMA table_info(bingo_app_user)")
            existing_columns = [row[1] for row in cursor.fetchall()]
        elif db_engine == 'postgresql':
            # Para PostgreSQL
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bingo_app_user' 
                AND table_schema = 'public';
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
        
        # 1. total_completed_events (de migración 0020)
        if 'total_completed_events' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN total_completed_events INTEGER DEFAULT 0 NOT NULL;
            """)
            print("Columna total_completed_events agregada")
        
        # 2. reputation_score (de migración 0020, eliminada en 0022/0023)
        if 'reputation_score' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN reputation_score INTEGER DEFAULT 0 NOT NULL;
            """)
            print("Columna reputation_score agregada")
        
        # 3. manual_reputation (de migración 0022)
        if 'manual_reputation' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN manual_reputation VARCHAR(10) DEFAULT 'AUTO' NOT NULL;
            """)
            print("Columna manual_reputation agregada")
        
        print("Todas las columnas faltantes verificadas/agregadas")


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0033_fix_blocked_credits_column'),
    ]

    operations = [
        migrations.RunPython(add_missing_user_columns, reverse_code=migrations.RunPython.noop),
    ]

