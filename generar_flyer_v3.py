from PIL import Image, ImageDraw, ImageFont
import os

# Paths
input_path = r"C:/Users/DELL VOSTRO 7500/.gemini/antigravity/brain/04ac407c-aeee-411e-999f-4dda433f905a/latino_family_promo_standard_appliances_1763924514486.png"
qr_path = "bingo_jym_qr.png"
output_path = "flyer_final_v3.png"

def create_professional_flyer():
    try:
        img = Image.open(input_path).convert("RGBA")
        qr = Image.open(qr_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    width, height = img.size
    
    # Create a separate transparent layer for alpha compositing
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # --- CONFIGURATION ---
    GOLD = (255, 215, 0, 255)
    WHITE = (255, 255, 255, 255)
    BLACK_BG = (0, 0, 0, 220) 
    SHADOW = (0, 0, 0, 255)

    # Fonts
    def load_font(name, size):
        try:
            return ImageFont.truetype(name, size)
        except:
            return ImageFont.load_default()

    title_font = load_font("arialbd.ttf", int(width * 0.07))
    tv_font = load_font("arialbd.ttf", int(width * 0.045))
    footer_font = load_font("arial.ttf", int(width * 0.025))

    # --- HELPER FUNCTIONS ---
    def draw_text_with_stroke(draw_obj, text, font, x, y, text_color, stroke_color, stroke_width=3):
        for adj_x in range(-stroke_width, stroke_width+1):
            for adj_y in range(-stroke_width, stroke_width+1):
                draw_obj.text((x+adj_x, y+adj_y), text, font=font, fill=stroke_color)
        draw_obj.text((x, y), text, font=font, fill=text_color)

    def get_centered_x(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return (width - (bbox[2] - bbox[0])) // 2

    # --- 1. HEADER ---
    header_height = int(height * 0.15)
    # Draw header background on overlay
    draw.rectangle([0, 0, width, header_height], fill=BLACK_BG)
    
    header_text = "Bingo y Rifa JyM"
    header_x = get_centered_x(header_text, title_font)
    # Draw text on overlay (or we can composite first then draw text on top, but drawing on overlay works)
    draw_text_with_stroke(draw, header_text, title_font, header_x, int(header_height * 0.3), GOLD, SHADOW, 4)

    # --- 2. TV SCREEN TEXT ---
    tv_text = "GRAN RIFA\nEQUIPA TU CASA"
    lines = tv_text.split('\n')
    
    # Calculate text block size
    max_w = 0
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=tv_font)
        max_w = max(max_w, bbox[2] - bbox[0])
        total_h += bbox[3] - bbox[1] + 10

    center_x = width // 2
    center_y = height // 2 # Approximate TV center
    
    # Screen box
    screen_w = max_w + 60
    screen_h = total_h + 40
    screen_x1 = center_x - screen_w // 2
    screen_y1 = center_y - screen_h // 2
    
    draw.rectangle(
        [screen_x1, screen_y1, screen_x1 + screen_w, screen_y1 + screen_h],
        fill=(0, 20, 60, 230), # Dark blue screen
        outline=(0, 100, 255, 180),
        width=4
    )

    curr_y = screen_y1 + 20
    for line in lines:
        line_w = draw.textbbox((0, 0), line, font=tv_font)[2] - draw.textbbox((0, 0), line, font=tv_font)[0]
        line_x = center_x - line_w // 2
        draw_text_with_stroke(draw, line, tv_font, line_x, curr_y, WHITE, SHADOW, 2)
        curr_y += draw.textbbox((0, 0), line, font=tv_font)[3] - draw.textbbox((0, 0), line, font=tv_font)[1] + 10

    # --- 3. FOOTER ---
    footer_height = int(height * 0.18)
    footer_y_start = height - footer_height
    
    draw.rectangle([0, footer_y_start, width, height], fill=BLACK_BG)

    # QR Code
    qr_size = int(footer_height * 0.9)
    qr_resized = qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    qr_bg_size = qr_size + 10
    qr_bg = Image.new("RGBA", (qr_bg_size, qr_bg_size), "white")
    qr_bg.paste(qr_resized, (5, 5), qr_resized)
    
    qr_x = width - qr_bg_size - 20
    qr_y = footer_y_start + (footer_height - qr_bg_size) // 2
    
    # We can't draw the QR on the 'overlay' easily if we want it opaque, 
    # but we can paste it on the final image later. 
    # Or just paste it on the overlay since overlay is RGBA.
    overlay.paste(qr_bg, (qr_x, qr_y))

    # Footer Text
    footer_text = "El sorteo se realizará al vender todos los números\ncon la lotería del Zulia Triple A 7:05 PM"
    lines = footer_text.split('\n')
    
    # Calculate vertical center for text
    text_h = sum([draw.textbbox((0, 0), l, font=footer_font)[3] - draw.textbbox((0, 0), l, font=footer_font)[1] for l in lines]) + 10
    text_y = footer_y_start + (footer_height - text_h) // 2
    
    for line in lines:
        draw.text((30, text_y), line, font=footer_font, fill=WHITE)
        text_y += footer_font.getsize(line)[1] + 10 if hasattr(footer_font, 'getsize') else 40

    # --- COMPOSITE ---
    final_img = Image.alpha_composite(img, overlay)
    
    final_img.save(output_path)
    print(f"Flyer saved to: {output_path}")

if __name__ == "__main__":
    create_professional_flyer()
