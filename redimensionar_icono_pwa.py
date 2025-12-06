#!/usr/bin/env python3
"""
Script para redimensionar imagen original a todos los tamaños de iconos PWA
"""
try:
    from PIL import Image
    import os
except ImportError:
    print("Error: Necesitas instalar Pillow")
    print("Ejecuta: pip install Pillow")
    exit(1)

# Tamaños de iconos necesarios
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Directorio de imágenes
IMAGES_DIR = "bingo_app/static/images"

# Nombre del archivo original (sin extensión)
ORIGINAL_NAME = "icono-original-2"

def find_image_file(base_name):
    """Busca el archivo de imagen con diferentes extensiones"""
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        file_path = os.path.join(IMAGES_DIR, base_name + ext)
        if os.path.exists(file_path):
            return file_path
    return None

def resize_image(input_path, output_path, size):
    """Redimensiona una imagen al tamaño especificado manteniendo aspecto cuadrado"""
    try:
        # Abrir imagen original
        img = Image.open(input_path)
        
        # Convertir a RGB si es necesario (para JPG)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar manteniendo aspecto (crop centrado si no es cuadrado)
        if img.width != img.height:
            # Si no es cuadrado, hacer crop centrado
            size_min = min(img.width, img.height)
            left = (img.width - size_min) // 2
            top = (img.height - size_min) // 2
            img = img.crop((left, top, left + size_min, top + size_min))
        
        # Redimensionar al tamaño requerido
        img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Guardar
        img_resized.save(output_path, "PNG", optimize=True)
        return True
    except Exception as e:
        print(f"Error redimensionando a {size}x{size}: {e}")
        return False

def main():
    print("=" * 70)
    print("REDIMENSIONANDO ICONO PARA PWA".center(70))
    print("=" * 70)
    print()
    
    # Buscar el archivo original
    original_path = find_image_file(ORIGINAL_NAME)
    
    if not original_path:
        print(f"ERROR: No se encontro la imagen '{ORIGINAL_NAME}'")
        print(f"Buscando en: {IMAGES_DIR}")
        print()
        print("Archivos encontrados en la carpeta:")
        if os.path.exists(IMAGES_DIR):
            files = os.listdir(IMAGES_DIR)
            for f in files:
                if 'icono' in f.lower():
                    print(f"  - {f}")
        exit(1)
    
    print(f"Imagen original encontrada: {original_path}")
    
    # Verificar tamaño de la imagen
    try:
        img = Image.open(original_path)
        print(f"Tamaño original: {img.width}x{img.height} píxeles")
        print(f"Formato: {img.format}")
        print()
    except Exception as e:
        print(f"Error abriendo imagen: {e}")
        exit(1)
    
    # Crear todos los tamaños
    print("Redimensionando a todos los tamaños necesarios...")
    print()
    
    success_count = 0
    for size in SIZES:
        output_filename = f"icon-{size}x{size}.png"
        output_path = os.path.join(IMAGES_DIR, output_filename)
        
        if resize_image(original_path, output_path, size):
            print(f"[OK] Creado: {output_filename} ({size}x{size})")
            success_count += 1
        else:
            print(f"[ERROR] No se pudo crear: {output_filename}")
    
    print()
    print("=" * 70)
    if success_count == len(SIZES):
        print("¡Iconos redimensionados exitosamente!")
        print(f"Se crearon {success_count} iconos en diferentes tamaños.")
        print()
        print("Próximo paso: Hacer commit y push para subir los cambios.")
    else:
        print(f"Advertencia: Solo se crearon {success_count} de {len(SIZES)} iconos.")
    print("=" * 70)

if __name__ == "__main__":
    main()






