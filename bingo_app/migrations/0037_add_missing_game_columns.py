# Generated manually on 2025-10-15 - Add missing Game columns

from django.db import migrations


def add_missing_game_columns(apps, schema_editor):
    """
    Agrega las columnas faltantes del modelo Game.
    Funciona tanto con SQLite como PostgreSQL.
    """
    db_engine = schema_editor.connection.vendor
    
    with schema_editor.connection.cursor() as cursor:
        game_columns = []
        
        if db_engine == 'sqlite':
            # Para SQLite
            cursor.execute("PRAGMA table_info(bingo_app_game)")
            game_columns = [row[1] for row in cursor.fetchall()]
        elif db_engine == 'postgresql':
            # Para PostgreSQL
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bingo_app_game' 
                AND table_schema = 'public';
            """)
            game_columns = [row[0] for row in cursor.fetchall()]
        
        # 1. held_balance en Game
        if 'held_balance' not in game_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_game 
                ADD COLUMN held_balance DECIMAL(10, 2) DEFAULT 0.0 NOT NULL;
            """)
            print("Columna held_balance agregada a bingo_app_game")
        
        print("Todas las columnas de Game verificadas/agregadas")


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0036_add_missing_blocked_columns'),
    ]

    operations = [
        migrations.RunPython(add_missing_game_columns, reverse_code=migrations.RunPython.noop),
    ]
