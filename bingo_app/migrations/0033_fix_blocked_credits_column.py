# Generated manually on 2025-10-13 - Fix missing blocked_credits column

from django.db import migrations


def add_blocked_credits_if_not_exists(apps, schema_editor):
    """
    Agrega la columna blocked_credits si no existe.
    Funciona tanto con SQLite como PostgreSQL.
    """
    db_engine = schema_editor.connection.vendor
    
    with schema_editor.connection.cursor() as cursor:
        columns = []
        
        if db_engine == 'sqlite':
            # Para SQLite
            cursor.execute("PRAGMA table_info(bingo_app_user)")
            columns = [row[1] for row in cursor.fetchall()]
        elif db_engine == 'postgresql':
            # Para PostgreSQL
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bingo_app_user' 
                AND table_schema = 'public';
            """)
            columns = [row[0] for row in cursor.fetchall()]
        
        if 'blocked_credits' not in columns:
            # La columna no existe, agregarla
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN blocked_credits DECIMAL(10, 2) DEFAULT 0.0 NOT NULL;
            """)
            print("Columna blocked_credits agregada exitosamente")
        else:
            print("Columna blocked_credits ya existe, no se hace nada")


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0032_videocallgroup_game'),
    ]

    operations = [
        migrations.RunPython(add_blocked_credits_if_not_exists, reverse_code=migrations.RunPython.noop),
    ]

