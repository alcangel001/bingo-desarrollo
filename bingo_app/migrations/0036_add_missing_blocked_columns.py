# Generated manually on 2025-10-15 - Add missing blocked user columns

from django.db import migrations


def add_blocked_user_columns(apps, schema_editor):
    """
    Agrega las columnas faltantes relacionadas con el bloqueo de usuarios.
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
        
        # 1. is_blocked
        if 'is_blocked' not in existing_columns:
            if db_engine == 'sqlite':
                cursor.execute("""
                    ALTER TABLE bingo_app_user 
                    ADD COLUMN is_blocked BOOLEAN DEFAULT 0 NOT NULL;
                """)
            else:  # PostgreSQL
                cursor.execute("""
                    ALTER TABLE bingo_app_user 
                    ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE NOT NULL;
                """)
            print("Columna is_blocked agregada")
        
        # 2. block_reason
        if 'block_reason' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN block_reason TEXT DEFAULT '' NOT NULL;
            """)
            print("Columna block_reason agregada")
        
        # 3. blocked_until
        if 'blocked_until' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN blocked_until TIMESTAMP NULL;
            """)
            print("Columna blocked_until agregada")
        
        # 4. blocked_at
        if 'blocked_at' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN blocked_at TIMESTAMP NULL;
            """)
            print("Columna blocked_at agregada")
        
        # 5. blocked_by_id
        if 'blocked_by_id' not in existing_columns:
            cursor.execute("""
                ALTER TABLE bingo_app_user 
                ADD COLUMN blocked_by_id INTEGER NULL REFERENCES bingo_app_user(id);
            """)
            print("Columna blocked_by_id agregada")
        
        print("Todas las columnas de bloqueo verificadas/agregadas")


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0035_percentagesettings_game_creation_fee_and_more'),
    ]

    operations = [
        migrations.RunPython(add_blocked_user_columns, reverse_code=migrations.RunPython.noop),
    ]
