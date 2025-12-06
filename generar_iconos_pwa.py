#!/usr/bin/env python3
"""
Script para generar iconos de la PWA
Requiere: pip install Pillow
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Error: Necesitas instalar Pillow")
    print("Ejecuta: pip install Pillow")
    exit(1)

# Colores del tema
BACKGROUND_COLOR = (22, 31, 44)  # #161f2c
PRIMARY_COLOR = (44, 62, 80)  # #2C3E50
ACCENT_COLOR = (231, 76, 60)  # #E74C3C
TEXT_COLOR = (236, 240, 241)  # #ECF0F1

# Tamaños de iconos necesarios
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Directorio de salida
OUTPUT_DIR = "bingo_app/static/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_icon(size):
    """Crea un icono estilo Imagen 2 - BINGO y RIFA JyM con fondo naranja"""
    # Crear imagen con fondo naranja degradado (como la Imagen 2)
    img = Image.new('RGB', (size, size), (255, 140, 0))  # Naranja base
    draw = ImageDraw.Draw(img)
    
    # Crear degradado radial naranja (más oscuro en bordes, más brillante en centro)
    center = size // 2
    max_radius = int(size * 0.8)
    for i in range(max_radius):
        ratio = i / max_radius
        # Interpolar entre naranja oscuro (220, 100, 0) y naranja brillante (255, 180, 50)
        r = int(220 + (255 - 220) * (1 - ratio))
        g = int(100 + (180 - 100) * (1 - ratio))
        b = int(0 + (50 - 0) * (1 - ratio))
        color = (r, g, b)
        draw.ellipse(
            [center - max_radius + i, center - max_radius + i, 
             center + max_radius - i, center + max_radius - i],
            outline=color,
            width=3
        )
    
    # Agregar estrellas pequeñas decorativas (solo en tamaños grandes)
    if size >= 192:
        import random
        random.seed(42)  # Para que sean consistentes
        for _ in range(10):
            x = random.randint(size // 10, size - size // 10)
            y = random.randint(size // 10, size - size // 10)
            # Dibujar estrella pequeña blanca
            star_size = size // 50
            points = []
            for i in range(5):
                angle = (i * 144 - 90) * 3.14159 / 180
                px = x + star_size * 0.5 * (1 if i % 2 == 0 else 0.3) * (1 if i < 2 else -1) * (1 if i % 4 < 2 else -1)
                py = y + star_size * 0.5 * (1 if i % 2 == 0 else 0.3) * (1 if i % 4 < 2 else -1) * (1 if i < 2 else -1)
                points.extend([int(px), int(py)])
            if len(points) >= 6:
                draw.polygon(points[:6], fill=(255, 255, 255, 200), outline=None)
    
    # Dibujar bingo balls pequeñas (solo en tamaños medianos/grandes)
    if size >= 128:
        ball_size = size // 7
        # Bola roja con "7" arriba-izquierda
        ball1_x = size // 6
        ball1_y = size // 6
        draw.ellipse(
            [ball1_x, ball1_y, ball1_x + ball_size, ball1_y + ball_size],
            fill=(255, 0, 0),  # Rojo
            outline=(200, 0, 0),
            width=2
        )
        if size >= 192:
            try:
                ball_font = ImageFont.truetype("arial.ttf", ball_size // 3)
                draw.text((ball1_x + ball_size // 3, ball1_y + ball_size // 3), 
                         "7", fill=(255, 255, 255), font=ball_font)
            except:
                pass
        
        # Bola verde con "17" abajo-izquierda
        ball2_x = size // 6
        ball2_y = size - size // 6 - ball_size
        draw.ellipse(
            [ball2_x, ball2_y, ball2_x + ball_size, ball2_y + ball_size],
            fill=(50, 200, 50),  # Verde
            outline=(30, 150, 30),
            width=2
        )
        if size >= 192:
            try:
                draw.text((ball2_x + ball_size // 3, ball2_y + ball_size // 3), 
                         "17", fill=(255, 255, 255), font=ball_font)
            except:
                pass
        
        # Bola naranja con "29" abajo-izquierda (más abajo)
        ball3_x = size // 6
        ball3_y = size - size // 4 - ball_size
        draw.ellipse(
            [ball3_x, ball3_y, ball3_x + ball_size, ball3_y + ball_size],
            fill=(255, 140, 0),  # Naranja
            outline=(220, 100, 0),
            width=2
        )
        if size >= 192:
            try:
                draw.text((ball3_x + ball_size // 3, ball3_y + ball_size // 3), 
                         "29", fill=(255, 255, 255), font=ball_font)
            except:
                pass
    
    # Dibujar texto "BINGO" arriba (dorado, grande)
    try:
        font_size_bingo = max(16, int(size * 0.25))
        font_bingo = ImageFont.truetype("arial.ttf", font_size_bingo)
    except:
        font_bingo = ImageFont.load_default()
    
    text_bingo = "BINGO"
    if font_bingo:
        bbox_bingo = draw.textbbox((0, 0), text_bingo, font=font_bingo)
        text_width_bingo = bbox_bingo[2] - bbox_bingo[0]
        text_height_bingo = bbox_bingo[3] - bbox_bingo[1]
        x_bingo = (size - text_width_bingo) // 2
        y_bingo = size // 5 - text_height_bingo // 2
        
        gold_color = (255, 215, 0)  # Dorado
        dark_outline = (180, 100, 0)  # Marrón oscuro para contorno
        
        # Dibujar contorno
        outline_width = max(3, size // 100)
        for adj in range(-outline_width, outline_width + 1):
            for adj2 in range(-outline_width, outline_width + 1):
                if abs(adj) + abs(adj2) <= outline_width:
                    draw.text((x_bingo + adj, y_bingo + adj2), text_bingo, 
                             fill=dark_outline, font=font_bingo)
        # Dibujar texto principal
        draw.text((x_bingo, y_bingo), text_bingo, fill=gold_color, font=font_bingo)
    
    # Dibujar "y RIFA" en el medio (dorado, mediano)
    try:
        font_size_rifa = max(12, int(size * 0.15))
        font_rifa = ImageFont.truetype("arial.ttf", font_size_rifa)
    except:
        font_rifa = ImageFont.load_default()
    
    text_rifa = "y RIFA"
    if font_rifa:
        bbox_rifa = draw.textbbox((0, 0), text_rifa, font=font_rifa)
        text_width_rifa = bbox_rifa[2] - bbox_rifa[0]
        text_height_rifa = bbox_rifa[3] - bbox_rifa[1]
        x_rifa = (size - text_width_rifa) // 2
        y_rifa = size // 2.5 - text_height_rifa // 2
        
        # Dibujar contorno
        for adj in range(-2, 3):
            for adj2 in range(-2, 3):
                draw.text((x_rifa + adj, y_rifa + adj2), text_rifa, 
                         fill=dark_outline, font=font_rifa)
        # Dibujar texto principal
        draw.text((x_rifa, y_rifa), text_rifa, fill=gold_color, font=font_rifa)
    
    # Dibujar "JyM" abajo (turquesa/azul, como en la Imagen 2)
    try:
        font_size_jym = max(20, int(size * 0.3))
        font_jym = ImageFont.truetype("arial.ttf", font_size_jym)
    except:
        font_jym = ImageFont.load_default()
    
    text_jym = "JyM"
    if font_jym:
        bbox_jym = draw.textbbox((0, 0), text_jym, font=font_jym)
        text_width_jym = bbox_jym[2] - bbox_jym[0]
        text_height_jym = bbox_jym[3] - bbox_jym[1]
        x_jym = (size - text_width_jym) // 2
        y_jym = size // 1.6 - text_height_jym // 2
        
        turquoise_color = (64, 224, 208)  # Turquesa/azul claro
        dark_blue_outline = (0, 100, 150)  # Azul oscuro para contorno
        
        # Dibujar contorno grueso
        outline_width_jym = max(3, size // 80)
        for adj in range(-outline_width_jym, outline_width_jym + 1):
            for adj2 in range(-outline_width_jym, outline_width_jym + 1):
                if abs(adj) + abs(adj2) <= outline_width_jym:
                    draw.text((x_jym + adj, y_jym + adj2), text_jym, 
                             fill=dark_blue_outline, font=font_jym)
        # Dibujar texto principal turquesa
        draw.text((x_jym, y_jym), text_jym, fill=turquoise_color, font=font_jym)
    
    return img

def main():
    print("Generando iconos para PWA...")
    print(f"Directorio de salida: {OUTPUT_DIR}")
    
    for size in SIZES:
        icon = create_icon(size)
        filename = f"{OUTPUT_DIR}/icon-{size}x{size}.png"
        icon.save(filename, "PNG")
        print(f"[OK] Creado: {filename}")
    
    print("\nIconos generados exitosamente!")
    print("Nota: Puedes reemplazar estos iconos con tus propios disenos mas adelante.")

if __name__ == "__main__":
    main()

