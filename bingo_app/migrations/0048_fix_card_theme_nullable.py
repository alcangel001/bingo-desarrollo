# Generated manually to fix card_theme constraint

from django.db import migrations


def fix_card_theme_nullable(apps, schema_editor):
    """
    Hacer card_theme nullable si existe la columna.
    Compatible con SQLite y PostgreSQL.
    Esta migración es principalmente para PostgreSQL.
    En SQLite, las columnas son nullable por defecto.
    """
    db_engine = schema_editor.connection.vendor
    
    if db_engine == 'postgresql':
        # PostgreSQL soporta ALTER COLUMN
        # Usar schema_editor para manejar transacciones correctamente
        try:
            # Verificar si la columna existe y tiene NOT NULL
            with schema_editor.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'bingo_app_user' 
                    AND column_name = 'card_theme';
                """)
                result = cursor.fetchone()
                
                if result and result[0] == 'NO':
                    # La columna existe y es NOT NULL, hacerla nullable
                    schema_editor.execute("""
                        ALTER TABLE bingo_app_user 
                        ALTER COLUMN card_theme DROP NOT NULL;
                    """)
        except Exception:
            # Si la columna no existe o ya es nullable, ignorar silenciosamente
            pass
    # Para SQLite y otros motores, no hacer nada (ya son nullable por defecto)


def reverse_fix_card_theme_nullable(apps, schema_editor):
    """Reversa de la migración"""
    db_engine = schema_editor.connection.vendor
    
    if db_engine == 'postgresql':
        try:
            schema_editor.execute("""
                ALTER TABLE bingo_app_user 
                ALTER COLUMN card_theme SET NOT NULL;
            """)
        except Exception:
            pass


class Migration(migrations.Migration):
    # Marcar como no atómica para evitar problemas de transacción
    atomic = False

    dependencies = [
        ('bingo_app', '0047_videocallgroup_active_users_and_more'),
    ]

    operations = [
        migrations.RunPython(
            fix_card_theme_nullable,
            reverse_fix_card_theme_nullable,
            atomic=False,  # No usar transacción atómica
        ),
    ]
