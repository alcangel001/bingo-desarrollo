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
        # Usar atomic=False para evitar problemas de transacción
        with schema_editor.connection.cursor() as cursor:
            try:
                # Usar una transacción separada
                cursor.execute("COMMIT;")
                cursor.execute("BEGIN;")
                cursor.execute(
                    "ALTER TABLE bingo_app_user ALTER COLUMN card_theme DROP NOT NULL;"
                )
                cursor.execute("COMMIT;")
            except Exception as e:
                # Si la columna no existe o ya es nullable, ignorar
                try:
                    cursor.execute("ROLLBACK;")
                except:
                    pass
                # Continuar sin error
                pass
    # Para SQLite y otros motores, no hacer nada (ya son nullable por defecto)


def reverse_fix_card_theme_nullable(apps, schema_editor):
    """Reversa de la migración"""
    db_engine = schema_editor.connection.vendor
    
    if db_engine == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            try:
                cursor.execute("COMMIT;")
                cursor.execute("BEGIN;")
                cursor.execute(
                    "ALTER TABLE bingo_app_user ALTER COLUMN card_theme SET NOT NULL;"
                )
                cursor.execute("COMMIT;")
            except Exception:
                try:
                    cursor.execute("ROLLBACK;")
                except:
                    pass
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
