from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from Library.DataFrame import pl

def image(df: pl.DataFrame) -> BytesIO:
    df_str = str(df)
    lines = df_str.splitlines()

    font_size = 200
    padding = 20
    background_color = "#1e1e1e"
    text_color = "#ffffff"

    font = ImageFont.truetype("consola.ttf", font_size)

    temp_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp_img)

    line_widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
    text_height = draw.textbbox((0, 0), "Ag", font=font)[3]

    width = int(max(line_widths) + 2 * padding)
    height = int(len(lines) * text_height + 2 * padding)

    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    for i, line in enumerate(lines):
        y = padding + i * text_height
        draw.text((padding, y), line, font=font, fill=text_color)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer