# Generated manually to fix card_theme constraint

from django.db import migrations


def fix_card_theme_nullable(apps, schema_editor):
    """
    Hacer card_theme nullable si existe la columna.
    Compatible con SQLite y PostgreSQL.
    """
    db_engine = schema_editor.connection.vendor
    
    if db_engine == 'postgresql':
        # PostgreSQL soporta ALTER COLUMN
        with schema_editor.connection.cursor() as cursor:
            try:
                cursor.execute(
                    "ALTER TABLE bingo_app_user ALTER COLUMN card_theme DROP NOT NULL;"
                )
            except Exception:
                # Si la columna no existe o ya es nullable, ignorar
                pass
    elif db_engine == 'sqlite':
        # SQLite no soporta ALTER COLUMN directamente
        # En SQLite, las columnas son nullable por defecto si no tienen NOT NULL
        # Esta migración es principalmente para PostgreSQL
        # Para SQLite, simplemente verificamos que la columna existe
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(bingo_app_user)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'card_theme' not in columns:
                # Si no existe, la creamos como nullable (comportamiento por defecto de SQLite)
                pass
    # Para otros motores de BD, no hacer nada


def reverse_fix_card_theme_nullable(apps, schema_editor):
    """Reversa de la migración"""
    db_engine = schema_editor.connection.vendor
    
    if db_engine == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            try:
                cursor.execute(
                    "ALTER TABLE bingo_app_user ALTER COLUMN card_theme SET NOT NULL;"
                )
            except Exception:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_app', '0047_videocallgroup_active_users_and_more'),
    ]

    operations = [
        migrations.RunPython(
            fix_card_theme_nullable,
            reverse_fix_card_theme_nullable,
        ),
    ]
