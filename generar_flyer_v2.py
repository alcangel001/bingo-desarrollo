from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import os

# Paths
input_path = r"C:/Users/DELL VOSTRO 7500/.gemini/antigravity/brain/04ac407c-aeee-411e-999f-4dda433f905a/latino_family_promo_flyer_layout_1763924392835.png"
qr_path = "bingo_jym_qr.png"
output_path = "flyer_final_v2.png"

def create_professional_flyer():
    try:
        img = Image.open(input_path).convert("RGBA")
        qr = Image.open(qr_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    width, height = img.size
    draw = ImageDraw.Draw(img)

    # --- CONFIGURATION ---
    # Colors
    GOLD = (255, 215, 0, 255)
    WHITE = (255, 255, 255, 255)
    BLACK_BG = (0, 0, 0, 220) # Darker, more opaque
    SHADOW = (0, 0, 0, 255)

    # Fonts - Attempt to load standard Windows fonts
    def load_font(name, size):
        try:
            return ImageFont.truetype(name, size)
        except:
            return ImageFont.load_default()

    title_font = load_font("arialbd.ttf", int(width * 0.07)) # Big Title
    tv_font = load_font("arialbd.ttf", int(width * 0.045))   # TV Text
    footer_font = load_font("arial.ttf", int(width * 0.025)) # Footer details

    # --- HELPER FUNCTIONS ---
    def draw_text_with_stroke(text, font, x, y, text_color, stroke_color, stroke_width=3):
        # Draw stroke
        for adj_x in range(-stroke_width, stroke_width+1):
            for adj_y in range(-stroke_width, stroke_width+1):
                draw.text((x+adj_x, y+adj_y), text, font=font, fill=stroke_color)
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)

    def get_centered_x(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return (width - (bbox[2] - bbox[0])) // 2

    # --- 1. HEADER: "Bingo y Rifa JyM" ---
    # Create a gradient-like header bar
    header_height = int(height * 0.12)
    header_overlay = Image.new("RGBA", (width, header_height), (0, 0, 0, 0))
    header_draw = ImageDraw.Draw(header_overlay)
    # Draw a semi-transparent black gradient (simulated with a solid block for now)
    header_draw.rectangle([0, 0, width, header_height], fill=BLACK_BG)
    img = Image.alpha_composite(img, header_overlay)
    draw = ImageDraw.Draw(img) # Re-init draw on new image

    header_text = "Bingo y Rifa JyM"
    header_x = get_centered_x(header_text, title_font)
    draw_text_with_stroke(header_text, title_font, header_x, int(header_height * 0.2), GOLD, SHADOW, 4)

    # --- 2. TV SCREEN TEXT: "Gran Rifa Equipa Tu Casa" ---
    # We assume the TV is roughly in the center. We'll create a "glow" effect box.
    tv_text = "GRAN RIFA\nEQUIPA TU CASA"
    
    # Calculate text block size
    lines = tv_text.split('\n')
    max_w = 0
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=tv_font)
        max_w = max(max_w, bbox[2] - bbox[0])
        total_h += bbox[3] - bbox[1] + 10

    # Center of image
    center_x = width // 2
    center_y = height // 2
    
    # Draw a "Screen" background behind the text to ensure readability regardless of image content
    screen_w = max_w + 60
    screen_h = total_h + 40
    screen_x1 = center_x - screen_w // 2
    screen_y1 = center_y - screen_h // 2
    
    # Semi-transparent blueish box for "TV glow"
    draw.rectangle(
        [screen_x1, screen_y1, screen_x1 + screen_w, screen_y1 + screen_h],
        fill=(0, 20, 60, 200),
        outline=(0, 100, 255, 150),
        width=4
    )

    # Draw Text
    curr_y = screen_y1 + 20
    for line in lines:
        line_x = center_x - (draw.textbbox((0, 0), line, font=tv_font)[2] - draw.textbbox((0, 0), line, font=tv_font)[0]) // 2
        draw_text_with_stroke(line, tv_font, line_x, curr_y, WHITE, SHADOW, 2)
        curr_y += draw.textbbox((0, 0), line, font=tv_font)[3] - draw.textbbox((0, 0), line, font=tv_font)[1] + 10

    # --- 3. FOOTER: Details + QR ---
    footer_text = "El sorteo se realizará al vender todos los números\ncon la lotería del Zulia Triple A 7:05 PM"
    
    # Footer background
    footer_height = int(height * 0.18)
    footer_y_start = height - footer_height
    
    footer_overlay = Image.new("RGBA", (width, footer_height), BLACK_BG)
    img.paste(footer_overlay, (0, footer_y_start), footer_overlay)
    
    # QR Code on the Right
    qr_size = int(footer_height * 0.9) # 90% of footer height
    qr = qr.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    # Add white border to QR
    qr_bg_size = qr_size + 10
    qr_bg = Image.new("RGBA", (qr_bg_size, qr_bg_size), "white")
    qr_bg.paste(qr, (5, 5), qr)
    
    qr_x = width - qr_bg_size - 20
    qr_y = footer_y_start + (footer_height - qr_bg_size) // 2
    
    img.paste(qr_bg, (qr_x, qr_y), qr_bg)

    # Footer Text (Left aligned, next to QR)
    # Wrap text to fit in the space left of QR
    text_area_width = qr_x - 40
    
    # Draw text vertically centered in footer
    lines = footer_text.split('\n')
    text_h = sum([draw.textbbox((0, 0), l, font=footer_font)[3] - draw.textbbox((0, 0), l, font=footer_font)[1] for l in lines]) + 10
    text_y = footer_y_start + (footer_height - text_h) // 2
    
    for line in lines:
        draw.text((30, text_y), line, font=footer_font, fill=WHITE)
        text_y += footer_font.getsize(line)[1] + 10 if hasattr(footer_font, 'getsize') else 40 # Fallback spacing

    # Save
    img.save(output_path)
    print(f"Flyer saved to: {output_path}")

if __name__ == "__main__":
    create_professional_flyer()
