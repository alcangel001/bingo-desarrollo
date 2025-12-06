from PIL import Image, ImageDraw, ImageFont
import os

# Paths
background_path = r"C:/Users/DELL VOSTRO 7500/.gemini/antigravity/brain/04ac407c-aeee-411e-999f-4dda433f905a/bingo_promotion_background_1763923583910.png"
qr_path = "bingo_jym_qr.png"
output_path = "flyer_promocion_jym.png"

def create_flyer():
    # Load images
    try:
        bg = Image.open(background_path).convert("RGBA")
        qr = Image.open(qr_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    # Resize background if needed (optional, but let's keep it reasonable)
    # bg.thumbnail((1024, 1024)) # Maintain aspect ratio
    width, height = bg.size

    draw = ImageDraw.Draw(bg)

    # Fonts - Try to load Arial, fallback to default
    try:
        # Adjust font sizes based on image width
        title_size = int(width * 0.08)
        subtitle_size = int(width * 0.05)
        text_size = int(width * 0.04)
        
        font_title = ImageFont.truetype("arial.ttf", title_size)
        font_subtitle = ImageFont.truetype("arialbd.ttf", subtitle_size) # Bold
        font_text = ImageFont.truetype("arial.ttf", text_size)
    except IOError:
        print("Arial font not found, using default.")
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Colors
    text_color = (255, 255, 255, 255) # White
    shadow_color = (0, 0, 0, 200) # Black semi-transparent

    # Helper to draw text with shadow
    def draw_text_centered(text, font, y_pos, color, shadow_offset=3):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_pos = (width - text_width) // 2
        
        # Shadow
        draw.text((x_pos + shadow_offset, y_pos + shadow_offset), text, font=font, fill=shadow_color)
        # Text
        draw.text((x_pos, y_pos), text, font=font, fill=color)
        return y_pos + (text_bbox[3] - text_bbox[1]) + 20 # Return next y position

    # Draw Text
    y = height * 0.1 # Start at 10% down
    y = draw_text_centered("¡GRAN LANZAMIENTO!", font_title, y, (255, 215, 0, 255)) # Gold color
    y = draw_text_centered("BINGO Y RIFA JYM", font_subtitle, y, text_color)
    y += 20
    y = draw_text_centered("¡Regístrate y Gana!", font_text, y, text_color)
    y = draw_text_centered("Bonos de Bienvenida", font_text, y, text_color)

    # Resize and Paste QR Code
    qr_size = int(width * 0.25) # QR code 25% of width
    qr = qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    qr_x = (width - qr_size) // 2
    qr_y = int(y + 40)
    
    # Add a white background for QR if needed (for scanability)
    qr_bg_size = qr_size + 20
    qr_bg = Image.new("RGBA", (qr_bg_size, qr_bg_size), "white")
    bg.paste(qr_bg, (qr_x - 10, qr_y - 10), qr_bg)
    bg.paste(qr, (qr_x, qr_y), qr)

    # URL text below QR
    y = qr_y + qr_size + 20
    draw_text_centered("https://bingoyrifajym.com", font_text, y, text_color)

    # Save
    bg.save(output_path)
    print(f"Flyer created: {output_path}")

if __name__ == "__main__":
    create_flyer()
