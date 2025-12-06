#!/usr/bin/env python
"""
Script para crear una copia de restauración completa del sistema Bingo
"""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def crear_backup_completo():
    """Crea un backup completo del sistema"""
    
    # Obtener fecha y hora actual
    fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    fecha_formato = datetime.now().strftime('%d-%m-%Y')
    
    # Nombre del backup
    nombre_backup = f"backup_restauracion_bingo_{fecha_hora}"
    directorio_backups = Path("backups")
    directorio_backups.mkdir(exist_ok=True)
    
    # Ruta completa del backup
    ruta_backup_zip = directorio_backups / f"{nombre_backup}.zip"
    ruta_backup_db = directorio_backups / f"db_{fecha_hora}.sqlite3"
    
    print(f"[*] Creando copia de restauracion: {nombre_backup}")
    print(f"[*] Fecha: {fecha_formato}")
    print("-" * 60)
    
    # 1. Copiar base de datos SQLite
    db_original = Path("db.sqlite3")
    if db_original.exists():
        print(f"[OK] Copiando base de datos...")
        shutil.copy2(db_original, ruta_backup_db)
        print(f"     Guardado: {ruta_backup_db}")
    else:
        print(f"[!] No se encontro db.sqlite3")
    
    # 2. Crear archivo ZIP con archivos importantes
    print(f"\n[*] Creando archivo ZIP con archivos criticos...")
    
    archivos_importantes = [
        # Configuración
        "requirements.txt",
        "Procfile",
        "entrypoint.sh",
        "manage.py",
        ".env",  # Si existe
        
        # Aplicación principal
        "bingo_app/",
        "bingo_project/",
        
        # Scripts de gestión
        "gestionar_sistemas.py",
        "gestionar_promociones_referidos.py",
        "ver_estado_sistemas.py",
        "activar_sistema_tickets.py",
        "desactivar_sistema_tickets.py",
        "check_launch_readiness.py",
        "verificar_railway.py",
        
        # Documentación
        "*.md",
    ]
    
    with zipfile.ZipFile(ruta_backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Agregar base de datos al ZIP
        if ruta_backup_db.exists():
            zipf.write(ruta_backup_db, f"db_{fecha_hora}.sqlite3")
            print(f"     [OK] Base de datos agregada al ZIP")
        
        # Agregar archivos y directorios
        for item in archivos_importantes:
            path_item = Path(item)
            
            if path_item.is_file() and path_item.exists():
                zipf.write(path_item, path_item)
                print(f"     [OK] {item}")
            
            elif path_item.is_dir() and path_item.exists():
                # Agregar directorio completo
                for root, dirs, files in os.walk(path_item):
                    # Excluir directorios innecesarios
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', '.venv']]
                    
                    for file in files:
                        if not file.endswith(('.pyc', '.pyo', '.log')):
                            file_path = Path(root) / file
                            arcname = file_path
                            zipf.write(file_path, arcname)
                print(f"     [OK] {item}/ (directorio completo)")
            
            elif '*' in item:
                # Buscar archivos con patrón
                if item == "*.md":
                    for md_file in Path('.').glob('*.md'):
                        zipf.write(md_file, md_file)
                        print(f"     [OK] {md_file}")
    
    # Obtener tamaño del archivo
    tamaño_mb = ruta_backup_zip.stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print(f"[OK] BACKUP COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"Archivo ZIP: {ruta_backup_zip}")
    print(f"Tamanio: {tamaño_mb:.2f} MB")
    print(f"Base de datos: {ruta_backup_db}")
    print(f"Fecha: {fecha_formato}")
    print("\nPara restaurar:")
    print(f"  1. Descomprimir: {ruta_backup_zip}")
    print(f"  2. Copiar db_{fecha_hora}.sqlite3 a db.sqlite3")
    print(f"  3. Ejecutar: python manage.py migrate")
    print("=" * 60)

if __name__ == "__main__":
    try:
        crear_backup_completo()
    except Exception as e:
        print(f"\n[ERROR] Error al crear backup: {e}")
        import traceback
        traceback.print_exc()

