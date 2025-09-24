from PIL import ImageFont


def autoscale_font(text, font_path, draw, max_width, max_font_size=100):
    """
    Scales the font size down (starting from max_font_size) so that
    the text fits in the given max_width.
    Returns (font_object, chosen_font_size).
    """
    font_size = max_font_size
    count = 0
    while font_size > 0:
        count += 1
        font = ImageFont.truetype(font_path, font_size)
        font.set_variation_by_name("Bold")
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        if text_width <= max_width:
            return font, font_size
        font_size *= 0.98

    # Fallback if somehow nothing fits
    return ImageFont.truetype(font_path, 1), 1
