# Generated manually on 2025-10-15 - Add held_balance to Raffle

from django.db import migrations


def add_raffle_held_balance(apps, schema_editor):
    """
    Agrega la columna held_balance al modelo Raffle.
    Funciona tanto con SQLite como PostgreSQL.
    """
    db_engine = schema_editor.connection.vendor
    
    with schema_editor.connection.cursor() as cursor:
        raffle_columns = []
        
        if db_engine == 'sqlite':
            # Para SQLite
            cursor.execute("PRAGMA table_info(bingo_app_raffle)")
            raffle_columns = [row[1] for row in cursor.fetchall()]
        elif db_engine == 'postgresql':
            # Para PostgreSQL
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bingo_app_raffle' 
                AND table_schema = 'public';
            """)
            raffle_columns = [row[0] for row in cursor.fetchall()]
        
        # held_balance en Raffle
        if 'held_balance' not in raffle_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_raffle 
                ADD COLUMN held_balance DECIMAL(10, 2) DEFAULT 0.0 NOT NULL;
            """)
            print("Columna held_balance agregada a bingo_app_raffle")
        else:
            print("Columna held_balance ya existe en bingo_app_raffle")


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0037_add_missing_game_columns'),
    ]

    operations = [
        migrations.RunPython(add_raffle_held_balance, reverse_code=migrations.RunPython.noop),
    ]
