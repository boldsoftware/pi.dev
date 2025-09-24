import io

from google.cloud.storage.bucket import Bucket
from PIL import Image, ImageDraw

from podcast_generator.server.autoscale_font import autoscale_font
from podcast_generator.server.gcs_utils import (
    download_with_cache,
    upload_blob_from_file,
)
from podcast_generator.server.get_shows_gcs_path import (
    get_show_logo_path,
)


def generate_podcast_image(public_bucket: Bucket, owner: str, name: str):
    img = Image.open(download_with_cache(public_bucket, "assets/logo.webp"))
    draw = ImageDraw.Draw(img)

    # The text you want to place
    user_text = name
    # The path to your font file
    font_path = download_with_cache(public_bucket, "assets/logo.ttf")

    # Set a margin (pixels) on the left and right
    margin = 20
    # We'll calculate the max width the text can occupy
    max_width = img.width - 2 * margin

    # Autoscale the font to fit into that width
    font, chosen_size = autoscale_font(user_text, font_path, draw, max_width)

    # Measure the final text size with the chosen font
    stroke_width = 3
    left, top, right, bottom = draw.textbbox(
        (0, 0), user_text, font=font, stroke_width=stroke_width
    )
    text_width = right - left
    text_height = bottom - top

    # 1) Horizontal center
    #    x = midpoint of image minus half text width
    x = (img.width - text_width) / 2

    # Center vertically within margin underneath the logo
    logo_bottom_margin = 166
    text_height_with_descenders = text_height * 1.176
    y = img.height - logo_bottom_margin / 2 - text_height_with_descenders / 2

    # Now draw the text in white
    draw.text(
        (x, y),
        user_text,
        fill=(97, 29, 97),
        font=font,
        stroke_width=stroke_width,
        stroke_fill=(255, 255, 255),
    )

    webp_buffer = io.BytesIO()
    img.save(webp_buffer, format="webp")
    webp_buffer.seek(0)
    upload_blob_from_file(
        public_bucket,
        get_show_logo_path(owner, name),
        webp_buffer,
        content_type="image/webp",
    )
