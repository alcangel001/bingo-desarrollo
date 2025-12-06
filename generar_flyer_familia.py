from PIL import Image, ImageDraw, ImageFont
import textwrap

# Paths
# Using the image generated in the previous step
input_path = r"C:/Users/DELL VOSTRO 7500/.gemini/antigravity/brain/04ac407c-aeee-411e-999f-4dda433f905a/latino_family_bingo_promo_1763923975089.png"
output_path = "flyer_familia_final.png"

def create_family_flyer():
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    width, height = img.size
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        # Sizes relative to image width
        title_size = int(width * 0.06)
        tv_text_size = int(width * 0.04)
        footer_size = int(width * 0.03)
        
        font_title = ImageFont.truetype("arialbd.ttf", title_size)
        font_tv = ImageFont.truetype("arialbd.ttf", tv_text_size)
        font_footer = ImageFont.truetype("arial.ttf", footer_size)
    except IOError:
        font_title = ImageFont.load_default()
        font_tv = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Helper for centered text with shadow/outline
    def draw_text_centered(text, font, y_pos, color, bg_color=None, padding=10):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x_pos = (width - text_width) // 2
        
        if bg_color:
            # Draw background box
            draw.rectangle(
                [x_pos - padding, y_pos - padding, x_pos + text_width + padding, y_pos + text_height + padding],
                fill=bg_color
            )
        
        # Shadow
        draw.text((x_pos + 2, y_pos + 2), text, font=font, fill=(0,0,0,200))
        # Text
        draw.text((x_pos, y_pos), text, font=font, fill=color)
        return y_pos + text_height + (padding * 2)

    # 1. Top Text: "Bingo y Rifa JyM"
    # Draw a semi-transparent bar at the top for better readability
    draw.rectangle([0, 0, width, int(height * 0.15)], fill=(0, 0, 0, 100))
    draw_text_centered("Bingo y Rifa JyM", font_title, int(height * 0.04), (255, 215, 0, 255)) # Gold

    # 2. TV Text: "Gran Rifa Equipa Tu Casa"
    # Since we can't detect the TV exactly, we'll place this centrally but slightly to the side or
    # in a "screen-like" box in the middle-ish.
    # Let's try to place it in the center-left, which is a common composition for "prizes"
    # Or just center it with a "TV screen" effect.
    tv_text = "Gran Rifa\nEquipa Tu Casa"
    
    # Calculate size for multi-line
    lines = tv_text.split('\n')
    max_width = 0
    total_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_tv)
        max_width = max(max_width, bbox[2] - bbox[0])
        total_height += bbox[3] - bbox[1] + 10 # line spacing

    # Position: Let's guess the TV is somewhat central. 
    # We'll put it at 40% height, centered.
    tv_x = (width - max_width) // 2
    tv_y = int(height * 0.4)
    
    # Draw a "Screen" box (dark blue/black)
    padding = 20
    draw.rectangle(
        [tv_x - padding, tv_y - padding, tv_x + max_width + padding, tv_y + total_height + padding],
        fill=(20, 20, 30, 230), # Dark screen look
        outline=(100, 100, 100, 255),
        width=3
    )
    
    current_y = tv_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_tv)
        line_width = bbox[2] - bbox[0]
        line_x = tv_x + (max_width - line_width) // 2
        draw.text((line_x, current_y), line, font=font_tv, fill=(255, 255, 255, 255))
        current_y += bbox[3] - bbox[1] + 10

    # 3. Bottom Text
    footer_text = "El sorteo se realizará al vender todos los números con la lotería del Zulia Triple A 7:05 PM"
    
    # Wrap text if it's too long
    avg_char_width = font_footer.getlength('x')
    max_chars = int((width - 40) / avg_char_width)
    wrapped_lines = textwrap.wrap(footer_text, width=max_chars)
    
    # Draw bottom bar
    footer_height = len(wrapped_lines) * (footer_size + 10) + 40
    draw.rectangle([0, height - footer_height, width, height], fill=(0, 0, 0, 180))
    
    footer_y = height - footer_height + 20
    for line in wrapped_lines:
        draw_text_centered(line, font_footer, footer_y, (255, 255, 255, 255))
        footer_y += footer_size + 10

    img.save(output_path)
    print(f"Flyer saved to: {output_path}")

if __name__ == "__main__":
    create_family_flyer()
